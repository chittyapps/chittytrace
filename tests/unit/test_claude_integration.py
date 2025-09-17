import pytest
import os
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

from claude_integration import ClaudeAnalyzer


class TestClaudeAnalyzer:

    @pytest.fixture
    def mock_env_key(self):
        """Mock environment with API key"""
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'}):
            yield

    @pytest.fixture
    def analyzer(self, mock_env_key):
        """Create ClaudeAnalyzer instance with mocked dependencies"""
        with patch('claude_integration.Anthropic') as mock_anthropic, \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings') as mock_embeddings, \
             patch('claude_integration.Chroma') as mock_chroma:

            analyzer = ClaudeAnalyzer()
            analyzer.client = mock_anthropic.return_value
            analyzer.chat_model = mock_chat.return_value
            analyzer.embeddings = mock_embeddings.return_value
            analyzer.vector_store = mock_chroma.return_value

            return analyzer

    def test_init_with_api_key(self):
        """Test initialization with provided API key"""
        with patch('claude_integration.Anthropic') as mock_anthropic, \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma'):

            analyzer = ClaudeAnalyzer(api_key="custom-key")
            assert analyzer.api_key == "custom-key"

    def test_init_with_env_api_key(self, mock_env_key):
        """Test initialization with environment API key"""
        with patch('claude_integration.Anthropic'), \
             patch('claude_integration.ChatAnthropic'), \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma'):

            analyzer = ClaudeAnalyzer()
            assert analyzer.api_key == "test-key-123"

    def test_init_without_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable not set"):
                ClaudeAnalyzer()

    def test_index_documents(self, analyzer):
        """Test document indexing"""
        documents = [
            {
                "file_path": "/test/doc1.pdf",
                "file_name": "doc1.pdf",
                "category": "financial",
                "content": "This is a test document with financial information."
            },
            {
                "file_path": "/test/doc2.txt",
                "file_name": "doc2.txt",
                "category": "legal",
                "content": "This is another test document."
            }
        ]

        # Mock text splitter
        analyzer.text_splitter = Mock()
        analyzer.text_splitter.split_text.side_effect = [
            ["Chunk 1 of doc1", "Chunk 2 of doc1"],
            ["Chunk 1 of doc2"]
        ]

        analyzer.index_documents(documents)

        # Verify vector store was called with correct documents
        analyzer.vector_store.add_documents.assert_called_once()
        call_args = analyzer.vector_store.add_documents.call_args[0][0]

        assert len(call_args) == 3  # Total chunks
        assert call_args[0].page_content == "Chunk 1 of doc1"
        assert call_args[0].metadata["file_name"] == "doc1.pdf"
        assert call_args[0].metadata["chunk_index"] == 0

    def test_index_documents_empty_content(self, analyzer):
        """Test indexing documents with empty content"""
        documents = [
            {
                "file_path": "/test/empty.pdf",
                "file_name": "empty.pdf",
                "category": "other",
                "content": ""
            }
        ]

        analyzer.index_documents(documents)

        # Should not call add_documents for empty content
        analyzer.vector_store.add_documents.assert_not_called()

    def test_search_documents(self, analyzer):
        """Test document searching"""
        mock_docs = [Mock(), Mock()]
        analyzer.vector_store.similarity_search.return_value = mock_docs

        result = analyzer.search_documents("test query", k=5)

        analyzer.vector_store.similarity_search.assert_called_once_with("test query", k=5)
        assert result == mock_docs

    def test_search_documents_default_k(self, analyzer):
        """Test document searching with default k value"""
        analyzer.search_documents("test query")
        analyzer.vector_store.similarity_search.assert_called_once_with("test query", k=10)

    @pytest.mark.asyncio
    async def test_analyze_with_context_provided_docs(self, analyzer):
        """Test analysis with provided context documents"""
        mock_docs = [
            Mock(metadata={'file_name': 'doc1.pdf'}, page_content='Content 1'),
            Mock(metadata={'file_name': 'doc2.txt'}, page_content='Content 2')
        ]

        mock_response = Mock()
        mock_response.content = "Analysis result"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer.analyze_with_context("test query", mock_docs)

        assert result == "Analysis result"
        analyzer.chat_model.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_with_context_search_docs(self, analyzer):
        """Test analysis with documents from search"""
        mock_docs = [Mock(metadata={'file_name': 'doc1.pdf'}, page_content='Content 1')]
        analyzer.vector_store.similarity_search.return_value = mock_docs

        mock_response = Mock()
        mock_response.content = "Analysis result"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer.analyze_with_context("test query")

        assert result == "Analysis result"
        analyzer.vector_store.similarity_search.assert_called_once_with("test query")

    @pytest.mark.asyncio
    async def test_generate_package(self, analyzer):
        """Test package generation"""
        requirements = {"type": "financial", "details": "test"}
        expected_package = {"summary": "test package", "documents": []}

        mock_response = Mock()
        mock_response.content = json.dumps(expected_package)
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer.generate_package("financial", requirements)

        assert result == expected_package
        analyzer.chat_model.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_package_invalid_json(self, analyzer):
        """Test package generation with invalid JSON response"""
        mock_response = Mock()
        mock_response.content = "Invalid JSON response"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer.generate_package("financial", {})

        assert result == {"raw_response": "Invalid JSON response"}

    @pytest.mark.asyncio
    async def test_fill_form(self, analyzer):
        """Test form filling"""
        form_template = "Name: [NAME]\nAmount: [AMOUNT]"
        data = {"NAME": "John Doe", "AMOUNT": "$1000"}

        mock_response = Mock()
        mock_response.content = "Name: John Doe\nAmount: $1000"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer.fill_form(form_template, data)

        assert result == "Name: John Doe\nAmount: $1000"
        analyzer.chat_model.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_analysis_command_valid(self, analyzer):
        """Test executing valid analysis command"""
        with patch.object(analyzer, '_trace_funds', new_callable=AsyncMock) as mock_trace:
            mock_trace.return_value = {"result": "fund trace"}

            result = await analyzer.execute_analysis_command("trace_funds", {"account": "123"})

            assert result == {"result": "fund trace"}
            mock_trace.assert_called_once_with({"account": "123"})

    @pytest.mark.asyncio
    async def test_execute_analysis_command_invalid(self, analyzer):
        """Test executing invalid analysis command"""
        result = await analyzer.execute_analysis_command("invalid_command", {})

        assert result == {"error": "Unknown command: invalid_command"}

    @pytest.mark.asyncio
    async def test_trace_funds(self, analyzer):
        """Test fund tracing"""
        params = {
            "source_account": "123456",
            "destination": "789012",
            "date_range": {"start": "2024-01-01", "end": "2024-01-31"}
        }

        mock_docs = [
            Mock(metadata={'file_name': 'transaction1.pdf'}, page_content='Transaction details'),
            Mock(metadata={'file_name': 'transaction2.pdf'}, page_content='More transactions')
        ]
        analyzer.vector_store.similarity_search.return_value = mock_docs

        mock_response = Mock()
        mock_response.content = "Fund trace analysis"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer._trace_funds(params)

        assert result["fund_trace"] == "Fund trace analysis"
        assert "transaction1.pdf" in result["source_documents"]
        assert "transaction2.pdf" in result["source_documents"]

    @pytest.mark.asyncio
    async def test_generate_timeline(self, analyzer):
        """Test timeline generation"""
        params = {"topic": "property transaction", "date_range": {"start": "2024-01-01", "end": "2024-12-31"}}

        mock_docs = [Mock(metadata={'file_name': 'doc1.pdf'}), Mock(metadata={'file_name': 'doc2.pdf'})]
        analyzer.vector_store.similarity_search.return_value = mock_docs

        mock_response = Mock()
        mock_response.content = "Timeline content"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer._generate_timeline(params)

        assert result["timeline"] == "Timeline content"
        assert len(result["source_documents"]) == 2

    @pytest.mark.asyncio
    async def test_analyze_transactions(self, analyzer):
        """Test transaction analysis"""
        params = {"account": "123456", "criteria": {"amount_threshold": 10000}}

        mock_docs = [Mock(metadata={'file_name': 'statement.pdf'})]
        analyzer.vector_store.similarity_search.return_value = mock_docs

        mock_response = Mock()
        mock_response.content = "Transaction analysis"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer._analyze_transactions(params)

        assert result["analysis"] == "Transaction analysis"
        assert result["source_documents"] == ["statement.pdf"]

    @pytest.mark.asyncio
    async def test_create_affidavit(self, analyzer):
        """Test affidavit creation"""
        params = {
            "affiant": "John Doe",
            "facts": ["Fact 1", "Fact 2"],
            "purpose": "Court filing"
        }

        mock_response = Mock()
        mock_response.content = "AFFIDAVIT\n\nI, John Doe, hereby swear..."
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer._create_affidavit(params)

        assert result["affidavit"] == "AFFIDAVIT\n\nI, John Doe, hereby swear..."
        assert result["metadata"]["affiant"] == "John Doe"
        assert result["metadata"]["purpose"] == "Court filing"
        assert result["metadata"]["fact_count"] == 2
        assert "created_date" in result["metadata"]

    @pytest.mark.asyncio
    async def test_compile_evidence(self, analyzer):
        """Test evidence compilation"""
        params = {
            "claim": "Tax evasion occurred",
            "evidence_types": ["financial documents", "bank statements"]
        }

        mock_docs = [Mock(metadata={'file_name': f'evidence{i}.pdf'}) for i in range(5)]
        analyzer.vector_store.similarity_search.return_value = mock_docs

        mock_response = Mock()
        mock_response.content = "Evidence compilation"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer._compile_evidence(params)

        assert result["evidence_compilation"] == "Evidence compilation"
        assert result["documents_reviewed"] == 5
        assert len(result["source_files"]) == 5

    @pytest.mark.asyncio
    async def test_calculate_penalties(self, analyzer):
        """Test penalty calculation"""
        params = {
            "tax_year": "2023",
            "amount_owed": 50000,
            "payment_date": "2024-06-01"
        }

        mock_response = Mock()
        mock_response.content = "Penalty calculation: $5,000 failure to file + $2,500 failure to pay + $1,200 interest"
        analyzer.chat_model.ainvoke = AsyncMock(return_value=mock_response)

        result = await analyzer._calculate_penalties(params)

        assert "Penalty calculation" in result["penalty_calculation"]
        assert result["parameters"] == params

    def test_generate_timeline_default_topic(self, analyzer):
        """Test timeline generation with default topic"""
        analyzer.vector_store.similarity_search.return_value = []

        # This is an internal method, so we can test it directly
        import asyncio
        async def test_timeline():
            with patch.object(analyzer.chat_model, 'ainvoke', new_callable=AsyncMock) as mock_invoke:
                mock_response = Mock()
                mock_response.content = "Timeline content"
                mock_invoke.return_value = mock_response

                result = await analyzer._generate_timeline({})
                return result

        result = asyncio.run(test_timeline())
        analyzer.vector_store.similarity_search.assert_called_with("timeline of all events", k=20)


@pytest.mark.integration
class TestClaudeAnalyzerIntegration:
    """Integration tests for ClaudeAnalyzer"""

    def test_initialization_with_real_components(self, mock_env_vars):
        """Test that analyzer initializes with real components (mocked external services)"""
        with patch('claude_integration.Anthropic') as mock_anthropic, \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings') as mock_embeddings, \
             patch('claude_integration.Chroma') as mock_chroma:

            analyzer = ClaudeAnalyzer()

            # Verify all components were initialized
            mock_anthropic.assert_called_once()
            mock_chat.assert_called_once()
            mock_embeddings.assert_called_once()
            mock_chroma.assert_called_once()

            # Verify configuration
            chat_call_args = mock_chat.call_args[1]
            assert chat_call_args['model'] == "claude-3-5-sonnet-20241022"
            assert chat_call_args['temperature'] == 0.0
            assert chat_call_args['max_tokens'] == 4096

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self, mock_env_vars):
        """Test complete analysis workflow"""
        with patch('claude_integration.Anthropic'), \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma') as mock_chroma:

            # Setup mocks
            mock_vector_store = Mock()
            mock_chroma.return_value = mock_vector_store

            mock_chat_instance = Mock()
            mock_chat.return_value = mock_chat_instance

            analyzer = ClaudeAnalyzer()
            analyzer.vector_store = mock_vector_store
            analyzer.chat_model = mock_chat_instance

            # Mock document search
            mock_doc = Mock()
            mock_doc.metadata = {'file_name': 'test.pdf'}
            mock_doc.page_content = 'Test content'
            mock_vector_store.similarity_search.return_value = [mock_doc]

            # Mock chat response
            mock_response = Mock()
            mock_response.content = "Analysis complete"
            mock_chat_instance.ainvoke = AsyncMock(return_value=mock_response)

            # Test the workflow
            result = await analyzer.analyze_with_context("What are the key findings?")

            assert result == "Analysis complete"
            mock_vector_store.similarity_search.assert_called_once()
            mock_chat_instance.ainvoke.assert_called_once()
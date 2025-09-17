"""
End-to-end workflow tests for ChittyTrace
Tests complete user workflows from document ingestion to exhibit generation
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import pandas as pd

from document_processor import DocumentProcessor
from claude_integration import ClaudeAnalyzer
from package_generator import PackageGenerator
from interactive_timeline import InteractiveTimeline
from database_handler import DatabaseHandler


@pytest.mark.e2e
class TestDocumentAnalysisWorkflow:
    """Test complete document analysis workflow"""

    @pytest.fixture
    def temp_documents_dir(self):
        """Create temporary directory with sample documents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create sample documents
            (temp_path / "bank_statement.pdf").write_text("Mock PDF content")
            (temp_path / "wire_transfer.txt").write_text("Wire transfer details: $50,000 to account 987654321")
            (temp_path / "contract.docx").write_text("Real estate purchase contract")

            # Create CSV with financial data
            csv_path = temp_path / "transactions.csv"
            df = pd.DataFrame({
                'Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
                'Amount': [50000, -25000, 1500],
                'Description': ['Deposit', 'Wire Transfer', 'Fee'],
                'Account': ['123456789', '123456789', '123456789']
            })
            df.to_csv(csv_path, index=False)

            yield temp_path

    @pytest.fixture
    def mock_claude_responses(self):
        """Mock Claude API responses for the workflow"""
        return {
            "document_analysis": "Found suspicious large cash deposits totaling $50,000",
            "timeline_extraction": json.dumps([
                {
                    "date": "2024-01-15",
                    "event": "Large cash deposit",
                    "amount": 50000,
                    "account": "123456789",
                    "type": "deposit"
                },
                {
                    "date": "2024-01-16",
                    "event": "Wire transfer to offshore account",
                    "amount": -25000,
                    "account": "123456789",
                    "type": "transfer"
                }
            ]),
            "exhibit_generation": "Exhibit A-1: Bank Statement showing suspicious activity"
        }

    @pytest.mark.asyncio
    async def test_complete_forensic_analysis_workflow(self, temp_documents_dir, mock_claude_responses):
        """Test complete forensic analysis from document scan to exhibit generation"""

        # Step 1: Initialize all components
        with patch('document_processor.BASE_DIR', temp_documents_dir):
            processor = DocumentProcessor()

        with patch('claude_integration.Anthropic') as mock_anthropic, \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma'):

            # Mock Claude responses
            mock_response = Mock()
            mock_response.content = mock_claude_responses["document_analysis"]
            mock_chat.return_value.ainvoke = AsyncMock(return_value=mock_response)

            analyzer = ClaudeAnalyzer(api_key="test-key")
            package_generator = PackageGenerator(analyzer)
            timeline_generator = InteractiveTimeline(analyzer)

        # Step 2: Scan and process documents
        with patch.object(processor, 'extract_text_from_pdf', return_value="Bank statement content"), \
             patch.object(processor, 'extract_text_from_txt', return_value="Wire transfer content"):

            documents = processor.scan_documents()

            assert len(documents) >= 3  # PDF, TXT, CSV
            assert any(doc["file_name"] == "bank_statement.pdf" for doc in documents)
            assert any(doc["file_name"] == "wire_transfer.txt" for doc in documents)
            assert any(doc["file_name"] == "transactions.csv" for doc in documents)

        # Step 3: Index documents for analysis
        analyzer.index_documents(documents)

        # Step 4: Perform natural language query
        query = "What suspicious financial activities can you identify?"

        # Mock document search
        mock_docs = [
            Mock(metadata={'file_name': 'bank_statement.pdf'}, page_content='Large deposit $50,000'),
            Mock(metadata={'file_name': 'wire_transfer.txt'}, page_content='Wire to offshore account')
        ]
        analyzer.vector_store.similarity_search.return_value = mock_docs

        analysis_result = await analyzer.analyze_with_context(query, mock_docs)

        assert "suspicious" in analysis_result.lower()
        assert "50,000" in analysis_result or "50000" in analysis_result

        # Step 5: Extract timeline events
        mock_response.content = mock_claude_responses["timeline_extraction"]

        timeline_events = await timeline_generator.extract_timeline_events(documents)

        assert len(timeline_events) >= 2
        assert any(event["type"] == "deposit" for event in timeline_events)
        assert any(event["type"] == "transfer" for event in timeline_events)

        # Step 6: Generate court exhibits
        case_info = {
            "case_number": "2024-CV-001",
            "case_caption": "People v. Defendant",
            "affiant": "Detective Smith"
        }

        mock_response.content = mock_claude_responses["exhibit_generation"]

        with patch.object(package_generator, '_save_exhibit_package', return_value="/tmp/exhibits.pdf"):
            exhibit_package = await package_generator.generate_exhibit_package(
                documents[:2],  # Use first 2 documents
                case_info,
                "Motion for Summary Judgment"
            )

        assert "exhibits" in exhibit_package
        assert "affidavit" in exhibit_package
        assert exhibit_package["case_info"]["case_number"] == "2024-CV-001"

        # Step 7: Verify complete workflow produces coherent results
        assert len(documents) > 0
        assert len(timeline_events) > 0
        assert "exhibits" in exhibit_package
        assert all(doc["content"] for doc in documents if doc["file_type"] in [".txt", ".csv"])


@pytest.mark.e2e
class TestCourtFilingWorkflow:
    """Test complete court filing preparation workflow"""

    @pytest.fixture
    def sample_case_documents(self):
        """Sample documents for court filing"""
        return [
            {
                "file_path": "/evidence/bank_statement_jan.pdf",
                "file_name": "bank_statement_jan.pdf",
                "category": "financial",
                "content": "Account 123456789 Statement January 2024\nDeposit: $75,000.00\nTransfer: -$50,000.00",
                "metadata": {"pages": 3}
            },
            {
                "file_path": "/evidence/wire_transfer_receipt.pdf",
                "file_name": "wire_transfer_receipt.pdf",
                "category": "financial",
                "content": "Wire Transfer Receipt\nAmount: $50,000.00\nDestination: Cayman Islands Bank",
                "metadata": {"pages": 1}
            },
            {
                "file_path": "/evidence/property_deed.pdf",
                "file_name": "property_deed.pdf",
                "category": "legal",
                "content": "Property Deed - 123 Main Street\nPurchase Price: $850,000.00\nDate: 2024-01-20",
                "metadata": {"pages": 2}
            }
        ]

    @pytest.mark.asyncio
    async def test_cook_county_exhibit_preparation(self, sample_case_documents):
        """Test complete Cook County exhibit preparation workflow"""

        # Initialize components with mocks
        with patch('claude_integration.Anthropic'), \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma'):

            analyzer = ClaudeAnalyzer(api_key="test-key")
            package_generator = PackageGenerator(analyzer)

        # Mock exhibit generation responses
        exhibit_responses = {
            "exhibit_a1": "EXHIBIT A-1\n\nBank Statement - January 2024\nShowing large cash deposit and subsequent wire transfer",
            "exhibit_a2": "EXHIBIT A-2\n\nWire Transfer Receipt\nShowing $50,000 transfer to offshore account",
            "exhibit_a3": "EXHIBIT A-3\n\nProperty Deed\nShowing cash purchase of luxury property",
            "affidavit": "AFFIDAVIT\n\nI, Detective Smith, hereby certify that the attached exhibits are true and accurate copies..."
        }

        mock_response = Mock()
        mock_chat.return_value.ainvoke = AsyncMock(return_value=mock_response)

        # Step 1: Analyze documents for exhibit relevance
        mock_response.content = json.dumps({
            "relevant_documents": [
                {"file_name": "bank_statement_jan.pdf", "exhibit_number": "A-1", "relevance": "Shows source of funds"},
                {"file_name": "wire_transfer_receipt.pdf", "exhibit_number": "A-2", "relevance": "Shows fund destination"},
                {"file_name": "property_deed.pdf", "exhibit_number": "A-3", "relevance": "Shows use of transferred funds"}
            ]
        })

        case_info = {
            "case_number": "2024-CV-12345",
            "case_caption": "People of Illinois v. John Doe",
            "affiant": "Detective Jane Smith",
            "court": "Cook County Circuit Court"
        }

        # Step 2: Generate individual exhibits
        with patch.object(package_generator, '_generate_individual_exhibit') as mock_gen_exhibit:
            mock_gen_exhibit.side_effect = [
                exhibit_responses["exhibit_a1"],
                exhibit_responses["exhibit_a2"],
                exhibit_responses["exhibit_a3"]
            ]

            # Step 3: Generate authentication affidavit
            mock_response.content = exhibit_responses["affidavit"]

            # Step 4: Create complete exhibit package
            with patch.object(package_generator, '_save_exhibit_package', return_value="/tmp/cook_county_exhibits.pdf"):
                exhibit_package = await package_generator.generate_exhibit_package(
                    sample_case_documents,
                    case_info,
                    "Motion for Summary Judgment - Tax Evasion Case"
                )

        # Step 5: Verify Cook County compliance
        assert exhibit_package["case_info"]["case_number"] == "2024-CV-12345"
        assert exhibit_package["case_info"]["court"] == "Cook County Circuit Court"
        assert "exhibits" in exhibit_package
        assert "affidavit" in exhibit_package
        assert len(exhibit_package["exhibits"]) == 3

        # Verify exhibit formatting
        for i, exhibit in enumerate(exhibit_package["exhibits"], 1):
            assert f"A-{i}" in exhibit or f"EXHIBIT A-{i}" in exhibit

        # Verify affidavit includes required elements
        affidavit = exhibit_package["affidavit"]
        assert "Detective Jane Smith" in affidavit
        assert "certify" in affidavit.lower()

    @pytest.mark.asyncio
    async def test_multi_jurisdiction_exhibit_workflow(self, sample_case_documents):
        """Test exhibit generation for multiple jurisdictions"""

        with patch('claude_integration.Anthropic'), \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma'):

            analyzer = ClaudeAnalyzer(api_key="test-key")
            package_generator = PackageGenerator(analyzer)

        jurisdictions = [
            {
                "name": "Cook County Circuit Court",
                "requirements": {"format": "cook_county", "numbering": "A-1, A-2, A-3"}
            },
            {
                "name": "Federal District Court",
                "requirements": {"format": "federal", "numbering": "1, 2, 3"}
            }
        ]

        mock_response = Mock()
        mock_chat.return_value.ainvoke = AsyncMock(return_value=mock_response)

        packages = []

        for jurisdiction in jurisdictions:
            case_info = {
                "case_number": f"2024-{jurisdiction['name'][:4]}-001",
                "case_caption": "Test Case v. Defendant",
                "affiant": "Officer Test",
                "court": jurisdiction["name"]
            }

            mock_response.content = f"Exhibit formatted for {jurisdiction['name']}"

            with patch.object(package_generator, '_save_exhibit_package', return_value=f"/tmp/{jurisdiction['name']}_exhibits.pdf"):
                package = await package_generator.generate_exhibit_package(
                    sample_case_documents,
                    case_info,
                    "Cross-jurisdiction filing"
                )
                packages.append(package)

        # Verify different packages were generated
        assert len(packages) == 2
        assert packages[0]["case_info"]["court"] != packages[1]["case_info"]["court"]


@pytest.mark.e2e
class TestDatabaseIntegrationWorkflow:
    """Test complete workflow with database integration"""

    @pytest.mark.asyncio
    async def test_full_database_workflow(self, mock_env_vars):
        """Test complete workflow with database storage and retrieval"""

        # Mock database
        with patch('asyncpg.create_pool') as mock_create_pool:
            mock_pool = AsyncMock()
            mock_conn = AsyncMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            mock_create_pool.return_value = mock_pool

            db_handler = DatabaseHandler("postgresql://test:test@localhost/test")
            await db_handler.initialize()

            # Mock components
            with patch('document_processor.BASE_DIR'), \
                 patch('claude_integration.Anthropic'), \
                 patch('claude_integration.ChatAnthropic') as mock_chat, \
                 patch('claude_integration.HuggingFaceEmbeddings'), \
                 patch('claude_integration.Chroma'):

                processor = DocumentProcessor()
                analyzer = ClaudeAnalyzer(api_key="test-key")

                # Mock document processing
                sample_docs = [
                    {
                        "file_path": "/test/doc1.pdf",
                        "relative_path": "doc1.pdf",
                        "file_name": "doc1.pdf",
                        "file_type": ".pdf",
                        "file_size": 1024,
                        "file_hash": "abc123",
                        "category": "financial",
                        "content": "Bank statement content",
                        "metadata": {"pages": 1},
                        "modified_time": "2024-01-15T10:00:00"
                    }
                ]

                with patch.object(processor, 'scan_documents', return_value=sample_docs):
                    # Step 1: Process and store documents
                    documents = processor.scan_documents()
                    mock_conn.fetchval.side_effect = [None, "doc_1"]  # No existing, then new ID
                    doc_ids = await db_handler.store_documents(documents)

                    assert doc_ids == ["doc_1"]

                    # Step 2: Extract and store timeline events
                    timeline_events = [
                        {
                            "date": "2024-01-15",
                            "type": "deposit",
                            "description": "Large cash deposit",
                            "amount": 50000.0,
                            "source_account": "123456789",
                            "metadata": {"branch": "downtown"},
                            "source_document_id": "doc_1"
                        }
                    ]

                    mock_conn.fetchval.return_value = "event_1"
                    event_ids = await db_handler.store_timeline_events(timeline_events)

                    assert event_ids == ["event_1"]

                    # Step 3: Perform analysis and store query
                    mock_response = Mock()
                    mock_response.content = "Analysis of suspicious financial activity"
                    mock_chat.return_value.ainvoke = AsyncMock(return_value=mock_response)

                    analyzer.vector_store.similarity_search.return_value = []
                    analysis_result = await analyzer.analyze_with_context("Find suspicious activity")

                    mock_conn.fetchval.return_value = "query_1"
                    query_id = await db_handler.store_analysis_query(
                        "Find suspicious activity",
                        analysis_result,
                        doc_ids,
                        {"model": "claude-3", "tokens": 500}
                    )

                    assert query_id == "query_1"

                    # Step 4: Generate and store exhibit
                    exhibit_data = {
                        "exhibit_number": "A-1",
                        "case_number": "2024-CV-001",
                        "case_caption": "Test Case",
                        "description": "Financial evidence",
                        "metadata": {"pages": 5},
                        "documents": [{"document_id": "doc_1"}]
                    }

                    mock_conn.fetchval.return_value = "exhibit_1"
                    exhibit_id = await db_handler.store_exhibit(exhibit_data)

                    assert exhibit_id == "exhibit_1"

                    # Step 5: Verify database interactions
                    assert mock_conn.fetchval.call_count >= 5  # Various inserts
                    assert mock_conn.execute.call_count >= 2  # Document links

                    await db_handler.close()


@pytest.mark.e2e
class TestPerformanceWorkflow:
    """Test system performance with realistic data loads"""

    @pytest.mark.asyncio
    async def test_large_document_set_processing(self):
        """Test processing large numbers of documents"""

        # Create mock large document set
        large_doc_set = []
        for i in range(100):
            large_doc_set.append({
                "file_path": f"/docs/document_{i:03d}.pdf",
                "file_name": f"document_{i:03d}.pdf",
                "category": "financial" if i % 2 == 0 else "legal",
                "content": f"Document {i} content with financial data: ${i * 1000}",
                "metadata": {"pages": i % 10 + 1},
                "file_size": 1024 * (i + 1),
                "file_hash": f"hash_{i:03d}",
                "modified_time": f"2024-01-{(i % 30) + 1:02d}T10:00:00"
            })

        with patch('claude_integration.Anthropic'), \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma'):

            analyzer = ClaudeAnalyzer(api_key="test-key")

            # Mock text splitter for performance
            analyzer.text_splitter = Mock()
            analyzer.text_splitter.split_text.return_value = ["chunk1", "chunk2"]

            # Test indexing performance
            import time
            start_time = time.time()

            analyzer.index_documents(large_doc_set)

            end_time = time.time()
            processing_time = end_time - start_time

            # Should process 100 documents reasonably quickly (< 5 seconds with mocks)
            assert processing_time < 5.0

            # Verify vector store was called appropriately
            analyzer.vector_store.add_documents.assert_called()
            call_args = analyzer.vector_store.add_documents.call_args[0][0]
            assert len(call_args) == 200  # 100 docs * 2 chunks each

    @pytest.mark.asyncio
    async def test_concurrent_analysis_workflow(self):
        """Test concurrent analysis operations"""

        with patch('claude_integration.Anthropic'), \
             patch('claude_integration.ChatAnthropic') as mock_chat, \
             patch('claude_integration.HuggingFaceEmbeddings'), \
             patch('claude_integration.Chroma'):

            analyzer = ClaudeAnalyzer(api_key="test-key")

            # Mock responses
            mock_response = Mock()
            mock_response.content = "Concurrent analysis result"
            mock_chat.return_value.ainvoke = AsyncMock(return_value=mock_response)

            # Mock search results
            analyzer.vector_store.similarity_search.return_value = [
                Mock(metadata={'file_name': 'doc.pdf'}, page_content='content')
            ]

            # Run multiple concurrent analyses
            queries = [
                "Find suspicious transactions",
                "Identify fund flows",
                "Generate timeline",
                "Extract key entities",
                "Summarize financial activity"
            ]

            tasks = [
                analyzer.analyze_with_context(query)
                for query in queries
            ]

            results = await asyncio.gather(*tasks)

            # All analyses should complete successfully
            assert len(results) == 5
            assert all(result == "Concurrent analysis result" for result in results)

            # Chat model should have been called for each query
            assert mock_chat.return_value.ainvoke.call_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
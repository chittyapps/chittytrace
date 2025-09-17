import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import os

from claude_openai_extension import app, analyzer, processor, package_generator, timeline_generator, db_handler


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_token():
    """Mock valid API token"""
    return "test-token-123"


@pytest.fixture
def auth_headers(mock_token):
    """Authentication headers"""
    return {"Authorization": f"Bearer {mock_token}"}


@pytest.fixture
def mock_services():
    """Mock all service dependencies"""
    mock_analyzer = Mock()
    mock_processor = Mock()
    mock_package_gen = Mock()
    mock_timeline_gen = Mock()
    mock_db = Mock()

    return {
        "analyzer": mock_analyzer,
        "processor": mock_processor,
        "package_generator": mock_package_gen,
        "timeline_generator": mock_timeline_gen,
        "db_handler": mock_db
    }


class TestHealthEndpoint:

    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data


class TestAuthenticationEndpoints:

    def test_endpoints_require_auth(self, client):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            ("/documents/scan", "POST"),
            ("/documents/query", "POST"),
            ("/timeline/extract", "POST"),
            ("/exhibits/generate", "POST"),
            ("/forms/fill", "POST"),
            ("/commands/execute", "POST"),
            ("/schema/cook-county", "GET")
        ]

        for endpoint, method in protected_endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)

            assert response.status_code == 403

    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected"""
        headers = {"Authorization": "Bearer invalid-token"}

        response = client.post("/documents/scan", headers=headers)
        assert response.status_code == 403

    @patch.dict(os.environ, {"API_TOKENS": "valid-token-1,valid-token-2"})
    def test_valid_token_accepted(self, client):
        """Test that valid tokens are accepted"""
        headers = {"Authorization": "Bearer valid-token-1"}

        with patch('claude_openai_extension.processor', Mock()):
            response = client.post("/documents/scan", headers=headers)
            assert response.status_code != 403


class TestDocumentEndpoints:

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_scan_documents_success(self, client, auth_headers):
        """Test successful document scanning"""
        mock_docs = [
            {"file_name": "doc1.pdf", "category": "financial"},
            {"file_name": "doc2.txt", "category": "legal"}
        ]

        with patch('claude_openai_extension.processor') as mock_processor, \
             patch('claude_openai_extension.analyzer') as mock_analyzer, \
             patch('claude_openai_extension.db_handler') as mock_db:

            mock_processor.scan_documents.return_value = mock_docs
            mock_db.store_documents = AsyncMock(return_value=["1", "2"])

            response = client.post("/documents/scan", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["result"]["documents_found"] == 2
            assert set(data["result"]["categories"]) == {"financial", "legal"}

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_scan_documents_no_processor(self, client, auth_headers):
        """Test document scanning when processor is not initialized"""
        with patch('claude_openai_extension.processor', None):
            response = client.post("/documents/scan", headers=auth_headers)

            assert response.status_code == 503
            assert "Document processor not initialized" in response.json()["detail"]

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_query_documents_success(self, client, auth_headers):
        """Test successful document querying"""
        query_data = {
            "query": "What are the suspicious transactions?",
            "limit": 5
        }

        mock_docs = [
            Mock(metadata={"file_name": "doc1.pdf"}, page_content="content1"),
            Mock(metadata={"file_name": "doc2.pdf"}, page_content="content2")
        ]

        with patch('claude_openai_extension.analyzer') as mock_analyzer:
            mock_analyzer.search_documents.return_value = mock_docs
            mock_analyzer.analyze_with_context = AsyncMock(return_value="Analysis result")

            response = client.post("/documents/query", json=query_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["result"] == "Analysis result"
            assert len(data["source_documents"]) == 2

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_query_documents_no_analyzer(self, client, auth_headers):
        """Test document querying when analyzer is not initialized"""
        query_data = {"query": "test query"}

        with patch('claude_openai_extension.analyzer', None):
            response = client.post("/documents/query", json=query_data, headers=auth_headers)

            assert response.status_code == 503
            assert "Analyzer not initialized" in response.json()["detail"]


class TestTimelineEndpoints:

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_extract_timeline_success(self, client, auth_headers):
        """Test successful timeline extraction"""
        query_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "min_amount": 1000.0
        }

        mock_events = [
            {"date": "2024-01-15", "type": "deposit", "amount": 5000.0},
            {"date": "2024-02-10", "type": "transfer", "amount": 1500.0},
            {"date": "2024-03-05", "type": "withdrawal", "amount": 500.0}  # Should be filtered out
        ]

        with patch('claude_openai_extension.analyzer'), \
             patch('claude_openai_extension.processor') as mock_processor, \
             patch('claude_openai_extension.timeline_generator') as mock_timeline:

            mock_processor.scan_documents.return_value = []
            mock_timeline.extract_timeline_events = AsyncMock(return_value=mock_events)

            response = client.post("/timeline/extract", json=query_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert len(data["result"]) == 2  # Only events >= 1000.0
            assert all(event["amount"] >= 1000.0 for event in data["result"])

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_extract_timeline_service_not_initialized(self, client, auth_headers):
        """Test timeline extraction when services are not initialized"""
        with patch('claude_openai_extension.analyzer', None):
            response = client.post("/timeline/extract", json={}, headers=auth_headers)

            assert response.status_code == 503
            assert "Services not initialized" in response.json()["detail"]


class TestExhibitEndpoints:

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_generate_exhibits_success(self, client, auth_headers):
        """Test successful exhibit generation"""
        request_data = {
            "documents": [
                {"path": "/test/doc1.pdf", "description": "Bank statement"},
                {"path": "/test/doc2.pdf", "description": "Wire transfer"}
            ],
            "case_info": {
                "case_number": "2024-CV-001",
                "caption": "Smith v. Jones",
                "affiant": "John Doe"
            },
            "purpose": "Motion for Summary Judgment",
            "cook_county_format": True
        }

        mock_package = {
            "exhibits": ["A-1", "A-2"],
            "saved_path": "/exhibits/package.pdf"
        }

        with patch('claude_openai_extension.package_generator') as mock_generator:
            mock_generator.generate_exhibit_package = AsyncMock(return_value=mock_package)

            response = client.post("/exhibits/generate", json=request_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["result"] == mock_package
            assert data["metadata"]["package_path"] == "/exhibits/package.pdf"

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_generate_exhibits_no_generator(self, client, auth_headers):
        """Test exhibit generation when generator is not initialized"""
        request_data = {
            "documents": [],
            "case_info": {},
            "purpose": "test"
        }

        with patch('claude_openai_extension.package_generator', None):
            response = client.post("/exhibits/generate", json=request_data, headers=auth_headers)

            assert response.status_code == 503
            assert "Package generator not initialized" in response.json()["detail"]


class TestFormEndpoints:

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_fill_form_success(self, client, auth_headers):
        """Test successful form filling"""
        request_data = {
            "template": "Name: [NAME]\nDate: [DATE]",
            "data": {"NAME": "John Doe", "DATE": "2024-01-15"},
            "form_type": "affidavit"
        }

        filled_form = "Name: John Doe\nDate: 2024-01-15"

        with patch('claude_openai_extension.analyzer') as mock_analyzer:
            mock_analyzer.fill_form = AsyncMock(return_value=filled_form)

            response = client.post("/forms/fill", json=request_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["result"] == filled_form
            assert data["metadata"]["form_type"] == "affidavit"

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_fill_form_no_analyzer(self, client, auth_headers):
        """Test form filling when analyzer is not initialized"""
        request_data = {
            "template": "test template",
            "data": {}
        }

        with patch('claude_openai_extension.analyzer', None):
            response = client.post("/forms/fill", json=request_data, headers=auth_headers)

            assert response.status_code == 503
            assert "Analyzer not initialized" in response.json()["detail"]


class TestCommandEndpoints:

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_execute_command_success(self, client, auth_headers):
        """Test successful command execution"""
        request_data = {
            "command": "trace_funds",
            "parameters": {
                "source_account": "123456",
                "amount": 50000
            }
        }

        command_result = {
            "fund_trace": "Funds traced from account 123456",
            "transactions": 5
        }

        with patch('claude_openai_extension.analyzer') as mock_analyzer:
            mock_analyzer.execute_analysis_command = AsyncMock(return_value=command_result)

            response = client.post("/commands/execute", json=request_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["result"] == command_result

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_execute_command_no_analyzer(self, client, auth_headers):
        """Test command execution when analyzer is not initialized"""
        request_data = {
            "command": "test_command",
            "parameters": {}
        }

        with patch('claude_openai_extension.analyzer', None):
            response = client.post("/commands/execute", json=request_data, headers=auth_headers)

            assert response.status_code == 503
            assert "Analyzer not initialized" in response.json()["detail"]


class TestSchemaEndpoints:

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_cook_county_requirements(self, client, auth_headers):
        """Test Cook County requirements endpoint"""
        response = client.get("/schema/cook-county", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "exhibit_requirements" in data
        assert "package_requirements" in data
        assert data["exhibit_requirements"]["page_size"] == "8.5x11 inches"
        assert data["exhibit_requirements"]["font"] == "Times New Roman or Arial, 12pt"

    def test_openai_functions_schema(self, client):
        """Test OpenAI functions schema endpoint"""
        response = client.get("/openai/functions")

        assert response.status_code == 200
        functions = response.json()
        assert isinstance(functions, list)
        assert len(functions) >= 3

        # Check for required functions
        function_names = [f["name"] for f in functions]
        assert "query_documents" in function_names
        assert "extract_timeline" in function_names
        assert "generate_exhibits" in function_names

    def test_claude_tools_schema(self, client):
        """Test Claude tools schema endpoint"""
        response = client.get("/claude/tools")

        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) >= 1

        tool = data["tools"][0]
        assert tool["name"] == "flow_analyzer"
        assert "input_schema" in tool
        assert "action" in tool["input_schema"]["properties"]


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API endpoints"""

    @patch.dict(os.environ, {"API_TOKENS": "integration-token"})
    def test_full_document_workflow(self, client):
        """Test complete document analysis workflow"""
        auth_headers = {"Authorization": "Bearer integration-token"}

        # Mock all services
        with patch('claude_openai_extension.processor') as mock_processor, \
             patch('claude_openai_extension.analyzer') as mock_analyzer, \
             patch('claude_openai_extension.db_handler') as mock_db:

            # Setup mocks
            mock_docs = [{"file_name": "test.pdf", "category": "financial"}]
            mock_processor.scan_documents.return_value = mock_docs
            mock_db.store_documents = AsyncMock(return_value=["1"])

            mock_search_docs = [Mock(metadata={"file_name": "test.pdf"}, page_content="content")]
            mock_analyzer.search_documents.return_value = mock_search_docs
            mock_analyzer.analyze_with_context = AsyncMock(return_value="Analysis complete")

            # Step 1: Scan documents
            scan_response = client.post("/documents/scan", headers=auth_headers)
            assert scan_response.status_code == 200

            # Step 2: Query documents
            query_data = {"query": "Show me the transactions"}
            query_response = client.post("/documents/query", json=query_data, headers=auth_headers)
            assert query_response.status_code == 200

            # Verify workflow
            mock_processor.scan_documents.assert_called()
            mock_analyzer.index_documents.assert_called_with(mock_docs)
            mock_analyzer.search_documents.assert_called_with("Show me the transactions", k=10)

    @patch.dict(os.environ, {"API_TOKENS": "integration-token"})
    def test_exhibit_generation_workflow(self, client):
        """Test exhibit generation workflow"""
        auth_headers = {"Authorization": "Bearer integration-token"}

        with patch('claude_openai_extension.package_generator') as mock_generator:
            mock_package = {
                "exhibits": ["A-1", "A-2"],
                "affidavit": "I hereby certify...",
                "saved_path": "/exhibits/package.pdf"
            }
            mock_generator.generate_exhibit_package = AsyncMock(return_value=mock_package)

            request_data = {
                "documents": [{"path": "/test.pdf", "description": "Evidence"}],
                "case_info": {"case_number": "2024-CV-001", "caption": "Test Case"},
                "purpose": "Motion"
            }

            response = client.post("/exhibits/generate", json=request_data, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "exhibits" in data["result"]

            mock_generator.generate_exhibit_package.assert_called_once()

    def test_error_handling_consistency(self, client):
        """Test consistent error handling across endpoints"""
        # Test without authentication
        endpoints_to_test = [
            ("/documents/scan", "POST", {}),
            ("/documents/query", "POST", {"query": "test"}),
            ("/timeline/extract", "POST", {}),
            ("/exhibits/generate", "POST", {"documents": [], "case_info": {}, "purpose": "test"}),
            ("/forms/fill", "POST", {"template": "test", "data": {}}),
            ("/commands/execute", "POST", {"command": "test", "parameters": {}})
        ]

        for endpoint, method, data in endpoints_to_test:
            if method == "POST":
                response = client.post(endpoint, json=data)
            else:
                response = client.get(endpoint)

            assert response.status_code == 403
            assert "detail" in response.json()

    @patch.dict(os.environ, {"API_TOKENS": "test-token"})
    def test_service_initialization_checks(self, client):
        """Test that endpoints properly check service initialization"""
        auth_headers = {"Authorization": "Bearer test-token"}

        # Test with all services disabled
        with patch('claude_openai_extension.processor', None), \
             patch('claude_openai_extension.analyzer', None), \
             patch('claude_openai_extension.package_generator', None):

            # Document scan should fail
            response = client.post("/documents/scan", headers=auth_headers)
            assert response.status_code == 503

            # Document query should fail
            response = client.post("/documents/query", json={"query": "test"}, headers=auth_headers)
            assert response.status_code == 503

            # Form fill should fail
            response = client.post("/forms/fill", json={"template": "test", "data": {}}, headers=auth_headers)
            assert response.status_code == 503
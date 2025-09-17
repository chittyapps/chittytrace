import pytest
import asyncio
import json
from datetime import datetime, date
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncpg
import numpy as np

from database_handler import DatabaseHandler


class TestDatabaseHandler:

    @pytest.fixture
    def database_url(self):
        """Database URL for testing"""
        return "postgresql://test:test@localhost:5432/test_db"

    @pytest.fixture
    def handler(self, database_url):
        """Create DatabaseHandler instance"""
        return DatabaseHandler(database_url)

    @pytest.fixture
    def mock_pool(self):
        """Mock asyncpg connection pool"""
        pool = AsyncMock()
        conn = AsyncMock()
        pool.acquire.return_value.__aenter__.return_value = conn
        return pool, conn

    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing"""
        return [
            {
                "file_path": "/test/doc1.pdf",
                "relative_path": "doc1.pdf",
                "file_name": "doc1.pdf",
                "file_type": ".pdf",
                "file_size": 1024,
                "file_hash": "abc123",
                "category": "financial",
                "content": "Sample document content",
                "metadata": {"pages": 1},
                "modified_time": "2024-01-15T10:00:00"
            },
            {
                "file_path": "/test/doc2.txt",
                "relative_path": "doc2.txt",
                "file_name": "doc2.txt",
                "file_type": ".txt",
                "file_size": 512,
                "file_hash": "def456",
                "category": "legal",
                "content": "Legal document content",
                "metadata": {"lines": 50},
                "modified_time": "2024-01-16T11:00:00"
            }
        ]

    @pytest.fixture
    def sample_timeline_events(self):
        """Sample timeline events for testing"""
        return [
            {
                "date": "2024-01-15",
                "type": "deposit",
                "description": "Large cash deposit",
                "amount": 15000.00,
                "source_account": "12345678",
                "destination_account": "87654321",
                "source_institution": "Bank A",
                "destination_institution": "Bank B",
                "reference_number": "REF123",
                "metadata": {"branch": "downtown"},
                "source_document_id": "1"
            },
            {
                "date": "2024-01-16",
                "type": "transfer",
                "description": "Wire transfer",
                "amount": 12000.00,
                "source_account": "87654321",
                "destination_account": "99887766",
                "source_institution": "Bank B",
                "destination_institution": "Bank C",
                "reference_number": "REF456",
                "metadata": {"purpose": "business"},
                "source_document_id": "2"
            }
        ]

    def test_init(self, handler, database_url):
        """Test DatabaseHandler initialization"""
        assert handler.database_url == database_url
        assert handler.pool is None
        assert handler.neon_integration is None

    @pytest.mark.asyncio
    async def test_initialize_success(self, handler):
        """Test successful database initialization"""
        mock_pool = AsyncMock()
        mock_neon = AsyncMock()

        with patch('asyncpg.create_pool', return_value=mock_pool) as mock_create_pool, \
             patch.object(handler, 'ensure_schema') as mock_ensure_schema, \
             patch('database_handler.NeonIntegration', return_value=mock_neon) as mock_neon_class:

            await handler.initialize()

            mock_create_pool.assert_called_once_with(
                handler.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            mock_ensure_schema.assert_called_once()
            mock_neon_class.assert_called_once_with(handler.database_url)
            mock_neon.initialize.assert_called_once()

            assert handler.pool == mock_pool
            assert handler.neon_integration == mock_neon

    @pytest.mark.asyncio
    async def test_initialize_failure(self, handler):
        """Test database initialization failure"""
        with patch('asyncpg.create_pool', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception, match="Connection failed"):
                await handler.initialize()

    @pytest.mark.asyncio
    async def test_ensure_schema_with_file(self, handler):
        """Test schema creation when schema file exists"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        schema_sql = "CREATE TABLE test (id INTEGER);"

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open_with_content(schema_sql)):

            await handler.ensure_schema()

            mock_conn.execute.assert_called_once_with(schema_sql)

    @pytest.mark.asyncio
    async def test_ensure_schema_without_file(self, handler):
        """Test schema creation when schema file doesn't exist"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        with patch('pathlib.Path.exists', return_value=False):
            await handler.ensure_schema()

            mock_conn.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_schema_error(self, handler):
        """Test schema creation error handling"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool
        mock_conn.execute.side_effect = Exception("Schema error")

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open_with_content("CREATE TABLE test;")), \
             patch('database_handler.logger') as mock_logger:

            await handler.ensure_schema()

            mock_logger.warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, handler):
        """Test database connection closure"""
        mock_pool = AsyncMock()
        mock_neon = AsyncMock()
        handler.pool = mock_pool
        handler.neon_integration = mock_neon

        await handler.close()

        mock_pool.close.assert_called_once()
        mock_neon.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_pool(self, handler):
        """Test closure when no pool exists"""
        await handler.close()  # Should not raise an exception

    @pytest.mark.asyncio
    async def test_store_documents_new(self, handler, sample_documents):
        """Test storing new documents"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        # Mock no existing documents
        mock_conn.fetchval.side_effect = [None, "1", None, "2"]

        result = await handler.store_documents(sample_documents)

        assert result == ["1", "2"]
        assert mock_conn.fetchval.call_count == 4  # 2 existence checks + 2 inserts

    @pytest.mark.asyncio
    async def test_store_documents_existing(self, handler, sample_documents):
        """Test storing documents when they already exist"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        # Mock existing documents
        mock_conn.fetchval.side_effect = ["1", "2"]

        result = await handler.store_documents(sample_documents)

        assert result == ["1", "2"]
        assert mock_conn.fetchval.call_count == 2  # Only existence checks

    @pytest.mark.asyncio
    async def test_store_documents_error_handling(self, handler, sample_documents):
        """Test error handling during document storage"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        mock_conn.fetchval.side_effect = Exception("Database error")

        with patch('database_handler.logger') as mock_logger:
            result = await handler.store_documents(sample_documents)

            assert result == []
            assert mock_logger.error.call_count == 2

    @pytest.mark.asyncio
    async def test_store_timeline_events(self, handler, sample_timeline_events):
        """Test storing timeline events"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        mock_conn.fetchval.side_effect = ["1", "2"]

        result = await handler.store_timeline_events(sample_timeline_events)

        assert result == ["1", "2"]
        assert mock_conn.fetchval.call_count == 2
        assert mock_conn.execute.call_count == 2  # Document links

    @pytest.mark.asyncio
    async def test_store_timeline_events_without_document_link(self, handler):
        """Test storing timeline events without document links"""
        events = [
            {
                "date": "2024-01-15",
                "type": "deposit",
                "description": "Cash deposit",
                "amount": 1000.00,
                "metadata": {}
            }
        ]

        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool
        mock_conn.fetchval.return_value = "1"

        result = await handler.store_timeline_events(events)

        assert result == ["1"]
        assert mock_conn.fetchval.call_count == 1
        assert mock_conn.execute.call_count == 0  # No document links

    @pytest.mark.asyncio
    async def test_store_exhibit(self, handler):
        """Test storing court exhibit"""
        exhibit_data = {
            "exhibit_number": "A-1",
            "case_number": "2024-CV-001",
            "case_caption": "Smith v. Jones",
            "description": "Bank statements",
            "metadata": {"pages": 5},
            "documents": [
                {"document_id": "1"},
                {"document_id": "2"}
            ]
        }

        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool
        mock_conn.fetchval.return_value = "exhibit_1"

        result = await handler.store_exhibit(exhibit_data)

        assert result == "exhibit_1"
        assert mock_conn.fetchval.call_count == 1
        assert mock_conn.execute.call_count == 2  # Document links

    @pytest.mark.asyncio
    async def test_store_analysis_query(self, handler):
        """Test storing analysis query"""
        query = "What are the suspicious transactions?"
        response = "Found 3 suspicious transactions..."
        documents = ["1", "2", "3"]
        metadata = {"model": "claude-3", "tokens_used": 500}

        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool
        mock_conn.fetchval.return_value = "query_1"

        result = await handler.store_analysis_query(query, response, documents, metadata)

        assert result == "query_1"
        assert mock_conn.fetchval.call_count == 1
        assert mock_conn.execute.call_count == 3  # Document links

    @pytest.mark.asyncio
    async def test_get_fund_flow_summary_no_dates(self, handler):
        """Test getting fund flow summary without date filters"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        mock_rows = [
            {"event_date": date(2024, 1, 15), "amount": 1000.00, "type": "deposit"},
            {"event_date": date(2024, 1, 16), "amount": -500.00, "type": "withdrawal"}
        ]
        mock_conn.fetch.return_value = mock_rows

        result = await handler.get_fund_flow_summary()

        assert len(result) == 2
        assert result[0]["amount"] == 1000.00
        assert result[1]["amount"] == -500.00

    @pytest.mark.asyncio
    async def test_get_fund_flow_summary_with_dates(self, handler):
        """Test getting fund flow summary with date filters"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool
        mock_conn.fetch.return_value = []

        await handler.get_fund_flow_summary(
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # Verify query was called with date parameters
        args, kwargs = mock_conn.fetch.call_args
        assert len(args) == 3  # query + 2 date parameters
        assert "event_date >=" in args[0]
        assert "event_date <=" in args[0]

    @pytest.mark.asyncio
    async def test_search_documents_vector(self, handler):
        """Test vector-based document search"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        query_vector = np.array([0.1, 0.2, 0.3, 0.4])
        mock_rows = [
            {"id": "1", "file_name": "doc1.pdf", "distance": 0.1},
            {"id": "2", "file_name": "doc2.pdf", "distance": 0.2}
        ]
        mock_conn.fetch.return_value = mock_rows

        result = await handler.search_documents_vector(query_vector, limit=5)

        assert len(result) == 2
        assert result[0]["file_name"] == "doc1.pdf"
        assert result[1]["file_name"] == "doc2.pdf"

        # Verify vector was converted to list
        args, kwargs = mock_conn.fetch.call_args
        assert args[1] == query_vector.tolist()
        assert args[2] == 5

    @pytest.mark.asyncio
    async def test_get_exhibit_package_exists(self, handler):
        """Test getting existing exhibit package"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool

        package_row = {
            "id": "pkg_1",
            "case_number": "2024-CV-001",
            "title": "Financial Evidence Package"
        }
        exhibit_rows = [
            {"id": "ex_1", "exhibit_number": "A-1", "order_number": 1},
            {"id": "ex_2", "exhibit_number": "A-2", "order_number": 2}
        ]

        mock_conn.fetchrow.return_value = package_row
        mock_conn.fetch.return_value = exhibit_rows

        result = await handler.get_exhibit_package("pkg_1")

        assert result["id"] == "pkg_1"
        assert result["case_number"] == "2024-CV-001"
        assert len(result["exhibits"]) == 2
        assert result["exhibits"][0]["exhibit_number"] == "A-1"

    @pytest.mark.asyncio
    async def test_get_exhibit_package_not_exists(self, handler):
        """Test getting non-existent exhibit package"""
        mock_pool, mock_conn = self.create_mock_pool()
        handler.pool = mock_pool
        mock_conn.fetchrow.return_value = None

        result = await handler.get_exhibit_package("nonexistent")

        assert result is None

    def create_mock_pool(self):
        """Helper to create mock pool and connection"""
        pool = AsyncMock()
        conn = AsyncMock()
        pool.acquire.return_value.__aenter__.return_value = conn
        return pool, conn


def mock_open_with_content(content):
    """Helper to create mock open with specific content"""
    from unittest.mock import mock_open
    return mock_open(read_data=content)


@pytest.mark.integration
class TestDatabaseHandlerIntegration:
    """Integration tests for DatabaseHandler"""

    @pytest.mark.asyncio
    async def test_full_workflow_simulation(self, mock_env_vars):
        """Test complete database workflow simulation"""
        handler = DatabaseHandler("postgresql://test:test@localhost/test")

        # Mock all external dependencies
        with patch('asyncpg.create_pool') as mock_create_pool, \
             patch('database_handler.NeonIntegration') as mock_neon:

            mock_pool = AsyncMock()
            mock_conn = AsyncMock()
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
            mock_create_pool.return_value = mock_pool

            # Initialize
            await handler.initialize()

            # Test document storage
            docs = [{
                "file_path": "/test.pdf",
                "relative_path": "test.pdf",
                "file_name": "test.pdf",
                "file_type": ".pdf",
                "file_size": 1024,
                "file_hash": "abc123",
                "category": "financial",
                "content": "content",
                "metadata": {},
                "modified_time": "2024-01-15T10:00:00"
            }]

            mock_conn.fetchval.side_effect = [None, "1"]  # No existing, then new ID

            doc_ids = await handler.store_documents(docs)
            assert doc_ids == ["1"]

            # Test timeline events
            events = [{
                "date": "2024-01-15",
                "type": "deposit",
                "description": "Test deposit",
                "amount": 1000.00,
                "metadata": {}
            }]

            mock_conn.fetchval.return_value = "event_1"

            event_ids = await handler.store_timeline_events(events)
            assert event_ids == ["event_1"]

            # Test analysis query storage
            mock_conn.fetchval.return_value = "query_1"

            query_id = await handler.store_analysis_query(
                "test query", "test response", ["1"], {"model": "claude"}
            )
            assert query_id == "query_1"

            # Close
            await handler.close()

            # Verify initialization calls
            mock_create_pool.assert_called_once()
            mock_neon.assert_called_once()

    def test_database_url_validation(self):
        """Test database URL validation"""
        # Valid URL
        handler = DatabaseHandler("postgresql://user:pass@host:5432/db")
        assert handler.database_url == "postgresql://user:pass@host:5432/db"

        # Empty URL should still work (will fail on connection)
        handler2 = DatabaseHandler("")
        assert handler2.database_url == ""
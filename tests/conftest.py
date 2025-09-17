import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime

from config import BASE_DIR


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'test-key-123',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test_db',
        'CLOUDFLARE_WORKER_URL': 'https://test.workers.dev/email',
        'CLOUDFLARE_WORKER_TOKEN': 'test-token-123'
    }):
        yield


@pytest.fixture
def sample_pdf_content():
    """Sample PDF text content for testing"""
    return "This is a sample PDF document with financial information. Account: 12345678. Amount: $1,500.00. Date: 2024-01-15."


@pytest.fixture
def sample_excel_data():
    """Sample Excel data for testing"""
    return pd.DataFrame({
        'Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'Account': ['12345678', '87654321', '12345678'],
        'Amount': [1500.00, -250.00, 75.50],
        'Description': ['Deposit', 'Withdrawal', 'Fee']
    })


@pytest.fixture
def sample_document_metadata():
    """Sample document metadata for testing"""
    return {
        'file_path': '/test/document.pdf',
        'file_name': 'document.pdf',
        'file_size': 1024,
        'file_type': 'pdf',
        'modified_date': datetime(2024, 1, 15),
        'hash': 'abc123def456',
        'content': 'Sample document content',
        'page_count': 1
    }


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic Claude client"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Mocked Claude response")]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None
    return mock_conn


@pytest.fixture
def sample_timeline_events():
    """Sample timeline events for testing"""
    return [
        {
            'date': '2024-01-15',
            'event': 'Large deposit received',
            'amount': 15000.00,
            'account': '12345678',
            'source_document': 'bank_statement.pdf'
        },
        {
            'date': '2024-01-16',
            'event': 'Wire transfer sent',
            'amount': -12000.00,
            'account': '12345678',
            'source_document': 'wire_transfer.pdf'
        }
    ]
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pandas as pd
from datetime import datetime

from document_processor import DocumentProcessor


class TestDocumentProcessor:

    @pytest.fixture
    def processor(self, temp_dir):
        """Create DocumentProcessor instance with temporary cache directory"""
        with patch('document_processor.CACHE_DIR', temp_dir / 'cache'):
            processor = DocumentProcessor()
            return processor

    @pytest.fixture
    def sample_file(self, temp_dir):
        """Create a sample file for testing"""
        file_path = temp_dir / "sample.txt"
        file_path.write_text("Sample file content for testing", encoding='utf-8')
        return file_path

    def test_init_creates_cache_directory(self, temp_dir):
        """Test that __init__ creates cache directory"""
        cache_dir = temp_dir / 'test_cache'
        with patch('document_processor.CACHE_DIR', cache_dir):
            processor = DocumentProcessor()
            assert cache_dir.exists()
            assert processor.cache_dir == cache_dir

    def test_get_file_hash(self, processor, sample_file):
        """Test file hash generation"""
        hash1 = processor.get_file_hash(sample_file)
        hash2 = processor.get_file_hash(sample_file)

        # Same file should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hex digest length
        assert isinstance(hash1, str)

    def test_get_file_hash_different_files(self, processor, temp_dir):
        """Test that different files produce different hashes"""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("Content 1")
        file2.write_text("Content 2")

        hash1 = processor.get_file_hash(file1)
        hash2 = processor.get_file_hash(file2)

        assert hash1 != hash2

    def test_get_cache_path(self, processor, sample_file):
        """Test cache path generation"""
        cache_path = processor.get_cache_path(sample_file)

        assert cache_path.parent == processor.cache_dir
        assert cache_path.suffix == '.json'
        assert len(cache_path.stem) == 32  # MD5 hash length

    def test_save_and_load_cache(self, processor, sample_file):
        """Test saving and loading cache data"""
        test_data = {
            'file_path': str(sample_file),
            'content': 'test content',
            'timestamp': datetime.now().isoformat()
        }

        # Save to cache
        processor.save_to_cache(sample_file, test_data)

        # Load from cache
        loaded_data = processor.load_from_cache(sample_file)

        assert loaded_data == test_data

    def test_load_from_cache_nonexistent(self, processor, sample_file):
        """Test loading from cache when cache doesn't exist"""
        result = processor.load_from_cache(sample_file)
        assert result is None

    @patch('document_processor.logger')
    def test_load_from_cache_invalid_json(self, mock_logger, processor, sample_file):
        """Test loading from cache with invalid JSON"""
        # Create invalid JSON cache file
        cache_path = processor.get_cache_path(sample_file)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("invalid json content")

        result = processor.load_from_cache(sample_file)

        assert result is None
        mock_logger.warning.assert_called_once()

    @patch('document_processor.logger')
    def test_save_to_cache_error_handling(self, mock_logger, processor, sample_file):
        """Test error handling when saving to cache fails"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            processor.save_to_cache(sample_file, {'test': 'data'})
            mock_logger.warning.assert_called_once()

    @patch('pdfplumber.open')
    def test_extract_text_from_pdf_success(self, mock_pdfplumber, processor, temp_dir):
        """Test successful PDF text extraction with pdfplumber"""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.touch()

        # Mock pdfplumber
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page 1 content"
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

        result = processor.extract_text_from_pdf(pdf_file)

        assert result == "Page 1 content"
        mock_pdfplumber.assert_called_once_with(pdf_file)

    @patch('pdfplumber.open')
    @patch('pypdf2.PdfReader')
    @patch('document_processor.logger')
    def test_extract_text_from_pdf_fallback_to_pypdf2(self, mock_logger, mock_pypdf2, mock_pdfplumber, processor, temp_dir):
        """Test PDF text extraction fallback to PyPDF2"""
        pdf_file = temp_dir / "test.pdf"
        pdf_file.touch()

        # Mock pdfplumber to fail
        mock_pdfplumber.side_effect = Exception("pdfplumber error")

        # Mock PyPDF2
        mock_page = Mock()
        mock_page.extract_text.return_value = "PyPDF2 content"
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pypdf2.return_value = mock_reader

        with patch('builtins.open', mock_open(read_data=b"pdf content")):
            result = processor.extract_text_from_pdf(pdf_file)

        assert result == "PyPDF2 content"
        mock_logger.warning.assert_called_once()

    @patch('pandas.read_excel')
    def test_extract_text_from_excel_success(self, mock_read_excel, processor, temp_dir):
        """Test successful Excel text extraction"""
        excel_file = temp_dir / "test.xlsx"
        excel_file.touch()

        # Mock pandas read_excel
        mock_df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        mock_read_excel.return_value = {'Sheet1': mock_df}

        result = processor.extract_text_from_excel(excel_file)

        assert "Sheet: Sheet1" in result
        assert "1" in result and "2" in result and "3" in result and "4" in result
        mock_read_excel.assert_called_once_with(excel_file, sheet_name=None)

    @patch('pandas.read_excel')
    @patch('document_processor.logger')
    def test_extract_text_from_excel_error(self, mock_logger, mock_read_excel, processor, temp_dir):
        """Test Excel text extraction error handling"""
        excel_file = temp_dir / "test.xlsx"
        excel_file.touch()

        mock_read_excel.side_effect = Exception("Excel read error")

        result = processor.extract_text_from_excel(excel_file)

        assert result == ""
        mock_logger.error.assert_called_once()

    @patch('pandas.read_csv')
    def test_extract_text_from_csv_success(self, mock_read_csv, processor, temp_dir):
        """Test successful CSV text extraction"""
        csv_file = temp_dir / "test.csv"
        csv_file.touch()

        mock_df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        mock_read_csv.return_value = mock_df

        result = processor.extract_text_from_csv(csv_file)

        assert "1" in result and "2" in result and "3" in result and "4" in result
        mock_read_csv.assert_called_once_with(csv_file)

    @patch('pandas.read_csv')
    @patch('document_processor.logger')
    def test_extract_text_from_csv_error(self, mock_logger, mock_read_csv, processor, temp_dir):
        """Test CSV text extraction error handling"""
        csv_file = temp_dir / "test.csv"
        csv_file.touch()

        mock_read_csv.side_effect = Exception("CSV read error")

        result = processor.extract_text_from_csv(csv_file)

        assert result == ""
        mock_logger.error.assert_called_once()

    @patch('chardet.detect')
    def test_extract_text_from_txt_success(self, mock_detect, processor, temp_dir):
        """Test successful text file extraction"""
        txt_file = temp_dir / "test.txt"
        content = "Test text file content"
        txt_file.write_text(content, encoding='utf-8')

        mock_detect.return_value = {'encoding': 'utf-8'}

        result = processor.extract_text_from_txt(txt_file)

        assert result == content

    @patch('chardet.detect')
    @patch('document_processor.logger')
    def test_extract_text_from_txt_error(self, mock_logger, mock_detect, processor, temp_dir):
        """Test text file extraction error handling"""
        txt_file = temp_dir / "test.txt"
        txt_file.touch()

        mock_detect.side_effect = Exception("Encoding detection error")

        result = processor.extract_text_from_txt(txt_file)

        assert result == ""
        mock_logger.error.assert_called_once()

    @patch('document_processor.BASE_DIR')
    def test_process_document_pdf(self, mock_base_dir, processor, temp_dir):
        """Test processing a PDF document"""
        mock_base_dir.__truediv__ = lambda self, other: temp_dir / other
        mock_base_dir.__str__ = lambda self: str(temp_dir)

        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("dummy pdf content")

        with patch.object(processor, 'extract_text_from_pdf', return_value="PDF content"):
            with patch.object(processor, '_determine_category', return_value="financial"):
                result = processor.process_document(pdf_file)

        assert result['file_name'] == 'test.pdf'
        assert result['file_type'] == '.pdf'
        assert result['content'] == 'PDF content'
        assert result['category'] == 'financial'
        assert 'modified_time' in result
        assert 'file_size' in result

    def test_process_document_uses_cache(self, processor, temp_dir):
        """Test that process_document uses cache when available"""
        sample_file = temp_dir / "test.txt"
        sample_file.write_text("content")

        cached_data = {'cached': True, 'content': 'cached content'}

        with patch.object(processor, 'load_from_cache', return_value=cached_data):
            result = processor.process_document(sample_file)

        assert result == cached_data

    @patch('document_processor.DOCUMENT_CATEGORIES', {
        'financial': {'paths': ['bank/', 'statements/']},
        'legal': {'paths': ['contracts/', 'agreements/']}
    })
    def test_determine_category(self, processor):
        """Test document category determination"""
        assert processor._determine_category(Path('bank/statement.pdf')) == 'financial'
        assert processor._determine_category(Path('statements/account.xlsx')) == 'financial'
        assert processor._determine_category(Path('contracts/service.pdf')) == 'legal'
        assert processor._determine_category(Path('random/file.txt')) == 'other'

    @patch('document_processor.SUPPORTED_FILE_TYPES', ['.txt', '.pdf'])
    @patch('document_processor.BASE_DIR')
    def test_scan_documents(self, mock_base_dir, processor, temp_dir):
        """Test scanning multiple documents"""
        mock_base_dir.rglob = lambda pattern: [
            temp_dir / 'file1.txt',
            temp_dir / 'file2.pdf',
            temp_dir / '.hidden.txt'  # Should be skipped
        ]

        # Create test files
        (temp_dir / 'file1.txt').write_text("content1")
        (temp_dir / 'file2.pdf').write_text("content2")
        (temp_dir / '.hidden.txt').write_text("hidden")

        with patch.object(processor, 'process_document') as mock_process:
            mock_process.side_effect = [
                {'file_name': 'file1.txt'},
                {'file_name': 'file2.pdf'}
            ]

            result = processor.scan_documents()

        assert len(result) == 2
        assert mock_process.call_count == 2

    @patch('document_processor.logger')
    def test_scan_documents_error_handling(self, mock_logger, processor, temp_dir):
        """Test error handling during document scanning"""
        with patch('document_processor.SUPPORTED_FILE_TYPES', ['.txt']):
            with patch('document_processor.BASE_DIR') as mock_base_dir:
                mock_base_dir.rglob.return_value = [temp_dir / 'error.txt']

                (temp_dir / 'error.txt').write_text("content")

                with patch.object(processor, 'process_document', side_effect=Exception("Process error")):
                    result = processor.scan_documents()

        assert result == []
        mock_logger.error.assert_called_once()


@pytest.mark.integration
class TestDocumentProcessorIntegration:
    """Integration tests for DocumentProcessor"""

    def test_real_text_file_processing(self, temp_dir):
        """Test processing a real text file end-to-end"""
        processor = DocumentProcessor()
        processor.cache_dir = temp_dir / 'cache'
        processor.cache_dir.mkdir()

        # Create a real text file
        text_file = temp_dir / 'sample.txt'
        content = "This is a sample document\nwith multiple lines\nfor testing purposes."
        text_file.write_text(content, encoding='utf-8')

        with patch('document_processor.BASE_DIR', temp_dir):
            result = processor.process_document(text_file)

        assert result['content'] == content
        assert result['file_name'] == 'sample.txt'
        assert result['file_type'] == '.txt'
        assert result['content_length'] == len(content)

        # Test cache was created
        cache_path = processor.get_cache_path(text_file)
        assert cache_path.exists()

        # Test cache loading
        cached_result = processor.load_from_cache(text_file)
        assert cached_result == result
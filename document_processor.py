import os
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

import pypdf2
import pdfplumber
import pandas as pd
import chardet
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import BASE_DIR, SUPPORTED_FILE_TYPES, CACHE_DIR

console = Console()
logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
    def get_file_hash(self, file_path: Path) -> str:
        """Generate hash of file for caching"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def get_cache_path(self, file_path: Path) -> Path:
        """Get cache file path for a document"""
        file_hash = self.get_file_hash(file_path)
        return self.cache_dir / f"{file_hash}.json"
    
    def load_from_cache(self, file_path: Path) -> Optional[Dict]:
        """Load processed document from cache"""
        cache_path = self.get_cache_path(file_path)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache for {file_path}: {e}")
        return None
    
    def save_to_cache(self, file_path: Path, data: Dict):
        """Save processed document to cache"""
        cache_path = self.get_cache_path(file_path)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save cache for {file_path}: {e}")
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        
        # Try pdfplumber first (better for tables)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as f:
                    reader = pypdf2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        
        return text.strip()
    
    def extract_text_from_excel(self, file_path: Path) -> str:
        """Extract text from Excel file"""
        try:
            dfs = pd.read_excel(file_path, sheet_name=None)
            text = ""
            for sheet_name, df in dfs.items():
                text += f"\n--- Sheet: {sheet_name} ---\n"
                text += df.to_string() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from Excel {file_path}: {e}")
            return ""
    
    def extract_text_from_csv(self, file_path: Path) -> str:
        """Extract text from CSV file"""
        try:
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            logger.error(f"Failed to extract text from CSV {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from text file with encoding detection"""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            return ""
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a single document and extract metadata and content"""
        # Check cache first
        cached_data = self.load_from_cache(file_path)
        if cached_data:
            return cached_data
        
        file_ext = file_path.suffix.lower()
        
        # Extract text based on file type
        text = ""
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            text = self.extract_text_from_excel(file_path)
        elif file_ext == '.csv':
            text = self.extract_text_from_csv(file_path)
        elif file_ext in ['.txt', '.md']:
            text = self.extract_text_from_txt(file_path)
        
        # Get file metadata
        stat = file_path.stat()
        relative_path = file_path.relative_to(BASE_DIR)
        
        document_data = {
            "file_path": str(file_path),
            "relative_path": str(relative_path),
            "file_name": file_path.name,
            "file_type": file_ext,
            "file_size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "content": text,
            "content_length": len(text),
            "category": self._determine_category(relative_path)
        }
        
        # Save to cache
        self.save_to_cache(file_path, document_data)
        
        return document_data
    
    def _determine_category(self, relative_path: Path) -> str:
        """Determine document category based on path"""
        from config import DOCUMENT_CATEGORIES
        
        path_str = str(relative_path)
        for category, info in DOCUMENT_CATEGORIES.items():
            for path_pattern in info["paths"]:
                if path_str.startswith(path_pattern):
                    return category
        return "other"
    
    def scan_documents(self, base_path: Path = BASE_DIR) -> List[Dict[str, Any]]:
        """Scan all documents in the package"""
        documents = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scanning documents...", total=None)
            
            for ext in SUPPORTED_FILE_TYPES:
                for file_path in base_path.rglob(f"*{ext}"):
                    # Skip hidden files and directories
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    
                    # Skip the flow_analyzer directory itself
                    if 'flow_analyzer' in file_path.parts:
                        continue
                    
                    progress.update(task, description=f"Processing {file_path.name}...")
                    
                    try:
                        doc_data = self.process_document(file_path)
                        documents.append(doc_data)
                    except Exception as e:
                        logger.error(f"Failed to process {file_path}: {e}")
        
        console.print(f"[green]✓[/green] Processed {len(documents)} documents")
        return documents
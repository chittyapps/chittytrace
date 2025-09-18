"""
Enhanced recursive document scanner with communication ingestion
Integrates with Cloudflare Workers for email and communication processing
"""

import os
import asyncio
import aiohttp
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
import email
from email import policy
from email.parser import BytesParser

from document_processor import DocumentProcessor
from config import BASE_DIR, SUPPORTED_FILE_TYPES

logger = logging.getLogger(__name__)


class RecursiveScanner:
    def __init__(self, cloudflare_worker_url: Optional[str] = None):
        self.processor = DocumentProcessor()
        self.cloudflare_worker_url = cloudflare_worker_url or os.getenv("CLOUDFLARE_WORKER_URL")
        self.scanned_paths: Set[str] = set()
        self.email_patterns = [
            r'nick@chitty\.cc',
            r'[\w\.-]+@[\w\.-]+\.\w+',  # General email pattern
        ]
        
        # Extended file types for communications
        self.communication_extensions = {
            '.eml': 'Email message',
            '.msg': 'Outlook message',
            '.mbox': 'Mailbox file',
            '.pst': 'Outlook data file',
            '.ost': 'Outlook offline file'
        }
        
        # Archive file types
        self.archive_extensions = {
            '.zip': 'ZIP archive',
            '.tar': 'TAR archive',
            '.gz': 'GZIP archive',
            '.7z': '7-Zip archive',
            '.rar': 'RAR archive'
        }
        
        # Additional document types
        self.additional_doc_types = {
            '.doc': 'Word document',
            '.docx': 'Word document',
            '.rtf': 'Rich text format',
            '.odt': 'OpenDocument text',
            '.pages': 'Apple Pages'
        }
        
        # Combine all supported types
        self.all_supported_types = {
            **SUPPORTED_FILE_TYPES,
            **self.communication_extensions,
            **self.archive_extensions,
            **self.additional_doc_types
        }
    
    async def scan_recursive(self, start_path: Path = BASE_DIR, 
                           max_depth: int = 10,
                           follow_symlinks: bool = False) -> List[Dict[str, Any]]:
        """Recursively scan for all documents including nested archives and communications"""
        documents = []
        
        async def scan_directory(path: Path, depth: int = 0):
            if depth > max_depth:
                return
            
            # Avoid scanning the same path twice
            abs_path = str(path.absolute())
            if abs_path in self.scanned_paths:
                return
            self.scanned_paths.add(abs_path)
            
            try:
                for item in path.iterdir():
                    if item.is_file():
                        # Process file
                        if self._should_process_file(item):
                            doc = await self._process_file(item)
                            if doc:
                                documents.append(doc)
                        
                        # Check if it's an archive to extract
                        if item.suffix.lower() in self.archive_extensions:
                            extracted_docs = await self._process_archive(item)
                            documents.extend(extracted_docs)
                    
                    elif item.is_dir():
                        # Skip hidden directories
                        if not item.name.startswith('.'):
                            await scan_directory(item, depth + 1)
                    
                    elif item.is_symlink() and follow_symlinks:
                        # Follow symlink if enabled
                        target = item.resolve()
                        if target.exists():
                            if target.is_file():
                                doc = await self._process_file(target)
                                if doc:
                                    documents.append(doc)
                            elif target.is_dir():
                                await scan_directory(target, depth + 1)
            
            except PermissionError:
                logger.warning(f"Permission denied: {path}")
            except Exception as e:
                logger.error(f"Error scanning {path}: {e}")
        
        # Start scanning
        await scan_directory(start_path)
        
        # Process email ingestion if configured
        if self.cloudflare_worker_url:
            email_docs = await self._ingest_cloudflare_emails()
            documents.extend(email_docs)
        
        logger.info(f"Recursive scan complete. Found {len(documents)} documents")
        return documents
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Check file extension
        if file_path.suffix.lower() not in self.all_supported_types:
            return False
        
        # Skip temporary files
        if file_path.name.startswith('~') or file_path.name.startswith('.'):
            return False
        
        # Check file size (skip files over 100MB)
        try:
            if file_path.stat().st_size > 100 * 1024 * 1024:
                logger.warning(f"Skipping large file: {file_path} (>100MB)")
                return False
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot access file {file_path}: {e}")
            return False
        
        return True
    
    async def _process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single file"""
        try:
            # Use existing document processor for standard files
            if file_path.suffix.lower() in SUPPORTED_FILE_TYPES:
                return self.processor.process_document(file_path)
            
            # Process communication files
            elif file_path.suffix.lower() in self.communication_extensions:
                return await self._process_communication_file(file_path)
            
            # Process additional document types
            elif file_path.suffix.lower() in self.additional_doc_types:
                return await self._process_additional_doc(file_path)
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            return None
    
    async def _process_communication_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process email and communication files"""
        try:
            if file_path.suffix.lower() == '.eml':
                return self._process_eml_file(file_path)
            elif file_path.suffix.lower() == '.msg':
                return await self._process_msg_file(file_path)
            elif file_path.suffix.lower() in ['.mbox', '.pst', '.ost']:
                logger.info(f"Found mailbox file: {file_path} (requires specialized processing)")
                # For now, just catalog these files
                return self._create_document_entry(file_path, "Mailbox file - requires extraction")
        
        except Exception as e:
            logger.error(f"Failed to process communication file {file_path}: {e}")
            return None
    
    def _process_eml_file(self, file_path: Path) -> Dict[str, Any]:
        """Process .eml email file"""
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        
        # Extract email metadata
        metadata = {
            'from': msg.get('From', ''),
            'to': msg.get('To', ''),
            'cc': msg.get('Cc', ''),
            'subject': msg.get('Subject', ''),
            'date': msg.get('Date', ''),
            'message_id': msg.get('Message-ID', '')
        }
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body += part.get_content() + "\n"
        else:
            body = msg.get_content()
        
        # Check for relevant email addresses
        all_text = f"{metadata['from']} {metadata['to']} {metadata['cc']} {body}"
        is_relevant = any(re.search(pattern, all_text, re.IGNORECASE) 
                         for pattern in self.email_patterns)
        
        doc_entry = self._create_document_entry(file_path, body)
        doc_entry['metadata'] = metadata
        doc_entry['category'] = 'communications' if is_relevant else 'other'
        doc_entry['email_metadata'] = metadata
        
        return doc_entry
    
    async def _process_msg_file(self, file_path: Path) -> Dict[str, Any]:
        """Process .msg Outlook file"""
        # For now, create a placeholder entry
        # Full .msg processing would require python-outlook or similar
        return self._create_document_entry(
            file_path, 
            "Outlook message file - requires specialized extraction"
        )
    
    async def _process_additional_doc(self, file_path: Path) -> Dict[str, Any]:
        """Process additional document types"""
        # For now, create catalog entries for these files
        # Full processing would require python-docx, python-odt, etc.
        return self._create_document_entry(
            file_path,
            f"{self.additional_doc_types[file_path.suffix.lower()]} - requires extraction"
        )
    
    async def _process_archive(self, archive_path: Path) -> List[Dict[str, Any]]:
        """Process archive files"""
        logger.info(f"Found archive: {archive_path}")
        # For now, just catalog the archive
        # Full extraction would require zipfile, tarfile, etc.
        doc = self._create_document_entry(
            archive_path,
            f"Archive file containing multiple documents"
        )
        return [doc]
    
    def _create_document_entry(self, file_path: Path, content: str = "") -> Dict[str, Any]:
        """Create a document entry for files that need special processing"""
        stat = file_path.stat()
        relative_path = file_path.relative_to(BASE_DIR)
        
        # Generate file hash
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)  # Read in 64kb chunks
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        
        return {
            "file_path": str(file_path),
            "relative_path": str(relative_path),
            "file_name": file_path.name,
            "file_type": file_path.suffix.lower(),
            "file_size": stat.st_size,
            "file_hash": hasher.hexdigest(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "content": content,
            "content_length": len(content),
            "category": self._determine_category(relative_path),
            "requires_extraction": True
        }
    
    def _determine_category(self, relative_path: Path) -> str:
        """Enhanced category determination"""
        from config import DOCUMENT_CATEGORIES
        
        path_str = str(relative_path).lower()
        
        # Check for communication indicators
        if any(term in path_str for term in ['email', 'mail', 'communication', 'correspond']):
            return 'communications'
        
        # Check standard categories
        for category, info in DOCUMENT_CATEGORIES.items():
            for path_pattern in info["paths"]:
                if path_str.startswith(path_pattern.lower()):
                    return category
        
        return "other"
    
    async def _ingest_cloudflare_emails(self) -> List[Dict[str, Any]]:
        """Ingest emails from Cloudflare Worker"""
        if not self.cloudflare_worker_url:
            return []
        
        documents = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Request emails from worker
                payload = {
                    "action": "fetch_emails",
                    "email": "nick@chitty.cc",
                    "date_range": {
                        "start": (datetime.now().replace(year=datetime.now().year-1)).isoformat(),
                        "end": datetime.now().isoformat()
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {os.getenv('CLOUDFLARE_WORKER_TOKEN', '')}",
                    "Content-Type": "application/json"
                }
                
                async with session.post(
                    self.cloudflare_worker_url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        emails = data.get("emails", [])
                        
                        for email_data in emails:
                            doc = self._create_email_document(email_data)
                            documents.append(doc)
                        
                        logger.info(f"Ingested {len(emails)} emails from Cloudflare Worker")
                    else:
                        logger.error(f"Failed to fetch emails: {response.status}")
        
        except Exception as e:
            logger.error(f"Error ingesting Cloudflare emails: {e}")
        
        return documents
    
    def _create_email_document(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create document entry from Cloudflare email data"""
        # Create a virtual path for the email
        email_id = email_data.get("id", hashlib.md5(
            f"{email_data.get('from', '')}{email_data.get('subject', '')}{email_data.get('date', '')}".encode()
        ).hexdigest())
        
        virtual_path = f"cloudflare_emails/{email_id}.eml"
        
        return {
            "file_path": virtual_path,
            "relative_path": virtual_path,
            "file_name": f"{email_id}.eml",
            "file_type": ".eml",
            "file_size": len(email_data.get("body", "")),
            "file_hash": email_id,
            "modified_time": email_data.get("date", datetime.now().isoformat()),
            "content": email_data.get("body", ""),
            "content_length": len(email_data.get("body", "")),
            "category": "communications",
            "email_metadata": {
                "from": email_data.get("from"),
                "to": email_data.get("to"),
                "cc": email_data.get("cc"),
                "subject": email_data.get("subject"),
                "date": email_data.get("date"),
                "attachments": email_data.get("attachments", [])
            },
            "source": "cloudflare_worker"
        }
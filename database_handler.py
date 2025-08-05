"""
Database handler for Neon PostgreSQL with vector support
"""

import os
import asyncio
import asyncpg
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path
import numpy as np
from neon_integration import NeonIntegration

logger = logging.getLogger(__name__)


class DatabaseHandler:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self.neon_integration: Optional[NeonIntegration] = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool created")
            
            # Ensure schema exists
            await self.ensure_schema()
            
            # Initialize Neon database integration
            self.neon_integration = NeonIntegration(self.database_url)
            await self.neon_integration.initialize()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def ensure_schema(self):
        """Ensure database schema exists"""
        schema_path = Path(__file__).parent / "database_schema.sql"
        
        if schema_path.exists():
            async with self.pool.acquire() as conn:
                try:
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()
                    
                    # Execute schema creation
                    await conn.execute(schema_sql)
                    logger.info("Database schema ensured")
                    
                except Exception as e:
                    logger.warning(f"Schema creation warning: {e}")
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
        
        if self.neon_integration:
            await self.neon_integration.close()
    
    async def store_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Store documents in database"""
        stored_ids = []
        
        async with self.pool.acquire() as conn:
            for doc in documents:
                try:
                    # Check if document already exists
                    existing = await conn.fetchval(
                        "SELECT id FROM documents WHERE file_hash = $1",
                        doc.get("file_hash", "")
                    )
                    
                    if existing:
                        stored_ids.append(str(existing))
                        continue
                    
                    # Insert new document
                    doc_id = await conn.fetchval("""
                        INSERT INTO documents (
                            file_path, relative_path, file_name, file_type,
                            file_size, file_hash, category, content, metadata,
                            modified_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        RETURNING id
                    """,
                        doc["file_path"],
                        doc["relative_path"],
                        doc["file_name"],
                        doc["file_type"],
                        doc["file_size"],
                        doc.get("file_hash", ""),
                        doc["category"],
                        doc.get("content", ""),
                        json.dumps(doc.get("metadata", {})),
                        datetime.fromisoformat(doc["modified_time"])
                    )
                    
                    stored_ids.append(str(doc_id))
                    
                except Exception as e:
                    logger.error(f"Failed to store document {doc['file_name']}: {e}")
        
        return stored_ids
    
    async def store_timeline_events(self, events: List[Dict[str, Any]]) -> List[str]:
        """Store timeline events in database"""
        stored_ids = []
        
        async with self.pool.acquire() as conn:
            for event in events:
                try:
                    event_id = await conn.fetchval("""
                        INSERT INTO timeline_events (
                            event_date, event_type, description, amount,
                            source_account, destination_account,
                            source_institution, destination_institution,
                            reference_number, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        RETURNING id
                    """,
                        datetime.fromisoformat(event["date"]).date(),
                        event["type"],
                        event["description"],
                        event.get("amount"),
                        event.get("source_account"),
                        event.get("destination_account"),
                        event.get("source_institution"),
                        event.get("destination_institution"),
                        event.get("reference_number"),
                        json.dumps(event.get("metadata", {}))
                    )
                    
                    stored_ids.append(str(event_id))
                    
                    # Link to source documents
                    if event.get("source_document_id"):
                        await conn.execute("""
                            INSERT INTO document_events (document_id, event_id, extracted_by)
                            VALUES ($1, $2, $3)
                            ON CONFLICT DO NOTHING
                        """,
                            event["source_document_id"],
                            event_id,
                            "claude"
                        )
                    
                except Exception as e:
                    logger.error(f"Failed to store event: {e}")
        
        return stored_ids
    
    async def store_exhibit(self, exhibit_data: Dict[str, Any]) -> str:
        """Store court exhibit in database"""
        async with self.pool.acquire() as conn:
            exhibit_id = await conn.fetchval("""
                INSERT INTO court_exhibits (
                    exhibit_number, case_number, case_caption,
                    exhibit_description, status, date_marked, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """,
                exhibit_data["exhibit_number"],
                exhibit_data["case_number"],
                exhibit_data["case_caption"],
                exhibit_data.get("description"),
                "draft",
                datetime.now().date(),
                json.dumps(exhibit_data.get("metadata", {}))
            )
            
            # Link documents to exhibit
            for doc_info in exhibit_data.get("documents", []):
                await conn.execute("""
                    INSERT INTO exhibit_documents (exhibit_id, document_id)
                    VALUES ($1, $2)
                """,
                    exhibit_id,
                    doc_info["document_id"]
                )
            
            return str(exhibit_id)
    
    async def store_analysis_query(self, query: str, response: str, 
                                 documents: List[str], metadata: Dict[str, Any]) -> str:
        """Store analysis query and response"""
        async with self.pool.acquire() as conn:
            query_id = await conn.fetchval("""
                INSERT INTO analysis_queries (
                    query_text, response, status, model_used,
                    tokens_used, metadata, completed_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """,
                query,
                response,
                "completed",
                metadata.get("model", "claude-3"),
                metadata.get("tokens_used"),
                json.dumps(metadata),
                datetime.now()
            )
            
            # Link related documents
            for doc_id in documents:
                await conn.execute("""
                    INSERT INTO query_documents (query_id, document_id)
                    VALUES ($1, $2)
                """,
                    query_id,
                    doc_id
                )
            
            return str(query_id)
    
    async def get_fund_flow_summary(self, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get fund flow summary from materialized view"""
        query = "SELECT * FROM fund_flow_summary WHERE 1=1"
        params = []
        
        if start_date:
            params.append(datetime.fromisoformat(start_date).date())
            query += f" AND event_date >= ${len(params)}"
        
        if end_date:
            params.append(datetime.fromisoformat(end_date).date())
            query += f" AND event_date <= ${len(params)}"
        
        query += " ORDER BY event_date"
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    async def search_documents_vector(self, query_vector: np.ndarray, 
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents using vector similarity"""
        async with self.pool.acquire() as conn:
            # Convert numpy array to list for PostgreSQL
            vector_list = query_vector.tolist()
            
            rows = await conn.fetch("""
                SELECT id, file_name, relative_path, category,
                       content_vector <-> $1::vector as distance
                FROM documents
                WHERE content_vector IS NOT NULL
                ORDER BY content_vector <-> $1::vector
                LIMIT $2
            """, vector_list, limit)
            
            return [dict(row) for row in rows]
    
    async def get_exhibit_package(self, package_id: str) -> Dict[str, Any]:
        """Get complete exhibit package with all exhibits"""
        async with self.pool.acquire() as conn:
            # Get package info
            package = await conn.fetchrow("""
                SELECT * FROM exhibit_packages WHERE id = $1
            """, package_id)
            
            if not package:
                return None
            
            package_dict = dict(package)
            
            # Get exhibits in package
            exhibits = await conn.fetch("""
                SELECT e.*, pe.order_number
                FROM court_exhibits e
                JOIN package_exhibits pe ON e.id = pe.exhibit_id
                WHERE pe.package_id = $1
                ORDER BY pe.order_number
            """, package_id)
            
            package_dict["exhibits"] = [dict(e) for e in exhibits]
            
            return package_dict
"""
Generic Neon database integration for ChittyTrace
Connects to any Neon PostgreSQL database with vector support
"""

import os
import asyncio
import asyncpg
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
import uuid

logger = logging.getLogger(__name__)


class NeonIntegration:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self.pool: Optional[asyncpg.Pool] = None
        
    async def initialize(self):
        """Initialize connection to Neon database"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=3,
                max_size=10,
                command_timeout=60
            )
            
            # Verify database connection
            await self.verify_database()
            logger.info("Connected to Neon database successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Neon database: {e}")
            raise
    
    async def verify_database(self):
        """Verify database connection and check for required tables"""
        async with self.pool.acquire() as conn:
            # Check for existing tables
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            table_names = [row['table_name'] for row in tables]
            logger.info(f"Found tables in database: {table_names}")
            
            # Check if we have the expected schema
            if 'documents' in table_names:
                doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
                logger.info(f"Found {doc_count} documents in database")
            
            return True
    
    async def cross_reference_transactions(self, transaction_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Cross-reference new transaction data with existing database records"""
        matches = []
        
        async with self.pool.acquire() as conn:
            # Search for matching amounts
            if transaction_data.get('amount'):
                amount_matches = await conn.fetch("""
                    SELECT e.*, d.file_name, d.relative_path
                    FROM timeline_events e
                    LEFT JOIN document_events de ON e.id = de.event_id
                    LEFT JOIN documents d ON de.document_id = d.id
                    WHERE e.amount BETWEEN $1 AND $2
                    ORDER BY e.event_date DESC
                """, 
                    float(transaction_data['amount']) * 0.99,  # 1% tolerance
                    float(transaction_data['amount']) * 1.01
                )
                
                for match in amount_matches:
                    matches.append({
                        "type": "amount_match",
                        "existing_event": dict(match),
                        "new_transaction": transaction_data,
                        "confidence": 0.9
                    })
            
            # Search for matching account numbers
            if transaction_data.get('source_account') or transaction_data.get('destination_account'):
                account_matches = await conn.fetch("""
                    SELECT e.*, d.file_name
                    FROM timeline_events e
                    LEFT JOIN document_events de ON e.id = de.event_id
                    LEFT JOIN documents d ON de.document_id = d.id
                    WHERE e.source_account = ANY($1) 
                       OR e.destination_account = ANY($1)
                """, [
                    transaction_data.get('source_account'),
                    transaction_data.get('destination_account')
                ])
                
                for match in account_matches:
                    matches.append({
                        "type": "account_match",
                        "existing_event": dict(match),
                        "new_transaction": transaction_data,
                        "confidence": 0.95
                    })
            
            # Search for matching dates (within 30 days)
            if transaction_data.get('date'):
                date_matches = await conn.fetch("""
                    SELECT e.*, d.file_name
                    FROM timeline_events e
                    LEFT JOIN document_events de ON e.id = de.event_id
                    LEFT JOIN documents d ON de.document_id = d.id
                    WHERE e.event_date BETWEEN $1::date - interval '30 days' 
                                           AND $1::date + interval '30 days'
                    AND e.amount IS NOT NULL
                """, transaction_data['date'])
                
                for match in date_matches:
                    matches.append({
                        "type": "date_proximity",
                        "existing_event": dict(match),
                        "new_transaction": transaction_data,
                        "confidence": 0.7
                    })
        
        return matches
    
    async def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """Search documents in the database"""
        async with self.pool.acquire() as conn:
            # Full-text search in documents
            documents = await conn.fetch("""
                SELECT d.*, 
                       ts_rank(to_tsvector('english', d.content), plainto_tsquery('english', $1)) as rank
                FROM documents d
                WHERE to_tsvector('english', d.content) @@ plainto_tsquery('english', $1)
                ORDER BY rank DESC, d.created_at DESC
                LIMIT 20
            """, query)
            
            return [dict(doc) for doc in documents]
    
    async def get_timeline(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get timeline events from database"""
        async with self.pool.acquire() as conn:
            query = """
                SELECT e.*, 
                       array_agg(DISTINCT d.file_name) as source_documents,
                       array_agg(DISTINCT d.category) as document_categories
                FROM timeline_events e
                LEFT JOIN document_events de ON e.id = de.event_id
                LEFT JOIN documents d ON de.document_id = d.id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                params.append(start_date)
                query += f" AND e.event_date >= ${len(params)}"
            
            if end_date:
                params.append(end_date)
                query += f" AND e.event_date <= ${len(params)}"
            
            query += """
                GROUP BY e.id, e.event_date, e.event_type, e.description, 
                         e.amount, e.source_account, e.destination_account
                ORDER BY e.event_date ASC
            """
            
            events = await conn.fetch(query, *params)
            return [dict(event) for event in events]
    
    async def store_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Store documents in database"""
        stored_ids = []
        
        async with self.pool.acquire() as conn:
            for doc in documents:
                try:
                    # Check if document already exists
                    existing = await conn.fetchval("""
                        SELECT id FROM documents WHERE file_hash = $1
                    """, doc.get('file_hash', ''))
                    
                    if existing:
                        stored_ids.append(str(existing))
                        continue
                    
                    # Insert new document
                    doc_id = await conn.fetchval("""
                        INSERT INTO documents (
                            file_path, relative_path, file_name, file_type,
                            file_size, file_hash, category, content, 
                            metadata, modified_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        RETURNING id
                    """,
                        doc['file_path'], doc['relative_path'], doc['file_name'],
                        doc['file_type'], doc['file_size'], doc.get('file_hash', ''),
                        doc['category'], doc.get('content', ''),
                        json.dumps(doc.get('metadata', {})),
                        datetime.fromisoformat(doc['modified_time'])
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
                    
                    # Link to source documents if provided
                    if event.get("source_document_id"):
                        await conn.execute("""
                            INSERT INTO document_events (document_id, event_id, extracted_by)
                            VALUES ($1, $2, $3)
                            ON CONFLICT DO NOTHING
                        """,
                            event["source_document_id"],
                            event_id,
                            "chittytrace"
                        )
                    
                except Exception as e:
                    logger.error(f"Failed to store event: {e}")
        
        return stored_ids
    
    async def close(self):
        """Close database connection"""
        if self.pool:
            await self.pool.close()
            logger.info("Closed Neon database connection")
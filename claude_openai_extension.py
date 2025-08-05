"""
Claude/OpenAI Extension for ChittyTrace
Provides a unified interface for AI assistants to interact with the analysis system
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from document_processor import DocumentProcessor
from claude_integration import ClaudeAnalyzer
from package_generator import PackageGenerator
from interactive_timeline import InteractiveTimeline
from database_handler import DatabaseHandler

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Models
class DocumentQuery(BaseModel):
    query: str
    category: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    limit: Optional[int] = 10

class TimelineQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    event_types: Optional[List[str]] = None
    min_amount: Optional[float] = None

class ExhibitRequest(BaseModel):
    documents: List[Dict[str, Any]]
    case_info: Dict[str, str]
    purpose: str
    cook_county_format: bool = True

class FormFillRequest(BaseModel):
    template: str
    data: Dict[str, Any]
    form_type: Optional[str] = None

class CommandRequest(BaseModel):
    command: str
    parameters: Dict[str, Any]

class AnalysisResponse(BaseModel):
    status: str
    result: Any
    metadata: Optional[Dict[str, Any]] = None
    source_documents: Optional[List[str]] = None

# FastAPI app
app = FastAPI(
    title="ChittyTrace API",
    description="AI-powered financial document analysis and exhibit generation",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Global instances
analyzer: Optional[ClaudeAnalyzer] = None
processor: Optional[DocumentProcessor] = None
package_generator: Optional[PackageGenerator] = None
timeline_generator: Optional[InteractiveTimeline] = None
db_handler: Optional[DatabaseHandler] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global analyzer, processor, package_generator, timeline_generator, db_handler
    
    try:
        # Initialize services
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not set")
        else:
            analyzer = ClaudeAnalyzer(api_key)
            processor = DocumentProcessor()
            package_generator = PackageGenerator(analyzer)
            timeline_generator = InteractiveTimeline(analyzer)
            
            # Initialize database if configured
            db_url = os.getenv("DATABASE_URL")
            if db_url:
                db_handler = DatabaseHandler(db_url)
                await db_handler.initialize()
        
        logger.info("Services initialized successfully")
        yield
        
    finally:
        # Cleanup
        if db_handler:
            await db_handler.close()

app = FastAPI(lifespan=lifespan)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token"""
    token = credentials.credentials
    valid_tokens = os.getenv("API_TOKENS", "").split(",")
    
    if not valid_tokens or token not in valid_tokens:
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    
    return token

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "analyzer": analyzer is not None,
            "processor": processor is not None,
            "database": db_handler is not None
        }
    }

@app.post("/documents/scan")
async def scan_documents(token: str = Depends(verify_token)):
    """Scan and index all documents"""
    if not processor:
        raise HTTPException(status_code=503, detail="Document processor not initialized")
    
    documents = processor.scan_documents()
    
    if analyzer and documents:
        analyzer.index_documents(documents)
        
    if db_handler:
        await db_handler.store_documents(documents)
    
    return AnalysisResponse(
        status="success",
        result={
            "documents_found": len(documents),
            "categories": list(set(d["category"] for d in documents))
        }
    )

@app.post("/documents/query", response_model=AnalysisResponse)
async def query_documents(query: DocumentQuery, token: str = Depends(verify_token)):
    """Query documents with natural language"""
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    # Search documents
    relevant_docs = analyzer.search_documents(query.query, k=query.limit)
    
    # Get analysis
    response = await analyzer.analyze_with_context(query.query, relevant_docs)
    
    return AnalysisResponse(
        status="success",
        result=response,
        source_documents=[doc.metadata["file_name"] for doc in relevant_docs[:5]]
    )

@app.post("/timeline/extract", response_model=AnalysisResponse)
async def extract_timeline(query: TimelineQuery, token: str = Depends(verify_token)):
    """Extract timeline events from documents"""
    if not analyzer or not processor:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    # Get documents
    documents = processor.scan_documents()
    
    # Extract events
    events = await timeline_generator.extract_timeline_events(documents)
    
    # Filter events based on query
    filtered_events = events
    if query.start_date:
        filtered_events = [e for e in filtered_events if e.get("date", "") >= query.start_date]
    if query.end_date:
        filtered_events = [e for e in filtered_events if e.get("date", "") <= query.end_date]
    if query.event_types:
        filtered_events = [e for e in filtered_events if e.get("type") in query.event_types]
    if query.min_amount is not None:
        filtered_events = [e for e in filtered_events if e.get("amount", 0) >= query.min_amount]
    
    return AnalysisResponse(
        status="success",
        result=filtered_events,
        metadata={"total_events": len(filtered_events)}
    )

@app.post("/exhibits/generate", response_model=AnalysisResponse)
async def generate_exhibits(request: ExhibitRequest, token: str = Depends(verify_token)):
    """Generate court-ready exhibit package"""
    if not package_generator:
        raise HTTPException(status_code=503, detail="Package generator not initialized")
    
    package = await package_generator.generate_exhibit_package(
        request.documents,
        request.case_info,
        request.purpose
    )
    
    return AnalysisResponse(
        status="success",
        result=package,
        metadata={"package_path": package.get("saved_path")}
    )

@app.post("/forms/fill", response_model=AnalysisResponse)
async def fill_form(request: FormFillRequest, token: str = Depends(verify_token)):
    """Fill a form template with data"""
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    filled_form = await analyzer.fill_form(request.template, request.data)
    
    return AnalysisResponse(
        status="success",
        result=filled_form,
        metadata={"form_type": request.form_type}
    )

@app.post("/commands/execute", response_model=AnalysisResponse)
async def execute_command(request: CommandRequest, token: str = Depends(verify_token)):
    """Execute analysis commands"""
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    result = await analyzer.execute_analysis_command(
        request.command,
        request.parameters
    )
    
    return AnalysisResponse(
        status="success",
        result=result
    )

@app.get("/schema/cook-county")
async def get_cook_county_requirements(token: str = Depends(verify_token)):
    """Get Cook County court filing requirements"""
    return {
        "exhibit_requirements": {
            "numbering": "sequential",
            "page_size": "8.5x11 inches",
            "margins": "1 inch all sides",
            "font": "Times New Roman or Arial, 12pt",
            "line_spacing": "double",
            "exhibit_sticker": {
                "required": True,
                "position": "bottom right",
                "content": ["Exhibit Number", "Case Number", "Date"]
            },
            "authentication": "notarized affidavit required"
        },
        "package_requirements": {
            "cover_sheet": True,
            "table_of_contents": True,
            "certificate_of_service": True,
            "index": True,
            "binding": "top left corner staple or binder clip"
        }
    }

# OpenAI Function Calling Schema
@app.get("/openai/functions")
async def get_openai_functions():
    """Get OpenAI function calling schema"""
    return [
        {
            "name": "query_documents",
            "description": "Search and analyze financial documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["bank_statements", "property_docs", "wire_transfers", 
                                "corporate_governance", "litigation", "tax_documents"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of documents to search"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "extract_timeline",
            "description": "Extract timeline of events from documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "event_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["wire_transfer", "property_purchase", "bank_transaction",
                                    "legal_filing", "tax_event", "corporate_event"]
                        }
                    }
                }
            }
        },
        {
            "name": "generate_exhibits",
            "description": "Generate court-ready exhibit packages",
            "parameters": {
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    },
                    "case_info": {
                        "type": "object",
                        "properties": {
                            "case_number": {"type": "string"},
                            "caption": {"type": "string"},
                            "affiant": {"type": "string"}
                        }
                    },
                    "purpose": {"type": "string"}
                },
                "required": ["documents", "case_info", "purpose"]
            }
        }
    ]

# Claude Tool Use Schema
@app.get("/claude/tools")
async def get_claude_tools():
    """Get Claude tool use schema"""
    return {
        "tools": [
            {
                "name": "flow_analyzer",
                "description": "Analyze financial documents and fund flows",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["query", "timeline", "exhibit", "form", "command"]
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters"
                        }
                    },
                    "required": ["action", "parameters"]
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
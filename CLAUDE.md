# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChittyTrace is a comprehensive AI-powered financial forensics platform for analyzing documents, tracing fund flows, generating court-ready exhibits, and providing intelligent financial analysis capabilities. It integrates with Neon PostgreSQL databases and supports Cook County court filing requirements.

## Key Commands

### Development & Testing
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the Streamlit GUI application
streamlit run app.py

# Start the API server for Claude/OpenAI extension
python claude_openai_extension.py

# Run tests (when implemented)
pytest tests/
```

### Linting & Type Checking
```bash
# Run linting
ruff check .

# Run type checking
mypy flow_analyzer/
```

## Architecture Overview

### Core Components

1. **document_processor.py**: Handles document scanning, text extraction, and caching
   - Supports PDF, Excel, CSV, text files
   - Implements intelligent caching system
   - Extracts metadata and content

2. **claude_integration.py**: Claude API integration and analysis engine
   - Vector store for semantic search using Chroma
   - Complex command execution (fund tracing, timeline generation)
   - Form filling and exhibit generation

3. **recursive_scanner.py**: Enhanced document discovery
   - Recursively scans directories for all document types
   - Integrates with Cloudflare Workers for email ingestion
   - Handles archives and communication files

4. **interactive_timeline.py**: Timeline visualization system
   - Creates interactive Plotly timelines
   - Links timeline events to source documents
   - Extracts events using Claude AI

5. **package_generator.py**: Cook County exhibit package generator
   - Formats exhibits per Cook County requirements
   - Generates cover sheets, affidavits, and indices
   - Creates complete filing packages

6. **database_handler.py**: Neon PostgreSQL integration
   - Vector search capabilities
   - Cross-references with connected Neon database
   - Stores documents, events, and analysis results

7. **claude_openai_extension.py**: API interface for AI assistants
   - FastAPI-based REST API
   - OpenAI function calling schema
   - Claude tool use integration

8. **app.py**: Streamlit GUI application
   - Six main tabs: Query, Package Creator, Form Filler, Commands, Visualizations, Browser
   - Real-time document analysis
   - Interactive visualizations

## Database Integration

The system uses Neon PostgreSQL with the following key tables:
- `documents`: Stores all scanned documents with embeddings
- `timeline_events`: Financial events extracted from documents
- `court_exhibits`: Tracks exhibit preparation
- `analysis_queries`: Query history and AI responses
- `exhibit_packages`: Complete court filing packages

**Important**: The system can cross-reference with connected Neon databases for matching transactions, property records, and legal filings when a database is configured.

## Cook County Requirements

When generating exhibits, the system automatically applies:
- 8.5" x 11" page size with 1" margins
- Times New Roman or Arial 12pt font
- Double spacing
- Sequential exhibit numbering
- Exhibit stickers (bottom right)
- Required authentication affidavits

## Email Ingestion

The system integrates with Cloudflare Workers to ingest emails from nick@chitty.cc. Configure via:
- `CLOUDFLARE_WORKER_URL`: Worker endpoint
- `CLOUDFLARE_WORKER_TOKEN`: Authentication token

## Environment Variables

Required in `.env`:
- `ANTHROPIC_API_KEY`: Claude API access
- `DATABASE_URL`: Neon database connection (optional)
- `CLOUDFLARE_WORKER_URL`: Email ingestion endpoint
- `API_TOKENS`: Bearer tokens for API authentication

## ChittyCorp Integration

This system integrates with ChittyCorp's enterprise AI infrastructure:
- **Website**: chittycorp.com
- **Support**: support@chittycorp.com
- **Email Ingestion**: Cloudflare Workers with nick@chitty.cc routing
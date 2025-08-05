# ChittyTrace-CC

[![ChittyCorp](https://img.shields.io/badge/ChittyCorp-LLC-blue.svg)](https://chittycorp.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**ChittyTrace-CC for Cook County Illinois (Chicago) - Financial Document Analysis & Court Ready Exhibit Package Development**

*Specialized version for Cook County Circuit Court with local attorney optimizations*

A comprehensive AI-powered financial forensics platform optimized specifically for Cook County attorneys and legal professionals.

**Developed by ChittyCorp, LLC** - Part of the Chitty ecosystem of AI-powered business solutions.

## Features

### Core Capabilities
- **Document Processing**: Recursive scanning and indexing of all financial documents
- **AI-Powered Analysis**: Claude integration for intelligent document querying
- **Interactive Timeline**: Visual timeline with document linking
- **Exhibit Generation**: Cook County court-compliant exhibit packages
- **Form Automation**: Automated filling of legal and financial forms
- **Command Execution**: Complex analysis commands (fund tracing, pattern detection)
- **Database Integration**: Neon PostgreSQL with vector search capabilities
- **Email Ingestion**: Cloudflare Worker integration for email processing
- **Database Integration**: Neon PostgreSQL with vector search

### Supported Document Types
- Financial statements (PDF, Excel, CSV)
- Bank statements
- Wire transfer records
- Property documents
- Legal filings
- Tax documents
- Email communications (.eml, .msg)
- Archive files (.zip, .tar, etc.)
- Office documents (.doc, .docx, .rtf)

## Installation

1. Clone the repository:
```bash
cd /Users/nickbianchi/Desktop/Flow_of_Funds_Package/flow_analyzer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Initialize database (if using Neon):
```bash
# The schema will be automatically applied on first run
```

## Usage

### 1. Streamlit GUI Application

Launch the interactive web interface:
```bash
streamlit run app.py
```

Features available in GUI:
- Document scanning and indexing
- Natural language queries
- Interactive timeline visualization
- Exhibit package generation
- Form filling interface
- Command execution center
- Data visualizations
- Document browser

### 2. API Extension for Claude/OpenAI

Start the API server:
```bash
python claude_openai_extension.py
```

The API runs on `http://localhost:8000` and provides endpoints for:
- `/documents/scan` - Scan and index documents
- `/documents/query` - Query documents with natural language
- `/timeline/extract` - Extract timeline events
- `/exhibits/generate` - Generate court exhibit packages
- `/forms/fill` - Fill form templates
- `/commands/execute` - Execute analysis commands

### 3. Command Line Usage

```python
from flow_analyzer import FlowAnalyzer

# Initialize analyzer
analyzer = FlowAnalyzer(api_key="your_anthropic_key")

# Scan documents
documents = analyzer.scan_all_documents()

# Query documents
result = analyzer.query("Trace funds from USAA to Colombia property")

# Generate exhibit package
package = analyzer.generate_exhibit_package(
    documents=selected_docs,
    case_info={
        "case_number": "2024-CH-00001",
        "caption": "Your Case Name v. Defendant",
        "affiant": "Your Name"
    },
    purpose="Property funding documentation"
)
```

## Cook County Exhibit Requirements

The system automatically formats exhibits according to Cook County Circuit Court requirements:

- **Page Size**: 8.5" x 11"
- **Margins**: 1 inch on all sides
- **Font**: Times New Roman or Arial, 12pt
- **Line Spacing**: Double-spaced
- **Exhibit Stickers**: Bottom right corner with:
  - Exhibit Number
  - Case Number
  - Date
- **Authentication**: Notarized affidavit required
- **Package Components**:
  - Cover sheet
  - Table of contents
  - Certificate of service
  - Sequential exhibit numbering

## Database Schema

The system uses PostgreSQL with vector extensions for semantic search:

### Main Tables
- `documents` - Scanned documents with content and embeddings
- `timeline_events` - Extracted financial events
- `court_exhibits` - Exhibit preparation and tracking
- `analysis_queries` - Query history and responses
- `exhibit_packages` - Complete exhibit packages

### Neon Database Integration
The system integrates with Neon PostgreSQL databases for:
- Document storage and indexing
- Timeline event tracking
- Cross-referencing transactions
- Vector-based semantic search
- Exhibit package management

## Email Ingestion

Configure Cloudflare Worker for email ingestion:

1. Set `CLOUDFLARE_WORKER_URL` in `.env`
2. Set `CLOUDFLARE_WORKER_TOKEN` for authentication
3. The system will automatically ingest emails from:
   - nick@chitty.cc
   - Other configured email addresses

## Advanced Features

### Pattern Detection
```python
result = analyzer.execute_command("detect_patterns", {
    "pattern_type": "structured_transactions",
    "threshold": {"amount": 10000, "frequency": "daily"}
})
```

### Fund Flow Visualization
```python
chart = analyzer.execute_command("generate_fund_flow_chart", {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "accounts": ["USAA", "Fidelity", "Mercury"]
})
```

### Property Chain Analysis
```python
analysis = analyzer.execute_command("analyze_property_chain", {
    "property_address": "123 Main St, Chicago, IL"
})
```

## Security

- API endpoints are protected with bearer token authentication
- Database connections use SSL
- Sensitive data is never logged
- File uploads are validated and sandboxed

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **API key errors**: Check `.env` configuration
3. **Database connection**: Verify DATABASE_URL format
4. **Large files**: Files over 100MB are skipped by default

### Logs
Check `logs/` directory for detailed error messages and debugging information.

## About ChittyCorp

This project is developed and maintained by **ChittyCorp, LLC**, a technology company specializing in AI-powered solutions for legal, financial, and business intelligence applications.

- **Website**: [chittycorp.com](https://chittycorp.com)
- **Contact**: support@chittycorp.com
- **Foundation**: [ChittyFoundation](https://chittyfoundation.org)

## Support

For issues, questions, or commercial licensing inquiries:
- Email: support@chittycorp.com
- Create an issue on GitHub
- Visit: [chittycorp.com](https://chittycorp.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 ChittyCorp, LLC
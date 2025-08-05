import os
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent.parent
FLOW_ANALYZER_DIR = Path(__file__).parent

DOCUMENT_CATEGORIES = {
    "bank_statements": {
        "paths": [
            "01_USAA_Statements",
            "02_Fidelity_Statements", 
            "02b_Fifth_Third_Statements",
            "02c_Robinhood_Statements",
            "02d_Coinbase_Statements",
            "03_Huntington_Statements",
            "03b_Mercury_Statements",
            "05b_Alianza_Colombia"
        ],
        "description": "Bank and financial institution statements"
    },
    "property_docs": {
        "paths": [
            "04_Property_Documentation",
            "05_Morada_Mami_Purchase",
            "05a_US_Property_Purchases"
        ],
        "description": "Property purchase and lease documentation"
    },
    "wire_transfers": {
        "paths": ["04_Wire_Transfers"],
        "description": "Wire transfer records and documentation"
    },
    "corporate_governance": {
        "paths": ["07_Corporate_Governance"],
        "description": "LLC formation and corporate documents"
    },
    "litigation": {
        "paths": [
            "08_Litigation_Expenses",
            "10_Member_Removal_Documentation"
        ],
        "description": "Legal and litigation documentation"
    },
    "tax_documents": {
        "paths": ["09_Tax_Documents"],
        "description": "Tax returns and IRS documentation"
    },
    "supporting_docs": {
        "paths": ["06_Supporting_Documents"],
        "description": "Additional supporting documentation"
    }
}

SUPPORTED_FILE_TYPES = {
    ".pdf": "PDF documents",
    ".xlsx": "Excel spreadsheets",
    ".xls": "Excel spreadsheets (legacy)",
    ".csv": "CSV files",
    ".txt": "Text files",
    ".md": "Markdown files",
    ".png": "PNG images",
    ".jpg": "JPEG images",
    ".jpeg": "JPEG images"
}

VECTOR_DB_PATH = FLOW_ANALYZER_DIR / "chroma_db"
CACHE_DIR = FLOW_ANALYZER_DIR / ".cache"
LOGS_DIR = FLOW_ANALYZER_DIR / "logs"

for dir_path in [VECTOR_DB_PATH, CACHE_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)
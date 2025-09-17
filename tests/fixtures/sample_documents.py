"""
Sample document fixtures for testing ChittyTrace
Provides realistic financial and legal document samples
"""

import json
from datetime import datetime, date
from pathlib import Path
import pandas as pd


class SampleDocuments:
    """Factory for creating sample documents for testing"""

    @staticmethod
    def bank_statement_metadata():
        """Sample bank statement document metadata"""
        return {
            "file_path": "/documents/chase_statement_jan2024.pdf",
            "relative_path": "bank_statements/chase_statement_jan2024.pdf",
            "file_name": "chase_statement_jan2024.pdf",
            "file_type": ".pdf",
            "file_size": 156789,
            "file_hash": "a1b2c3d4e5f6789012345678901234567890abcd",
            "category": "bank_statements",
            "content": SampleDocuments.bank_statement_content(),
            "metadata": {
                "pages": 3,
                "account_number": "****6789",
                "statement_period": "01/01/2024 - 01/31/2024",
                "bank": "Chase Bank"
            },
            "modified_time": "2024-02-01T09:15:30",
            "content_length": 2456
        }

    @staticmethod
    def bank_statement_content():
        """Sample bank statement text content"""
        return """
CHASE BANK
STATEMENT PERIOD: 01/01/2024 - 01/31/2024
ACCOUNT: ****6789

BEGINNING BALANCE: $12,450.67

DEPOSITS:
01/05/2024  DIRECT DEPOSIT - PAYROLL           $5,850.00
01/15/2024  CASH DEPOSIT - BRANCH               $75,000.00
01/20/2024  WIRE TRANSFER - CAYMAN NATL BANK    $125,000.00
01/25/2024  CHECK DEPOSIT                       $3,200.00

WITHDRAWALS:
01/08/2024  ATM WITHDRAWAL                      -$200.00
01/16/2024  WIRE TRANSFER - SWISS BANK          -$50,000.00
01/22/2024  CHECK #1234 - LUXURY AUTO SALES     -$85,000.00
01/28/2024  DEBIT CARD - ROLEX BOUTIQUE         -$45,000.00
01/30/2024  WIRE TRANSFER - PROPERTY ESCROW     -$150,000.00

ENDING BALANCE: $-108,699.33

OVERDRAFT FEES: $350.00
"""

    @staticmethod
    def wire_transfer_metadata():
        """Sample wire transfer document metadata"""
        return {
            "file_path": "/documents/wire_transfer_012024.pdf",
            "relative_path": "wire_transfers/wire_transfer_012024.pdf",
            "file_name": "wire_transfer_012024.pdf",
            "file_type": ".pdf",
            "file_size": 45632,
            "file_hash": "b2c3d4e5f6a1789012345678901234567890bcde",
            "category": "wire_transfers",
            "content": SampleDocuments.wire_transfer_content(),
            "metadata": {
                "pages": 1,
                "amount": 150000.00,
                "currency": "USD",
                "destination_country": "Switzerland"
            },
            "modified_time": "2024-01-30T14:22:15",
            "content_length": 890
        }

    @staticmethod
    def wire_transfer_content():
        """Sample wire transfer receipt content"""
        return """
INTERNATIONAL WIRE TRANSFER RECEIPT
CHASE BANK - WIRE TRANSFER DEPARTMENT

DATE: January 30, 2024
REFERENCE NUMBER: WT-2024-0130-7891

SENDER INFORMATION:
Account Holder: John A. Doe
Account Number: ****6789
Routing Number: 021000021

RECIPIENT INFORMATION:
Beneficiary: Offshore Holdings LLC
Bank: Credit Suisse Private Banking
SWIFT Code: CRESCHZZ80A
Account Number: CH93 0076 2011 6238 5295 7
Address: Zurich, Switzerland

TRANSFER DETAILS:
Amount: $150,000.00 USD
Purpose: Real Estate Investment
Fee: $45.00
Exchange Rate: N/A

AUTHORIZATION:
Authorized by: John A. Doe
Date: 01/30/2024
Time: 14:22:15 EST
"""

    @staticmethod
    def property_deed_metadata():
        """Sample property deed metadata"""
        return {
            "file_path": "/documents/property_deed_123main.pdf",
            "relative_path": "property/property_deed_123main.pdf",
            "file_name": "property_deed_123main.pdf",
            "file_type": ".pdf",
            "file_size": 234567,
            "file_hash": "c3d4e5f6a1b2789012345678901234567890cdef",
            "category": "property_docs",
            "content": SampleDocuments.property_deed_content(),
            "metadata": {
                "pages": 4,
                "property_address": "123 Main Street, Chicago, IL 60601",
                "purchase_price": 850000.00,
                "property_type": "Residential"
            },
            "modified_time": "2024-02-15T11:30:45",
            "content_length": 3421
        }

    @staticmethod
    def property_deed_content():
        """Sample property deed content"""
        return """
WARRANTY DEED

KNOW ALL MEN BY THESE PRESENTS, that for and in consideration of the sum of
EIGHT HUNDRED FIFTY THOUSAND DOLLARS ($850,000.00), the receipt whereof is
hereby acknowledged, Premium Properties LLC, a Delaware limited liability
company, does hereby grant, bargain, sell and convey unto JOHN A. DOE, an
individual, the following described real estate:

LEGAL DESCRIPTION:
Lot 15 in Block 8 of Downtown Plaza Subdivision, being a subdivision of part
of the Southeast Quarter of Section 12, Township 39 North, Range 14 East of
the Third Principal Meridian, in Cook County, Illinois.

COMMONLY KNOWN AS: 123 Main Street, Chicago, IL 60601

PIN: 17-12-345-678-9012

This conveyance is made subject to:
1. Real estate taxes for the year 2024 and subsequent years
2. Covenants, conditions and restrictions of record
3. Easements and rights of way of record

PAYMENT METHOD: Cash - $850,000.00 (Certified funds)

The Grantor hereby covenants with the Grantee that the Grantor is lawfully
seized in fee simple of said premises; that they are free from encumbrances
except as noted above; and that the Grantor will warrant and defend the same.

IN WITNESS WHEREOF, the Grantor has executed this deed on February 15, 2024.

PREMIUM PROPERTIES LLC

By: _________________________
    Maria Rodriguez, Manager

STATE OF ILLINOIS  )
                   ) SS.
COUNTY OF COOK     )

I, the undersigned, a Notary Public in and for said County and State, do
hereby certify that Maria Rodriguez, who is personally known to me to be
the Manager of Premium Properties LLC, appeared before me this day in person
and acknowledged that as such Manager, she signed and delivered the said
instrument as her free and voluntary act, for the uses and purposes therein
set forth.

Given under my hand and notarial seal, this 15th day of February, 2024.

_________________________
Notary Public
"""

    @staticmethod
    def tax_document_metadata():
        """Sample tax document metadata"""
        return {
            "file_path": "/documents/form_1040_2023.pdf",
            "relative_path": "tax_documents/form_1040_2023.pdf",
            "file_name": "form_1040_2023.pdf",
            "file_type": ".pdf",
            "file_size": 89234,
            "file_hash": "d4e5f6a1b2c3789012345678901234567890deff",
            "category": "tax_documents",
            "content": SampleDocuments.tax_document_content(),
            "metadata": {
                "pages": 2,
                "tax_year": 2023,
                "filing_status": "Single",
                "agi": 125000
            },
            "modified_time": "2024-04-10T16:45:20",
            "content_length": 1876
        }

    @staticmethod
    def tax_document_content():
        """Sample tax return content"""
        return """
Form 1040 - U.S. Individual Income Tax Return
Tax Year: 2023

TAXPAYER INFORMATION:
Name: John A. Doe
SSN: XXX-XX-1234
Address: 123 Main Street, Chicago, IL 60601
Filing Status: Single

INCOME:
Wages, salaries, tips (Form W-2): $125,000
Interest income: $2,500
Dividend income: $5,800
Capital gains/losses: $75,000
Total Income: $208,300

ADJUSTMENTS TO INCOME:
IRA contributions: $6,500
Adjusted Gross Income: $201,800

STANDARD DEDUCTION: $13,850
Taxable Income: $187,950

TAX COMPUTATION:
Federal income tax: $42,617
Self-employment tax: $0
Total tax: $42,617

PAYMENTS:
Federal tax withheld: $28,000
Estimated tax payments: $0
Total payments: $28,000

AMOUNT OWED: $14,617

NOTE: Significant increase in capital gains compared to previous years.
Review of investment transactions recommended.
"""

    @staticmethod
    def financial_spreadsheet_data():
        """Sample financial spreadsheet data"""
        return pd.DataFrame({
            'Date': [
                '2024-01-05', '2024-01-15', '2024-01-16', '2024-01-20',
                '2024-01-22', '2024-01-25', '2024-01-28', '2024-01-30'
            ],
            'Transaction_Type': [
                'Deposit', 'Deposit', 'Withdrawal', 'Deposit',
                'Withdrawal', 'Deposit', 'Withdrawal', 'Withdrawal'
            ],
            'Amount': [
                5850.00, 75000.00, -50000.00, 125000.00,
                -85000.00, 3200.00, -45000.00, -150000.00
            ],
            'Description': [
                'Payroll Direct Deposit',
                'Cash Deposit - Branch Location',
                'Wire Transfer to Swiss Bank',
                'Wire from Cayman National Bank',
                'Luxury Auto Purchase',
                'Check Deposit',
                'Rolex Purchase',
                'Property Escrow Wire'
            ],
            'Account': [
                '****6789', '****6789', '****6789', '****6789',
                '****6789', '****6789', '****6789', '****6789'
            ],
            'Balance_After': [
                18300.67, 93300.67, 43300.67, 168300.67,
                83300.67, 86500.67, 41500.67, -108499.33
            ],
            'Flag': [
                'Normal', 'Suspicious - Large Cash', 'Suspicious - Offshore',
                'Suspicious - Offshore', 'Suspicious - Luxury Purchase',
                'Normal', 'Suspicious - Luxury Purchase', 'Suspicious - Large Transfer'
            ]
        })

    @staticmethod
    def create_all_sample_documents():
        """Create a complete set of sample documents for testing"""
        documents = [
            SampleDocuments.bank_statement_metadata(),
            SampleDocuments.wire_transfer_metadata(),
            SampleDocuments.property_deed_metadata(),
            SampleDocuments.tax_document_metadata()
        ]

        # Add spreadsheet as a document
        spreadsheet_df = SampleDocuments.financial_spreadsheet_data()
        spreadsheet_content = spreadsheet_df.to_string(index=False)

        spreadsheet_doc = {
            "file_path": "/documents/financial_analysis.xlsx",
            "relative_path": "spreadsheets/financial_analysis.xlsx",
            "file_name": "financial_analysis.xlsx",
            "file_type": ".xlsx",
            "file_size": 23456,
            "file_hash": "e5f6a1b2c3d4789012345678901234567890efab",
            "category": "financial",
            "content": spreadsheet_content,
            "metadata": {
                "sheets": 1,
                "rows": len(spreadsheet_df),
                "columns": len(spreadsheet_df.columns),
                "suspicious_transactions": len(spreadsheet_df[spreadsheet_df['Flag'].str.contains('Suspicious')])
            },
            "modified_time": "2024-02-01T12:30:00",
            "content_length": len(spreadsheet_content)
        }

        documents.append(spreadsheet_doc)
        return documents

    @staticmethod
    def create_timeline_events():
        """Create sample timeline events extracted from documents"""
        return [
            {
                "date": "2024-01-05",
                "event": "Payroll deposit received",
                "type": "deposit",
                "amount": 5850.00,
                "source_account": "****6789",
                "destination_account": "****6789",
                "source_institution": "Employer Bank",
                "destination_institution": "Chase Bank",
                "description": "Regular payroll direct deposit",
                "source_document": "chase_statement_jan2024.pdf",
                "metadata": {"routine": True}
            },
            {
                "date": "2024-01-15",
                "event": "Large cash deposit",
                "type": "deposit",
                "amount": 75000.00,
                "source_account": "Unknown",
                "destination_account": "****6789",
                "source_institution": "Unknown",
                "destination_institution": "Chase Bank",
                "description": "Suspicious large cash deposit at branch",
                "source_document": "chase_statement_jan2024.pdf",
                "metadata": {"suspicious": True, "cash": True}
            },
            {
                "date": "2024-01-16",
                "event": "Wire transfer to Swiss bank",
                "type": "transfer",
                "amount": -50000.00,
                "source_account": "****6789",
                "destination_account": "CH93-0076-2011-6238-5295-7",
                "source_institution": "Chase Bank",
                "destination_institution": "Credit Suisse",
                "description": "International wire transfer to Switzerland",
                "source_document": "chase_statement_jan2024.pdf",
                "metadata": {"suspicious": True, "offshore": True}
            },
            {
                "date": "2024-01-20",
                "event": "Wire received from Cayman Islands",
                "type": "deposit",
                "amount": 125000.00,
                "source_account": "Unknown",
                "destination_account": "****6789",
                "source_institution": "Cayman National Bank",
                "destination_institution": "Chase Bank",
                "description": "Large wire transfer from offshore bank",
                "source_document": "chase_statement_jan2024.pdf",
                "metadata": {"suspicious": True, "offshore": True}
            },
            {
                "date": "2024-01-22",
                "event": "Luxury vehicle purchase",
                "type": "expense",
                "amount": -85000.00,
                "source_account": "****6789",
                "destination_account": "Unknown",
                "source_institution": "Chase Bank",
                "destination_institution": "Luxury Auto Sales",
                "description": "High-value automobile purchase",
                "source_document": "chase_statement_jan2024.pdf",
                "metadata": {"suspicious": True, "luxury": True}
            },
            {
                "date": "2024-01-28",
                "event": "Luxury goods purchase",
                "type": "expense",
                "amount": -45000.00,
                "source_account": "****6789",
                "destination_account": "Unknown",
                "source_institution": "Chase Bank",
                "destination_institution": "Rolex Boutique",
                "description": "High-value luxury watch purchase",
                "source_document": "chase_statement_jan2024.pdf",
                "metadata": {"suspicious": True, "luxury": True}
            },
            {
                "date": "2024-01-30",
                "event": "Property purchase wire transfer",
                "type": "transfer",
                "amount": -150000.00,
                "source_account": "****6789",
                "destination_account": "Unknown",
                "source_institution": "Chase Bank",
                "destination_institution": "Property Escrow",
                "description": "Wire transfer for real estate purchase",
                "source_document": "wire_transfer_012024.pdf",
                "metadata": {"property": True}
            },
            {
                "date": "2024-02-15",
                "event": "Property deed recorded",
                "type": "property",
                "amount": 850000.00,
                "source_account": "Cash",
                "destination_account": "N/A",
                "source_institution": "N/A",
                "destination_institution": "N/A",
                "description": "Cash purchase of luxury property",
                "source_document": "property_deed_123main.pdf",
                "metadata": {"property": True, "cash_purchase": True}
            }
        ]

    @staticmethod
    def create_case_info():
        """Create sample case information for exhibit generation"""
        return {
            "case_number": "2024-CV-12345",
            "case_caption": "People of the State of Illinois v. John A. Doe",
            "court": "Cook County Circuit Court",
            "judge": "Hon. Patricia Williams",
            "affiant": "Detective Sarah Johnson",
            "affiant_title": "Financial Crimes Detective",
            "affiant_badge": "Badge #4567",
            "department": "Chicago Police Department - Financial Crimes Unit",
            "filing_date": "2024-03-15",
            "case_type": "Money Laundering Investigation"
        }

    @staticmethod
    def create_mock_claude_responses():
        """Create mock Claude API responses for various operations"""
        return {
            "document_analysis": """
Based on the financial documents provided, I have identified several concerning patterns:

1. **Large Cash Deposits**: A $75,000 cash deposit on 01/15/2024 with no clear source documentation
2. **Offshore Transfers**: Wire transfers to and from offshore banks (Switzerland, Cayman Islands)
3. **Luxury Purchases**: High-value purchases including $85,000 vehicle and $45,000 watch
4. **Structured Activity**: Rapid sequence of large transactions within a short timeframe
5. **Cash Property Purchase**: $850,000 property purchased entirely with cash

These patterns are consistent with potential money laundering activity.
            """,

            "timeline_extraction": json.dumps([
                {
                    "date": "2024-01-15",
                    "event": "Large cash deposit",
                    "amount": 75000,
                    "type": "deposit",
                    "suspicious": True
                },
                {
                    "date": "2024-01-20",
                    "event": "Offshore wire received",
                    "amount": 125000,
                    "type": "transfer",
                    "suspicious": True
                },
                {
                    "date": "2024-02-15",
                    "event": "Cash property purchase",
                    "amount": 850000,
                    "type": "property",
                    "suspicious": True
                }
            ]),

            "exhibit_description": """
This exhibit package contains financial evidence demonstrating a pattern of suspicious monetary transactions consistent with money laundering activities. The evidence includes bank statements showing large cash deposits, international wire transfers to offshore accounts, and documentation of high-value cash purchases.
            """,

            "affidavit_content": """
AFFIDAVIT

I, Detective Sarah Johnson, Badge #4567, of the Chicago Police Department Financial Crimes Unit, being first duly sworn, depose and state:

1. I am a sworn law enforcement officer with over 12 years of experience investigating financial crimes.

2. I have reviewed the financial documents attached as Exhibits A-1 through A-4 in this matter.

3. These exhibits are true and accurate copies of original documents obtained through lawful investigation.

4. The documents show a pattern of suspicious financial activity including large cash deposits, offshore wire transfers, and cash purchases of luxury items.

5. This activity occurred during the period of January 2024 through February 2024.

Further affiant sayeth not.

_________________________
Detective Sarah Johnson
Badge #4567
Chicago Police Department

Subscribed and sworn to before me this 15th day of March, 2024.

_________________________
Notary Public
            """
        }


# Convenience functions for pytest fixtures
def get_sample_documents():
    """Get all sample documents as a fixture"""
    return SampleDocuments.create_all_sample_documents()


def get_timeline_events():
    """Get sample timeline events as a fixture"""
    return SampleDocuments.create_timeline_events()


def get_case_info():
    """Get sample case information as a fixture"""
    return SampleDocuments.create_case_info()


def get_mock_responses():
    """Get mock Claude responses as a fixture"""
    return SampleDocuments.create_mock_claude_responses()
"""
Automated form filling system with template support
"""

import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from claude_integration import ClaudeAnalyzer


class FormFiller:
    def __init__(self, analyzer: ClaudeAnalyzer):
        self.analyzer = analyzer
        self.templates_dir = Path("form_templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Common form templates
        self.default_templates = {
            "affidavit": self._get_affidavit_template(),
            "wire_transfer_declaration": self._get_wire_transfer_template(),
            "property_purchase_statement": self._get_property_purchase_template(),
            "irs_penalty_abatement": self._get_irs_template(),
            "exhibit_authentication": self._get_exhibit_auth_template()
        }
    
    async def fill_form(self, template_name: str, data: Dict[str, Any]) -> str:
        """Fill a form template with provided data"""
        # Get template
        if template_name in self.default_templates:
            template = self.default_templates[template_name]
        else:
            template_path = self.templates_dir / f"{template_name}.txt"
            if template_path.exists():
                template = template_path.read_text()
            else:
                raise ValueError(f"Template '{template_name}' not found")
        
        # Use Claude to intelligently fill the form
        filled_form = await self.analyzer.fill_form(template, data)
        
        # Post-process for any missed placeholders
        filled_form = self._replace_placeholders(filled_form, data)
        
        return filled_form
    
    def _replace_placeholders(self, template: str, data: Dict[str, Any]) -> str:
        """Replace any remaining placeholders"""
        # Find all placeholders in format [PLACEHOLDER_NAME]
        placeholders = re.findall(r'\[([A-Z_]+)\]', template)
        
        for placeholder in placeholders:
            # Try to find matching data key (case insensitive)
            for key, value in data.items():
                if key.upper().replace(' ', '_') == placeholder:
                    template = template.replace(f"[{placeholder}]", str(value))
                    break
        
        return template
    
    def _get_affidavit_template(self) -> str:
        return """AFFIDAVIT OF [AFFIANT_NAME]

STATE OF [STATE]
COUNTY OF [COUNTY]

I, [AFFIANT_NAME], being first duly sworn, depose and state as follows:

1. I am over the age of eighteen (18) years and competent to testify to the matters stated herein.

2. I have personal knowledge of the facts set forth in this affidavit.

3. [STATEMENT_1]

4. [STATEMENT_2]

5. [STATEMENT_3]

6. All funds referenced in this affidavit were obtained through lawful means, specifically: [SOURCE_OF_FUNDS].

7. I declare under penalty of perjury under the laws of [STATE] that the foregoing is true and correct.

FURTHER AFFIANT SAYETH NAUGHT.

_______________________________
[AFFIANT_NAME]
Affiant

SUBSCRIBED AND SWORN to before me this _____ day of __________, 20___.

_______________________________
Notary Public
My Commission Expires: ___________"""
    
    def _get_wire_transfer_template(self) -> str:
        return """WIRE TRANSFER DECLARATION

I, [DECLARANT_NAME], hereby declare:

TRANSFER DETAILS:
- Date of Transfer: [TRANSFER_DATE]
- Amount: $[AMOUNT]
- Originating Bank: [SOURCE_BANK]
- Originating Account: [SOURCE_ACCOUNT]
- Beneficiary Bank: [DEST_BANK]
- Beneficiary Account: [DEST_ACCOUNT]
- Beneficiary Name: [BENEFICIARY_NAME]
- Reference Number: [REFERENCE_NUMBER]

PURPOSE OF TRANSFER:
[PURPOSE]

SOURCE OF FUNDS:
The funds transferred originated from [SOURCE_OF_FUNDS] and were obtained through [MEANS_OF_ACQUISITION].

DECLARATION:
I declare that:
1. The information provided above is true and accurate
2. The funds were lawfully obtained
3. The transfer was made for legitimate business/personal purposes
4. No laws were violated in connection with this transfer

Signature: _______________________________
Date: [SIGNATURE_DATE]
Print Name: [DECLARANT_NAME]"""
    
    def _get_property_purchase_template(self) -> str:
        return """PROPERTY PURCHASE STATEMENT

PURCHASER INFORMATION:
Name: [PURCHASER_NAME]
Address: [PURCHASER_ADDRESS]

PROPERTY INFORMATION:
Property Address: [PROPERTY_ADDRESS]
Purchase Date: [PURCHASE_DATE]
Purchase Price: $[PURCHASE_PRICE]
Property Type: [PROPERTY_TYPE]

FUNDING SOURCES:
[FUNDING_SOURCE_1]: $[AMOUNT_1]
[FUNDING_SOURCE_2]: $[AMOUNT_2]
[FUNDING_SOURCE_3]: $[AMOUNT_3]
Total Funds: $[TOTAL_AMOUNT]

TRANSACTION DETAILS:
Escrow Company: [ESCROW_COMPANY]
Closing Date: [CLOSING_DATE]
Deed Recording: [DEED_NUMBER]

DECLARATION:
I, [PURCHASER_NAME], declare that all funds used in this property purchase were obtained through legitimate means as detailed above. All information provided is true and accurate to the best of my knowledge.

_______________________________
Signature

Date: [SIGNATURE_DATE]"""
    
    def _get_irs_template(self) -> str:
        return """REQUEST FOR PENALTY ABATEMENT
FORM 843 ATTACHMENT

TAXPAYER INFORMATION:
Name: [TAXPAYER_NAME]
SSN/EIN: [TAX_ID]
Tax Period: [TAX_PERIOD]
Form Number: [FORM_NUMBER]

PENALTY INFORMATION:
Penalty Amount: $[PENALTY_AMOUNT]
Penalty Type: [PENALTY_TYPE]
Assessment Date: [ASSESSMENT_DATE]

REASONABLE CAUSE EXPLANATION:
[REASONABLE_CAUSE]

SUPPORTING FACTS:
1. [FACT_1]
2. [FACT_2]
3. [FACT_3]

COMPLIANCE HISTORY:
[COMPLIANCE_STATEMENT]

CORRECTIVE ACTIONS:
[CORRECTIVE_ACTIONS]

DECLARATION:
Under penalties of perjury, I declare that I have examined this request, including accompanying documents, and to the best of my knowledge and belief, it is true, correct, and complete.

_______________________________
Signature

Date: [SIGNATURE_DATE]
Phone: [PHONE_NUMBER]"""
    
    def _get_exhibit_auth_template(self) -> str:
        return """AFFIDAVIT OF AUTHENTICITY

RE: [CASE_CAPTION]
Case No.: [CASE_NUMBER]
Exhibit: [EXHIBIT_NUMBER]

I, [AFFIANT_NAME], being first duly sworn, depose and state:

1. I am [TITLE/RELATIONSHIP] and have personal knowledge of the matters stated herein.

2. The attached document marked as Exhibit [EXHIBIT_NUMBER] is a true and accurate copy of [DOCUMENT_DESCRIPTION].

3. This document was [DOCUMENT_ORIGIN] and maintained in the ordinary course of business.

4. The document has not been altered, modified, or tampered with in any way.

5. I am the custodian of records for [ORGANIZATION] and am authorized to certify the authenticity of this document.

I declare under penalty of perjury that the foregoing is true and correct.

_______________________________
[AFFIANT_NAME]
[TITLE]

Subscribed and sworn to before me this _____ day of __________, 20___.

_______________________________
Notary Public
Commission Expires: ___________"""
"""
Federal Rules of Evidence Compliance System
Ensures all evidence meets FRE requirements for court admissibility
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FederalRule(Enum):
    """Federal Rules of Evidence relevant to digital/financial evidence"""
    RULE_104 = "104"  # Preliminary Questions
    RULE_401 = "401"  # Test for Relevant Evidence
    RULE_402 = "402"  # General Admissibility of Relevant Evidence
    RULE_403 = "403"  # Excluding Relevant Evidence for Prejudice, Confusion, or Other Reasons
    RULE_701 = "701"  # Opinion Testimony by Lay Witnesses
    RULE_702 = "702"  # Testimony by Expert Witnesses
    RULE_703 = "703"  # Bases of an Expert's Opinion Testimony
    RULE_704 = "704"  # Opinion on an Ultimate Issue
    RULE_705 = "705"  # Disclosing the Facts or Data Underlying an Expert's Opinion
    RULE_801 = "801"  # Definitions That Apply to This Article; Exclusions from Hearsay
    RULE_802 = "802"  # The Rule Against Hearsay
    RULE_803 = "803"  # Exceptions to the Rule Against Hearsay
    RULE_804 = "804"  # Exceptions to the Rule Against Hearsay When the Declarant Is Unavailable
    RULE_901 = "901"  # Authenticating or Identifying Evidence
    RULE_902 = "902"  # Evidence That Is Self-Authenticating
    RULE_1001 = "1001"  # Definitions That Apply to This Article
    RULE_1002 = "1002"  # Requirement of the Original
    RULE_1003 = "1003"  # Admissibility of Duplicates
    RULE_1004 = "1004"  # Admissibility of Other Evidence of Content
    RULE_1005 = "1005"  # Copies of Public Records to Prove Content
    RULE_1006 = "1006"  # Summaries to Prove Content
    RULE_1007 = "1007"  # Testimony or Statement of a Party to Prove Content
    RULE_1008 = "1008"  # Functions of the Court and Jury


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REQUIRES_FOUNDATION = "requires_foundation"
    CONDITIONAL = "conditional"
    UNKNOWN = "unknown"


@dataclass
class ComplianceCheck:
    """Individual compliance check result"""
    rule: FederalRule
    status: ComplianceStatus
    description: str
    requirements_met: List[str]
    deficiencies: List[str]
    remediation_steps: List[str]
    supporting_evidence: List[str]


class FederalRulesComplianceChecker:
    """Comprehensive FRE compliance checking system"""

    def __init__(self):
        self.rule_requirements = self._initialize_rule_requirements()

    def _initialize_rule_requirements(self) -> Dict[FederalRule, Dict[str, Any]]:
        """Initialize requirements for each Federal Rule"""
        return {
            FederalRule.RULE_401: {
                "name": "Test for Relevant Evidence",
                "requirements": [
                    "Evidence must have tendency to make fact more/less probable",
                    "Fact must be of consequence in determining action"
                ],
                "applies_to": ["financial_analysis", "document_analysis", "timeline_reconstruction"]
            },
            FederalRule.RULE_403: {
                "name": "Excluding Relevant Evidence",
                "requirements": [
                    "Probative value must not be substantially outweighed by prejudice",
                    "Must not confuse issues or mislead jury",
                    "Must not cause undue delay or waste time"
                ],
                "applies_to": ["ai_analysis_results", "statistical_presentations"]
            },
            FederalRule.RULE_702: {
                "name": "Expert Witness Testimony",
                "requirements": [
                    "Expert must be qualified by knowledge, skill, experience, training, or education",
                    "Testimony must help trier of fact understand evidence",
                    "Testimony must be based on sufficient facts or data",
                    "Testimony must be product of reliable principles and methods",
                    "Expert must reliably apply principles and methods to facts"
                ],
                "applies_to": ["ai_analysis_validation", "expert_opinions", "forensic_accounting"]
            },
            FederalRule.RULE_703: {
                "name": "Bases of Expert Opinion",
                "requirements": [
                    "Expert may base opinion on facts/data not admissible in evidence",
                    "Facts/data must be of type reasonably relied upon by experts",
                    "Probative value must substantially outweigh prejudicial effect"
                ],
                "applies_to": ["ai_training_data", "database_analysis", "pattern_recognition"]
            },
            FederalRule.RULE_801: {
                "name": "Hearsay Definitions and Exclusions",
                "requirements": [
                    "Must not be hearsay (out-of-court statement offered for truth)",
                    "If hearsay, must fall under exception",
                    "Machine-generated records may not be hearsay"
                ],
                "applies_to": ["database_records", "automated_reports", "ai_generated_summaries"]
            },
            FederalRule.RULE_803: {
                "name": "Hearsay Exceptions",
                "requirements": [
                    "Business records exception (803(6))",
                    "Public records exception (803(8))",
                    "Computer records exception (803(6))",
                    "Records must be made in regular course of business"
                ],
                "applies_to": ["bank_statements", "transaction_records", "database_entries"]
            },
            FederalRule.RULE_901: {
                "name": "Authentication Requirements",
                "requirements": [
                    "Evidence must be what proponent claims it is",
                    "Sufficient evidence to support finding of authenticity",
                    "May use distinctive characteristics, chain of custody, etc."
                ],
                "applies_to": ["digital_documents", "electronic_records", "database_extracts"]
            },
            FederalRule.RULE_902: {
                "name": "Self-Authenticating Evidence",
                "requirements": [
                    "Certified copies of public records",
                    "Acknowledged documents",
                    "Commercial paper and related documents",
                    "Certified data from electronic processes"
                ],
                "applies_to": ["government_records", "certified_documents", "digital_certificates"]
            },
            FederalRule.RULE_1002: {
                "name": "Best Evidence Rule",
                "requirements": [
                    "Original document required to prove content",
                    "Must account for originals",
                    "Duplicates acceptable unless unfair or question of authenticity"
                ],
                "applies_to": ["document_copies", "scanned_documents", "digital_reproductions"]
            },
            FederalRule.RULE_1003: {
                "name": "Admissibility of Duplicates",
                "requirements": [
                    "Duplicate admissible to same extent as original",
                    "Unless genuine question about original's authenticity",
                    "Unless circumstances make it unfair to admit duplicate"
                ],
                "applies_to": ["photocopies", "digital_copies", "database_printouts"]
            },
            FederalRule.RULE_1006: {
                "name": "Summaries to Prove Content",
                "requirements": [
                    "Summary may be used if originals/duplicates are voluminous",
                    "Underlying documents must be available for examination",
                    "Court may order production of originals/duplicates"
                ],
                "applies_to": ["ai_analysis_summaries", "financial_summaries", "transaction_compilations"]
            }
        }

    def check_digital_evidence_compliance(self, evidence_data: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check digital evidence against FRE requirements"""
        compliance_results = []

        # Rule 901 - Authentication
        auth_check = self._check_authentication_rule_901(evidence_data)
        compliance_results.append(auth_check)

        # Rule 902 - Self-Authentication
        self_auth_check = self._check_self_authentication_rule_902(evidence_data)
        compliance_results.append(self_auth_check)

        # Rule 1002/1003 - Best Evidence Rule
        best_evidence_check = self._check_best_evidence_rules(evidence_data)
        compliance_results.append(best_evidence_check)

        # Rule 803 - Hearsay Exception (Business Records)
        hearsay_check = self._check_hearsay_exception_803(evidence_data)
        compliance_results.append(hearsay_check)

        return compliance_results

    def check_expert_testimony_compliance(self, expert_data: Dict[str, Any],
                                        analysis_data: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check expert testimony against FRE 702-705 requirements"""
        compliance_results = []

        # Rule 702 - Expert Qualifications
        expert_qual_check = self._check_expert_qualifications_rule_702(expert_data)
        compliance_results.append(expert_qual_check)

        # Rule 703 - Basis of Opinion
        opinion_basis_check = self._check_opinion_basis_rule_703(analysis_data)
        compliance_results.append(opinion_basis_check)

        # Rule 704 - Ultimate Issue
        ultimate_issue_check = self._check_ultimate_issue_rule_704(analysis_data)
        compliance_results.append(ultimate_issue_check)

        # Rule 705 - Disclosure of Facts/Data
        disclosure_check = self._check_disclosure_rule_705(analysis_data)
        compliance_results.append(disclosure_check)

        return compliance_results

    def check_ai_analysis_compliance(self, ai_results: Dict[str, Any]) -> List[ComplianceCheck]:
        """Check AI analysis results against relevant FRE rules"""
        compliance_results = []

        # Rule 401 - Relevance
        relevance_check = self._check_relevance_rule_401(ai_results)
        compliance_results.append(relevance_check)

        # Rule 403 - Prejudice vs. Probative Value
        prejudice_check = self._check_prejudice_rule_403(ai_results)
        compliance_results.append(prejudice_check)

        # Rule 1006 - Summaries
        summary_check = self._check_summary_rule_1006(ai_results)
        compliance_results.append(summary_check)

        return compliance_results

    def _check_authentication_rule_901(self, evidence_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 901 - Authentication requirements"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        # Check for digital signatures
        if evidence_data.get("digital_signature"):
            requirements_met.append("Digital signature present")
        else:
            deficiencies.append("No digital signature for authentication")
            remediation_steps.append("Obtain digital signature or certification")

        # Check for hash verification
        if evidence_data.get("hashes"):
            requirements_met.append("Cryptographic hashes available for integrity verification")
        else:
            deficiencies.append("No hash values for integrity verification")
            remediation_steps.append("Calculate and document file hashes")

        # Check for chain of custody
        if evidence_data.get("chain_of_custody"):
            requirements_met.append("Chain of custody documented")
        else:
            deficiencies.append("Chain of custody not documented")
            remediation_steps.append("Establish and document chain of custody")

        # Check for custodian testimony
        if evidence_data.get("custodian"):
            requirements_met.append("Custodian identified for testimony")
        else:
            deficiencies.append("No custodian identified")
            remediation_steps.append("Identify custodian for authentication testimony")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) == 0 else ComplianceStatus.REQUIRES_FOUNDATION

        return ComplianceCheck(
            rule=FederalRule.RULE_901,
            status=status,
            description="Authentication of digital evidence",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Digital signatures", "Hash values", "Chain of custody records"]
        )

    def _check_self_authentication_rule_902(self, evidence_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 902 - Self-authenticating evidence"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        # Check for certified records
        if evidence_data.get("certified_copy"):
            requirements_met.append("Certified copy available")

        # Check for acknowledged documents
        if evidence_data.get("notarized"):
            requirements_met.append("Notarized/acknowledged document")

        # Check for commercial paper
        if evidence_data.get("commercial_paper"):
            requirements_met.append("Commercial paper with standard markings")

        # Check for certified electronic records (Rule 902(13))
        if evidence_data.get("electronic_process_certification"):
            requirements_met.append("Certified electronic process documentation")
        else:
            deficiencies.append("No certification of electronic process")
            remediation_steps.append("Obtain certification of electronic record-keeping process")

        status = ComplianceStatus.COMPLIANT if len(requirements_met) > 0 else ComplianceStatus.CONDITIONAL

        return ComplianceCheck(
            rule=FederalRule.RULE_902,
            status=status,
            description="Self-authenticating evidence provisions",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Certifications", "Acknowledgments", "Process documentation"]
        )

    def _check_best_evidence_rules(self, evidence_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rules 1002/1003 - Best Evidence Rule"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        # Check for original vs. duplicate
        if evidence_data.get("is_original"):
            requirements_met.append("Original document available")
        elif evidence_data.get("duplicate_explanation"):
            requirements_met.append("Explanation for using duplicate provided")
        else:
            deficiencies.append("No explanation for absence of original")
            remediation_steps.append("Provide explanation for why original is not available")

        # Check duplicate integrity
        if evidence_data.get("exact_duplicate"):
            requirements_met.append("Exact duplicate verified")
        else:
            deficiencies.append("Duplicate accuracy not verified")
            remediation_steps.append("Verify duplicate is exact copy of original")

        # Check for authenticity questions
        if evidence_data.get("authenticity_questioned"):
            deficiencies.append("Authenticity of original questioned")
            remediation_steps.append("Address authenticity concerns before admitting duplicate")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) == 0 else ComplianceStatus.REQUIRES_FOUNDATION

        return ComplianceCheck(
            rule=FederalRule.RULE_1002,
            status=status,
            description="Best Evidence Rule compliance",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Original documents", "Duplicate certifications", "Integrity verification"]
        )

    def _check_hearsay_exception_803(self, evidence_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 803(6) - Business Records Exception"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        # Check for business record characteristics
        if evidence_data.get("business_record"):
            requirements_met.append("Qualifies as business record")
        else:
            deficiencies.append("Does not qualify as business record")
            remediation_steps.append("Establish business record foundation")

        # Check for regular course of business
        if evidence_data.get("regular_course"):
            requirements_met.append("Made in regular course of business")
        else:
            deficiencies.append("Not made in regular course of business")
            remediation_steps.append("Establish record was made in regular course of business")

        # Check for contemporaneous creation
        if evidence_data.get("contemporaneous"):
            requirements_met.append("Record made at or near time of event")
        else:
            deficiencies.append("Record not made contemporaneously")
            remediation_steps.append("Establish timing of record creation")

        # Check for custodian/qualified witness
        if evidence_data.get("qualified_witness"):
            requirements_met.append("Qualified witness available")
        else:
            deficiencies.append("No qualified witness for foundation")
            remediation_steps.append("Identify custodian or other qualified witness")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) <= 1 else ComplianceStatus.REQUIRES_FOUNDATION

        return ComplianceCheck(
            rule=FederalRule.RULE_803,
            status=status,
            description="Business Records Exception to Hearsay",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Business record certification", "Custodian testimony", "Process documentation"]
        )

    def _check_expert_qualifications_rule_702(self, expert_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 702 - Expert Witness Qualifications"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        # Check qualifications
        if expert_data.get("education"):
            requirements_met.append("Relevant education documented")
        if expert_data.get("experience_years", 0) >= 5:
            requirements_met.append("Sufficient experience (5+ years)")
        elif expert_data.get("experience_years", 0) > 0:
            requirements_met.append(f"Some experience ({expert_data['experience_years']} years)")
        else:
            deficiencies.append("Insufficient experience documented")
            remediation_steps.append("Document relevant experience and training")

        if expert_data.get("certifications"):
            requirements_met.append("Professional certifications")

        if expert_data.get("prior_testimony", 0) > 0:
            requirements_met.append("Prior court testimony experience")

        # Check methodology reliability
        if expert_data.get("reliable_methodology"):
            requirements_met.append("Reliable methodology employed")
        else:
            deficiencies.append("Methodology reliability not established")
            remediation_steps.append("Establish reliability of methodology under Daubert standard")

        # Check if testimony will help trier of fact
        if expert_data.get("helpful_to_jury"):
            requirements_met.append("Testimony will help jury understand evidence")
        else:
            deficiencies.append("Helpfulness to jury not established")
            remediation_steps.append("Demonstrate how testimony will help jury")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) == 0 else ComplianceStatus.REQUIRES_FOUNDATION

        return ComplianceCheck(
            rule=FederalRule.RULE_702,
            status=status,
            description="Expert witness qualifications and reliability",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["CV", "Certifications", "Prior testimony records", "Methodology documentation"]
        )

    def _check_opinion_basis_rule_703(self, analysis_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 703 - Basis of Expert Opinion"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        # Check if based on admissible evidence
        if analysis_data.get("based_on_admissible_evidence"):
            requirements_met.append("Opinion based on admissible evidence")

        # Check if inadmissible data is reasonably relied upon
        if analysis_data.get("reasonably_relied_upon_data"):
            requirements_met.append("Uses data reasonably relied upon by experts in field")
        else:
            deficiencies.append("Basis for relying on inadmissible data not established")
            remediation_steps.append("Establish that data is reasonably relied upon by experts")

        # Check probative value vs. prejudicial effect
        if analysis_data.get("probative_value_outweighs_prejudice"):
            requirements_met.append("Probative value outweighs prejudicial effect")
        else:
            deficiencies.append("Probative value vs. prejudice not assessed")
            remediation_steps.append("Assess probative value vs. prejudicial effect")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) == 0 else ComplianceStatus.CONDITIONAL

        return ComplianceCheck(
            rule=FederalRule.RULE_703,
            status=status,
            description="Basis of expert opinion",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Data sources documentation", "Industry practice evidence"]
        )

    def _check_ultimate_issue_rule_704(self, analysis_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 704 - Opinion on Ultimate Issue"""
        # Rule 704 generally allows opinion on ultimate issue
        return ComplianceCheck(
            rule=FederalRule.RULE_704,
            status=ComplianceStatus.COMPLIANT,
            description="Opinion on ultimate issue permitted",
            requirements_met=["Expert may testify to ultimate issue"],
            deficiencies=[],
            remediation_steps=[],
            supporting_evidence=["Rule 704 permits ultimate issue testimony"]
        )

    def _check_disclosure_rule_705(self, analysis_data: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 705 - Disclosure of Facts/Data"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        if analysis_data.get("facts_disclosed"):
            requirements_met.append("Underlying facts and data disclosed")
        else:
            deficiencies.append("Underlying facts and data not fully disclosed")
            remediation_steps.append("Disclose facts and data underlying opinion")

        if analysis_data.get("cross_examination_possible"):
            requirements_met.append("Facts/data subject to cross-examination")
        else:
            deficiencies.append("Cross-examination of underlying data not facilitated")
            remediation_steps.append("Ensure underlying data is available for cross-examination")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) == 0 else ComplianceStatus.REQUIRES_FOUNDATION

        return ComplianceCheck(
            rule=FederalRule.RULE_705,
            status=status,
            description="Disclosure of underlying facts and data",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Disclosed facts and data", "Cross-examination materials"]
        )

    def _check_relevance_rule_401(self, ai_results: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 401 - Relevance"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        if ai_results.get("makes_fact_probable"):
            requirements_met.append("Evidence makes fact more or less probable")
        else:
            deficiencies.append("Relevance to material fact not established")
            remediation_steps.append("Establish how evidence makes material fact more/less probable")

        if ai_results.get("material_to_case"):
            requirements_met.append("Fact is material to the case")
        else:
            deficiencies.append("Materiality not established")
            remediation_steps.append("Establish materiality of fact to case")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) == 0 else ComplianceStatus.REQUIRES_FOUNDATION

        return ComplianceCheck(
            rule=FederalRule.RULE_401,
            status=status,
            description="Relevance of AI analysis results",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Materiality documentation", "Probative value analysis"]
        )

    def _check_prejudice_rule_403(self, ai_results: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 403 - Prejudice vs. Probative Value"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        if ai_results.get("high_probative_value"):
            requirements_met.append("High probative value")

        if ai_results.get("low_prejudicial_effect"):
            requirements_met.append("Low prejudicial effect")
        else:
            deficiencies.append("Potential for prejudicial effect")
            remediation_steps.append("Address potential prejudicial effects")

        if ai_results.get("not_confusing"):
            requirements_met.append("Unlikely to confuse jury")
        else:
            deficiencies.append("May confuse jury")
            remediation_steps.append("Simplify presentation to avoid jury confusion")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) <= 1 else ComplianceStatus.CONDITIONAL

        return ComplianceCheck(
            rule=FederalRule.RULE_403,
            status=status,
            description="Probative value vs. prejudicial effect",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Probative value analysis", "Prejudice assessment"]
        )

    def _check_summary_rule_1006(self, ai_results: Dict[str, Any]) -> ComplianceCheck:
        """Check Rule 1006 - Summaries"""
        requirements_met = []
        deficiencies = []
        remediation_steps = []

        if ai_results.get("underlying_docs_voluminous"):
            requirements_met.append("Underlying documents are voluminous")

        if ai_results.get("underlying_docs_available"):
            requirements_met.append("Underlying documents available for examination")
        else:
            deficiencies.append("Underlying documents not available")
            remediation_steps.append("Make underlying documents available for examination")

        if ai_results.get("accurate_summary"):
            requirements_met.append("Summary accurately reflects underlying documents")
        else:
            deficiencies.append("Accuracy of summary not verified")
            remediation_steps.append("Verify summary accurately reflects underlying documents")

        status = ComplianceStatus.COMPLIANT if len(deficiencies) == 0 else ComplianceStatus.REQUIRES_FOUNDATION

        return ComplianceCheck(
            rule=FederalRule.RULE_1006,
            status=status,
            description="Summaries of voluminous documents",
            requirements_met=requirements_met,
            deficiencies=deficiencies,
            remediation_steps=remediation_steps,
            supporting_evidence=["Underlying documents", "Summary accuracy verification"]
        )

    def generate_compliance_report(self, all_checks: List[ComplianceCheck]) -> str:
        """Generate comprehensive compliance report"""
        compliant_count = sum(1 for check in all_checks if check.status == ComplianceStatus.COMPLIANT)
        total_count = len(all_checks)

        report = f"""
FEDERAL RULES OF EVIDENCE COMPLIANCE REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

SUMMARY:
Compliant Rules: {compliant_count}/{total_count} ({compliant_count/total_count*100:.1f}%)

DETAILED ANALYSIS:
"""

        for check in all_checks:
            status_symbol = "✓" if check.status == ComplianceStatus.COMPLIANT else "⚠" if check.status == ComplianceStatus.CONDITIONAL else "✗"

            report += f"""
{status_symbol} RULE {check.rule.value} - {check.description}
Status: {check.status.value.upper()}

Requirements Met:
"""
            for req in check.requirements_met:
                report += f"  ✓ {req}\n"

            if check.deficiencies:
                report += "\nDeficiencies:\n"
                for def_ in check.deficiencies:
                    report += f"  ✗ {def_}\n"

            if check.remediation_steps:
                report += "\nRemediation Steps:\n"
                for step in check.remediation_steps:
                    report += f"  → {step}\n"

            report += "\n" + "="*80 + "\n"

        return report
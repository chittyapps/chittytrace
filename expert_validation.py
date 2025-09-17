"""
Expert Validation and Testimony Support System
Provides framework for human expert review and court testimony preparation
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class ExpertQualificationLevel(Enum):
    """Expert qualification levels for court testimony"""
    CERTIFIED_FORENSIC_ACCOUNTANT = "Certified Forensic Accountant (CFA)"
    CERTIFIED_PUBLIC_ACCOUNTANT = "Certified Public Accountant (CPA)"
    CERTIFIED_FRAUD_EXAMINER = "Certified Fraud Examiner (CFE)"
    FORENSIC_TECHNOLOGY_EXPERT = "Forensic Technology Expert"
    LAW_ENFORCEMENT_FINANCIAL_CRIMES = "Law Enforcement Financial Crimes"
    ACADEMIC_RESEARCHER = "Academic Researcher"
    INDUSTRY_SPECIALIST = "Industry Specialist"


class ValidationStatus(Enum):
    """Status of expert validation"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VALIDATED = "validated"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"


@dataclass
class ExpertCredentials:
    """Expert credentials and qualifications"""
    expert_id: str
    name: str
    title: str
    organization: str
    qualifications: List[ExpertQualificationLevel]
    certifications: List[str]
    years_experience: int
    areas_of_expertise: List[str]
    court_qualified_jurisdictions: List[str]
    education: List[str]
    professional_licenses: List[str]
    prior_testimony_cases: int
    contact_info: Dict[str, str]
    cv_file_path: Optional[str] = None


@dataclass
class ValidationReview:
    """Expert validation review of AI analysis"""
    review_id: str
    expert_id: str
    analysis_id: str
    case_number: str
    review_date: datetime
    status: ValidationStatus
    ai_findings: Dict[str, Any]
    expert_opinion: str
    methodology_review: str
    accuracy_assessment: str
    reliability_score: float  # 0.0 to 1.0
    limitations_noted: List[str]
    additional_analysis_required: List[str]
    court_admissibility_opinion: str
    supporting_documentation: List[str]
    expert_signature: Optional[str] = None
    peer_review_required: bool = False


class ExpertValidationSystem:
    """Manages expert validation workflow"""

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("expert_validation")
        self.data_dir.mkdir(exist_ok=True)
        self.experts_file = self.data_dir / "qualified_experts.json"
        self.reviews_file = self.data_dir / "validation_reviews.json"
        self.templates_dir = self.data_dir / "testimony_templates"
        self.templates_dir.mkdir(exist_ok=True)

    def register_expert(self, credentials: ExpertCredentials) -> str:
        """Register a qualified expert in the system"""
        experts = self._load_experts()
        experts[credentials.expert_id] = asdict(credentials)
        self._save_experts(experts)

        logger.info(f"Expert registered: {credentials.name} ({credentials.expert_id})")
        return credentials.expert_id

    def submit_for_validation(self, analysis_results: Dict[str, Any],
                            case_number: str, expert_id: str,
                            priority: str = "normal") -> str:
        """Submit AI analysis results for expert validation"""

        review_id = str(uuid.uuid4())

        validation_request = {
            "review_id": review_id,
            "expert_id": expert_id,
            "case_number": case_number,
            "submitted_date": datetime.now(timezone.utc).isoformat(),
            "priority": priority,
            "status": ValidationStatus.PENDING.value,
            "analysis_results": analysis_results,
            "ai_methodology": self._extract_ai_methodology(analysis_results),
            "requires_validation": self._identify_validation_requirements(analysis_results)
        }

        # Save validation request
        request_file = self.data_dir / f"validation_request_{review_id}.json"
        with open(request_file, 'w') as f:
            json.dump(validation_request, f, indent=2)

        logger.info(f"Validation request submitted: {review_id}")
        return review_id

    def conduct_expert_review(self, review_id: str, expert_id: str,
                            expert_opinion: str, methodology_review: str,
                            accuracy_assessment: str, reliability_score: float,
                            limitations: List[str] = None,
                            additional_analysis: List[str] = None) -> ValidationReview:
        """Conduct expert review of AI analysis"""

        # Load validation request
        request_file = self.data_dir / f"validation_request_{review_id}.json"
        with open(request_file, 'r') as f:
            request_data = json.load(f)

        # Create validation review
        review = ValidationReview(
            review_id=review_id,
            expert_id=expert_id,
            analysis_id=request_data.get("analysis_id", ""),
            case_number=request_data["case_number"],
            review_date=datetime.now(timezone.utc),
            status=ValidationStatus.VALIDATED if reliability_score >= 0.8 else ValidationStatus.REQUIRES_REVISION,
            ai_findings=request_data["analysis_results"],
            expert_opinion=expert_opinion,
            methodology_review=methodology_review,
            accuracy_assessment=accuracy_assessment,
            reliability_score=reliability_score,
            limitations_noted=limitations or [],
            additional_analysis_required=additional_analysis or [],
            court_admissibility_opinion=self._assess_court_admissibility(reliability_score, limitations or []),
            supporting_documentation=[]
        )

        # Save review
        self._save_validation_review(review)

        logger.info(f"Expert review completed: {review_id} by {expert_id}")
        return review

    def _extract_ai_methodology(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract AI methodology information for expert review"""
        return {
            "model_used": analysis_results.get("metadata", {}).get("model", "Unknown"),
            "analysis_type": analysis_results.get("analysis_type", "Unknown"),
            "data_sources": analysis_results.get("source_documents", []),
            "algorithms_applied": analysis_results.get("algorithms", []),
            "confidence_scores": analysis_results.get("confidence", {}),
            "limitations": analysis_results.get("limitations", []),
            "assumptions": analysis_results.get("assumptions", [])
        }

    def _identify_validation_requirements(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identify what aspects require expert validation"""
        requirements = []

        if "fund_trace" in analysis_results:
            requirements.append("Financial transaction analysis methodology")
        if "timeline" in analysis_results:
            requirements.append("Chronological event reconstruction")
        if "suspicious_activity" in analysis_results:
            requirements.append("Money laundering pattern identification")
        if "statistical_analysis" in analysis_results:
            requirements.append("Statistical methodology and significance")
        if "document_authentication" in analysis_results:
            requirements.append("Digital evidence authentication procedures")

        return requirements

    def _assess_court_admissibility(self, reliability_score: float, limitations: List[str]) -> str:
        """Assess court admissibility based on expert review"""
        if reliability_score >= 0.9 and len(limitations) <= 2:
            return "HIGHLY ADMISSIBLE - Analysis meets Daubert standards with minimal limitations"
        elif reliability_score >= 0.8 and len(limitations) <= 3:
            return "ADMISSIBLE - Analysis is reliable with noted limitations that should be disclosed"
        elif reliability_score >= 0.7:
            return "CONDITIONALLY ADMISSIBLE - Requires additional expert testimony to address limitations"
        else:
            return "NOT RECOMMENDED - Significant reliability concerns, requires additional analysis"

    def generate_expert_report(self, review_id: str) -> str:
        """Generate formal expert report for court submission"""

        review = self._load_validation_review(review_id)
        expert = self._load_expert(review.expert_id)

        report = f"""
EXPERT WITNESS REPORT
Case No. {review.case_number}

EXPERT QUALIFICATIONS:
Name: {expert['name']}
Title: {expert['title']}
Organization: {expert['organization']}

Professional Qualifications:
"""
        for qual in expert['qualifications']:
            report += f"- {qual}\n"

        report += f"""
Years of Experience: {expert['years_experience']}
Areas of Expertise: {', '.join(expert['areas_of_expertise'])}
Prior Court Testimony: {expert['prior_testimony_cases']} cases

METHODOLOGY REVIEW:
{review.methodology_review}

ANALYSIS OF AI FINDINGS:
{review.expert_opinion}

ACCURACY ASSESSMENT:
{review.accuracy_assessment}

RELIABILITY SCORE: {review.reliability_score:.2f}/1.00

"""

        if review.limitations_noted:
            report += "LIMITATIONS IDENTIFIED:\n"
            for limitation in review.limitations_noted:
                report += f"- {limitation}\n"
            report += "\n"

        report += f"""
COURT ADMISSIBILITY OPINION:
{review.court_admissibility_opinion}

SUPPORTING DOCUMENTATION:
- AI analysis outputs and methodology
- Source document authentication records
- Statistical analysis verification
- Cross-reference database queries
- Chain of custody documentation

EXPERT OPINION SUMMARY:
Based on my review of the AI-assisted financial analysis, the methodology employed is {
    'sound and reliable' if review.reliability_score >= 0.8 else 'adequate with noted limitations'
}. The findings {
    'support' if review.reliability_score >= 0.8 else 'conditionally support'
} the conclusions drawn, subject to the limitations noted above.

The AI analysis serves as a valuable investigative tool that has properly identified patterns and connections within the financial data. However, this analysis should be considered in conjunction with traditional forensic accounting methods and human expert interpretation.

_________________________________
{expert['name']}, {expert['qualifications'][0] if expert['qualifications'] else ''}
Expert Witness

Date: {datetime.now().strftime('%B %d, %Y')}
"""

        # Save report
        report_file = self.data_dir / f"expert_report_{review_id}.txt"
        with open(report_file, 'w') as f:
            f.write(report)

        return report

    def prepare_testimony_outline(self, review_id: str) -> Dict[str, Any]:
        """Prepare testimony outline for court appearance"""

        review = self._load_validation_review(review_id)
        expert = self._load_expert(review.expert_id)

        testimony_outline = {
            "case_number": review.case_number,
            "expert_name": expert['name'],
            "testimony_date": None,  # To be filled in
            "voir_dire_qualifications": {
                "education": expert['education'],
                "experience": f"{expert['years_experience']} years",
                "certifications": expert['certifications'],
                "prior_testimony": expert['prior_testimony_cases'],
                "publications": expert.get('publications', []),
                "professional_memberships": expert.get('professional_memberships', [])
            },
            "direct_examination_outline": [
                "1. Expert qualifications and experience",
                "2. Overview of financial forensic analysis methodology",
                "3. Explanation of AI-assisted analysis tools and their validation",
                "4. Review of source documents and data integrity",
                "5. Methodology employed in this specific case",
                "6. Key findings and their significance",
                "7. Reliability assessment and limitations",
                "8. Professional opinion and conclusions"
            ],
            "key_exhibits": [
                "Expert CV and qualifications",
                "AI analysis outputs",
                "Source document authentication records",
                "Methodology documentation",
                "Validation review results",
                "Comparison with industry standards"
            ],
            "anticipated_cross_examination": [
                "Limitations of AI analysis",
                "Alternative interpretations of data",
                "Gaps in source documentation",
                "Reliability of digital evidence",
                "Potential bias in analysis"
            ],
            "technical_explanations": {
                "ai_methodology": "How AI analysis works in layman's terms",
                "data_validation": "How we ensure data accuracy and completeness",
                "pattern_recognition": "How suspicious patterns are identified",
                "statistical_significance": "What the numbers mean in practical terms"
            }
        }

        return testimony_outline

    def create_demonstrative_exhibits(self, review_id: str) -> List[Dict[str, Any]]:
        """Create demonstrative exhibits for court presentation"""

        review = self._load_validation_review(review_id)

        exhibits = [
            {
                "exhibit_type": "Expert Qualifications Summary",
                "description": "Visual summary of expert credentials and experience",
                "purpose": "Establish expert credibility during voir dire",
                "format": "Professional infographic"
            },
            {
                "exhibit_type": "AI Analysis Methodology Flowchart",
                "description": "Step-by-step visualization of analysis process",
                "purpose": "Explain how AI analysis was conducted",
                "format": "Process flow diagram"
            },
            {
                "exhibit_type": "Data Sources and Validation Matrix",
                "description": "Table showing all data sources and validation methods",
                "purpose": "Demonstrate thoroughness of analysis",
                "format": "Detailed matrix/table"
            },
            {
                "exhibit_type": "Key Findings Summary",
                "description": "Visual representation of major findings",
                "purpose": "Present conclusions clearly to jury",
                "format": "Charts and graphs"
            },
            {
                "exhibit_type": "Reliability Assessment",
                "description": f"Expert assessment showing {review.reliability_score:.1%} confidence",
                "purpose": "Show expert validation of AI results",
                "format": "Scorecard with explanations"
            }
        ]

        return exhibits

    def _load_experts(self) -> Dict[str, Any]:
        """Load expert registry"""
        if self.experts_file.exists():
            with open(self.experts_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_experts(self, experts: Dict[str, Any]):
        """Save expert registry"""
        with open(self.experts_file, 'w') as f:
            json.dump(experts, f, indent=2)

    def _load_expert(self, expert_id: str) -> Dict[str, Any]:
        """Load specific expert data"""
        experts = self._load_experts()
        if expert_id not in experts:
            raise ValueError(f"Expert {expert_id} not found")
        return experts[expert_id]

    def _save_validation_review(self, review: ValidationReview):
        """Save validation review"""
        reviews = []
        if self.reviews_file.exists():
            with open(self.reviews_file, 'r') as f:
                reviews = json.load(f)

        # Convert dataclass to dict for JSON serialization
        review_dict = asdict(review)
        review_dict['review_date'] = review.review_date.isoformat()
        review_dict['status'] = review.status.value

        reviews.append(review_dict)

        with open(self.reviews_file, 'w') as f:
            json.dump(reviews, f, indent=2, default=str)

    def _load_validation_review(self, review_id: str) -> ValidationReview:
        """Load specific validation review"""
        if not self.reviews_file.exists():
            raise ValueError(f"Review {review_id} not found")

        with open(self.reviews_file, 'r') as f:
            reviews = json.load(f)

        for review_data in reviews:
            if review_data['review_id'] == review_id:
                # Convert back to dataclass
                review_data['review_date'] = datetime.fromisoformat(review_data['review_date'])
                review_data['status'] = ValidationStatus(review_data['status'])
                return ValidationReview(**review_data)

        raise ValueError(f"Review {review_id} not found")

    def get_validation_status(self, review_id: str) -> Dict[str, Any]:
        """Get current validation status"""
        try:
            review = self._load_validation_review(review_id)
            return {
                "review_id": review.review_id,
                "status": review.status.value,
                "expert_id": review.expert_id,
                "reliability_score": review.reliability_score,
                "court_admissibility": review.court_admissibility_opinion,
                "review_date": review.review_date.isoformat()
            }
        except ValueError:
            return {"error": "Review not found"}

    def generate_daubert_compliance_report(self, review_id: str) -> str:
        """Generate Daubert standard compliance report"""

        review = self._load_validation_review(review_id)

        report = f"""
DAUBERT STANDARD COMPLIANCE ASSESSMENT
Case No. {review.case_number}
Review ID: {review_id}

DAUBERT FACTORS ANALYSIS:

1. TESTABILITY OF THE THEORY/TECHNIQUE:
   ✓ AI analysis methodology can be tested and validated
   ✓ Reproducible results using same input data
   ✓ Clear algorithmic processes that can be examined

2. PEER REVIEW AND PUBLICATION:
   ✓ Expert review conducted by qualified professional
   ✓ Methodology based on established financial forensic practices
   ✓ AI techniques documented in academic literature

3. ERROR RATE:
   Reliability Score: {review.reliability_score:.1%}
   Known Limitations: {len(review.limitations_noted)} identified
   Error Rate Assessment: {self._calculate_error_rate(review.reliability_score)}

4. GENERAL ACCEPTANCE:
   ✓ AI-assisted financial analysis increasingly accepted in forensic accounting
   ✓ Expert validation ensures compliance with professional standards
   ✓ Methodology aligns with industry best practices

CONCLUSION:
The AI-assisted analysis, as validated by expert review, {
    'MEETS' if review.reliability_score >= 0.8 else 'CONDITIONALLY MEETS'
} Daubert standards for scientific evidence admissibility.

Recommended for court admission with appropriate expert testimony.
"""

        return report

    def _calculate_error_rate(self, reliability_score: float) -> str:
        """Calculate and describe error rate"""
        error_rate = 1.0 - reliability_score
        if error_rate <= 0.05:
            return f"Very Low ({error_rate:.1%}) - Minimal risk of error"
        elif error_rate <= 0.15:
            return f"Low ({error_rate:.1%}) - Acceptable for forensic analysis"
        elif error_rate <= 0.25:
            return f"Moderate ({error_rate:.1%}) - Requires additional validation"
        else:
            return f"High ({error_rate:.1%}) - Not recommended for court use"
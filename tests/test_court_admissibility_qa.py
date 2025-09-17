"""
Comprehensive QA Testing for Court Admissibility Features
Tests all new court admissibility components end-to-end
"""

import pytest
import tempfile
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import hashlib

# Import the new court admissibility modules
from evidence_authentication import DigitalEvidenceAuthenticator
from expert_validation import ExpertValidationSystem, ExpertCredentials, ExpertQualificationLevel
from federal_rules_compliance import FederalRulesComplianceChecker, FederalRule, ComplianceStatus
from court_admissible_package_generator import CourtAdmissiblePackageGenerator


class TestDigitalEvidenceAuthentication:
    """Test the digital evidence authentication system"""

    @pytest.fixture
    def temp_evidence_dir(self):
        """Create temporary directory for evidence testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def sample_document(self, temp_evidence_dir):
        """Create a sample document for testing"""
        doc_path = temp_evidence_dir / "sample_document.txt"
        doc_path.write_text("This is a sample financial document with transaction data.")
        return doc_path

    def test_authenticator_initialization(self, temp_evidence_dir):
        """Test digital evidence authenticator initialization"""
        authenticator = DigitalEvidenceAuthenticator(temp_evidence_dir)

        assert authenticator.evidence_dir == temp_evidence_dir
        assert (temp_evidence_dir / "signing_key.pem").exists()
        assert (temp_evidence_dir / "public_key.pem").exists()

    def test_file_hash_calculation(self, temp_evidence_dir, sample_document):
        """Test multiple hash algorithm calculation"""
        authenticator = DigitalEvidenceAuthenticator(temp_evidence_dir)

        hashes = authenticator._calculate_file_hashes(sample_document)

        assert "md5" in hashes
        assert "sha1" in hashes
        assert "sha256" in hashes
        assert "sha512" in hashes
        assert len(hashes["sha256"]) == 64  # SHA-256 produces 64 hex characters

    def test_document_authentication(self, temp_evidence_dir, sample_document):
        """Test complete document authentication"""
        authenticator = DigitalEvidenceAuthenticator(temp_evidence_dir)

        auth_record = authenticator.authenticate_document(
            sample_document,
            custodian="Test Custodian",
            collection_method="automated"
        )

        assert auth_record["file_name"] == "sample_document.txt"
        assert auth_record["custodian"] == "Test Custodian"
        assert "digital_signature" in auth_record
        assert "hashes" in auth_record
        assert auth_record["compliance"]["fed_rules_evidence"] == ["901", "902", "1001"]

    def test_signature_verification(self, temp_evidence_dir, sample_document):
        """Test digital signature verification"""
        authenticator = DigitalEvidenceAuthenticator(temp_evidence_dir)

        auth_record = authenticator.authenticate_document(
            sample_document,
            custodian="Test Custodian"
        )

        # Verify signature
        is_valid = authenticator.verify_signature(auth_record)
        assert is_valid is True

    def test_chain_of_custody(self, temp_evidence_dir, sample_document):
        """Test chain of custody tracking"""
        authenticator = DigitalEvidenceAuthenticator(temp_evidence_dir)

        # Authenticate document
        auth_record = authenticator.authenticate_document(
            sample_document,
            custodian="Initial Custodian"
        )

        # Transfer custody
        transfer_record = authenticator.create_custody_transfer_record(
            "sample_document.txt",
            "Initial Custodian",
            "Detective Smith",
            "Evidence analysis"
        )

        assert transfer_record["from_custodian"] == "Initial Custodian"
        assert transfer_record["to_custodian"] == "Detective Smith"
        assert "transfer_id" in transfer_record

    def test_integrity_verification(self, temp_evidence_dir, sample_document):
        """Test file integrity verification"""
        authenticator = DigitalEvidenceAuthenticator(temp_evidence_dir)

        # Authenticate original
        original_record = authenticator.authenticate_document(
            sample_document,
            custodian="Test Custodian"
        )

        # Verify integrity (should pass)
        integrity_check = authenticator.verify_file_integrity(sample_document, original_record)
        assert integrity_check["integrity_status"] == "verified"

        # Modify file and test again
        sample_document.write_text("Modified content")
        integrity_check2 = authenticator.verify_file_integrity(sample_document, original_record)
        assert integrity_check2["integrity_status"] == "compromised"


class TestExpertValidationSystem:
    """Test the expert validation workflow"""

    @pytest.fixture
    def validation_system(self):
        """Create expert validation system with temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ExpertValidationSystem(Path(temp_dir))

    @pytest.fixture
    def sample_expert_credentials(self):
        """Create sample expert credentials"""
        return ExpertCredentials(
            expert_id="expert_001",
            name="Dr. Sarah Johnson",
            title="Senior Forensic Accountant",
            organization="Financial Crimes Investigation Unit",
            qualifications=[
                ExpertQualificationLevel.CERTIFIED_FORENSIC_ACCOUNTANT,
                ExpertQualificationLevel.CERTIFIED_PUBLIC_ACCOUNTANT
            ],
            certifications=["CFA", "CPA", "CFE"],
            years_experience=15,
            areas_of_expertise=["Financial Forensics", "Money Laundering", "Digital Evidence"],
            court_qualified_jurisdictions=["Cook County", "Federal District"],
            education=["MBA Finance", "MS Accounting"],
            professional_licenses=["CPA IL-12345"],
            prior_testimony_cases=25,
            contact_info={"email": "sarah.johnson@expert.com", "phone": "555-0123"}
        )

    def test_expert_registration(self, validation_system, sample_expert_credentials):
        """Test expert registration"""
        expert_id = validation_system.register_expert(sample_expert_credentials)

        assert expert_id == "expert_001"

        # Verify expert was saved
        experts = validation_system._load_experts()
        assert "expert_001" in experts
        assert experts["expert_001"]["name"] == "Dr. Sarah Johnson"

    def test_validation_submission(self, validation_system, sample_expert_credentials):
        """Test validation request submission"""
        # Register expert first
        validation_system.register_expert(sample_expert_credentials)

        analysis_results = {
            "fund_trace": "Suspicious activity detected",
            "confidence": 0.85,
            "source_documents": ["bank_statement.pdf", "wire_transfer.pdf"]
        }

        review_id = validation_system.submit_for_validation(
            analysis_results,
            "2024-CV-001",
            "expert_001",
            priority="high"
        )

        assert review_id is not None
        assert len(review_id) == 36  # UUID length

    @pytest.mark.asyncio
    async def test_expert_review_process(self, validation_system, sample_expert_credentials):
        """Test complete expert review process"""
        # Register expert
        validation_system.register_expert(sample_expert_credentials)

        # Submit for validation
        analysis_results = {
            "fund_trace": "Multiple suspicious transactions identified",
            "methodology": "AI-assisted pattern recognition",
            "confidence": 0.87
        }

        review_id = validation_system.submit_for_validation(
            analysis_results, "2024-CV-001", "expert_001"
        )

        # Conduct expert review
        review = validation_system.conduct_expert_review(
            review_id,
            "expert_001",
            expert_opinion="Analysis is sound and conclusions are supported",
            methodology_review="Methodology follows industry best practices",
            accuracy_assessment="95% accuracy verified through cross-checking",
            reliability_score=0.87,
            limitations=["Limited to provided documents"],
            additional_analysis=[]
        )

        assert review.reliability_score == 0.87
        assert review.expert_id == "expert_001"
        assert len(review.limitations_noted) == 1

    def test_expert_report_generation(self, validation_system, sample_expert_credentials):
        """Test expert report generation"""
        # Setup
        validation_system.register_expert(sample_expert_credentials)
        review_id = validation_system.submit_for_validation(
            {"test": "data"}, "2024-CV-001", "expert_001"
        )

        validation_system.conduct_expert_review(
            review_id, "expert_001", "Test opinion", "Test methodology",
            "Test accuracy", 0.85
        )

        # Generate report
        report = validation_system.generate_expert_report(review_id)

        assert "EXPERT WITNESS REPORT" in report
        assert "Dr. Sarah Johnson" in report
        assert "Case No. 2024-CV-001" in report
        assert "RELIABILITY SCORE: 0.85" in report

    def test_daubert_compliance_report(self, validation_system, sample_expert_credentials):
        """Test Daubert standard compliance assessment"""
        # Setup complete review
        validation_system.register_expert(sample_expert_credentials)
        review_id = validation_system.submit_for_validation(
            {"test": "data"}, "2024-CV-001", "expert_001"
        )

        validation_system.conduct_expert_review(
            review_id, "expert_001", "Test opinion", "Test methodology",
            "Test accuracy", 0.88
        )

        # Generate Daubert report
        daubert_report = validation_system.generate_daubert_compliance_report(review_id)

        assert "DAUBERT STANDARD COMPLIANCE ASSESSMENT" in daubert_report
        assert "TESTABILITY OF THE THEORY/TECHNIQUE" in daubert_report
        assert "MEETS" in daubert_report  # Should meet standards with 0.88 score


class TestFederalRulesCompliance:
    """Test Federal Rules of Evidence compliance checking"""

    @pytest.fixture
    def compliance_checker(self):
        """Create compliance checker instance"""
        return FederalRulesComplianceChecker()

    def test_digital_evidence_compliance_check(self, compliance_checker):
        """Test digital evidence compliance checking"""
        evidence_data = {
            "digital_signature": "valid_signature",
            "hashes": {"sha256": "abc123"},
            "chain_of_custody": True,
            "custodian": "Detective Smith",
            "certified_copy": True,
            "business_record": True,
            "regular_course": True,
            "contemporaneous": True,
            "qualified_witness": True
        }

        compliance_results = compliance_checker.check_digital_evidence_compliance(evidence_data)

        # Should have checks for Rules 901, 902, 1002, 803
        rule_numbers = [check.rule.value for check in compliance_results]
        assert "901" in rule_numbers  # Authentication
        assert "902" in rule_numbers  # Self-authentication
        assert "1002" in rule_numbers  # Best evidence
        assert "803" in rule_numbers  # Hearsay exception

    def test_expert_testimony_compliance(self, compliance_checker):
        """Test expert testimony compliance checking"""
        expert_data = {
            "education": ["PhD Finance"],
            "experience_years": 15,
            "certifications": ["CFA", "CPA"],
            "prior_testimony": 20,
            "reliable_methodology": True,
            "helpful_to_jury": True
        }

        analysis_data = {
            "based_on_admissible_evidence": True,
            "reasonably_relied_upon_data": True,
            "probative_value_outweighs_prejudice": True,
            "facts_disclosed": True,
            "cross_examination_possible": True
        }

        compliance_results = compliance_checker.check_expert_testimony_compliance(
            expert_data, analysis_data
        )

        rule_numbers = [check.rule.value for check in compliance_results]
        assert "702" in rule_numbers  # Expert qualifications
        assert "703" in rule_numbers  # Basis of opinion
        assert "705" in rule_numbers  # Disclosure

    def test_ai_analysis_compliance(self, compliance_checker):
        """Test AI analysis compliance checking"""
        ai_results = {
            "makes_fact_probable": True,
            "material_to_case": True,
            "high_probative_value": True,
            "low_prejudicial_effect": True,
            "not_confusing": True,
            "underlying_docs_voluminous": True,
            "underlying_docs_available": True,
            "accurate_summary": True
        }

        compliance_results = compliance_checker.check_ai_analysis_compliance(ai_results)

        rule_numbers = [check.rule.value for check in compliance_results]
        assert "401" in rule_numbers  # Relevance
        assert "403" in rule_numbers  # Prejudice vs probative value
        assert "1006" in rule_numbers  # Summaries

    def test_compliance_report_generation(self, compliance_checker):
        """Test comprehensive compliance report generation"""
        # Create mock compliance checks
        mock_checks = [
            Mock(rule=FederalRule.RULE_901, status=ComplianceStatus.COMPLIANT,
                 description="Authentication", requirements_met=["Digital signature"],
                 deficiencies=[], remediation_steps=[]),
            Mock(rule=FederalRule.RULE_702, status=ComplianceStatus.REQUIRES_FOUNDATION,
                 description="Expert qualifications", requirements_met=["Experience"],
                 deficiencies=["No CV provided"], remediation_steps=["Provide expert CV"])
        ]

        report = compliance_checker.generate_compliance_report(mock_checks)

        assert "FEDERAL RULES OF EVIDENCE COMPLIANCE REPORT" in report
        assert "1/2 (50.0%)" in report  # 1 compliant out of 2
        assert "✓ RULE 901" in report
        assert "⚠ RULE 702" in report


class TestCourtAdmissiblePackageGenerator:
    """Test the enhanced court admissible package generator"""

    @pytest.fixture
    def temp_package_dir(self):
        """Create temporary directory for package testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_analyzer(self):
        """Create mock Claude analyzer"""
        analyzer = Mock()
        analyzer.index_documents = Mock()
        analyzer.execute_analysis_command = Mock(return_value={
            "fund_trace": "Suspicious patterns detected",
            "timeline": "Events reconstructed"
        })
        analyzer.analyze_with_context = Mock(return_value="Analysis complete")
        return analyzer

    @pytest.fixture
    def sample_documents(self, temp_package_dir):
        """Create sample documents for testing"""
        docs = []
        for i in range(3):
            doc_path = temp_package_dir / f"document_{i+1}.txt"
            doc_path.write_text(f"Sample document {i+1} content")
            docs.append({
                "file_path": str(doc_path),
                "file_name": f"document_{i+1}.txt",
                "category": "financial",
                "content": f"Sample document {i+1} content"
            })
        return docs

    @pytest.fixture
    def case_info(self):
        """Sample case information"""
        return {
            "case_number": "2024-CV-12345",
            "case_caption": "People v. Defendant",
            "court": "Cook County Circuit Court",
            "affiant": "Detective Johnson"
        }

    def test_package_generator_initialization(self, mock_analyzer):
        """Test package generator initialization"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        assert generator.analyzer == mock_analyzer
        assert generator.authenticator is not None
        assert generator.validator is not None
        assert generator.compliance_checker is not None

    def test_expert_registration(self, mock_analyzer):
        """Test expert registration functionality"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        expert_id = generator.register_expert(
            name="Dr. Test Expert",
            title="Forensic Accountant",
            organization="Test Org",
            qualifications=["CFA", "CPA"],
            years_experience=10
        )

        assert expert_id is not None
        assert len(expert_id) == 36  # UUID length

    @pytest.mark.asyncio
    async def test_comprehensive_ai_analysis(self, mock_analyzer, sample_documents):
        """Test comprehensive AI analysis functionality"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        # Mock the async methods
        mock_analyzer.execute_analysis_command = Mock(side_effect=asyncio.coroutine(
            lambda cmd, params: {"result": f"Analysis for {cmd}"}
        ))
        mock_analyzer.analyze_with_context = Mock(side_effect=asyncio.coroutine(
            lambda query: f"Response to: {query}"
        ))

        analysis = await generator._perform_comprehensive_analysis(sample_documents)

        assert "analysis_id" in analysis
        assert "analyses" in analysis
        assert analysis["document_count"] == 3

    def test_compliance_checking(self, mock_analyzer, temp_package_dir):
        """Test Federal Rules compliance checking"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        # Create mock authenticated documents
        authenticated_docs = [{
            "document": {"file_path": str(temp_package_dir / "test.txt")},
            "authentication": {
                "digital_signature": "test_sig",
                "hashes": {"sha256": "test_hash"},
                "chain_of_custody": True,
                "custodian": "Test Custodian"
            }
        }]

        # Mock expert review
        mock_expert_review = Mock()
        mock_expert_review.expert_id = "expert_001"
        mock_expert_review.reliability_score = 0.85

        # Mock AI analysis
        ai_analysis = {"test": "analysis"}

        compliance_results = generator._check_all_compliance(
            authenticated_docs, mock_expert_review, ai_analysis
        )

        assert len(compliance_results) > 0
        assert all(hasattr(check, 'rule') for check in compliance_results)

    def test_admissibility_assessment(self, mock_analyzer):
        """Test admissibility assessment logic"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        # Create mock compliance results (all compliant)
        mock_compliance = [
            Mock(status=Mock(value="compliant")),
            Mock(status=Mock(value="compliant"))
        ]

        # Create mock expert review (high reliability)
        mock_expert_review = Mock()
        mock_expert_review.reliability_score = 0.9
        mock_expert_review.limitations_noted = ["Minor limitation"]

        is_admissible = generator._is_admissible(mock_compliance, mock_expert_review)
        assert is_admissible is True

        # Test with low reliability score
        mock_expert_review.reliability_score = 0.6
        is_admissible = generator._is_admissible(mock_compliance, mock_expert_review)
        assert is_admissible is False

    @pytest.mark.asyncio
    async def test_exhibit_content_generation(self, mock_analyzer, temp_package_dir, case_info):
        """Test individual exhibit content generation"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        doc_data = {
            "document": {
                "file_name": "test_document.pdf",
                "category": "financial",
                "modified_time": "2024-01-15T10:00:00",
                "content": "Sample financial document content"
            },
            "authentication": {
                "hashes": {"sha256": "abc123def456"},
                "custodian": "Detective Smith",
                "authenticated_at": "2024-01-15T10:00:00Z"
            }
        }

        exhibit_content = await generator._generate_exhibit_content(
            doc_data, "A-1", case_info, {"analysis": "test"}
        )

        assert "EXHIBIT A-1" in exhibit_content
        assert case_info["case_number"] in exhibit_content
        assert "SHA-256 Hash: abc123def456" in exhibit_content
        assert "Detective Smith" in exhibit_content

    def test_cover_letter_generation(self, mock_analyzer, case_info):
        """Test cover letter generation"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        cover_letter = generator._generate_cover_letter(case_info, "pkg_123", 5)

        assert "COURT EXHIBIT PACKAGE SUBMISSION" in cover_letter
        assert case_info["case_number"] in cover_letter
        assert "5 exhibits" in cover_letter
        assert "Package ID: pkg_123" in cover_letter

    def test_table_of_contents_generation(self, mock_analyzer):
        """Test table of contents generation"""
        generator = CourtAdmissiblePackageGenerator(mock_analyzer)

        mock_exhibits = [
            {"exhibit_number": "A-1", "document": {"file_name": "doc1.pdf"}},
            {"exhibit_number": "A-2", "document": {"file_name": "doc2.pdf"}}
        ]

        auth_package = {"package_files": ["auth_records.json", "hashes.txt"]}

        toc = generator._generate_table_of_contents(mock_exhibits, auth_package)

        assert "TABLE OF CONTENTS" in toc
        assert "A-1 - doc1.pdf" in toc
        assert "A-2 - doc2.pdf" in toc
        assert "TOTAL EXHIBITS: 2" in toc


@pytest.mark.integration
class TestFullWorkflowIntegration:
    """Integration tests for complete court admissibility workflow"""

    @pytest.fixture
    def full_system_setup(self):
        """Set up complete system for integration testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock analyzer
            analyzer = Mock()
            analyzer.index_documents = Mock()
            analyzer.execute_analysis_command = Mock(side_effect=asyncio.coroutine(
                lambda cmd, params: {"result": f"Mock {cmd} analysis"}
            ))
            analyzer.analyze_with_context = Mock(side_effect=asyncio.coroutine(
                lambda query: f"Mock analysis for: {query}"
            ))

            # Create package generator
            generator = CourtAdmissiblePackageGenerator(analyzer)
            generator.output_dir = temp_path / "packages"
            generator.output_dir.mkdir()

            # Create sample documents
            docs_dir = temp_path / "documents"
            docs_dir.mkdir()

            documents = []
            for i in range(2):
                doc_path = docs_dir / f"evidence_{i+1}.txt"
                doc_path.write_text(f"Evidence document {i+1} with financial data")
                documents.append({
                    "file_path": str(doc_path),
                    "file_name": f"evidence_{i+1}.txt",
                    "category": "financial",
                    "content": f"Evidence document {i+1} with financial data"
                })

            yield {
                "generator": generator,
                "analyzer": analyzer,
                "documents": documents,
                "temp_dir": temp_path
            }

    @pytest.mark.asyncio
    async def test_complete_admissible_package_workflow(self, full_system_setup):
        """Test complete workflow from documents to admissible package"""
        setup = full_system_setup
        generator = setup["generator"]
        documents = setup["documents"]

        # Register expert
        expert_id = generator.register_expert(
            name="Dr. Integration Test",
            title="Test Expert",
            organization="Test Org",
            qualifications=["CFA"],
            years_experience=10
        )

        case_info = {
            "case_number": "2024-TEST-001",
            "case_caption": "Test Case v. Defendant",
            "court": "Test Court",
            "affiant": "Test Detective"
        }

        # Generate admissible package
        with patch('evidence_authentication.DigitalEvidenceAuthenticator._load_or_generate_signing_key'):
            # Mock the RSA key generation to avoid cryptography issues in testing
            mock_key = Mock()
            mock_key.sign = Mock(return_value=b"mock_signature")
            mock_key.public_key = Mock(return_value=Mock())

            with patch('evidence_authentication.DigitalEvidenceAuthenticator.private_key', mock_key):
                package = await generator.generate_admissible_exhibit_package(
                    documents, case_info, expert_id, "Test Custodian"
                )

        # Verify package structure
        assert "package_id" in package
        assert package["case_number"] == "2024-TEST-001"

        # Check for admissible vs non-admissible
        if package.get("status") == "NON_ADMISSIBLE":
            assert "remediation_steps" in package
            assert len(package["remediation_steps"]) > 0
        else:
            assert package["court_admissibility"] == "ADMISSIBLE"
            assert package["exhibits_count"] == 2

    def test_error_handling_and_remediation(self, full_system_setup):
        """Test error handling and remediation guidance"""
        setup = full_system_setup
        generator = setup["generator"]

        # Test with missing expert
        case_info = {"case_number": "2024-ERROR-001"}

        with pytest.raises(Exception):
            # This should fail because expert doesn't exist
            asyncio.run(generator.generate_admissible_exhibit_package(
                [], case_info, "nonexistent_expert"
            ))

    def test_performance_with_multiple_documents(self, full_system_setup):
        """Test system performance with multiple documents"""
        setup = full_system_setup
        temp_dir = setup["temp_dir"]

        # Create larger document set
        large_doc_set = []
        for i in range(10):
            doc_path = temp_dir / f"large_doc_{i}.txt"
            doc_path.write_text(f"Large document {i} content " * 100)  # Make it bigger
            large_doc_set.append({
                "file_path": str(doc_path),
                "file_name": f"large_doc_{i}.txt",
                "category": "financial",
                "content": f"Large document {i} content"
            })

        # Test authentication performance
        authenticator = DigitalEvidenceAuthenticator(temp_dir / "auth")

        import time
        start_time = time.time()

        with patch('evidence_authentication.DigitalEvidenceAuthenticator._load_or_generate_signing_key'):
            mock_key = Mock()
            mock_key.sign = Mock(return_value=b"mock_signature")
            mock_key.public_key = Mock(return_value=Mock())

            with patch('evidence_authentication.DigitalEvidenceAuthenticator.private_key', mock_key):
                for doc in large_doc_set[:3]:  # Test with first 3 documents
                    authenticator.authenticate_document(
                        Path(doc["file_path"]),
                        "Test Custodian"
                    )

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process documents reasonably quickly
        assert processing_time < 10.0  # Allow up to 10 seconds for 3 documents


if __name__ == "__main__":
    # Run specific test categories
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "auth":
            pytest.main(["-v", "TestDigitalEvidenceAuthentication"])
        elif sys.argv[1] == "expert":
            pytest.main(["-v", "TestExpertValidationSystem"])
        elif sys.argv[1] == "compliance":
            pytest.main(["-v", "TestFederalRulesCompliance"])
        elif sys.argv[1] == "package":
            pytest.main(["-v", "TestCourtAdmissiblePackageGenerator"])
        elif sys.argv[1] == "integration":
            pytest.main(["-v", "TestFullWorkflowIntegration"])
        else:
            pytest.main(["-v", __file__])
    else:
        pytest.main(["-v", __file__])
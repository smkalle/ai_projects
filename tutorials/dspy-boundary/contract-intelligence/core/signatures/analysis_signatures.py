"""DSPy signatures for contract analysis tasks."""

import dspy
from typing import List, Dict, Any


class ContractAnalysisSignature(dspy.Signature):
    """Analyze a contract and extract key information."""
    
    contract_text = dspy.InputField(desc="The full text of the contract to analyze")
    contract_type = dspy.OutputField(desc="Type of contract (e.g., employment, service, lease, NDA)")
    parties = dspy.OutputField(desc="JSON list of parties involved with their roles")
    key_dates = dspy.OutputField(desc="JSON object of important dates (effective, expiration, etc.)")
    key_terms = dspy.OutputField(desc="JSON object of key financial and business terms")
    executive_summary = dspy.OutputField(desc="Brief 2-3 sentence summary of the contract")


class ClauseExtractionSignature(dspy.Signature):
    """Extract and categorize clauses from a contract."""
    
    contract_text = dspy.InputField(desc="The contract text to analyze for clauses")
    target_clause_types = dspy.InputField(desc="Comma-separated list of clause types to look for")
    extracted_clauses = dspy.OutputField(desc="JSON list of extracted clauses with type, text, and importance")
    unusual_clauses = dspy.OutputField(desc="JSON list of unusual or non-standard clauses found")


class RiskAssessmentSignature(dspy.Signature):
    """Assess risks in a contract."""
    
    contract_text = dspy.InputField(desc="The contract text to assess for risks")
    contract_type = dspy.InputField(desc="Type of contract for context")
    risk_factors = dspy.OutputField(desc="JSON list of identified risks with severity and impact")
    overall_risk_score = dspy.OutputField(desc="Overall risk score from 1-10 (10 being highest risk)")
    mitigation_recommendations = dspy.OutputField(desc="JSON list of recommended risk mitigation strategies")


class ObligationTrackingSignature(dspy.Signature):
    """Track obligations and commitments in a contract."""
    
    contract_text = dspy.InputField(desc="The contract text to analyze for obligations")
    party_focus = dspy.InputField(desc="Which party's obligations to focus on (or 'all')")
    obligations = dspy.OutputField(desc="JSON list of obligations with party, description, deadlines")
    deliverables = dspy.OutputField(desc="JSON list of deliverables and milestones")
    payment_obligations = dspy.OutputField(desc="JSON list of payment terms and schedules")


class ComplianceCheckSignature(dspy.Signature):
    """Check contract compliance against regulations."""
    
    contract_text = dspy.InputField(desc="The contract text to check for compliance")
    regulation_type = dspy.InputField(desc="Type of regulation to check (GDPR, SOX, HIPAA, etc.)")
    compliance_status = dspy.OutputField(desc="Overall compliance status (compliant/non-compliant/needs-review)")
    violations = dspy.OutputField(desc="JSON list of potential compliance violations found")
    recommendations = dspy.OutputField(desc="JSON list of actions needed to achieve compliance")


class ContractComparisonSignature(dspy.Signature):
    """Compare two contracts and identify differences."""
    
    contract_a = dspy.InputField(desc="First contract text for comparison")
    contract_b = dspy.InputField(desc="Second contract text for comparison")
    comparison_focus = dspy.InputField(desc="Aspect to focus on (terms, clauses, risks, all)")
    key_differences = dspy.OutputField(desc="JSON list of major differences between contracts")
    similarity_score = dspy.OutputField(desc="Similarity percentage between contracts")
    risk_comparison = dspy.OutputField(desc="Comparison of risk levels between contracts")


class KeyTermsExtractionSignature(dspy.Signature):
    """Extract key terms and values from a contract."""
    
    contract_text = dspy.InputField(desc="The contract text to analyze")
    term_categories = dspy.InputField(desc="Categories of terms to extract (financial, dates, parties, etc.)")
    parties_info = dspy.OutputField(desc="JSON object with detailed party information")
    financial_terms = dspy.OutputField(desc="JSON object with monetary values, payment terms, etc.")
    important_dates = dspy.OutputField(desc="JSON object with all contract dates and deadlines")
    jurisdiction_info = dspy.OutputField(desc="Governing law and jurisdiction information")


class ContractSummarySignature(dspy.Signature):
    """Generate comprehensive contract summary."""
    
    contract_text = dspy.InputField(desc="The full contract text to summarize")
    summary_type = dspy.InputField(desc="Type of summary needed (executive, detailed, technical)")
    executive_summary = dspy.OutputField(desc="High-level summary for executives (2-3 paragraphs)")
    key_highlights = dspy.OutputField(desc="JSON list of the most important contract points")
    action_items = dspy.OutputField(desc="JSON list of immediate actions required")
    red_flags = dspy.OutputField(desc="JSON list of concerning clauses or terms")


class ContractClassificationSignature(dspy.Signature):
    """Classify contract type and characteristics."""
    
    contract_text = dspy.InputField(desc="Contract text to classify")
    primary_type = dspy.OutputField(desc="Primary contract type (service, employment, lease, etc.)")
    sub_categories = dspy.OutputField(desc="JSON list of applicable sub-categories")
    industry_sector = dspy.OutputField(desc="Industry or sector this contract applies to")
    complexity_level = dspy.OutputField(desc="Complexity level (simple, moderate, complex)")
    standard_vs_custom = dspy.OutputField(desc="Assessment of how standard vs customized the contract is")


class LegalReviewSignature(dspy.Signature):
    """Provide legal review insights for a contract."""
    
    contract_text = dspy.InputField(desc="Contract text for legal review")
    review_focus = dspy.InputField(desc="Focus area for review (general, specific clause type)")
    legal_concerns = dspy.OutputField(desc="JSON list of legal issues or concerns identified")
    enforceability_assessment = dspy.OutputField(desc="Assessment of contract enforceability")
    missing_clauses = dspy.OutputField(desc="JSON list of important clauses that may be missing")
    revision_suggestions = dspy.OutputField(desc="JSON list of suggested revisions or improvements")
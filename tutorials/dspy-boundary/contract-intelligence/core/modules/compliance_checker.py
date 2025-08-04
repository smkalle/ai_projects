"""Compliance checking module using DSPy for regulatory compliance analysis."""

import json
import logging
import re
from typing import Dict, List, Any, Optional

import dspy

from core.signatures.analysis_signatures import ComplianceCheckSignature
from models.document import ParsedDocument, ComplianceCheck
from config.settings import settings

logger = logging.getLogger(__name__)


class ComplianceChecker(dspy.Module):
    """Check contract compliance against various regulations using DSPy."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        
        self.checker = dspy.ChainOfThought(ComplianceCheckSignature)
        
        # Regulation templates and requirements
        self.regulations = {
            "GDPR": {
                "name": "General Data Protection Regulation",
                "requirements": [
                    "Data processing lawful basis",
                    "Data subject consent mechanisms",
                    "Right to erasure (right to be forgotten)",
                    "Data portability provisions",
                    "Privacy by design principles",
                    "Data breach notification procedures",
                    "Data Protection Officer requirements",
                    "Cross-border data transfer safeguards"
                ],
                "keywords": [
                    "personal data", "data subject", "processing", "consent",
                    "privacy", "data protection", "erasure", "portability"
                ],
                "risk_patterns": [
                    r"unlimited\s+data\s+retention",
                    r"no\s+consent\s+mechanism",
                    r"third\s+party\s+transfer\s+without\s+safeguards"
                ]
            },
            "SOX": {
                "name": "Sarbanes-Oxley Act",
                "requirements": [
                    "Financial reporting controls",
                    "Internal control documentation",
                    "Audit trail requirements",
                    "Record retention policies",
                    "Whistleblower protections",
                    "Management certification requirements"
                ],
                "keywords": [
                    "financial controls", "audit", "records", "certification",
                    "internal controls", "financial reporting"
                ],
                "risk_patterns": [
                    r"no\s+audit\s+trail",
                    r"inadequate\s+record\s+keeping",
                    r"lack\s+of\s+internal\s+controls"
                ]
            },
            "HIPAA": {
                "name": "Health Insurance Portability and Accountability Act",
                "requirements": [
                    "Protected Health Information (PHI) safeguards",
                    "Business Associate Agreements",
                    "Minimum necessary standards",
                    "Security safeguards for ePHI",
                    "Breach notification requirements",
                    "Patient rights provisions"
                ],
                "keywords": [
                    "protected health information", "PHI", "medical records",
                    "health data", "patient information", "medical privacy"
                ],
                "risk_patterns": [
                    r"unrestricted\s+access\s+to\s+PHI",
                    r"no\s+encryption\s+for\s+health\s+data",
                    r"missing\s+business\s+associate\s+agreement"
                ]
            },
            "PCI_DSS": {
                "name": "Payment Card Industry Data Security Standard",
                "requirements": [
                    "Secure network and systems",
                    "Protect cardholder data",
                    "Maintain vulnerability management",
                    "Implement strong access controls",
                    "Regular monitoring and testing",
                    "Information security policy"
                ],
                "keywords": [
                    "payment card", "cardholder data", "credit card",
                    "payment processing", "card data security"
                ],
                "risk_patterns": [
                    r"unencrypted\s+card\s+data",
                    r"inadequate\s+access\s+controls",
                    r"no\s+regular\s+security\s+testing"
                ]
            },
            "CCPA": {
                "name": "California Consumer Privacy Act",
                "requirements": [
                    "Consumer right to know",
                    "Consumer right to delete",
                    "Consumer right to opt-out",
                    "Non-discrimination provisions",
                    "Data minimization principles",
                    "Third-party disclosure requirements"
                ],
                "keywords": [
                    "personal information", "consumer rights", "opt-out",
                    "data deletion", "privacy rights", "california"
                ],
                "risk_patterns": [
                    r"no\s+opt-out\s+mechanism",
                    r"unclear\s+data\s+collection\s+notice",
                    r"discriminatory\s+practices"
                ]
            }
        }
        
        if model_name:
            self.lm = dspy.LM(model=model_name)
            dspy.configure(lm=self.lm)
    
    def check_compliance(
        self, 
        parsed_doc: ParsedDocument,
        regulations: Optional[List[str]] = None
    ) -> List[ComplianceCheck]:
        """Check compliance against specified regulations."""
        
        if regulations is None:
            # Auto-detect relevant regulations based on content
            regulations = self._detect_relevant_regulations(parsed_doc.text)
        
        compliance_results = []
        
        for regulation in regulations:
            if regulation not in self.regulations:
                logger.warning(f"Unknown regulation: {regulation}")
                continue
            
            try:
                # Check compliance using DSPy
                ai_result = self._check_with_dspy(parsed_doc, regulation)
                
                # Check compliance using rules
                rule_result = self._check_with_rules(parsed_doc, regulation)
                
                # Combine results
                combined_result = self._combine_compliance_results(ai_result, rule_result, regulation)
                compliance_results.append(combined_result)
                
            except Exception as e:
                logger.error(f"Compliance check failed for {regulation}: {str(e)}")
                fallback_result = self._fallback_compliance_check(regulation)
                compliance_results.append(fallback_result)
        
        logger.info(f"Compliance check completed for {len(compliance_results)} regulations")
        return compliance_results
    
    def _detect_relevant_regulations(self, text: str) -> List[str]:
        """Auto-detect which regulations might be relevant to this contract."""
        
        text_lower = text.lower()
        relevant_regulations = []
        
        for regulation, config in self.regulations.items():
            # Check for keyword matches
            keyword_matches = 0
            for keyword in config["keywords"]:
                if keyword.lower() in text_lower:
                    keyword_matches += 1
            
            # If we find multiple relevant keywords, include this regulation
            if keyword_matches >= 2:
                relevant_regulations.append(regulation)
        
        # Always include GDPR for any contract mentioning data/privacy
        data_privacy_indicators = ["data", "privacy", "personal information", "processing"]
        if any(indicator in text_lower for indicator in data_privacy_indicators):
            if "GDPR" not in relevant_regulations:
                relevant_regulations.append("GDPR")
        
        # Default to GDPR if no specific regulations detected
        if not relevant_regulations:
            relevant_regulations = ["GDPR"]
        
        return relevant_regulations
    
    def _check_with_dspy(self, parsed_doc: ParsedDocument, regulation: str) -> Dict[str, Any]:
        """Check compliance using DSPy module."""
        
        try:
            text = self._prepare_text_for_analysis(parsed_doc.text)
            
            result = self.checker(
                contract_text=text,
                regulation_type=regulation
            )
            
            return {
                "status": result.compliance_status,
                "violations": self._parse_json_safely(result.violations),
                "recommendations": self._parse_json_safely(result.recommendations)
            }
            
        except Exception as e:
            logger.error(f"DSPy compliance check failed for {regulation}: {str(e)}")
            return {"status": "needs-review", "violations": [], "recommendations": []}
    
    def _check_with_rules(self, parsed_doc: ParsedDocument, regulation: str) -> Dict[str, Any]:
        """Check compliance using rule-based analysis."""
        
        text = parsed_doc.text.lower()
        config = self.regulations[regulation]
        
        violations = []
        recommendations = []
        
        # Check for risk patterns
        for pattern in config["risk_patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Potential violation: {pattern}")
                recommendations.append(f"Review and address: {pattern}")
        
        # Check for missing requirements
        missing_requirements = []
        for requirement in config["requirements"]:
            if not self._check_requirement_present(text, requirement):
                missing_requirements.append(requirement)
        
        if missing_requirements:
            violations.extend([f"Missing requirement: {req}" for req in missing_requirements])
            recommendations.extend([f"Consider adding: {req}" for req in missing_requirements])
        
        # Determine status
        if violations:
            status = "non-compliant" if len(violations) > 3 else "needs-review"
        else:
            # Check for positive indicators
            keyword_matches = sum(1 for keyword in config["keywords"] if keyword in text)
            status = "compliant" if keyword_matches >= 3 else "needs-review"
        
        return {
            "status": status,
            "violations": violations,
            "recommendations": recommendations
        }
    
    def _check_requirement_present(self, text: str, requirement: str) -> bool:
        """Check if a specific requirement appears to be addressed in the text."""
        
        # Create search terms from the requirement
        requirement_lower = requirement.lower()
        
        # Key terms mapping
        requirement_terms = {
            "data processing lawful basis": ["lawful basis", "legal basis", "legitimate interest"],
            "consent mechanisms": ["consent", "agree", "authorization"],
            "right to erasure": ["erasure", "deletion", "remove", "forget"],
            "data portability": ["portability", "transfer", "export"],
            "privacy by design": ["privacy by design", "data protection by design"],
            "breach notification": ["breach notification", "security incident"],
            "data protection officer": ["data protection officer", "dpo"],
            "cross-border transfer": ["international transfer", "cross-border", "third country"],
            "financial controls": ["financial controls", "internal controls"],
            "audit trail": ["audit trail", "audit log", "record keeping"],
            "record retention": ["retention", "record keeping", "document retention"],
            "whistleblower": ["whistleblower", "reporting", "complaint"],
            "protected health information": ["phi", "protected health", "medical records"],
            "business associate": ["business associate", "ba agreement"],
            "minimum necessary": ["minimum necessary", "need to know"],
            "security safeguards": ["security safeguards", "security measures"],
            "cardholder data": ["cardholder data", "card data", "payment card"],
            "access controls": ["access control", "authentication", "authorization"],
            "vulnerability management": ["vulnerability", "security testing", "penetration test"],
            "consumer right to know": ["right to know", "transparency"],
            "right to delete": ["right to delete", "deletion", "erasure"],
            "opt-out": ["opt-out", "opt out", "withdraw consent"]
        }
        
        # Check if any relevant terms are present
        for req_key, terms in requirement_terms.items():
            if req_key in requirement_lower:
                return any(term in text for term in terms)
        
        # Fallback: check for key words from the requirement itself
        requirement_words = [word for word in requirement_lower.split() if len(word) > 3]
        matches = sum(1 for word in requirement_words if word in text)
        
        return matches >= len(requirement_words) // 2  # At least half the words present
    
    def _combine_compliance_results(
        self, 
        ai_result: Dict[str, Any], 
        rule_result: Dict[str, Any],
        regulation: str
    ) -> ComplianceCheck:
        """Combine AI and rule-based compliance results."""
        
        # Determine overall status (most restrictive)
        statuses = [ai_result["status"], rule_result["status"]]
        if "non-compliant" in statuses:
            overall_status = "non-compliant"
        elif "needs-review" in statuses:
            overall_status = "needs-review"
        else:
            overall_status = "compliant"
        
        # Combine findings
        all_violations = []
        all_violations.extend(ai_result.get("violations", []))
        all_violations.extend(rule_result.get("violations", []))
        
        # Deduplicate violations
        unique_violations = list(set(str(v) for v in all_violations))
        
        # Combine recommendations
        all_recommendations = []
        all_recommendations.extend(ai_result.get("recommendations", []))
        all_recommendations.extend(rule_result.get("recommendations", []))
        
        # Deduplicate recommendations
        unique_recommendations = list(set(str(r) for r in all_recommendations))
        
        return ComplianceCheck(
            check_id=f"compliance_{regulation.lower()}",
            regulation=regulation,
            requirement=self.regulations[regulation]["name"],
            status=overall_status,
            findings=unique_violations[:10],  # Limit to top 10
            recommendations=unique_recommendations[:10],  # Limit to top 10
            clause_references=["Full contract review"]
        )
    
    def _prepare_text_for_analysis(self, text: str, max_chars: int = 10000) -> str:
        """Prepare text for DSPy analysis."""
        if len(text) <= max_chars:
            return text
        
        # Take first and last portions
        first_part = text[:max_chars//2]
        last_part = text[-(max_chars//2):]
        
        return f"{first_part}\n\n[... CONTENT TRUNCATED ...]\n\n{last_part}"
    
    def _parse_json_safely(self, json_str: str) -> List[Any]:
        """Safely parse JSON string."""
        try:
            if isinstance(json_str, str):
                result = json.loads(json_str)
                return result if isinstance(result, list) else [result]
            elif isinstance(json_str, list):
                return json_str
            else:
                return [json_str] if json_str else []
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse JSON: {json_str}")
            return []
    
    def _fallback_compliance_check(self, regulation: str) -> ComplianceCheck:
        """Fallback compliance check when main methods fail."""
        
        return ComplianceCheck(
            check_id=f"fallback_{regulation.lower()}",
            regulation=regulation,
            requirement=self.regulations.get(regulation, {}).get("name", regulation),
            status="needs-review",
            findings=["Unable to perform automated compliance check"],
            recommendations=[
                f"Manual review required for {regulation} compliance",
                "Consult with legal counsel specializing in this regulation",
                "Review specific regulatory requirements and contract terms"
            ],
            clause_references=["Entire contract"]
        )
    
    def get_regulation_summary(self, regulation: str) -> Dict[str, Any]:
        """Get summary information about a regulation."""
        
        if regulation not in self.regulations:
            return {"error": f"Unknown regulation: {regulation}"}
        
        config = self.regulations[regulation]
        
        return {
            "name": config["name"],
            "key_requirements": config["requirements"],
            "compliance_indicators": config["keywords"],
            "common_violations": [pattern.replace(r'\s+', ' ') for pattern in config["risk_patterns"]]
        }
    
    def get_supported_regulations(self) -> List[str]:
        """Get list of supported regulations."""
        return list(self.regulations.keys())
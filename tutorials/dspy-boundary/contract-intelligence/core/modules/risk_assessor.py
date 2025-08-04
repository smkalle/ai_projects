"""Risk assessment module using DSPy for contract risk analysis."""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

import dspy

from core.signatures.analysis_signatures import RiskAssessmentSignature
from models.document import ParsedDocument, RiskAssessment
from config.settings import settings

logger = logging.getLogger(__name__)


class RiskAssessor(dspy.Module):
    """Assess risks in contracts using DSPy and rule-based analysis."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        
        self.assessor = dspy.ChainOfThought(RiskAssessmentSignature)
        
        # Risk categories and their indicators
        self.risk_categories = {
            "financial": {
                "patterns": [
                    r"unlimited\s+liability", r"no\s+cap\s+on\s+damages",
                    r"liquidated\s+damages", r"penalty\s+of", r"fine\s+of",
                    r"personal\s+guarantee", r"jointly\s+and\s+severally"
                ],
                "keywords": ["penalty", "damages", "liability", "guarantee", "surety"]
            },
            "operational": {
                "patterns": [
                    r"sole\s+discretion", r"may\s+terminate\s+at\s+any\s+time",
                    r"without\s+cause", r"immediate\s+termination",
                    r"exclusive\s+dealing", r"non-compete"
                ],
                "keywords": ["exclusive", "terminate", "discretion", "cause", "notice"]
            },
            "legal": {
                "patterns": [
                    r"indemnify.*harmless", r"defend.*indemnify",
                    r"waive.*rights", r"governing\s+law.*foreign",
                    r"arbitration.*binding", r"class\s+action\s+waiver"
                ],
                "keywords": ["indemnify", "waive", "arbitration", "jurisdiction", "governing"]
            },
            "compliance": {
                "patterns": [
                    r"regulatory\s+compliance", r"data\s+protection",
                    r"privacy\s+policy", r"audit\s+rights",
                    r"certification\s+required"
                ],
                "keywords": ["compliance", "regulation", "audit", "certification", "privacy"]
            },
            "intellectual_property": {
                "patterns": [
                    r"work\s+for\s+hire", r"intellectual\s+property.*assign",
                    r"proprietary\s+information", r"trade\s+secrets",
                    r"copyright.*transfer"
                ],
                "keywords": ["intellectual", "proprietary", "copyright", "trademark", "patent"]
            }
        }
        
        # Severity scoring weights
        self.severity_weights = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        if model_name:
            self.lm = dspy.LM(model=model_name)
            dspy.configure(lm=self.lm)
    
    def assess_risks(
        self, 
        parsed_doc: ParsedDocument,
        contract_type: Optional[str] = None
    ) -> Tuple[List[RiskAssessment], float]:
        """Perform comprehensive risk assessment of the contract."""
        
        try:
            # Get AI-powered risk assessment
            ai_risks = self._assess_with_dspy(parsed_doc, contract_type)
            
            # Get rule-based risk assessment
            rule_risks = self._assess_with_rules(parsed_doc)
            
            # Combine and deduplicate risks
            all_risks = self._combine_risks(ai_risks, rule_risks)
            
            # Calculate overall risk score
            overall_score = self._calculate_overall_risk_score(all_risks)
            
            logger.info(f"Risk assessment completed. Found {len(all_risks)} risks, overall score: {overall_score}")
            
            return all_risks, overall_score
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return self._fallback_risk_assessment(parsed_doc)
    
    def _assess_with_dspy(
        self, 
        parsed_doc: ParsedDocument,
        contract_type: Optional[str] = None
    ) -> List[RiskAssessment]:
        """Assess risks using DSPy module."""
        
        try:
            text = self._prepare_text_for_analysis(parsed_doc.text)
            contract_type = contract_type or "general"
            
            result = self.assessor(
                contract_text=text,
                contract_type=contract_type
            )
            
            risks = []
            
            # Parse risk factors
            risk_factors = self._parse_json_safely(result.risk_factors)
            if isinstance(risk_factors, list):
                for i, risk_data in enumerate(risk_factors):
                    risk = self._create_risk_from_data(risk_data, f"ai_risk_{i}")
                    if risk:
                        risks.append(risk)
            
            # Parse mitigation recommendations
            mitigations = self._parse_json_safely(result.mitigation_recommendations)
            if isinstance(mitigations, list) and risks:
                # Assign mitigations to risks
                for i, mitigation in enumerate(mitigations):
                    if i < len(risks):
                        if isinstance(mitigation, dict):
                            risks[i].mitigation = mitigation.get('recommendation', str(mitigation))
                        else:
                            risks[i].mitigation = str(mitigation)
            
            return risks
            
        except Exception as e:
            logger.error(f"DSPy risk assessment failed: {str(e)}")
            return []
    
    def _assess_with_rules(self, parsed_doc: ParsedDocument) -> List[RiskAssessment]:
        """Assess risks using rule-based analysis."""
        
        risks = []
        text = parsed_doc.text.lower()
        
        for category, indicators in self.risk_categories.items():
            category_risks = self._find_category_risks(text, category, indicators)
            risks.extend(category_risks)
        
        # Add specific contract clause risks
        clause_risks = self._assess_clause_specific_risks(text)
        risks.extend(clause_risks)
        
        return risks
    
    def _find_category_risks(
        self, 
        text: str, 
        category: str, 
        indicators: Dict[str, List[str]]
    ) -> List[RiskAssessment]:
        """Find risks in a specific category."""
        
        risks = []
        
        # Check patterns
        for pattern in indicators.get("patterns", []):
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                risk = RiskAssessment(
                    risk_id=f"rule_{category}_{hash(match.group()) % 10000}",
                    risk_type=category,
                    description=f"Potential {category} risk: {match.group()}",
                    severity=self._assess_pattern_severity(pattern),
                    likelihood="medium",
                    impact=f"Could lead to {category} exposure",
                    mitigation=f"Review and potentially modify {category} terms",
                    clause_references=[f"Text: '{match.group()}'"]
                )
                risks.append(risk)
        
        # Check keywords (less severe than patterns)
        keyword_matches = []
        for keyword in indicators.get("keywords", []):
            if keyword in text:
                keyword_matches.append(keyword)
        
        if keyword_matches:
            risk = RiskAssessment(
                risk_id=f"rule_{category}_keywords",
                risk_type=category,
                description=f"{category.title()} terms present: {', '.join(keyword_matches)}",
                severity="low",
                likelihood="low",
                impact=f"Potential {category} considerations",
                mitigation=f"Review {category} related clauses carefully",
                clause_references=[f"Keywords: {', '.join(keyword_matches)}"]
            )
            risks.append(risk)
        
        return risks
    
    def _assess_clause_specific_risks(self, text: str) -> List[RiskAssessment]:
        """Assess risks from specific problematic clauses."""
        
        risks = []
        
        # High-risk clause combinations
        high_risk_checks = [
            {
                "pattern": r"terminate.*without.*cause.*notice",
                "description": "Contract can be terminated without cause with minimal notice",
                "severity": "high",
                "impact": "Sudden contract termination risk"
            },
            {
                "pattern": r"exclusive.*perpetual|perpetual.*exclusive",
                "description": "Perpetual exclusivity clause",
                "severity": "high", 
                "impact": "Long-term business flexibility limitation"
            },
            {
                "pattern": r"automatic.*renewal.*unless.*notice",
                "description": "Automatic renewal with notice requirements",
                "severity": "medium",
                "impact": "Inadvertent contract extension"
            },
            {
                "pattern": r"personally.*liable|personal.*guarantee",
                "description": "Personal liability or guarantee required",
                "severity": "high",
                "impact": "Personal financial exposure"
            }
        ]
        
        for check in high_risk_checks:
            if re.search(check["pattern"], text, re.IGNORECASE):
                risk = RiskAssessment(
                    risk_id=f"clause_risk_{hash(check['pattern']) % 10000}",
                    risk_type="contractual",
                    description=check["description"],
                    severity=check["severity"],
                    likelihood="medium",
                    impact=check["impact"],
                    mitigation="Consider negotiating alternative terms",
                    clause_references=["Pattern-based detection"]
                )
                risks.append(risk)
        
        return risks
    
    def _create_risk_from_data(self, risk_data: Any, risk_id: str) -> Optional[RiskAssessment]:
        """Create RiskAssessment from DSPy output data."""
        
        try:
            if isinstance(risk_data, str):
                return RiskAssessment(
                    risk_id=risk_id,
                    risk_type="general",
                    description=risk_data,
                    severity="medium",
                    likelihood="medium",
                    impact="Potential negative consequences",
                    mitigation="Review with legal counsel",
                    clause_references=[]
                )
            
            elif isinstance(risk_data, dict):
                return RiskAssessment(
                    risk_id=risk_data.get('id', risk_id),
                    risk_type=risk_data.get('type', 'general'),
                    description=risk_data.get('description', risk_data.get('risk', '')),
                    severity=risk_data.get('severity', 'medium').lower(),
                    likelihood=risk_data.get('likelihood', 'medium').lower(),
                    impact=risk_data.get('impact', 'Unknown impact'),
                    mitigation=risk_data.get('mitigation', 'Review recommended'),
                    clause_references=risk_data.get('clause_references', [])
                )
            
        except Exception as e:
            logger.error(f"Error creating risk from data: {str(e)}")
        
        return None
    
    def _assess_pattern_severity(self, pattern: str) -> str:
        """Assess severity level based on pattern type."""
        
        high_risk_indicators = [
            "unlimited", "no cap", "personal guarantee", 
            "jointly and severally", "indemnify.*harmless"
        ]
        
        medium_risk_indicators = [
            "penalty", "liquidated damages", "sole discretion",
            "without cause", "exclusive"
        ]
        
        pattern_lower = pattern.lower()
        
        for indicator in high_risk_indicators:
            if indicator in pattern_lower:
                return "high"
        
        for indicator in medium_risk_indicators:
            if indicator in pattern_lower:
                return "medium"
        
        return "low"
    
    def _combine_risks(
        self, 
        ai_risks: List[RiskAssessment], 
        rule_risks: List[RiskAssessment]
    ) -> List[RiskAssessment]:
        """Combine risks from different sources and remove duplicates."""
        
        all_risks = ai_risks + rule_risks
        
        # Simple deduplication based on description similarity
        unique_risks = []
        seen_descriptions = set()
        
        for risk in all_risks:
            # Create a normalized key for comparison
            key = self._normalize_risk_description(risk.description)
            
            if key not in seen_descriptions:
                seen_descriptions.add(key)
                unique_risks.append(risk)
        
        # Sort by severity (high first)
        return sorted(unique_risks, key=lambda r: self.severity_weights.get(r.severity, 1), reverse=True)
    
    def _normalize_risk_description(self, description: str) -> str:
        """Normalize risk description for deduplication."""
        
        # Remove common words and normalize
        words = description.lower().split()
        important_words = [w for w in words if len(w) > 3 and w not in {'risk', 'potential', 'could', 'lead', 'may'}]
        
        return ' '.join(sorted(important_words[:5]))  # Top 5 important words, sorted
    
    def _calculate_overall_risk_score(self, risks: List[RiskAssessment]) -> float:
        """Calculate overall risk score from 1-10."""
        
        if not risks:
            return 1.0
        
        # Weight risks by severity
        total_weighted_score = 0
        total_weight = 0
        
        for risk in risks:
            weight = self.severity_weights.get(risk.severity, 1)
            
            # Base score by severity
            base_score = {"high": 8, "medium": 5, "low": 2}.get(risk.severity, 3)
            
            total_weighted_score += base_score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 1.0
        
        # Normalize to 1-10 scale
        average_score = total_weighted_score / total_weight
        
        # Apply risk count factor (more risks = higher overall score)
        risk_count_factor = min(1.5, 1 + (len(risks) - 1) * 0.1)
        
        final_score = min(10.0, average_score * risk_count_factor)
        
        return round(final_score, 1)
    
    def _prepare_text_for_analysis(self, text: str, max_chars: int = 10000) -> str:
        """Prepare text for DSPy analysis."""
        if len(text) <= max_chars:
            return text
        
        # Take first and last portions to preserve context
        first_part = text[:max_chars//2]
        last_part = text[-(max_chars//2):]
        
        return f"{first_part}\n\n[... CONTENT TRUNCATED ...]\n\n{last_part}"
    
    def _parse_json_safely(self, json_str: str) -> Any:
        """Safely parse JSON string."""
        try:
            if isinstance(json_str, str):
                return json.loads(json_str)
            return json_str
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse JSON: {json_str}")
            return []
    
    def _fallback_risk_assessment(self, parsed_doc: ParsedDocument) -> Tuple[List[RiskAssessment], float]:
        """Fallback risk assessment when main methods fail."""
        
        fallback_risks = [
            RiskAssessment(
                risk_id="fallback_general",
                risk_type="general",
                description="Unable to perform detailed risk analysis. Manual review recommended.",
                severity="medium",
                likelihood="unknown",
                impact="Unassessed contractual risks",
                mitigation="Conduct manual legal review of all contract terms",
                clause_references=["Entire contract"]
            )
        ]
        
        return fallback_risks, 5.0  # Medium risk score
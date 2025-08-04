"""Clause extraction module using DSPy."""

import json
import logging
import re
from typing import Dict, List, Any, Optional

import dspy

from core.signatures.analysis_signatures import ClauseExtractionSignature
from models.document import ParsedDocument, ClauseExtraction
from config.settings import settings

logger = logging.getLogger(__name__)


class ClauseExtractor(dspy.Module):
    """Extract and categorize contract clauses using DSPy."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        
        self.extractor = dspy.ChainOfThought(ClauseExtractionSignature)
        
        # Standard clause types to look for
        self.standard_clause_types = [
            "termination", "liability", "confidentiality", "payment", 
            "warranty", "indemnification", "force_majeure", "dispute_resolution",
            "governing_law", "assignment", "modification", "severability",
            "notices", "entire_agreement", "counterparts", "effective_date"
        ]
        
        # High-risk clause patterns
        self.risk_patterns = {
            "unlimited_liability": r"unlimited\s+liability|no\s+limitation\s+of\s+liability",
            "automatic_renewal": r"automatic\s+renewal|auto-renew|automatically\s+extend",
            "exclusivity": r"exclusive|solely|exclusively|only\s+provider",
            "penalty_clauses": r"penalty|liquidated\s+damages|fine",
            "personal_guarantee": r"personal\s+guarantee|personally\s+liable",
            "broad_indemnification": r"indemnify.*harmless|defend.*indemnify",
            "ip_assignment": r"intellectual\s+property.*assign|work\s+for\s+hire",
            "non_compete": r"non-compete|not\s+compete|restraint\s+of\s+trade"
        }
        
        if model_name:
            self.lm = dspy.LM(model=model_name)
            dspy.configure(lm=self.lm)
    
    def extract_clauses(
        self, 
        parsed_doc: ParsedDocument,
        clause_types: Optional[List[str]] = None
    ) -> List[ClauseExtraction]:
        """Extract clauses from the contract."""
        
        if clause_types is None:
            clause_types = self.standard_clause_types
        
        try:
            # Extract clauses using DSPy
            dspy_clauses = self._extract_with_dspy(parsed_doc, clause_types)
            
            # Extract using pattern matching as backup
            pattern_clauses = self._extract_with_patterns(parsed_doc)
            
            # Combine and deduplicate
            all_clauses = self._combine_and_deduplicate(dspy_clauses, pattern_clauses)
            
            # Assess importance and risk
            for clause in all_clauses:
                clause.importance = self._assess_importance(clause)
                clause.risk_level = self._assess_risk_level(clause)
            
            return all_clauses
            
        except Exception as e:
            logger.error(f"Clause extraction failed: {str(e)}")
            return self._fallback_extraction(parsed_doc)
    
    def _extract_with_dspy(
        self, 
        parsed_doc: ParsedDocument, 
        clause_types: List[str]
    ) -> List[ClauseExtraction]:
        """Extract clauses using DSPy module."""
        
        text = self._prepare_text_for_analysis(parsed_doc.text)
        clause_types_str = ", ".join(clause_types)
        
        try:
            result = self.extractor(
                contract_text=text,
                target_clause_types=clause_types_str
            )
            
            clauses = []
            
            # Process extracted clauses
            extracted = self._parse_json_safely(result.extracted_clauses)
            if isinstance(extracted, list):
                for clause_data in extracted:
                    clause = self._create_clause_from_data(clause_data, parsed_doc)
                    if clause:
                        clauses.append(clause)
            
            # Process unusual clauses
            unusual = self._parse_json_safely(result.unusual_clauses)
            if isinstance(unusual, list):
                for clause_data in unusual:
                    clause = self._create_clause_from_data(clause_data, parsed_doc, is_unusual=True)
                    if clause:
                        clauses.append(clause)
            
            return clauses
            
        except Exception as e:
            logger.error(f"DSPy clause extraction failed: {str(e)}")
            return []
    
    def _extract_with_patterns(self, parsed_doc: ParsedDocument) -> List[ClauseExtraction]:
        """Extract clauses using pattern matching."""
        
        clauses = []
        text = parsed_doc.text.lower()
        
        # Common clause section headers
        section_patterns = {
            "termination": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:termination|expiration|end\s+of\s+agreement)[\s\.\:]+(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "liability": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:liability|limitation\s+of\s+liability|damages)[\s\.\:]+(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "confidentiality": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:confidential|non-disclosure|proprietary)[\s\.\:]+(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "payment": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:payment|compensation|fees|remuneration)[\s\.\:]+(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "warranty": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:warrant|representation|guarantee)[\s\.\:]+(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "governing_law": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:governing\s+law|jurisdiction|applicable\s+law)[\s\.\:]+(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))"
        }
        
        for clause_type, pattern in section_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            
            for i, match in enumerate(matches):
                clause_text = match.group(1).strip() if match.groups() else match.group(0).strip()
                
                if len(clause_text) > 50:  # Only include substantial clauses
                    start_char = match.start()
                    end_char = match.end()
                    
                    clause = ClauseExtraction(
                        clause_id=f"{clause_type}_{i}",
                        clause_type=clause_type,
                        text=clause_text,
                        location={
                            "start_char": start_char,
                            "end_char": end_char,
                            "page": self._get_page_number(parsed_doc, start_char)
                        },
                        importance="medium",
                        risk_level="medium"
                    )
                    clauses.append(clause)
        
        return clauses
    
    def _create_clause_from_data(
        self, 
        clause_data: Dict[str, Any], 
        parsed_doc: ParsedDocument,
        is_unusual: bool = False
    ) -> Optional[ClauseExtraction]:
        """Create ClauseExtraction from DSPy output data."""
        
        try:
            if isinstance(clause_data, str):
                # Simple text format
                return ClauseExtraction(
                    clause_id=f"clause_{hash(clause_data) % 10000}",
                    clause_type="unusual" if is_unusual else "general",
                    text=clause_data,
                    location={"start_char": 0, "end_char": 0, "page": 1},
                    importance="high" if is_unusual else "medium",
                    risk_level="high" if is_unusual else "low"
                )
            
            elif isinstance(clause_data, dict):
                # Structured format
                clause_id = clause_data.get('id', f"clause_{hash(str(clause_data)) % 10000}")
                clause_type = clause_data.get('type', 'unusual' if is_unusual else 'general')
                text = clause_data.get('text', clause_data.get('clause', ''))
                
                if not text:
                    return None
                
                # Try to find location in document
                location = self._find_text_location(parsed_doc.text, text)
                
                return ClauseExtraction(
                    clause_id=clause_id,
                    clause_type=clause_type,
                    text=text,
                    location=location,
                    importance=clause_data.get('importance', 'high' if is_unusual else 'medium'),
                    risk_level=clause_data.get('risk_level', 'high' if is_unusual else 'low'),
                    notes=clause_data.get('notes')
                )
            
        except Exception as e:
            logger.error(f"Error creating clause from data: {str(e)}")
            return None
    
    def _find_text_location(self, full_text: str, clause_text: str) -> Dict[str, int]:
        """Find the location of clause text in the full document."""
        
        # Try exact match first
        start_pos = full_text.find(clause_text[:100])  # First 100 chars
        
        if start_pos == -1:
            # Try case-insensitive match
            start_pos = full_text.lower().find(clause_text[:100].lower())
        
        if start_pos == -1:
            # Try fuzzy matching with keywords
            words = clause_text.split()[:5]  # First 5 words
            for word in words:
                if len(word) > 3:
                    pos = full_text.lower().find(word.lower())
                    if pos != -1:
                        start_pos = pos
                        break
        
        if start_pos == -1:
            start_pos = 0
        
        end_pos = min(start_pos + len(clause_text), len(full_text))
        
        return {
            "start_char": start_pos,
            "end_char": end_pos,
            "page": self._get_page_number_from_char(full_text, start_pos)
        }
    
    def _get_page_number(self, parsed_doc: ParsedDocument, char_position: int) -> int:
        """Get page number for a character position."""
        return self._get_page_number_from_char(parsed_doc.text, char_position)
    
    def _get_page_number_from_char(self, text: str, char_position: int) -> int:
        """Estimate page number based on character position."""
        # Rough estimate: 2000 characters per page
        return max(1, char_position // 2000 + 1)
    
    def _assess_importance(self, clause: ClauseExtraction) -> str:
        """Assess the importance level of a clause."""
        
        high_importance_types = {
            "termination", "liability", "payment", "warranty", 
            "indemnification", "governing_law", "confidentiality"
        }
        
        medium_importance_types = {
            "force_majeure", "assignment", "modification", 
            "dispute_resolution", "notices"
        }
        
        if clause.clause_type.lower() in high_importance_types:
            return "high"
        elif clause.clause_type.lower() in medium_importance_types:
            return "medium"
        else:
            return "low"
    
    def _assess_risk_level(self, clause: ClauseExtraction) -> str:
        """Assess the risk level of a clause."""
        
        text = clause.text.lower()
        
        # Check for high-risk patterns
        for pattern_name, pattern in self.risk_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return "high"
        
        # Check for medium-risk indicators
        medium_risk_indicators = [
            "exclusive", "penalty", "liquidated", "terminate", 
            "breach", "default", "indemnify"
        ]
        
        for indicator in medium_risk_indicators:
            if indicator in text:
                return "medium"
        
        return "low"
    
    def _combine_and_deduplicate(
        self, 
        dspy_clauses: List[ClauseExtraction], 
        pattern_clauses: List[ClauseExtraction]
    ) -> List[ClauseExtraction]:
        """Combine clauses from different sources and remove duplicates."""
        
        all_clauses = dspy_clauses + pattern_clauses
        
        # Simple deduplication based on clause type and text similarity
        unique_clauses = []
        seen_combinations = set()
        
        for clause in all_clauses:
            # Create a key for deduplication
            key = f"{clause.clause_type}_{clause.text[:100]}"
            
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_clauses.append(clause)
        
        return unique_clauses
    
    def _prepare_text_for_analysis(self, text: str, max_chars: int = 12000) -> str:
        """Prepare text for DSPy analysis."""
        if len(text) <= max_chars:
            return text
        
        # Take first and last portions
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
    
    def _fallback_extraction(self, parsed_doc: ParsedDocument) -> List[ClauseExtraction]:
        """Fallback clause extraction when main methods fail."""
        
        # Simple keyword-based extraction
        fallback_clauses = []
        text = parsed_doc.text
        
        keywords = {
            "termination": ["terminate", "expiration", "end of agreement"],
            "liability": ["liability", "damages", "limitation"],
            "payment": ["payment", "pay", "compensation", "fee"],
            "confidentiality": ["confidential", "non-disclosure", "proprietary"]
        }
        
        for clause_type, keyword_list in keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in text.lower():
                    # Find context around keyword
                    pos = text.lower().find(keyword.lower())
                    start = max(0, pos - 200)
                    end = min(len(text), pos + 800)
                    context = text[start:end]
                    
                    clause = ClauseExtraction(
                        clause_id=f"fallback_{clause_type}",
                        clause_type=clause_type,
                        text=context,
                        location={"start_char": start, "end_char": end, "page": 1},
                        importance="medium",
                        risk_level="medium",
                        notes="Extracted using fallback method"
                    )
                    fallback_clauses.append(clause)
                    break  # Only one per type
        
        return fallback_clauses
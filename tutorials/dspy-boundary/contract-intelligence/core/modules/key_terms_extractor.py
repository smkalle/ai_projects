"""Key terms extraction module using DSPy for contract key terms analysis."""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

import dspy

from core.signatures.analysis_signatures import KeyTermsExtractionSignature
from models.document import ParsedDocument
from config.settings import settings

logger = logging.getLogger(__name__)


class KeyTermsExtractor(dspy.Module):
    """Extract key terms and values from contracts using DSPy."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        
        self.extractor = dspy.ChainOfThought(KeyTermsExtractionSignature)
        
        # Term extraction patterns
        self.term_patterns = {
            "monetary_values": [
                r'\$[\d,]+(?:\.\d{2})?',  # $1,000.00
                r'(?:USD|EUR|GBP|CAD)\s*[\d,]+(?:\.\d{2})?',  # USD 1,000.00
                r'[\d,]+(?:\.\d{2})?\s*(?:dollars?|euros?|pounds?)',  # 1000 dollars
                r'(?:sum|amount|fee|cost|price|value)\s+of\s+\$?[\d,]+(?:\.\d{2})?'
            ],
            "dates": [
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                r'(?:effective|start|end|expir|terminat|due)\s+(?:date|on)[\s:]?\s*([^\n\.,;]{1,50})',
                r'(?:by|before|after|on|from)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
                r'within\s+\d+\s+(?:days?|weeks?|months?|years?)'
            ],
            "parties": [
                r'(?:between|by and between)\s+([^,\n]+?)\s+(?:and|&)\s+([^,\n]+?)(?:\s|,|\.)',
                r'(?:party|client|customer|vendor|contractor|company|corporation|llc|inc\.?|ltd\.?)\s*[:\-]?\s*([A-Z][^,\n\.]{5,50})',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:LLC|Inc\.?|Corp\.?|Ltd\.?|Co\.?))?)',
                r'(?:^|\n)\s*([A-Z][A-Z\s&]{3,}(?:LLC|INC|CORP|LTD)?)\s*(?:\n|,|\()'
            ],
            "percentages": [
                r'\b\d+(?:\.\d+)?%',
                r'\b\d+(?:\.\d+)?\s*percent',
                r'(?:interest|rate|fee|commission|percentage)\s+of\s+\d+(?:\.\d+)?%?'
            ],
            "durations": [
                r'\b\d+\s*(?:days?|weeks?|months?|years?)\b',
                r'(?:term|period|duration)\s+of\s+\d+\s*(?:days?|weeks?|months?|years?)',
                r'(?:for\s+a\s+period\s+of|lasting)\s+\d+\s*(?:days?|weeks?|months?|years?)'
            ]
        }
        
        # Jurisdiction/governing law patterns
        self.jurisdiction_patterns = [
            r'(?:governed?\s+by|subject\s+to)\s+(?:the\s+)?laws?\s+of\s+([^,\n\.;]+)',
            r'jurisdiction\s+of\s+([^,\n\.;]+)',
            r'courts?\s+of\s+([^,\n\.;]+)\s+shall\s+have\s+(?:exclusive\s+)?jurisdiction',
            r'(?:state\s+of\s+|province\s+of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+law\s+(?:shall\s+)?govern'
        ]
        
        if model_name:
            self.lm = dspy.LM(model=model_name)
            dspy.configure(lm=self.lm)
    
    def extract_key_terms(
        self, 
        parsed_doc: ParsedDocument,
        term_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extract key terms from the contract."""
        
        if term_categories is None:
            term_categories = ["financial", "dates", "parties", "jurisdiction"]
        
        try:
            # Extract using DSPy
            ai_terms = self._extract_with_dspy(parsed_doc, term_categories)
            
            # Extract using patterns
            pattern_terms = self._extract_with_patterns(parsed_doc)
            
            # Combine results
            combined_terms = self._combine_terms(ai_terms, pattern_terms)
            
            logger.info("Key terms extraction completed")
            return combined_terms
            
        except Exception as e:
            logger.error(f"Key terms extraction failed: {str(e)}")
            return self._fallback_extraction(parsed_doc)
    
    def _extract_with_dspy(
        self, 
        parsed_doc: ParsedDocument, 
        term_categories: List[str]
    ) -> Dict[str, Any]:
        """Extract key terms using DSPy module."""
        
        try:
            text = self._prepare_text_for_analysis(parsed_doc.text)
            categories_str = ", ".join(term_categories)
            
            result = self.extractor(
                contract_text=text,
                term_categories=categories_str
            )
            
            return {
                "parties_info": self._parse_json_safely(result.parties_info),
                "financial_terms": self._parse_json_safely(result.financial_terms),
                "important_dates": self._parse_json_safely(result.important_dates),
                "jurisdiction_info": result.jurisdiction_info
            }
            
        except Exception as e:
            logger.error(f"DSPy key terms extraction failed: {str(e)}")
            return {}
    
    def _extract_with_patterns(self, parsed_doc: ParsedDocument) -> Dict[str, Any]:
        """Extract key terms using pattern matching."""
        
        text = parsed_doc.text
        extracted_terms = {
            "monetary_values": [],
            "dates": [],
            "parties": [],
            "percentages": [],
            "durations": [],
            "jurisdiction": []
        }
        
        # Extract monetary values
        for pattern in self.term_patterns["monetary_values"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted_terms["monetary_values"].extend(matches)
        
        # Extract dates
        for pattern in self.term_patterns["dates"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted_terms["dates"].extend(matches)
        
        # Extract parties
        parties_found = set()
        for pattern in self.term_patterns["parties"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties_found.update(match)
                else:
                    parties_found.add(match)
        
        # Clean and filter party names
        cleaned_parties = []
        for party in parties_found:
            party = party.strip()
            if len(party) > 2 and not party.lower() in ['the', 'and', 'or', 'of', 'in', 'to', 'for']:
                cleaned_parties.append(party)
        
        extracted_terms["parties"] = list(set(cleaned_parties))[:10]  # Limit to 10
        
        # Extract percentages
        for pattern in self.term_patterns["percentages"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted_terms["percentages"].extend(matches)
        
        # Extract durations
        for pattern in self.term_patterns["durations"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted_terms["durations"].extend(matches)
        
        # Extract jurisdiction information
        for pattern in self.jurisdiction_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted_terms["jurisdiction"].extend(matches)
        
        # Remove duplicates and clean up
        for key, values in extracted_terms.items():
            if isinstance(values, list):
                extracted_terms[key] = list(set(str(v).strip() for v in values if v.strip()))
        
        return extracted_terms
    
    def _combine_terms(
        self, 
        ai_terms: Dict[str, Any], 
        pattern_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine terms from AI and pattern extraction."""
        
        combined = {
            "parties": [],
            "financial_terms": {},
            "important_dates": {},
            "jurisdiction": {},
            "contract_details": {}
        }
        
        # Combine parties information
        ai_parties = ai_terms.get("parties_info", {})
        pattern_parties = pattern_terms.get("parties", [])
        
        if isinstance(ai_parties, dict):
            combined["parties"] = list(ai_parties.values()) if ai_parties else []
        elif isinstance(ai_parties, list):
            combined["parties"] = ai_parties
        
        # Add pattern-detected parties
        combined["parties"].extend(pattern_parties)
        combined["parties"] = list(set(combined["parties"]))[:10]  # Deduplicate and limit
        
        # Combine financial terms
        ai_financial = ai_terms.get("financial_terms", {})
        if isinstance(ai_financial, dict):
            combined["financial_terms"] = ai_financial
        
        # Add pattern-detected monetary values
        combined["financial_terms"]["monetary_values"] = pattern_terms.get("monetary_values", [])
        combined["financial_terms"]["percentages"] = pattern_terms.get("percentages", [])
        
        # Combine dates
        ai_dates = ai_terms.get("important_dates", {})
        if isinstance(ai_dates, dict):
            combined["important_dates"] = ai_dates
        
        # Add pattern-detected dates
        combined["important_dates"]["extracted_dates"] = pattern_terms.get("dates", [])
        combined["important_dates"]["durations"] = pattern_terms.get("durations", [])
        
        # Combine jurisdiction
        ai_jurisdiction = ai_terms.get("jurisdiction_info", "")
        pattern_jurisdiction = pattern_terms.get("jurisdiction", [])
        
        combined["jurisdiction"]["ai_detected"] = ai_jurisdiction
        combined["jurisdiction"]["pattern_detected"] = pattern_jurisdiction
        
        # Add contract details
        combined["contract_details"] = {
            "word_count": len(pattern_terms.get("text", "").split()) if "text" in pattern_terms else 0,
            "extraction_timestamp": datetime.now().isoformat(),
            "total_monetary_values": len(pattern_terms.get("monetary_values", [])),
            "total_dates": len(pattern_terms.get("dates", [])),
            "total_parties": len(combined["parties"])
        }
        
        return combined
    
    def extract_specific_terms(
        self, 
        parsed_doc: ParsedDocument, 
        specific_terms: List[str]
    ) -> Dict[str, List[str]]:
        """Extract specific named terms from the contract."""
        
        results = {}
        text = parsed_doc.text.lower()
        
        for term in specific_terms:
            term_lower = term.lower()
            results[term] = []
            
            # Look for the term and extract surrounding context
            pattern = rf'\b{re.escape(term_lower)}\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                context = parsed_doc.text[start:end].strip()
                
                results[term].append(context)
        
        return results
    
    def get_contract_summary_stats(self, extracted_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from extracted terms."""
        
        stats = {
            "total_parties": len(extracted_terms.get("parties", [])),
            "total_financial_terms": len(extracted_terms.get("financial_terms", {}).get("monetary_values", [])),
            "total_dates": len(extracted_terms.get("important_dates", {}).get("extracted_dates", [])),
            "has_jurisdiction": bool(extracted_terms.get("jurisdiction", {}).get("ai_detected") or 
                                  extracted_terms.get("jurisdiction", {}).get("pattern_detected")),
            "contract_complexity": "unknown"
        }
        
        # Assess complexity
        total_terms = stats["total_parties"] + stats["total_financial_terms"] + stats["total_dates"]
        
        if total_terms < 5:
            stats["contract_complexity"] = "simple"
        elif total_terms < 15:
            stats["contract_complexity"] = "moderate"
        else:
            stats["contract_complexity"] = "complex"
        
        return stats
    
    def _prepare_text_for_analysis(self, text: str, max_chars: int = 12000) -> str:
        """Prepare text for DSPy analysis."""
        if len(text) <= max_chars:
            return text
        
        # For key terms extraction, prioritize the beginning and end
        first_part = text[:int(max_chars * 0.6)]  # 60% from beginning
        last_part = text[-int(max_chars * 0.4):]  # 40% from end
        
        return f"{first_part}\n\n[... CONTENT TRUNCATED ...]\n\n{last_part}"
    
    def _parse_json_safely(self, json_str: str) -> Any:
        """Safely parse JSON string."""
        try:
            if isinstance(json_str, str):
                return json.loads(json_str)
            return json_str
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse JSON: {json_str}")
            return {}
    
    def _fallback_extraction(self, parsed_doc: ParsedDocument) -> Dict[str, Any]:
        """Fallback extraction when main methods fail."""
        
        # Simple keyword-based extraction
        text = parsed_doc.text
        
        fallback_terms = {
            "parties": [],
            "financial_terms": {"monetary_values": [], "percentages": []},
            "important_dates": {"extracted_dates": [], "durations": []},
            "jurisdiction": {"ai_detected": "", "pattern_detected": []},
            "contract_details": {
                "word_count": len(text.split()),
                "extraction_timestamp": datetime.now().isoformat(),
                "extraction_method": "fallback",
                "total_monetary_values": 0,
                "total_dates": 0,
                "total_parties": 0
            }
        }
        
        # Try to find at least some basic information
        dollar_amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', text)
        fallback_terms["financial_terms"]["monetary_values"] = dollar_amounts[:5]
        
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
        fallback_terms["important_dates"]["extracted_dates"] = dates[:5]
        
        # Update counts
        fallback_terms["contract_details"]["total_monetary_values"] = len(dollar_amounts)
        fallback_terms["contract_details"]["total_dates"] = len(dates)
        
        return fallback_terms
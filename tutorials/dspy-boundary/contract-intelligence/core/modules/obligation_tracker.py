"""Obligation tracking module using DSPy for contract obligation analysis."""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import dspy

from core.signatures.analysis_signatures import ObligationTrackingSignature
from models.document import ParsedDocument, Obligation
from config.settings import settings

logger = logging.getLogger(__name__)


class ObligationTracker(dspy.Module):
    """Track obligations and commitments in contracts using DSPy."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        
        self.tracker = dspy.ChainOfThought(ObligationTrackingSignature)
        
        # Date patterns for deadline extraction
        self.date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}\b',
            r'\b\d{1,2}\s+days?\b|\b\d{1,2}\s+weeks?\b|\b\d{1,2}\s+months?\b|\b\d{1,2}\s+years?\b',
            r'\bwithin\s+\d+\s+(?:days?|weeks?|months?|years?)\b',
            r'\bby\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        ]
        
        # Obligation indicators
        self.obligation_patterns = {
            "payment": [
                r"shall\s+pay", r"must\s+pay", r"payment\s+due", r"invoice",
                r"remuneration", r"compensation", r"fee", r"amount"
            ],
            "delivery": [
                r"shall\s+deliver", r"must\s+deliver", r"provide", r"supply",
                r"deliverable", r"milestone", r"completion"
            ],
            "reporting": [
                r"shall\s+report", r"must\s+report", r"provide\s+report",
                r"submit", r"documentation", r"records"
            ],
            "compliance": [
                r"shall\s+comply", r"must\s+comply", r"adherence",
                r"certification", r"audit", r"inspection"
            ],
            "maintenance": [
                r"maintain", r"upkeep", r"service", r"support",
                r"warranty", r"repair", r"replace"
            ],
            "notification": [
                r"shall\s+notify", r"must\s+notify", r"give\s+notice",
                r"inform", r"communicate", r"advise"
            ]
        }
        
        # Frequency indicators
        self.frequency_patterns = {
            "daily": r"\bdaily\b|\bevery\s+day\b|\beach\s+day\b",
            "weekly": r"\bweekly\b|\bevery\s+week\b|\beach\s+week\b",
            "monthly": r"\bmonthly\b|\bevery\s+month\b|\beach\s+month\b",
            "quarterly": r"\bquarterly\b|\bevery\s+quarter\b|\beach\s+quarter\b",
            "annually": r"\bannually\b|\byearly\b|\bevery\s+year\b|\beach\s+year\b",
            "one-time": r"\bone\s+time\b|\bsingle\b|\bonce\b"
        }
        
        if model_name:
            self.lm = dspy.LM(model=model_name)
            dspy.configure(lm=self.lm)
    
    def track_obligations(
        self, 
        parsed_doc: ParsedDocument,
        party_focus: str = "all"
    ) -> List[Obligation]:
        """Track all obligations in the contract."""
        
        try:
            # Get AI-powered obligation extraction
            ai_obligations = self._extract_with_dspy(parsed_doc, party_focus)
            
            # Get rule-based obligation extraction
            rule_obligations = self._extract_with_rules(parsed_doc)
            
            # Combine and deduplicate
            all_obligations = self._combine_obligations(ai_obligations, rule_obligations)
            
            # Extract and assign dates
            for obligation in all_obligations:
                obligation.due_date = self._extract_due_date(obligation.description, parsed_doc.text)
                obligation.frequency = self._extract_frequency(obligation.description)
            
            logger.info(f"Obligation tracking completed. Found {len(all_obligations)} obligations")
            
            return all_obligations
            
        except Exception as e:
            logger.error(f"Obligation tracking failed: {str(e)}")
            return self._fallback_obligations(parsed_doc)
    
    def _extract_with_dspy(
        self, 
        parsed_doc: ParsedDocument, 
        party_focus: str
    ) -> List[Obligation]:
        """Extract obligations using DSPy module."""
        
        try:
            text = self._prepare_text_for_analysis(parsed_doc.text)
            
            result = self.tracker(
                contract_text=text,
                party_focus=party_focus
            )
            
            obligations = []
            
            # Process general obligations
            obligations_data = self._parse_json_safely(result.obligations)
            if isinstance(obligations_data, list):
                for i, obligation_data in enumerate(obligations_data):
                    obligation = self._create_obligation_from_data(
                        obligation_data, 
                        f"ai_obligation_{i}",
                        "general"
                    )
                    if obligation:
                        obligations.append(obligation)
            
            # Process deliverables
            deliverables_data = self._parse_json_safely(result.deliverables)
            if isinstance(deliverables_data, list):
                for i, deliverable_data in enumerate(deliverables_data):
                    obligation = self._create_obligation_from_data(
                        deliverable_data,
                        f"ai_deliverable_{i}",
                        "delivery"
                    )
                    if obligation:
                        obligations.append(obligation)
            
            # Process payment obligations
            payment_data = self._parse_json_safely(result.payment_obligations)
            if isinstance(payment_data, list):
                for i, payment_obligation in enumerate(payment_data):
                    obligation = self._create_obligation_from_data(
                        payment_obligation,
                        f"ai_payment_{i}",
                        "payment"
                    )
                    if obligation:
                        obligations.append(obligation)
            
            return obligations
            
        except Exception as e:
            logger.error(f"DSPy obligation extraction failed: {str(e)}")
            return []
    
    def _extract_with_rules(self, parsed_doc: ParsedDocument) -> List[Obligation]:
        """Extract obligations using rule-based analysis."""
        
        obligations = []
        text = parsed_doc.text
        
        # Find obligations by category
        for category, patterns in self.obligation_patterns.items():
            category_obligations = self._find_category_obligations(text, category, patterns)
            obligations.extend(category_obligations)
        
        # Find specific obligation keywords
        specific_obligations = self._find_specific_obligations(text)
        obligations.extend(specific_obligations)
        
        return obligations
    
    def _find_category_obligations(
        self, 
        text: str, 
        category: str, 
        patterns: List[str]
    ) -> List[Obligation]:
        """Find obligations in a specific category."""
        
        obligations = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 300)
                context = text[start:end].strip()
                
                # Try to identify the party
                party = self._identify_party_from_context(context, text)
                
                obligation = Obligation(
                    obligation_id=f"rule_{category}_{hash(context) % 10000}",
                    party=party,
                    description=context,
                    status="pending",
                    clause_reference=f"Pattern match: {match.group()}"
                )
                
                obligations.append(obligation)
        
        return obligations
    
    def _find_specific_obligations(self, text: str) -> List[Obligation]:
        """Find specific common obligations."""
        
        obligations = []
        
        # Specific obligation patterns with context
        specific_patterns = [
            {
                "pattern": r"(insurance.*maintain|maintain.*insurance)",
                "description": "Maintain insurance coverage",
                "category": "compliance"
            },
            {
                "pattern": r"(confidential.*maintain|maintain.*confidential)",
                "description": "Maintain confidentiality",
                "category": "compliance"
            },
            {
                "pattern": r"(records.*keep|keep.*records|maintain.*records)",
                "description": "Maintain records and documentation",
                "category": "reporting"
            },
            {
                "pattern": r"(license.*obtain|obtain.*license|permit.*obtain)",
                "description": "Obtain necessary licenses/permits",
                "category": "compliance"
            },
            {
                "pattern": r"(warranty.*provide|provide.*warranty)",
                "description": "Provide warranty coverage",
                "category": "maintenance"
            }
        ]
        
        for pattern_info in specific_patterns:
            matches = re.finditer(pattern_info["pattern"], text, re.IGNORECASE)
            
            for match in matches:
                start = max(0, match.start() - 150)
                end = min(len(text), match.end() + 150)
                context = text[start:end].strip()
                
                party = self._identify_party_from_context(context, text)
                
                obligation = Obligation(
                    obligation_id=f"specific_{pattern_info['category']}_{hash(context) % 10000}",
                    party=party,
                    description=pattern_info["description"],
                    status="pending",
                    clause_reference=context[:200] + ("..." if len(context) > 200 else "")
                )
                
                obligations.append(obligation)
        
        return obligations
    
    def _create_obligation_from_data(
        self, 
        obligation_data: Any, 
        obligation_id: str,
        category: str
    ) -> Optional[Obligation]:
        """Create Obligation from DSPy output data."""
        
        try:
            if isinstance(obligation_data, str):
                return Obligation(
                    obligation_id=obligation_id,
                    party="Unknown",
                    description=obligation_data,
                    status="pending"
                )
            
            elif isinstance(obligation_data, dict):
                return Obligation(
                    obligation_id=obligation_data.get('id', obligation_id),
                    party=obligation_data.get('party', 'Unknown'),
                    description=obligation_data.get('description', obligation_data.get('obligation', '')),
                    due_date=obligation_data.get('due_date'),
                    frequency=obligation_data.get('frequency'),
                    status=obligation_data.get('status', 'pending'),
                    clause_reference=obligation_data.get('clause_reference')
                )
            
        except Exception as e:
            logger.error(f"Error creating obligation from data: {str(e)}")
        
        return None
    
    def _identify_party_from_context(self, context: str, full_text: str) -> str:
        """Try to identify which party has the obligation."""
        
        # Common party identifiers
        party_patterns = [
            r"(?:company|contractor|vendor|supplier|client|customer|buyer|seller|lessor|lessee)",
            r"(?:party a|party b|first party|second party)",
            r"(?:employer|employee|service provider|consultant)"
        ]
        
        context_lower = context.lower()
        
        # Look for party mentions in context
        for pattern in party_patterns:
            matches = re.findall(pattern, context_lower)
            if matches:
                return matches[0].title()
        
        # Try to find party names (capitalized words that appear multiple times)
        words = re.findall(r'\b[A-Z][a-z]+\b', context)
        word_counts = {}
        
        for word in words:
            if len(word) > 3:  # Skip short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Return most frequent capitalized word
        if word_counts:
            most_frequent = max(word_counts, key=word_counts.get)
            if word_counts[most_frequent] > 1:
                return most_frequent
        
        return "Unknown Party"
    
    def _extract_due_date(self, description: str, full_text: str) -> Optional[str]:
        """Extract due date from obligation description."""
        
        # Look in the description first
        for pattern in self.date_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return self._normalize_date(match.group())
        
        # Look for relative dates
        relative_match = re.search(r'within\s+(\d+)\s+(days?|weeks?|months?|years?)', description, re.IGNORECASE)
        if relative_match:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2).lower()
            
            return self._calculate_future_date(amount, unit)
        
        return None
    
    def _extract_frequency(self, description: str) -> Optional[str]:
        """Extract frequency from obligation description."""
        
        description_lower = description.lower()
        
        for frequency, pattern in self.frequency_patterns.items():
            if re.search(pattern, description_lower):
                return frequency
        
        return None
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to consistent format."""
        
        # Try to parse and reformat date
        common_formats = [
            "%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y",
            "%B %d, %Y", "%B %d %Y", "%d %B %Y"
        ]
        
        for fmt in common_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Return original if parsing fails
        return date_str
    
    def _calculate_future_date(self, amount: int, unit: str) -> str:
        """Calculate future date based on relative terms."""
        
        today = datetime.now()
        
        if "day" in unit:
            future_date = today + timedelta(days=amount)
        elif "week" in unit:
            future_date = today + timedelta(weeks=amount)
        elif "month" in unit:
            future_date = today + timedelta(days=amount * 30)  # Approximate
        elif "year" in unit:
            future_date = today + timedelta(days=amount * 365)  # Approximate
        else:
            return None
        
        return future_date.strftime("%Y-%m-%d")
    
    def _combine_obligations(
        self, 
        ai_obligations: List[Obligation], 
        rule_obligations: List[Obligation]
    ) -> List[Obligation]:
        """Combine obligations from different sources and remove duplicates."""
        
        all_obligations = ai_obligations + rule_obligations
        
        # Simple deduplication based on description similarity
        unique_obligations = []
        seen_descriptions = set()
        
        for obligation in all_obligations:
            # Create normalized key for comparison
            key = self._normalize_obligation_description(obligation.description)
            
            if key not in seen_descriptions and len(key) > 10:  # Skip very short descriptions
                seen_descriptions.add(key)
                unique_obligations.append(obligation)
        
        return unique_obligations
    
    def _normalize_obligation_description(self, description: str) -> str:
        """Normalize obligation description for deduplication."""
        
        # Remove common words and normalize
        words = description.lower().split()
        important_words = [w for w in words if len(w) > 3 and w not in {
            'shall', 'must', 'will', 'should', 'party', 'contract', 'agreement',
            'provide', 'ensure', 'make', 'take', 'have', 'with', 'this', 'that'
        }]
        
        return ' '.join(sorted(important_words[:8]))  # Top 8 important words, sorted
    
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
    
    def _fallback_obligations(self, parsed_doc: ParsedDocument) -> List[Obligation]:
        """Fallback obligation extraction when main methods fail."""
        
        fallback_obligations = [
            Obligation(
                obligation_id="fallback_general",
                party="All Parties",
                description="Manual review required to identify specific obligations",
                status="pending",
                clause_reference="Entire contract"
            ),
            Obligation(
                obligation_id="fallback_payment",
                party="Unknown",
                description="Review payment terms and schedules",
                status="pending",
                clause_reference="Payment sections"
            ),
            Obligation(
                obligation_id="fallback_delivery",
                party="Unknown", 
                description="Review delivery and performance obligations",
                status="pending",
                clause_reference="Performance sections"
            )
        ]
        
        return fallback_obligations
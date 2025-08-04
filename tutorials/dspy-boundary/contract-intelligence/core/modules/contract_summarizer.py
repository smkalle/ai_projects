"""Contract summarization module using DSPy for comprehensive contract summaries."""

import json
import logging
from typing import Dict, List, Any, Optional

import dspy

from core.signatures.analysis_signatures import ContractSummarySignature
from models.document import ParsedDocument, ContractAnalysis
from config.settings import settings

logger = logging.getLogger(__name__)


class ContractSummarizer(dspy.Module):
    """Generate comprehensive contract summaries using DSPy."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        
        self.summarizer = dspy.ChainOfThought(ContractSummarySignature)
        
        # Summary templates for different contract types
        self.summary_templates = {
            "employment": {
                "key_sections": [
                    "Position and responsibilities",
                    "Compensation and benefits", 
                    "Work schedule and location",
                    "Termination conditions",
                    "Confidentiality obligations",
                    "Non-compete/non-solicitation"
                ],
                "critical_terms": ["salary", "benefits", "vacation", "termination", "confidentiality"]
            },
            "service": {
                "key_sections": [
                    "Scope of services",
                    "Payment terms and schedule",
                    "Service level agreements",
                    "Deliverables and milestones",
                    "Liability and warranties",
                    "Termination clauses"
                ],
                "critical_terms": ["services", "payment", "sla", "deliverables", "liability"]
            },
            "lease": {
                "key_sections": [
                    "Property description",
                    "Lease term and rent",
                    "Security deposit",
                    "Maintenance responsibilities",
                    "Use restrictions",
                    "Renewal and termination"
                ],
                "critical_terms": ["rent", "term", "deposit", "maintenance", "use"]
            },
            "nda": {
                "key_sections": [
                    "Definition of confidential information",
                    "Permitted uses and restrictions",
                    "Duration of obligations",
                    "Return/destruction of information",
                    "Remedies for breach",
                    "Governing law"
                ],
                "critical_terms": ["confidential", "disclosure", "term", "remedies"]
            }
        }
        
        if model_name:
            self.lm = dspy.LM(model=model_name)
            dspy.configure(lm=self.lm)
    
    def generate_summary(
        self, 
        parsed_doc: ParsedDocument,
        summary_type: str = "executive",
        contract_analysis: Optional[ContractAnalysis] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive contract summary."""
        
        try:
            # Generate AI-powered summary
            ai_summary = self._generate_with_dspy(parsed_doc, summary_type)
            
            # Generate structured summary using templates
            structured_summary = self._generate_structured_summary(parsed_doc, contract_analysis)
            
            # Generate section-wise summary
            section_summary = self._generate_section_summary(parsed_doc)
            
            # Combine all summaries
            complete_summary = self._combine_summaries(
                ai_summary, structured_summary, section_summary
            )
            
            logger.info(f"Contract summary generated ({summary_type})")
            return complete_summary
            
        except Exception as e:
            logger.error(f"Contract summarization failed: {str(e)}")
            return self._fallback_summary(parsed_doc)
    
    def _generate_with_dspy(
        self, 
        parsed_doc: ParsedDocument, 
        summary_type: str
    ) -> Dict[str, Any]:
        """Generate summary using DSPy module."""
        
        try:
            text = self._prepare_text_for_analysis(parsed_doc.text)
            
            result = self.summarizer(
                contract_text=text,
                summary_type=summary_type
            )
            
            return {
                "executive_summary": result.executive_summary,
                "key_highlights": self._parse_json_safely(result.key_highlights),
                "action_items": self._parse_json_safely(result.action_items),
                "red_flags": self._parse_json_safely(result.red_flags)
            }
            
        except Exception as e:
            logger.error(f"DSPy summarization failed: {str(e)}")
            return {}
    
    def _generate_structured_summary(
        self, 
        parsed_doc: ParsedDocument,
        contract_analysis: Optional[ContractAnalysis] = None
    ) -> Dict[str, Any]:
        """Generate structured summary based on contract type."""
        
        # Determine contract type
        contract_type = "general"
        if contract_analysis and contract_analysis.contract_type:
            contract_type = contract_analysis.contract_type.lower()
        else:
            contract_type = self._detect_contract_type(parsed_doc.text)
        
        template = self.summary_templates.get(contract_type, self.summary_templates["service"])
        
        structured = {
            "contract_type": contract_type,
            "key_sections": {},
            "critical_terms": {},
            "parties_summary": {},
            "financial_summary": {},
            "timeline_summary": {}
        }
        
        # Extract information for each key section
        for section in template["key_sections"]:
            structured["key_sections"][section] = self._extract_section_info(
                parsed_doc.text, section
            )
        
        # Extract critical terms
        for term in template["critical_terms"]:
            structured["critical_terms"][term] = self._extract_term_info(
                parsed_doc.text, term
            )
        
        # Use contract analysis data if available
        if contract_analysis:
            structured["parties_summary"] = {
                "parties": [str(party) for party in contract_analysis.parties][:5],
                "total_parties": len(contract_analysis.parties)
            }
            structured["financial_summary"] = contract_analysis.key_terms
            structured["timeline_summary"] = contract_analysis.key_dates
        
        return structured
    
    def _generate_section_summary(self, parsed_doc: ParsedDocument) -> Dict[str, str]:
        """Generate summary for each major section of the contract."""
        
        sections = self._identify_contract_sections(parsed_doc.text)
        section_summaries = {}
        
        for section_name, section_text in sections.items():
            if len(section_text) > 100:
                summary = self._summarize_section(section_text, section_name)
                section_summaries[section_name] = summary
        
        return section_summaries
    
    def _identify_contract_sections(self, text: str) -> Dict[str, str]:
        """Identify major sections in the contract."""
        
        sections = {}
        
        # Common section headers
        section_patterns = {
            "definitions": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:definitions|defined terms)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "scope": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:scope|services|work|deliverables)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "payment": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:payment|compensation|fees|remuneration)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "term": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:term|duration|period)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "termination": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:termination|expiration|end)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "confidentiality": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:confidential|non-disclosure|proprietary)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "liability": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:liability|limitation|damages)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))",
            "governing_law": r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:governing law|jurisdiction|applicable law)[\s\.:]*\n(.{0,2000}?)(?=\n\s*(?:\d+\.|\n|$))"
        }
        
        text_lower = text.lower()
        
        for section_name, pattern in section_patterns.items():
            import re
            matches = re.findall(pattern, text_lower, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if matches:
                # Take the first substantial match
                for match in matches:
                    if len(match.strip()) > 50:
                        sections[section_name] = match.strip()
                        break
        
        return sections
    
    def _summarize_section(self, section_text: str, section_name: str) -> str:
        """Create a brief summary of a contract section."""
        
        # Simple extractive summarization
        sentences = section_text.split('.')
        
        # Keep first sentence and any sentence with key terms
        key_terms = ["shall", "must", "will", "may", "party", "agreement", "contract"]
        important_sentences = []
        
        for i, sentence in enumerate(sentences[:5]):  # Look at first 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:
                if i == 0 or any(term in sentence.lower() for term in key_terms):
                    important_sentences.append(sentence)
        
        summary = '. '.join(important_sentences[:3])  # Max 3 sentences
        
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        return summary if summary else "Section content available for review."
    
    def _extract_section_info(self, text: str, section_name: str) -> str:
        """Extract key information about a specific section."""
        
        text_lower = text.lower()
        section_lower = section_name.lower()
        
        # Look for section mentions
        import re
        
        # Create search terms based on section name
        search_terms = {
            "position and responsibilities": ["position", "role", "responsibilities", "duties"],
            "compensation and benefits": ["salary", "compensation", "benefits", "pay"],
            "work schedule and location": ["schedule", "hours", "location", "remote"],
            "termination conditions": ["termination", "terminate", "end", "expiration"],
            "scope of services": ["services", "scope", "work", "deliverables"],
            "payment terms and schedule": ["payment", "invoice", "schedule", "due"],
            "service level agreements": ["sla", "service level", "performance", "uptime"],
            "liability and warranties": ["liability", "warranty", "guarantee", "damages"],
            "property description": ["property", "premises", "address", "location"],
            "lease term and rent": ["term", "rent", "monthly", "lease period"],
            "security deposit": ["deposit", "security", "refundable"],
            "maintenance responsibilities": ["maintenance", "repair", "upkeep"]
        }
        
        terms = search_terms.get(section_lower, [section_lower])
        
        # Find relevant text snippets
        relevant_snippets = []
        for term in terms:
            pattern = rf'.{{0,100}}{re.escape(term)}.{{0,200}}'
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            relevant_snippets.extend(matches[:2])  # Max 2 per term
        
        if relevant_snippets:
            return '; '.join(set(relevant_snippets))[:300]
        
        return f"Information about {section_name} may be present in the contract."
    
    def _extract_term_info(self, text: str, term: str) -> str:
        """Extract information about a specific term."""
        
        import re
        
        # Look for the term and surrounding context
        pattern = rf'.{{0,75}}{re.escape(term)}.{{0,150}}'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            # Return the first substantial match
            for match in matches:
                if len(match.strip()) > 20:
                    return match.strip()[:200]
        
        return f"Term '{term}' may be referenced in the contract."
    
    def _detect_contract_type(self, text: str) -> str:
        """Detect contract type from text content."""
        
        text_lower = text.lower()
        
        type_indicators = {
            "employment": ["employee", "employer", "employment", "job", "position", "salary"],
            "service": ["services", "provider", "client", "deliverables", "sla"],
            "lease": ["lease", "rent", "tenant", "landlord", "premises", "property"],
            "nda": ["confidential", "non-disclosure", "proprietary", "trade secret"]
        }
        
        scores = {}
        for contract_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            scores[contract_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return "general"
    
    def _combine_summaries(
        self, 
        ai_summary: Dict[str, Any],
        structured_summary: Dict[str, Any],
        section_summary: Dict[str, str]
    ) -> Dict[str, Any]:
        """Combine all summary types into comprehensive result."""
        
        return {
            "executive_summary": ai_summary.get("executive_summary", "Executive summary not available"),
            "key_highlights": ai_summary.get("key_highlights", []),
            "action_items": ai_summary.get("action_items", []),
            "red_flags": ai_summary.get("red_flags", []),
            "contract_type": structured_summary.get("contract_type", "general"),
            "key_sections": structured_summary.get("key_sections", {}),
            "critical_terms": structured_summary.get("critical_terms", {}),
            "parties_summary": structured_summary.get("parties_summary", {}),
            "financial_summary": structured_summary.get("financial_summary", {}),
            "timeline_summary": structured_summary.get("timeline_summary", {}),
            "section_summaries": section_summary,
            "summary_stats": {
                "total_sections": len(section_summary),
                "total_highlights": len(ai_summary.get("key_highlights", [])),
                "total_action_items": len(ai_summary.get("action_items", [])),
                "total_red_flags": len(ai_summary.get("red_flags", []))
            }
        }
    
    def generate_one_page_summary(self, complete_summary: Dict[str, Any]) -> str:
        """Generate a concise one-page summary."""
        
        summary_parts = []
        
        # Executive summary
        if complete_summary.get("executive_summary"):
            summary_parts.append(f"EXECUTIVE SUMMARY:\n{complete_summary['executive_summary']}\n")
        
        # Key highlights (top 5)
        highlights = complete_summary.get("key_highlights", [])[:5]
        if highlights:
            summary_parts.append("KEY HIGHLIGHTS:")
            for highlight in highlights:
                summary_parts.append(f"• {highlight}")
            summary_parts.append("")
        
        # Critical terms
        critical_terms = complete_summary.get("critical_terms", {})
        if critical_terms:
            summary_parts.append("CRITICAL TERMS:")
            for term, info in list(critical_terms.items())[:5]:
                summary_parts.append(f"• {term.title()}: {str(info)[:100]}...")
            summary_parts.append("")
        
        # Red flags
        red_flags = complete_summary.get("red_flags", [])[:3]
        if red_flags:
            summary_parts.append("RED FLAGS:")
            for flag in red_flags:
                summary_parts.append(f"⚠ {flag}")
            summary_parts.append("")
        
        # Action items
        action_items = complete_summary.get("action_items", [])[:3]
        if action_items:
            summary_parts.append("IMMEDIATE ACTION ITEMS:")
            for item in action_items:
                summary_parts.append(f"→ {item}")
        
        return "\n".join(summary_parts)
    
    def _prepare_text_for_analysis(self, text: str, max_chars: int = 15000) -> str:
        """Prepare text for DSPy analysis."""
        if len(text) <= max_chars:
            return text
        
        # For summarization, take beginning, middle, and end
        chunk_size = max_chars // 3
        first_part = text[:chunk_size]
        middle_start = len(text) // 2 - chunk_size // 2
        middle_part = text[middle_start:middle_start + chunk_size]
        last_part = text[-chunk_size:]
        
        return f"{first_part}\n\n[... CONTENT TRUNCATED ...]\n\n{middle_part}\n\n[... CONTENT TRUNCATED ...]\n\n{last_part}"
    
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
    
    def _fallback_summary(self, parsed_doc: ParsedDocument) -> Dict[str, Any]:
        """Fallback summary when main methods fail."""
        
        text = parsed_doc.text
        word_count = len(text.split())
        
        return {
            "executive_summary": f"Contract analysis summary not available. Document contains {word_count} words and requires manual review.",
            "key_highlights": ["Manual review required", "Automated analysis unavailable"],
            "action_items": ["Conduct manual contract review", "Identify key terms and obligations"],
            "red_flags": ["Unable to perform automated risk assessment"],
            "contract_type": "unknown",
            "key_sections": {},
            "critical_terms": {},
            "parties_summary": {"parties": [], "total_parties": 0},
            "financial_summary": {},
            "timeline_summary": {},
            "section_summaries": {},
            "summary_stats": {
                "total_sections": 0,
                "total_highlights": 2,
                "total_action_items": 2,
                "total_red_flags": 1
            }
        }
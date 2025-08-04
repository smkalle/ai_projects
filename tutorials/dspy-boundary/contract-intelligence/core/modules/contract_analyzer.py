"""Main contract analyzer module using DSPy."""

import json
import logging
import time
from typing import Dict, List, Any, Optional

import dspy
from dspy import LM

from core.signatures.analysis_signatures import (
    ContractAnalysisSignature,
    ContractClassificationSignature,
    LegalReviewSignature
)
from models.document import ParsedDocument, ContractAnalysis, AnalysisResult
from config.settings import settings

logger = logging.getLogger(__name__)


class ContractAnalyzer(dspy.Module):
    """Main contract analyzer orchestrating multiple analysis tasks."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        
        # Initialize DSPy components
        self.analyzer = dspy.ChainOfThought(ContractAnalysisSignature)
        self.classifier = dspy.ChainOfThought(ContractClassificationSignature) 
        self.legal_reviewer = dspy.ChainOfThought(LegalReviewSignature)
        
        # Configure LM if provided
        if model_name:
            self.lm = dspy.LM(model=model_name)
            dspy.configure(lm=self.lm)
    
    def analyze_contract(self, parsed_doc: ParsedDocument) -> ContractAnalysis:
        """Perform comprehensive contract analysis."""
        start_time = time.time()
        
        try:
            # Step 1: Basic contract analysis
            basic_analysis = self._perform_basic_analysis(parsed_doc)
            
            # Step 2: Contract classification  
            classification = self._perform_classification(parsed_doc)
            
            # Step 3: Legal review
            legal_review = self._perform_legal_review(parsed_doc)
            
            # Combine results
            analysis = self._combine_analysis_results(
                parsed_doc, basic_analysis, classification, legal_review
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Contract analysis completed in {processing_time:.2f}s")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Contract analysis failed: {str(e)}")
            raise
    
    def _perform_basic_analysis(self, parsed_doc: ParsedDocument) -> Dict[str, Any]:
        """Perform basic contract analysis using DSPy."""
        try:
            # Truncate text if too long for LLM context
            text = self._prepare_text_for_analysis(parsed_doc.text)
            
            result = self.analyzer(contract_text=text)
            
            return {
                'contract_type': result.contract_type,
                'parties': self._parse_json_field(result.parties),
                'key_dates': self._parse_json_field(result.key_dates),
                'key_terms': self._parse_json_field(result.key_terms),
                'executive_summary': result.executive_summary
            }
            
        except Exception as e:
            logger.error(f"Basic analysis failed: {str(e)}")
            return self._get_fallback_basic_analysis()
    
    def _perform_classification(self, parsed_doc: ParsedDocument) -> Dict[str, Any]:
        """Classify the contract type and characteristics."""
        try:
            text = self._prepare_text_for_analysis(parsed_doc.text)
            
            result = self.classifier(contract_text=text)
            
            return {
                'primary_type': result.primary_type,
                'sub_categories': self._parse_json_field(result.sub_categories),
                'industry_sector': result.industry_sector,
                'complexity_level': result.complexity_level,
                'standard_vs_custom': result.standard_vs_custom
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return self._get_fallback_classification()
    
    def _perform_legal_review(self, parsed_doc: ParsedDocument) -> Dict[str, Any]:
        """Perform legal review of the contract."""
        try:
            text = self._prepare_text_for_analysis(parsed_doc.text)
            
            result = self.legal_reviewer(
                contract_text=text,
                review_focus="general"
            )
            
            return {
                'legal_concerns': self._parse_json_field(result.legal_concerns),
                'enforceability_assessment': result.enforceability_assessment,
                'missing_clauses': self._parse_json_field(result.missing_clauses),
                'revision_suggestions': self._parse_json_field(result.revision_suggestions)
            }
            
        except Exception as e:
            logger.error(f"Legal review failed: {str(e)}")
            return self._get_fallback_legal_review()
    
    def _combine_analysis_results(
        self, 
        parsed_doc: ParsedDocument,
        basic_analysis: Dict[str, Any],
        classification: Dict[str, Any],
        legal_review: Dict[str, Any]
    ) -> ContractAnalysis:
        """Combine all analysis results into a comprehensive analysis."""
        
        # Create analysis results
        analysis_results = [
            AnalysisResult(
                document_id=parsed_doc.filename,
                document_name=parsed_doc.filename,
                analysis_type="basic_analysis",
                results=basic_analysis,
                confidence_score=0.85,
                processing_time=1.0
            ),
            AnalysisResult(
                document_id=parsed_doc.filename,
                document_name=parsed_doc.filename,
                analysis_type="classification",
                results=classification,
                confidence_score=0.90,
                processing_time=0.5
            ),
            AnalysisResult(
                document_id=parsed_doc.filename,
                document_name=parsed_doc.filename,
                analysis_type="legal_review",
                results=legal_review,
                confidence_score=0.80,
                processing_time=1.5
            )
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(basic_analysis, legal_review)
        
        return ContractAnalysis(
            document=parsed_doc,
            contract_type=basic_analysis.get('contract_type', 'Unknown'),
            parties=basic_analysis.get('parties', []),
            key_dates=basic_analysis.get('key_dates', {}),
            key_terms=basic_analysis.get('key_terms', {}),
            clauses=[],  # Will be populated by clause extractor
            risks=[],    # Will be populated by risk assessor
            obligations=[], # Will be populated by obligation tracker
            compliance_checks={}, # Will be populated by compliance checker
            summary=basic_analysis.get('executive_summary', 'Summary not available'),
            recommendations=recommendations,
            analysis_results=analysis_results
        )
    
    def _prepare_text_for_analysis(self, text: str, max_chars: int = 15000) -> str:
        """Prepare text for LLM analysis by truncating if necessary."""
        if len(text) <= max_chars:
            return text
        
        # Take the first portion and last portion to preserve context
        first_part = text[:max_chars//2]
        last_part = text[-(max_chars//2):]
        
        return f"{first_part}\n\n[... CONTENT TRUNCATED ...]\n\n{last_part}"
    
    def _parse_json_field(self, field_value: str) -> Any:
        """Safely parse JSON field from DSPy output."""
        try:
            if isinstance(field_value, str):
                return json.loads(field_value)
            return field_value
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse JSON field: {field_value}")
            return field_value if field_value else []
    
    def _generate_recommendations(
        self, 
        basic_analysis: Dict[str, Any], 
        legal_review: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Add legal review recommendations
        if legal_review.get('revision_suggestions'):
            for suggestion in legal_review['revision_suggestions']:
                if isinstance(suggestion, dict) and 'recommendation' in suggestion:
                    recommendations.append(suggestion['recommendation'])
                elif isinstance(suggestion, str):
                    recommendations.append(suggestion)
        
        # Add missing clause recommendations
        if legal_review.get('missing_clauses'):
            for clause in legal_review['missing_clauses']:
                if isinstance(clause, dict) and 'clause' in clause:
                    recommendations.append(f"Consider adding: {clause['clause']}")
                elif isinstance(clause, str):
                    recommendations.append(f"Consider adding: {clause}")
        
        # Add contract type specific recommendations
        contract_type = basic_analysis.get('contract_type', '').lower()
        if 'employment' in contract_type:
            recommendations.append("Ensure compliance with local employment laws")
        elif 'service' in contract_type:
            recommendations.append("Review service level agreements and penalties")
        elif 'lease' in contract_type:
            recommendations.append("Verify property laws and tenant rights")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _get_fallback_basic_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when DSPy fails."""
        return {
            'contract_type': 'Unknown',
            'parties': [],
            'key_dates': {},
            'key_terms': {},
            'executive_summary': 'Analysis not available due to processing error'
        }
    
    def _get_fallback_classification(self) -> Dict[str, Any]:
        """Fallback classification when DSPy fails."""
        return {
            'primary_type': 'Unknown',
            'sub_categories': [],
            'industry_sector': 'Unknown',
            'complexity_level': 'Unknown',
            'standard_vs_custom': 'Unknown'
        }
    
    def _get_fallback_legal_review(self) -> Dict[str, Any]:
        """Fallback legal review when DSPy fails."""
        return {
            'legal_concerns': [],
            'enforceability_assessment': 'Review not available',
            'missing_clauses': [],
            'revision_suggestions': []
        }
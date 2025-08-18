"""
Confidence Calculator Module
Uncertainty quantification for medical AI predictions
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ConfidenceCalculator:
    """Calculate and manage confidence scores for medical predictions"""
    
    def __init__(self):
        self.confidence_thresholds = {
            'very_high': 0.90,
            'high': 0.80,
            'moderate': 0.60,
            'low': 0.40,
            'very_low': 0.0
        }
        
        self.decay_rate = 0.02  # Confidence decay per hour
    
    def calculate(self, factors: Dict[str, float]) -> float:
        """Calculate basic confidence score from multiple factors"""
        if not factors:
            return 0.0
        
        # Simple average of all factors
        confidence = sum(factors.values()) / len(factors)
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def calculate_weighted(self, factors: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate weighted confidence score"""
        if not factors or not weights:
            return 0.0
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for factor, value in factors.items():
            weight = weights.get(factor, 1.0)
            weighted_sum += value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        confidence = weighted_sum / total_weight
        return max(0.0, min(1.0, confidence))
    
    def calculate_with_uncertainty(self, prediction_scores: List[float]) -> Dict[str, float]:
        """Calculate confidence with uncertainty bounds"""
        if not prediction_scores:
            return {
                'mean_confidence': 0.0,
                'lower_bound': 0.0,
                'upper_bound': 0.0,
                'std_dev': 0.0
            }
        
        scores_array = np.array(prediction_scores)
        mean_confidence = float(np.mean(scores_array))
        std_dev = float(np.std(scores_array))
        
        # Calculate 95% confidence interval
        margin = 1.96 * std_dev / np.sqrt(len(prediction_scores))
        
        return {
            'mean_confidence': mean_confidence,
            'lower_bound': max(0.0, mean_confidence - margin),
            'upper_bound': min(1.0, mean_confidence + margin),
            'std_dev': std_dev
        }
    
    def ensemble_confidence(self, model_predictions: Dict[str, Dict[str, float]]) -> float:
        """Calculate ensemble confidence from multiple model predictions"""
        if not model_predictions:
            return 0.0
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for model_name, prediction in model_predictions.items():
            score = prediction.get('score', 0.0)
            weight = prediction.get('weight', 1.0)
            
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def categorize_confidence(self, confidence: float) -> str:
        """Categorize confidence score into descriptive categories"""
        for category, threshold in self.confidence_thresholds.items():
            if confidence >= threshold:
                return category
        
        return 'very_low'
    
    def adjust_for_edge_cases(self, 
                             base_confidence: float, 
                             edge_case_factors: Dict[str, bool]) -> float:
        """Adjust confidence for known edge cases"""
        adjusted_confidence = base_confidence
        
        # Apply penalties for edge cases
        if edge_case_factors.get('rare_condition', False):
            adjusted_confidence *= 0.8
        
        if edge_case_factors.get('limited_data', False):
            adjusted_confidence *= 0.85
        
        if edge_case_factors.get('conflicting_symptoms', False):
            adjusted_confidence *= 0.9
        
        # Apply bonus for clear cases
        if edge_case_factors.get('textbook_presentation', False):
            adjusted_confidence *= 1.1
        
        return max(0.0, min(1.0, adjusted_confidence))
    
    def apply_temporal_decay(self, initial_confidence: float, hours_elapsed: float) -> float:
        """Apply temporal decay to confidence score"""
        if hours_elapsed <= 0:
            return initial_confidence
        
        # Exponential decay
        decay_factor = np.exp(-self.decay_rate * hours_elapsed)
        decayed_confidence = initial_confidence * decay_factor
        
        # Minimum confidence threshold
        min_confidence = 0.3
        
        return max(min_confidence, decayed_confidence)
    
    def meets_threshold(self, confidence: float, threshold: float) -> bool:
        """Check if confidence meets required threshold"""
        return confidence >= threshold
    
    def combine_image_text_confidence(self, 
                                     image_confidence: float, 
                                     text_confidence: float,
                                     image_weight: float = 0.6) -> float:
        """Combine confidence from image and text analysis"""
        text_weight = 1.0 - image_weight
        
        combined = (image_confidence * image_weight + 
                   text_confidence * text_weight)
        
        return max(0.0, min(1.0, combined))
    
    def calculate_diagnostic_confidence(self,
                                       symptoms_match: float,
                                       imaging_clarity: float,
                                       lab_results_match: float,
                                       medical_history_relevance: float) -> Dict[str, Any]:
        """Calculate comprehensive diagnostic confidence"""
        
        # Define weights for each component
        weights = {
            'symptoms': 0.25,
            'imaging': 0.35,
            'lab_results': 0.25,
            'medical_history': 0.15
        }
        
        # Calculate weighted confidence
        weighted_confidence = (
            symptoms_match * weights['symptoms'] +
            imaging_clarity * weights['imaging'] +
            lab_results_match * weights['lab_results'] +
            medical_history_relevance * weights['medical_history']
        )
        
        # Determine confidence category
        category = self.categorize_confidence(weighted_confidence)
        
        # Calculate component contributions
        contributions = {
            'symptoms': symptoms_match * weights['symptoms'],
            'imaging': imaging_clarity * weights['imaging'],
            'lab_results': lab_results_match * weights['lab_results'],
            'medical_history': medical_history_relevance * weights['medical_history']
        }
        
        return {
            'overall_confidence': weighted_confidence,
            'confidence_category': category,
            'component_contributions': contributions,
            'meets_clinical_threshold': weighted_confidence >= 0.7,
            'timestamp': datetime.now().isoformat()
        }
"""
Unit tests for confidence calculator module
Phase 1: Unit Testing
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class TestConfidenceCalculator:
    """Test confidence calculation functionality"""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance"""
        from utils.confidence_calculator import ConfidenceCalculator
        return ConfidenceCalculator()
    
    def test_basic_confidence_calculation(self, calculator):
        """Test basic confidence score calculation"""
        factors = {
            'image_quality': 0.9,
            'symptom_clarity': 0.8,
            'medical_history_completeness': 0.7
        }
        
        confidence = calculator.calculate(factors)
        
        assert 0 <= confidence <= 1
        assert confidence == pytest.approx(0.8, rel=0.1)
    
    def test_weighted_confidence(self, calculator):
        """Test weighted confidence calculation"""
        factors = {
            'image_quality': 0.9,
            'symptom_match': 0.6,
            'lab_results': 0.95
        }
        weights = {
            'image_quality': 0.4,
            'symptom_match': 0.3,
            'lab_results': 0.3
        }
        
        confidence = calculator.calculate_weighted(factors, weights)
        
        assert 0 <= confidence <= 1
        assert confidence == pytest.approx(0.825, rel=0.01)
    
    def test_confidence_with_uncertainty(self, calculator):
        """Test confidence calculation with uncertainty bounds"""
        prediction_scores = [0.8, 0.75, 0.82, 0.79, 0.81]
        
        result = calculator.calculate_with_uncertainty(prediction_scores)
        
        assert 'mean_confidence' in result
        assert 'lower_bound' in result
        assert 'upper_bound' in result
        assert result['lower_bound'] <= result['mean_confidence'] <= result['upper_bound']
    
    def test_multi_model_ensemble_confidence(self, calculator):
        """Test ensemble confidence from multiple models"""
        model_predictions = {
            'model1': {'score': 0.85, 'weight': 0.4},
            'model2': {'score': 0.78, 'weight': 0.3},
            'model3': {'score': 0.92, 'weight': 0.3}
        }
        
        ensemble_confidence = calculator.ensemble_confidence(model_predictions)
        
        assert 0 <= ensemble_confidence <= 1
        assert ensemble_confidence == pytest.approx(0.85, rel=0.05)
    
    @pytest.mark.parametrize("confidence,expected_category", [
        (0.95, 'very_high'),
        (0.85, 'high'),
        (0.70, 'moderate'),
        (0.50, 'low'),
        (0.30, 'very_low'),
    ])
    def test_confidence_categorization(self, calculator, confidence, expected_category):
        """Test categorization of confidence scores"""
        category = calculator.categorize_confidence(confidence)
        assert category == expected_category
    
    def test_confidence_adjustment_for_edge_cases(self, calculator):
        """Test confidence adjustment for edge cases"""
        base_confidence = 0.8
        edge_case_factors = {
            'rare_condition': True,
            'limited_data': True,
            'conflicting_symptoms': False
        }
        
        adjusted = calculator.adjust_for_edge_cases(base_confidence, edge_case_factors)
        
        assert adjusted < base_confidence  # Should reduce confidence
        assert 0 <= adjusted <= 1
    
    def test_temporal_confidence_decay(self, calculator):
        """Test confidence decay over time"""
        initial_confidence = 0.9
        hours_elapsed = 24
        
        decayed_confidence = calculator.apply_temporal_decay(
            initial_confidence, 
            hours_elapsed
        )
        
        assert decayed_confidence < initial_confidence
        assert decayed_confidence > 0
    
    def test_confidence_threshold_validation(self, calculator):
        """Test validation against confidence thresholds"""
        confidence = 0.65
        threshold = 0.7
        
        is_acceptable = calculator.meets_threshold(confidence, threshold)
        
        assert is_acceptable == False
        
        confidence = 0.75
        is_acceptable = calculator.meets_threshold(confidence, threshold)
        
        assert is_acceptable == True
"""
Unit tests for medical knowledge base module
Phase 1: Unit Testing
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class TestMedicalKnowledgeBase:
    """Test medical knowledge base functionality"""
    
    @pytest.fixture
    def knowledge_base(self):
        """Create a mock knowledge base instance"""
        from models.medical_knowledge_base import MedicalKnowledgeBase
        return MedicalKnowledgeBase()
    
    def test_symptom_analysis(self, knowledge_base):
        """Test symptom analysis returns correct structure"""
        symptoms = "fever, cough, difficulty breathing"
        result = knowledge_base.analyze_symptoms(symptoms)
        
        assert isinstance(result, dict)
        assert 'severity' in result
        assert 'possible_conditions' in result
        assert 'urgency_level' in result
        assert result['severity'] in ['low', 'medium', 'high', 'critical']
    
    def test_triage_classification(self, knowledge_base):
        """Test triage classification for emergency cases"""
        emergency_symptoms = {
            'chest_pain': True,
            'difficulty_breathing': True,
            'consciousness': 'altered'
        }
        
        result = knowledge_base.classify_triage(emergency_symptoms)
        
        assert result['priority'] == 'EMERGENCY'
        assert 'recommended_action' in result
        assert 'time_to_treatment' in result
    
    def test_medical_terminology_extraction(self, knowledge_base):
        """Test extraction of medical terms from text"""
        text = "Patient presents with acute myocardial infarction and hypertension"
        terms = knowledge_base.extract_medical_terms(text)
        
        assert isinstance(terms, list)
        assert 'myocardial infarction' in terms
        assert 'hypertension' in terms
    
    def test_icd10_code_mapping(self, knowledge_base):
        """Test ICD-10 code mapping for conditions"""
        condition = "pneumonia"
        codes = knowledge_base.get_icd10_codes(condition)
        
        assert isinstance(codes, list)
        assert len(codes) > 0
        assert all('J' in code for code in codes)  # Pneumonia codes start with J
    
    def test_drug_interaction_check(self, knowledge_base):
        """Test drug interaction checking"""
        medications = ['aspirin', 'warfarin']
        interactions = knowledge_base.check_drug_interactions(medications)
        
        assert isinstance(interactions, list)
        assert len(interactions) > 0
        assert interactions[0]['severity'] in ['minor', 'moderate', 'major']
    
    @pytest.mark.parametrize("age,vital_signs,expected_risk", [
        (25, {'bp': '120/80', 'pulse': 70}, 'low'),
        (65, {'bp': '160/95', 'pulse': 90}, 'high'),
        (45, {'bp': '140/90', 'pulse': 85}, 'medium'),
    ])
    def test_risk_assessment(self, knowledge_base, age, vital_signs, expected_risk):
        """Test risk assessment with different patient profiles"""
        risk = knowledge_base.assess_risk(age, vital_signs)
        assert risk['level'] == expected_risk
    
    def test_medical_history_parsing(self, knowledge_base):
        """Test parsing of medical history text"""
        history = "Diabetes Type 2 diagnosed 2020, Hypertension since 2018"
        parsed = knowledge_base.parse_medical_history(history)
        
        assert len(parsed['conditions']) == 2
        assert parsed['conditions'][0]['name'] == 'Diabetes Type 2'
        assert parsed['conditions'][0]['year'] == 2020
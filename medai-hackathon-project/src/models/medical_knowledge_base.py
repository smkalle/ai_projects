"""
Medical Knowledge Base Module
Core medical reasoning and knowledge management
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class MedicalKnowledgeBase:
    """Medical knowledge base for diagnostic support"""
    
    def __init__(self):
        self.icd10_mapping = {
            'pneumonia': ['J18.9', 'J15.9', 'J18.0'],
            'hypertension': ['I10', 'I11.9', 'I15.9'],
            'diabetes': ['E11.9', 'E10.9', 'E13.9'],
            'myocardial infarction': ['I21.9', 'I21.4', 'I22.9']
        }
        
        self.drug_interactions = {
            ('aspirin', 'warfarin'): {
                'severity': 'major',
                'description': 'Increased bleeding risk'
            },
            ('metformin', 'contrast'): {
                'severity': 'major',
                'description': 'Risk of lactic acidosis'
            }
        }
        
        self.triage_criteria = {
            'EMERGENCY': ['chest_pain', 'difficulty_breathing', 'altered_consciousness'],
            'URGENT': ['severe_pain', 'high_fever', 'bleeding'],
            'STANDARD': ['mild_symptoms', 'chronic_condition'],
            'NON_URGENT': ['follow_up', 'prescription_refill']
        }
    
    def analyze_symptoms(self, symptoms: str) -> Dict[str, Any]:
        """Analyze symptoms and return severity assessment"""
        symptoms_lower = symptoms.lower()
        
        severity = 'low'
        possible_conditions = []
        urgency_level = 'routine'
        
        # Check for critical symptoms
        critical_keywords = ['chest pain', 'difficulty breathing', 'unconscious']
        if any(keyword in symptoms_lower for keyword in critical_keywords):
            severity = 'critical'
            urgency_level = 'immediate'
        
        # Check for high severity symptoms
        elif any(keyword in symptoms_lower for keyword in ['fever', 'severe pain', 'bleeding']):
            severity = 'high'
            urgency_level = 'urgent'
        
        # Check for medium severity
        elif any(keyword in symptoms_lower for keyword in ['cough', 'headache', 'nausea']):
            severity = 'medium'
            urgency_level = 'soon'
        
        # Identify possible conditions
        if 'fever' in symptoms_lower and 'cough' in symptoms_lower:
            possible_conditions.append('respiratory infection')
        if 'chest' in symptoms_lower:
            possible_conditions.append('cardiac condition')
        if 'breathing' in symptoms_lower:
            possible_conditions.append('respiratory condition')
        
        return {
            'severity': severity,
            'possible_conditions': possible_conditions,
            'urgency_level': urgency_level,
            'timestamp': datetime.now().isoformat()
        }
    
    def classify_triage(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """Classify triage priority based on symptoms"""
        priority = 'NON_URGENT'
        recommended_action = 'Schedule appointment'
        time_to_treatment = '48-72 hours'
        
        # Check for emergency symptoms
        if symptoms.get('chest_pain') or symptoms.get('difficulty_breathing'):
            priority = 'EMERGENCY'
            recommended_action = 'Call 911 immediately'
            time_to_treatment = 'Immediate'
        elif symptoms.get('consciousness') == 'altered':
            priority = 'EMERGENCY'
            recommended_action = 'Emergency transport required'
            time_to_treatment = 'Immediate'
        elif symptoms.get('severe_pain') or symptoms.get('high_fever'):
            priority = 'URGENT'
            recommended_action = 'Visit emergency room'
            time_to_treatment = 'Within 1 hour'
        
        return {
            'priority': priority,
            'recommended_action': recommended_action,
            'time_to_treatment': time_to_treatment,
            'assessment_time': datetime.now().isoformat()
        }
    
    def extract_medical_terms(self, text: str) -> List[str]:
        """Extract medical terminology from text"""
        text_lower = text.lower()
        medical_terms = []
        
        # Common medical terms to detect
        term_patterns = [
            'myocardial infarction',
            'hypertension',
            'diabetes',
            'pneumonia',
            'acute',
            'chronic',
            'bilateral',
            'unilateral'
        ]
        
        for term in term_patterns:
            if term in text_lower:
                medical_terms.append(term)
        
        return medical_terms
    
    def get_icd10_codes(self, condition: str) -> List[str]:
        """Get ICD-10 codes for a medical condition"""
        condition_lower = condition.lower()
        
        for key, codes in self.icd10_mapping.items():
            if key in condition_lower or condition_lower in key:
                return codes
        
        return ['R69']  # Unknown diagnosis code
    
    def check_drug_interactions(self, medications: List[str]) -> List[Dict[str, Any]]:
        """Check for drug interactions between medications"""
        interactions = []
        medications_lower = [med.lower() for med in medications]
        
        for i, med1 in enumerate(medications_lower):
            for med2 in medications_lower[i+1:]:
                key1 = (med1, med2)
                key2 = (med2, med1)
                
                if key1 in self.drug_interactions:
                    interaction = self.drug_interactions[key1].copy()
                    interaction['drugs'] = [med1, med2]
                    interactions.append(interaction)
                elif key2 in self.drug_interactions:
                    interaction = self.drug_interactions[key2].copy()
                    interaction['drugs'] = [med1, med2]
                    interactions.append(interaction)
        
        return interactions if interactions else [{'severity': 'none', 'drugs': medications}]
    
    def assess_risk(self, age: int, vital_signs: Dict[str, Any]) -> Dict[str, str]:
        """Assess patient risk based on age and vital signs"""
        risk_level = 'low'
        
        # Parse blood pressure
        bp = vital_signs.get('bp', '120/80')
        systolic = int(bp.split('/')[0])
        
        # Age-based risk
        if age > 60:
            risk_level = 'medium'
        
        # Vital signs risk
        if systolic >= 140:
            risk_level = 'high' if age > 60 else 'medium'
        elif systolic > 160:
            risk_level = 'high'
        
        return {
            'level': risk_level,
            'factors': {
                'age': age,
                'blood_pressure': bp,
                'assessment_date': datetime.now().isoformat()
            }
        }
    
    def parse_medical_history(self, history: str) -> Dict[str, Any]:
        """Parse medical history text into structured data"""
        conditions = []
        
        # Pattern to find conditions with years
        pattern = r'([A-Za-z\s]+(?:Type \d)?)\s*(?:diagnosed |since )?(\d{4})'
        matches = re.findall(pattern, history)
        
        for condition, year in matches:
            conditions.append({
                'name': condition.strip(),
                'year': int(year)
            })
        
        return {
            'conditions': conditions,
            'parsed_at': datetime.now().isoformat()
        }
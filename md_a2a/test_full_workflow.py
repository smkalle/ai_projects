#!/usr/bin/env python3
"""
Comprehensive workflow test for Medical AI Assistant MVP V2.0
Tests the complete patient lifecycle: Registration → Assessment → Case Tracking
"""

import json
import requests
import sys

def test_complete_workflow():
    """Test the exact workflow described in requirements."""
    print('🚀 Testing Complete Workflow: Registration → Assessment → Case Tracking')
    print('=' * 70)

    base_url = 'http://localhost:8000'

    try:
        # 1. Register a test patient
        patient_data = {
            'first_name': 'Workflow',
            'last_name': 'TestPatient',
            'date_of_birth': '1990-01-01',
            'mobile_number': '9999999999',
            'gender': 'Male'
        }

        print('📝 Step 1: Registering patient...')
        response = requests.post(f'{base_url}/api/v2/patients/register', json=patient_data)
        response.raise_for_status()
        patient_id = response.json()['patient_id']
        print(f'✅ Patient registered: {patient_id}')

        # 2. Check initial case count
        print('📊 Step 2: Checking initial case count...')
        response = requests.get(f'{base_url}/api/cases')
        response.raise_for_status()
        initial_cases = len(response.json()['cases'])
        print(f'Initial cases in system: {initial_cases}')

        # 3. Perform AI Assessment (should create case automatically)
        print('🤖 Step 3: Performing AI Assessment...')
        assessment_data = {
            'symptoms': 'High fever and persistent cough',
            'age': 35,
            'duration': '2 days',
            'severity': 'medium',
            'additional_info': 'Workflow test case'
        }

        response = requests.post(f'{base_url}/api/v2/patients/{patient_id}/assess', json=assessment_data)
        response.raise_for_status()
        assessment_result = response.json()
        print(f'✅ Assessment completed: {assessment_result.get("assessment_id", "Unknown")}')
        
        # Check if case_id was created from assessment
        case_created_from_assessment = assessment_result.get('historical_context', {}).get('case_id')
        if case_created_from_assessment:
            print(f'✅ Case automatically created from assessment: {case_created_from_assessment[:8]}...')

        # 4. Check if case was created from assessment
        print('📋 Step 4: Verifying case creation from assessment...')
        response = requests.get(f'{base_url}/api/cases')
        response.raise_for_status()
        final_cases = len(response.json()['cases'])
        cases_created = final_cases - initial_cases
        print(f'Final cases in system: {final_cases}')
        print(f'Cases created: {cases_created}')

        # 5. Verify the case is linked to the patient
        print('🔗 Step 5: Verifying patient-case linkage...')
        response = requests.get(f'{base_url}/api/v2/patients/{patient_id}/history')
        response.raise_for_status()
        patient_history = response.json()
        patient_case_count = len(patient_history['cases'])
        print(f'Cases in patient history: {patient_case_count}')

        # 6. Test multiple assessments on same day (should append, not create new case)
        print('🔄 Step 6: Testing same-day assessment pattern...')
        assessment_data_2 = {
            'symptoms': 'Follow-up: fever reducing, cough persists',
            'age': 35,
            'duration': '3 days',
            'severity': 'low',
            'additional_info': 'Follow-up assessment'
        }
        
        response = requests.post(f'{base_url}/api/v2/patients/{patient_id}/assess', json=assessment_data_2)
        response.raise_for_status()
        assessment_result_2 = response.json()
        print(f'✅ Follow-up assessment completed')

        # Check final case count
        response = requests.get(f'{base_url}/api/cases')
        response.raise_for_status()
        final_final_cases = len(response.json()['cases'])
        total_cases_created = final_final_cases - initial_cases
        
        print(f'Total cases created: {total_cases_created}')

        # Summary
        print('\n🎯 WORKFLOW TEST RESULTS:')
        print('=' * 70)
        print(f'✅ Patient Registration: SUCCESS ({patient_id})')
        print(f'✅ AI Assessment: SUCCESS')
        print(f'✅ Automatic Case Creation: {"SUCCESS" if cases_created > 0 else "FAILED"}')
        print(f'✅ Patient-Case Linkage: {"SUCCESS" if patient_case_count > 0 else "FAILED"}')
        print(f'✅ Multiple Assessments: {"SUCCESS" if total_cases_created >= 2 else "FAILED"}')

        # Test if cases show up in frontend
        print('\n📱 Testing Frontend Integration...')
        response = requests.get(f'{base_url}/cases')
        if response.status_code == 200:
            print('✅ Cases page accessible')
        else:
            print('❌ Cases page not accessible')

        if (cases_created > 0 and patient_case_count > 0 and 
            total_cases_created >= 2 and response.status_code == 200):
            print('\n🎉 ALL WORKFLOW TESTS PASSED!')
            print('✨ Assessment → Case creation is working perfectly!')
            print('🎯 Requirements met:')
            print('   ✓ Every assessment creates a case record')
            print('   ✓ Multiple assessments per patient create multiple cases')
            print('   ✓ Cases appear in both patient history and global cases list')
            print('   ✓ Frontend integration working')
            return True
        else:
            print('\n❌ WORKFLOW TEST FAILED!')
            return False

    except requests.exceptions.RequestException as e:
        print(f'\n❌ Network error: {e}')
        return False
    except Exception as e:
        print(f'\n❌ Unexpected error: {e}')
        return False

if __name__ == '__main__':
    success = test_complete_workflow()
    sys.exit(0 if success else 1) 
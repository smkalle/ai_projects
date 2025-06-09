"""Patient management router for Medical AI Assistant MVP V2.0."""

import logging
import base64
import qrcode
import json
from io import BytesIO
from datetime import datetime, date
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from ..database import DatabaseManager
from ..models import (
    PatientRegistration,
    PatientResponse,
    PatientSearchResponse,
    PatientSearchResult,
    CaseHistoryResponse,
    VisitAlertResponse,
    AssessmentRequest,
    EnhancedAssessmentResponse,
    CaseCreateV2,
    CaseResponseV2,
    APIError
)
from ..agents import HybridTriageAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/patients", tags=["patients"])


def generate_qr_code(patient_id: str) -> str:
    """Generate QR code for patient ID."""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(patient_id)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return ""


@router.post("/register", response_model=PatientResponse)
async def register_patient(patient_data: PatientRegistration):
    """
    Register a new patient with unique ID generation.
    
    Creates a new patient record with a unique patient ID and generates
    a QR code for easy identification.
    """
    try:
        # Convert Pydantic model to dict
        patient_dict = patient_data.model_dump()
        
        # Register patient in database
        patient_id = DatabaseManager.register_patient(patient_dict)
        
        # Get complete patient data
        registered_patient = DatabaseManager.get_patient(patient_id)
        
        # Generate QR code
        qr_code = generate_qr_code(patient_id)
        
        logger.info(f"Patient registered successfully: {patient_id}")
        
        return PatientResponse(
            patient_id=patient_id,
            patient_data=registered_patient,
            qr_code=qr_code,
            success=True,
            message="Patient registered successfully"
        )
        
    except Exception as e:
        logger.error(f"Error registering patient: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register patient: {str(e)}"
        )


@router.get("/search", response_model=PatientSearchResponse)
async def search_patients(
    query: Optional[str] = Query(None, description="General search term"),
    patient_id: Optional[str] = Query(None, description="Exact patient ID match"),
    mobile: Optional[str] = Query(None, description="Mobile number search"),
    name: Optional[str] = Query(None, description="Name fuzzy search"),
    limit: int = Query(20, ge=1, le=50, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Search patients by multiple criteria.
    
    Supports searching by patient ID, mobile number, name, or general query.
    Returns paginated results with patient information and alert status.
    """
    try:
        # Search patients
        patients = DatabaseManager.search_patients(
            query=query,
            patient_id=patient_id,
            mobile=mobile,
            name=name,
            limit=limit + 1,  # Get one extra to check if there are more
            offset=offset
        )
        
        # Check if there are more results
        has_more = len(patients) > limit
        if has_more:
            patients = patients[:limit]  # Remove the extra result
        
        # Convert to response format
        search_results = []
        for patient in patients:
            # Calculate age if not already calculated
            age = patient.get('age', 0)
            if not age and patient.get('date_of_birth'):
                birth_date = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d').date()
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            search_result = PatientSearchResult(
                patient_id=patient['patient_id'],
                name=f"{patient['first_name']} {patient['last_name']}",
                age=age,
                mobile=patient['mobile_number'],
                last_visit=datetime.fromisoformat(patient['last_visit']) if patient.get('last_visit') else None,
                alert_status=patient.get('alert_status', 'normal'),
                total_visits=patient.get('total_visits', 0)
            )
            search_results.append(search_result)
        
        # Get total count for the search (without limit)
        total_patients = DatabaseManager.search_patients(
            query=query,
            patient_id=patient_id,
            mobile=mobile,
            name=name,
            limit=1000,  # Large limit to get total count
            offset=0
        )
        total_count = len(total_patients)
        
        logger.info(f"Patient search completed: {len(search_results)} results")
        
        return PatientSearchResponse(
            patients=search_results,
            total_count=total_count,
            has_more=has_more
        )
        
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search patients: {str(e)}"
        )


@router.get("/{patient_id}", response_model=dict)
async def get_patient(patient_id: str):
    """
    Get patient information by ID.
    
    Returns complete patient information including demographics and medical history.
    """
    try:
        patient = DatabaseManager.get_patient(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        
        # Calculate age
        if patient.get('date_of_birth'):
            birth_date = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            patient['age'] = age
        
        logger.info(f"Patient retrieved: {patient_id}")
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving patient {patient_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve patient: {str(e)}"
        )


@router.get("/{patient_id}/history", response_model=CaseHistoryResponse)
async def get_patient_history(
    patient_id: str,
    case_type: Optional[str] = Query(None, description="Filter by case type"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of cases")
):
    """
    Retrieve complete case history for a patient.
    
    Returns patient information, case history, and visit pattern analysis.
    """
    try:
        # Get patient history
        history_data = DatabaseManager.get_patient_history(
            patient_id=patient_id,
            case_type=case_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if not history_data:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        
        # Convert to response format
        patient_info = history_data['patient_info']
        
        # Calculate age
        if patient_info.get('date_of_birth'):
            birth_date = datetime.strptime(patient_info['date_of_birth'], '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        else:
            age = 0
        
        # Format patient info
        formatted_patient_info = {
            "patient_id": patient_info['patient_id'],
            "name": f"{patient_info['first_name']} {patient_info['last_name']}",
            "age": age,
            "mobile": patient_info['mobile_number'],
            "chronic_conditions": patient_info.get('chronic_conditions', '').split(',') if patient_info.get('chronic_conditions') else [],
            "allergies": patient_info.get('allergies', '').split(',') if patient_info.get('allergies') else [],
            "gender": patient_info.get('gender')
        }
        
        # Format cases
        formatted_cases = []
        for case in history_data['cases']:
            formatted_case = {
                "case_id": case['case_id'],
                "visit_date": datetime.fromisoformat(case['visit_datetime']),
                "case_type": case['case_type'],
                "chief_complaint": case.get('chief_complaint'),
                "urgency_level": case['urgency_level'],
                "healthcare_worker": case.get('healthcare_worker'),
                "summary": case.get('recommendations'),
                "ai_assessment": case.get('ai_assessment')
            }
            formatted_cases.append(formatted_case)
        
        # Format visit patterns
        visit_patterns = history_data['visit_patterns']
        formatted_patterns = {
            "total_visits": visit_patterns.get('total_visits', 0),
            "last_visit": datetime.fromisoformat(visit_patterns['last_visit']) if visit_patterns.get('last_visit') else None,
            "frequent_visitor": visit_patterns.get('pattern_type') == 'Frequent',
            "repeat_visit_alert": visit_patterns.get('concern_level') in ['Medium', 'High'],
            "pattern_type": visit_patterns.get('pattern_type'),
            "concern_level": visit_patterns.get('concern_level')
        }
        
        logger.info(f"Patient history retrieved: {patient_id}, {len(formatted_cases)} cases")
        
        return CaseHistoryResponse(
            patient_info=formatted_patient_info,
            cases=formatted_cases,
            visit_patterns=formatted_patterns
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving patient history {patient_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve patient history: {str(e)}"
        )


@router.get("/{patient_id}/alerts", response_model=VisitAlertResponse)
async def check_visit_alerts(patient_id: str):
    """
    Check for repeat visit alerts and patterns.
    
    Analyzes visit patterns and returns alerts for concerning visit frequency
    or patterns that may indicate deteriorating health conditions.
    """
    try:
        # Check if patient exists
        patient = DatabaseManager.get_patient(patient_id)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        
        # Get visit alerts
        alerts = DatabaseManager.check_visit_alerts(patient_id)
        
        logger.info(f"Visit alerts checked for patient: {patient_id}")
        
        return VisitAlertResponse(**alerts)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking visit alerts for {patient_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check visit alerts: {str(e)}"
        )


@router.post("/{patient_id}/assess", response_model=EnhancedAssessmentResponse)
async def assess_with_history(
    patient_id: str,
    assessment_data: AssessmentRequest
):
    """
    Conduct AI assessment with patient history context.
    
    Performs AI-powered medical assessment considering the patient's
    medical history, previous cases, and chronic conditions.
    Automatically creates a case record for tracking.
    """
    try:
        # Check if patient exists
        patient = DatabaseManager.get_patient(patient_id)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        
        # Get patient history for context
        history_data = DatabaseManager.get_patient_history(patient_id, limit=10)
        
        # Build enhanced prompt with historical context
        enhanced_prompt = f"""
        Patient Assessment with Historical Context:
        
        Current Symptoms: {assessment_data.symptoms}
        Patient Age: {assessment_data.age}
        Duration: {assessment_data.duration or 'Not specified'}
        Severity: {assessment_data.severity or 'Not specified'}
        Additional Info: {assessment_data.additional_info or 'None'}
        
        Medical History:
        - Previous Conditions: {patient.get('chronic_conditions', 'None')}
        - Known Allergies: {patient.get('allergies', 'None')}
        - Recent Cases: {len(history_data['cases']) if history_data else 0} cases in history
        
        Please provide assessment considering:
        1. Current symptoms in context of medical history
        2. Pattern analysis from previous cases
        3. Risk factors based on patient profile
        4. Urgency level and recommended actions
        """
        
        # Get AI assessment
        ai_agent = HybridTriageAgent()
        ai_response = await ai_agent.assess_symptoms(enhanced_prompt, assessment_data.age)
        
        # Create assessment ID
        assessment_id = f"ASSESS_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze historical context
        similar_episodes = 0
        last_similar_case = None
        if history_data and history_data['cases']:
            # Simple similarity check based on keywords
            current_keywords = set(assessment_data.symptoms.lower().split())
            for case in history_data['cases']:
                case_keywords = set(case.get('symptoms', '').lower().split())
                if len(current_keywords.intersection(case_keywords)) >= 2:
                    similar_episodes += 1
                    if not last_similar_case:
                        last_similar_case = datetime.fromisoformat(case['visit_datetime']).date()
        
        historical_context = {
            "similar_episodes": similar_episodes,
            "last_similar_case": last_similar_case,
            "treatment_response": "Previous treatments showed good response" if similar_episodes > 0 else None,
            "chronic_conditions_impact": "Consider chronic conditions in treatment plan" if patient.get('chronic_conditions') else "No chronic conditions identified",
            "case_count": len(history_data['cases']) if history_data else 0
        }
        
        # Analyze patterns
        visit_patterns = history_data['visit_patterns'] if history_data else {}
        pattern_insights = {
            "seasonal_pattern": None,
            "frequency_concern": visit_patterns.get('concern_level') in ['Medium', 'High'],
            "escalation_needed": visit_patterns.get('concern_level') == 'High'
        }
        
        # CREATE CASE RECORD - This is the key addition!
        # Every assessment creates a case record for tracking
        case_data = {
            "patient_id": patient_id,
            "case_type": "Assessment",
            "chief_complaint": assessment_data.symptoms[:100] + "..." if len(assessment_data.symptoms) > 100 else assessment_data.symptoms,
            "symptoms": assessment_data.symptoms,
            "urgency_level": ai_response.urgency.title(),  # Convert to proper case
            "recommendations": ", ".join(ai_response.actions) if ai_response.actions else None,
            "follow_up_required": ai_response.escalate,
            "notes": f"AI Assessment - Duration: {assessment_data.duration}, Severity: {assessment_data.severity}, Additional: {assessment_data.additional_info}",
            "ai_assessment": ai_response.model_dump()
        }
        
        try:
            case_id = DatabaseManager.create_case_v2(case_data)
            logger.info(f"Case record created from assessment: {case_id} for patient {patient_id}")
            
            # Add case_id to historical context
            historical_context["case_id"] = case_id
            
        except Exception as case_error:
            logger.warning(f"Failed to create case record for assessment {assessment_id}: {case_error}")
            # Continue with assessment even if case creation fails
            historical_context["case_creation_error"] = str(case_error)
        
        logger.info(f"Enhanced AI assessment completed for patient: {patient_id}")
        
        return EnhancedAssessmentResponse(
            assessment_id=assessment_id,
            ai_assessment=ai_response,
            historical_context=historical_context,
            pattern_insights=pattern_insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced assessment for patient {patient_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Assessment failed: {str(e)}"
        )


@router.post("/{patient_id}/cases", response_model=CaseResponseV2)
async def create_case(
    patient_id: str,
    case_data: CaseCreateV2
):
    """
    Create a new medical case for a patient.
    
    Creates a new case record linked to the patient and updates
    visit patterns for repeat visit detection.
    """
    try:
        # Check if patient exists
        patient = DatabaseManager.get_patient(patient_id)
        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )
        
        # Ensure patient_id matches
        case_dict = case_data.model_dump()
        case_dict['patient_id'] = patient_id
        
        # Create case
        case_id = DatabaseManager.create_case_v2(case_dict)
        
        # Get created case
        created_case = {
            "case_id": case_id,
            "patient_id": patient_id,
            "healthcare_worker_id": case_dict.get('healthcare_worker_id', 'HW001'),
            "visit_datetime": datetime.now(),
            "case_type": case_dict.get('case_type', 'Assessment'),
            "chief_complaint": case_dict.get('chief_complaint'),
            "symptoms": case_dict['symptoms'],
            "urgency_level": case_dict.get('urgency_level', 'Medium'),
            "recommendations": case_dict.get('recommendations'),
            "case_status": "Open",
            "created_at": datetime.now()
        }
        
        logger.info(f"Case created for patient {patient_id}: {case_id}")
        
        return CaseResponseV2(**created_case)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating case for patient {patient_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create case: {str(e)}"
        )


@router.get("/stats/summary")
async def get_patient_stats():
    """
    Get patient management statistics.
    
    Returns summary statistics for patient registration and activity.
    """
    try:
        stats = DatabaseManager.get_stats()
        
        return {
            "total_patients": stats.get("total_patients", 0),
            "new_patients_30_days": stats.get("new_patients_30_days", 0),
            "total_cases": stats.get("total_cases", 0),
            "pending_cases": stats.get("pending_cases", 0),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting patient stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        ) 
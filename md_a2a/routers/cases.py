"""Cases router for Medical AI Assistant MVP."""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Query

from ..agents import HybridTriageAgent, HybridMedicalTools
from ..config import settings
from ..database import DatabaseManager
from ..models import (
    CaseCreate,
    CaseResponse,
    DoctorReview,
    PhotoUploadResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["cases"])

# Initialize hybrid agents with AI integration
triage_agent = HybridTriageAgent()
medical_tools = HybridMedicalTools()


@router.post("/cases", response_model=CaseResponse)
async def create_case(case_data: CaseCreate) -> CaseResponse:
    """Create a new medical case with AI assessment."""
    try:
        # Generate unique case ID
        case_id = str(uuid.uuid4())

        logger.info(f"Creating case {case_id} for symptoms: {case_data.symptoms}")

        # Get AI assessment using hybrid agent
        ai_assessment = await triage_agent.assess_symptoms(
            symptoms=case_data.symptoms,
            age=case_data.patient.age_years,
            severity=case_data.severity,
        )

        # Prepare case data for database
        db_case_data = {
            "id": case_id,
            "patient_data": case_data.patient.model_dump(),
            "symptoms": case_data.symptoms,
            "severity": case_data.severity,
            "ai_assessment": ai_assessment.model_dump(),
            "photo_paths": [],
            "volunteer_id": case_data.volunteer_id,
        }

        # Save to database
        DatabaseManager.create_case(db_case_data)

        # Return response
        response = CaseResponse(
            case_id=case_id,
            patient=case_data.patient,
            symptoms=case_data.symptoms,
            severity=case_data.severity,
            ai_assessment=ai_assessment,
            photo_paths=[],
            status="new",
            volunteer_id=case_data.volunteer_id,
            created_at=datetime.utcnow(),
        )

        logger.info(f"Case {case_id} created successfully with urgency: {ai_assessment.urgency}")
        return response

    except Exception as e:
        logger.error(f"Error creating case: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create case: {str(e)}")


@router.get("/cases")
async def get_cases(
    status: Optional[str] = Query(None, description="Filter by case status (new, reviewed, closed)"),
    patient_name: Optional[str] = Query(None, description="Filter by patient name (partial match)")
) -> dict:
    """Get all cases, optionally filtered by status and/or patient name."""
    try:
        cases = DatabaseManager.get_cases(status=status, patient_name=patient_name)
        logger.info(f"Retrieved {len(cases)} cases")
        return {"cases": cases}
    except Exception as e:
        logger.error(f"Error retrieving cases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cases: {str(e)}")


@router.get("/cases/{case_id}")
async def get_case(case_id: str) -> dict:
    """Get a specific case by ID."""
    try:
        # Try V2 cases first
        case = DatabaseManager.get_case_v2(case_id)
        if not case:
            # Fallback to legacy cases
            case = DatabaseManager.get_case(case_id)
            if not case:
                raise HTTPException(status_code=404, detail="Case not found")
        
        logger.info(f"Retrieved case details: {case_id}")
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve case: {str(e)}")


@router.post("/cases/{case_id}/photos", response_model=PhotoUploadResponse)
async def upload_photo(case_id: str, file: UploadFile = File(...)) -> PhotoUploadResponse:
    """Upload a photo for a case."""
    try:
        # Validate case exists
        case = DatabaseManager.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Validate file type
        if file.content_type not in settings.allowed_file_types_list:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.allowed_file_types_list)}"
            )

        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            )

        # Create upload directory
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"{case_id}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = upload_dir / filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Update case with photo path
        DatabaseManager.add_photo_to_case(case_id, str(file_path))

        logger.info(f"Photo uploaded for case {case_id}: {filename}")

        return PhotoUploadResponse(
            case_id=case_id,
            filename=filename,
            photo_url=f"/static/photos/{filename}",
            upload_time=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading photo for case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload photo: {str(e)}")


@router.post("/cases/{case_id}/review")
async def review_case(case_id: str, review: DoctorReview) -> dict:
    """Doctor reviews a case."""
    try:
        # Validate case exists
        case = DatabaseManager.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Update case with doctor review
        DatabaseManager.add_doctor_review(case_id, review.review, review.doctor_id)

        logger.info(f"Case {case_id} reviewed by doctor {review.doctor_id}")

        return {
            "case_id": case_id,
            "status": "reviewed",
            "review_time": datetime.utcnow(),
            "doctor_id": review.doctor_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to review case: {str(e)}")


# New AI-powered endpoints
@router.post("/v2/cases/assess")
async def ai_assess_symptoms(request: dict) -> dict:
    """Direct AI assessment endpoint for testing."""
    try:
        symptoms = request.get("symptoms")
        age = request.get("age")
        severity = request.get("severity", "medium")
        
        if not symptoms or not age:
            raise HTTPException(status_code=400, detail="symptoms and age are required")
        
        assessment = await triage_agent.assess_symptoms(symptoms, age, severity)
        return {
            "assessment": assessment.model_dump(),
            "ai_used": not settings.dev_mock_ai,
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"Error in AI assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.post("/v2/cases/dosage")
async def ai_calculate_dosage(request: dict) -> dict:
    """Direct AI dosage calculation endpoint."""
    try:
        medication = request.get("medication")
        weight_kg = request.get("weight_kg")
        age_years = request.get("age_years")
        
        if not medication or not weight_kg or not age_years:
            raise HTTPException(status_code=400, detail="medication, weight_kg, and age_years are required")
        
        dosage = await medical_tools.calculate_dose(medication, weight_kg, age_years)
        return {
            "dosage": dosage,
            "ai_used": not settings.dev_mock_ai,
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"Error in dosage calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Dosage calculation failed: {str(e)}")


@router.post("/cases/{case_id}/reassess")
async def reassess_case(case_id: str) -> dict:
    """Re-run AI assessment for an existing case."""
    try:
        # Get existing case
        case = DatabaseManager.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Extract patient data
        patient_data = case.get("patient_data", {})
        age = patient_data.get("age_years", 0)
        
        # Re-run assessment
        new_assessment = await triage_agent.assess_symptoms(
            symptoms=case["symptoms"],
            age=age,
            severity=case["severity"]
        )

        # Update case with new assessment
        DatabaseManager.update_case_assessment(case_id, new_assessment.model_dump())

        logger.info(f"Case {case_id} reassessed with new urgency: {new_assessment.urgency}")

        return {
            "case_id": case_id,
            "new_assessment": new_assessment.model_dump(),
            "reassess_time": datetime.utcnow(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reassessing case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reassess case: {str(e)}")


@router.put("/cases/{case_id}/status")
async def update_case_status(case_id: str, status: str = Query(..., description="New status: new, reviewed, closed")) -> dict:
    """Update the status of a case."""
    try:
        # Validate status
        valid_statuses = ["new", "reviewed", "closed"]
        if status.lower() not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"
            )
        
        # Check if case exists (try both legacy and V2 tables)
        case = DatabaseManager.get_case(case_id)
        if not case:
            # Try V2 cases table
            v2_case = DatabaseManager.get_case_v2(case_id)
            if not v2_case:
                raise HTTPException(status_code=404, detail="Case not found")
            
            # Update V2 case
            success = DatabaseManager.update_case_v2_status(case_id, status)
        else:
            # Update legacy case
            success = DatabaseManager.update_case(case_id, {"status": status})
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update case status")

        logger.info(f"Case {case_id} status updated to: {status}")
        return {
            "success": True,
            "message": f"Case status updated to {status}",
            "case_id": case_id,
            "new_status": status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case status {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update case status: {str(e)}")

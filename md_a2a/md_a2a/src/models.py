"""Pydantic models for Medical AI Assistant MVP."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    """Patient information model."""

    age_years: int = Field(..., ge=0, le=120, description="Patient age in years")
    weight_kg: Optional[float] = Field(
        None, ge=0.5, le=300, description="Patient weight in kg"
    )
    gender: Optional[str] = Field(None, pattern="^(male|female|other|unknown)$")


class TriageAssessment(BaseModel):
    """AI triage assessment result."""

    urgency: str = Field(..., description="Urgency level: low, medium, high, emergency")
    actions: list[str] = Field(..., description="Recommended first aid actions")
    escalate: bool = Field(..., description="Whether to escalate to doctor")
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score"
    )
    red_flags: list[str] = Field(
        default_factory=list, description="Warning signs detected"
    )


class CaseCreate(BaseModel):
    """Model for creating a new medical case."""

    patient: PatientInfo
    symptoms: str = Field(
        ..., min_length=1, max_length=1000, description="Patient symptoms"
    )
    severity: str = Field(default="medium", pattern="^(low|medium|high|emergency)$")
    volunteer_id: Optional[str] = None


class CaseResponse(BaseModel):
    """Model for case response."""

    case_id: str
    patient: PatientInfo
    symptoms: str
    severity: str
    ai_assessment: Optional[TriageAssessment] = None
    doctor_review: Optional[str] = None
    photo_paths: list[str] = Field(default_factory=list)
    status: str = Field(default="new")
    volunteer_id: Optional[str] = None
    doctor_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class DoctorReview(BaseModel):
    """Model for doctor review of a case."""

    review: str = Field(
        ..., min_length=1, max_length=2000, description="Doctor's review and advice"
    )
    doctor_id: Optional[str] = None


class PhotoUploadResponse(BaseModel):
    """Model for photo upload response."""

    photo_url: str
    case_id: str
    uploaded_at: datetime


class HealthCheck(BaseModel):
    """Model for health check response."""

    status: str
    timestamp: datetime
    version: str
    checks: dict[str, str] = Field(default_factory=dict)


class APIError(BaseModel):
    """Model for API error responses."""

    error: str
    detail: Optional[str] = None
    timestamp: datetime

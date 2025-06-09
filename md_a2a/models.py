"""Pydantic models for Medical AI Assistant MVP."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


# Enums for validation
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class CaseType(str, Enum):
    ASSESSMENT = "Assessment"
    DOSAGE = "Dosage"
    PHOTO = "Photo"
    FOLLOW_UP = "Follow-up"
    EMERGENCY = "Emergency"


class UrgencyLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class CaseStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    REFERRED = "Referred"


class PatternType(str, Enum):
    NORMAL = "Normal"
    FREQUENT = "Frequent"
    EMERGENCY = "Emergency"
    FOLLOW_UP = "Follow-up"


class ConcernLevel(str, Enum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class HealthcareWorkerRole(str, Enum):
    DOCTOR = "Doctor"
    NURSE = "Nurse"
    HEALTH_WORKER = "Health_Worker"
    SUPERVISOR = "Supervisor"


# V2.0 Patient Management Models
class PatientRegistration(BaseModel):
    """Model for patient registration."""
    
    first_name: str = Field(..., min_length=1, max_length=50, description="Patient's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Patient's last name")
    date_of_birth: date = Field(..., description="Patient's date of birth")
    mobile_number: str = Field(..., pattern=r"^\d{10}$", description="10-digit mobile number")
    gender: Gender = Field(..., description="Patient's gender")
    village: Optional[str] = Field(None, max_length=100, description="Village name")
    district: Optional[str] = Field(None, max_length=100, description="District name")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    emergency_contact: Optional[str] = Field(None, pattern=r"^\d{10}$", description="Emergency contact number")
    guardian_name: Optional[str] = Field(None, max_length=100, description="Guardian's name")
    occupation: Optional[str] = Field(None, max_length=100, description="Patient's occupation")
    blood_group: Optional[str] = Field(None, max_length=5, description="Blood group")
    allergies: Optional[str] = Field(None, description="Known allergies")
    chronic_conditions: Optional[str] = Field(None, description="Chronic medical conditions")


class PatientResponse(BaseModel):
    """Model for patient registration response."""
    
    patient_id: str = Field(..., description="Unique patient identifier")
    patient_data: Dict[str, Any] = Field(..., description="Complete patient information")
    qr_code: Optional[str] = Field(None, description="Base64 encoded QR code")
    success: bool = Field(..., description="Registration success status")
    message: str = Field(..., description="Response message")


class PatientSearchResult(BaseModel):
    """Model for individual patient search result."""
    
    patient_id: str = Field(..., description="Unique patient identifier")
    name: str = Field(..., description="Patient's full name")
    age: int = Field(..., description="Patient's age")
    mobile: str = Field(..., description="Mobile number")
    last_visit: Optional[datetime] = Field(None, description="Last visit date")
    alert_status: str = Field(..., description="Alert status: normal|repeat|frequent|emergency")
    total_visits: int = Field(default=0, description="Total number of visits")


class PatientSearchResponse(BaseModel):
    """Model for patient search response."""
    
    patients: List[PatientSearchResult] = Field(..., description="List of matching patients")
    total_count: int = Field(..., description="Total number of matching patients")
    has_more: bool = Field(..., description="Whether more results are available")


class CaseHistoryItem(BaseModel):
    """Model for individual case in patient history."""
    
    case_id: str = Field(..., description="Unique case identifier")
    visit_date: datetime = Field(..., description="Visit date and time")
    case_type: CaseType = Field(..., description="Type of case")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")
    urgency_level: UrgencyLevel = Field(..., description="Urgency level")
    healthcare_worker: Optional[str] = Field(None, description="Healthcare worker name")
    summary: Optional[str] = Field(None, description="Case summary")
    ai_assessment: Optional[Dict[str, Any]] = Field(None, description="AI assessment results")


class VisitPatternInfo(BaseModel):
    """Model for visit pattern information."""
    
    total_visits: int = Field(..., description="Total number of visits")
    last_visit: Optional[datetime] = Field(None, description="Last visit date")
    frequent_visitor: bool = Field(..., description="Whether patient is a frequent visitor")
    repeat_visit_alert: bool = Field(..., description="Whether there's a repeat visit alert")
    pattern_type: Optional[PatternType] = Field(None, description="Visit pattern type")
    concern_level: Optional[ConcernLevel] = Field(None, description="Concern level")


class PatientInfo(BaseModel):
    """Enhanced patient information model."""

    patient_id: str = Field(..., description="Unique patient identifier")
    name: str = Field(..., description="Patient's full name")
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    mobile: str = Field(..., description="Mobile number")
    chronic_conditions: Optional[List[str]] = Field(None, description="List of chronic conditions")
    allergies: Optional[List[str]] = Field(None, description="List of allergies")
    weight_kg: Optional[float] = Field(
        None, ge=0.5, le=300, description="Patient weight in kg"
    )
    gender: Optional[Gender] = Field(None, description="Patient's gender")


class CaseHistoryResponse(BaseModel):
    """Model for patient case history response."""
    
    patient_info: PatientInfo = Field(..., description="Patient information")
    cases: List[CaseHistoryItem] = Field(..., description="List of cases")
    visit_patterns: VisitPatternInfo = Field(..., description="Visit pattern analysis")


class LastVisitInfo(BaseModel):
    """Model for last visit information."""
    
    date: Optional[datetime] = Field(None, description="Last visit date")
    days_ago: int = Field(..., description="Days since last visit")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")
    urgency_level: Optional[UrgencyLevel] = Field(None, description="Urgency level")


class PatternAnalysis(BaseModel):
    """Model for visit pattern analysis."""
    
    visits_last_30_days: int = Field(..., description="Number of visits in last 30 days")
    average_interval: Optional[float] = Field(None, description="Average days between visits")
    concerning_pattern: bool = Field(..., description="Whether pattern is concerning")
    pattern_type: Optional[PatternType] = Field(None, description="Pattern type")


class VisitAlertResponse(BaseModel):
    """Model for visit alert response."""
    
    has_alerts: bool = Field(..., description="Whether there are active alerts")
    alert_level: str = Field(..., description="Alert level: green|yellow|orange|red")
    alert_type: str = Field(..., description="Type of alert")
    last_visit: Optional[LastVisitInfo] = Field(None, description="Last visit information")
    pattern_analysis: PatternAnalysis = Field(..., description="Pattern analysis")
    recommendations: List[str] = Field(..., description="Recommended actions")


class AssessmentRequest(BaseModel):
    """Model for AI assessment request with patient context."""
    
    symptoms: str = Field(..., min_length=1, max_length=1000, description="Patient symptoms")
    age: int = Field(..., ge=0, le=120, description="Patient age")
    duration: Optional[str] = Field(None, description="Symptom duration")
    severity: Optional[str] = Field(None, description="Symptom severity")
    additional_info: Optional[str] = Field(None, description="Additional information")


class HistoricalContext(BaseModel):
    """Model for historical context in AI assessment."""
    
    similar_episodes: int = Field(..., description="Number of similar episodes")
    last_similar_case: Optional[date] = Field(None, description="Date of last similar case")
    treatment_response: Optional[str] = Field(None, description="Previous treatment response")
    chronic_conditions_impact: Optional[str] = Field(None, description="Impact of chronic conditions")


class PatternInsights(BaseModel):
    """Model for pattern insights in AI assessment."""
    
    seasonal_pattern: Optional[str] = Field(None, description="Seasonal pattern description")
    frequency_concern: bool = Field(..., description="Whether frequency is concerning")
    escalation_needed: bool = Field(..., description="Whether escalation is needed")


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
    primary_diagnosis: Optional[str] = Field(None, description="Primary diagnosis")
    recommendations: List[str] = Field(default_factory=list, description="Treatment recommendations")


class EnhancedAssessmentResponse(BaseModel):
    """Model for enhanced AI assessment response with history."""
    
    assessment_id: str = Field(..., description="Unique assessment identifier")
    ai_assessment: TriageAssessment = Field(..., description="AI assessment results")
    historical_context: HistoricalContext = Field(..., description="Historical context")
    pattern_insights: PatternInsights = Field(..., description="Pattern insights")


class CaseCreateV2(BaseModel):
    """Model for creating a new medical case with V2.0 schema."""

    patient_id: Optional[str] = Field(None, description="Patient identifier (will be set from URL)")
    healthcare_worker_id: Optional[str] = Field(None, description="Healthcare worker identifier")
    case_type: CaseType = Field(default=CaseType.ASSESSMENT, description="Type of case")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")
    symptoms: str = Field(..., min_length=1, max_length=1000, description="Patient symptoms")
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM, description="Urgency level")
    recommendations: Optional[str] = Field(None, description="Treatment recommendations")
    follow_up_required: bool = Field(default=False, description="Whether follow-up is required")
    notes: Optional[str] = Field(None, description="Additional notes")


class CaseResponseV2(BaseModel):
    """Model for V2.0 case response."""

    case_id: str = Field(..., description="Unique case identifier")
    patient_id: str = Field(..., description="Patient identifier")
    healthcare_worker_id: str = Field(..., description="Healthcare worker identifier")
    visit_datetime: datetime = Field(..., description="Visit date and time")
    case_type: CaseType = Field(..., description="Type of case")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")
    symptoms: str = Field(..., description="Patient symptoms")
    ai_assessment: Optional[TriageAssessment] = Field(None, description="AI assessment")
    urgency_level: UrgencyLevel = Field(..., description="Urgency level")
    recommendations: Optional[str] = Field(None, description="Treatment recommendations")
    case_status: CaseStatus = Field(default=CaseStatus.OPEN, description="Case status")
    created_at: datetime = Field(..., description="Case creation timestamp")


# Legacy models for backward compatibility
class CaseCreate(BaseModel):
    """Model for creating a new medical case (legacy)."""

    patient: PatientInfo
    symptoms: str = Field(
        ..., min_length=1, max_length=1000, description="Patient symptoms"
    )
    severity: str = Field(default="medium", pattern="^(low|medium|high|emergency)$")
    volunteer_id: Optional[str] = None


class CaseResponse(BaseModel):
    """Model for case response (legacy)."""

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

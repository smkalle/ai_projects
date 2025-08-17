"""
Pydantic models for MediPulse API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Literal
from datetime import datetime

class DocumentProcessingRequest(BaseModel):
    """Request model for document processing"""
    file_data: str = Field(..., description="Base64 encoded image data")
    document_type: Optional[str] = Field(None, description="Optional document type hint")
    priority: Optional[Literal["low", "normal", "high"]] = Field("normal")

class DocumentProcessingResponse(BaseModel):
    """Response model for document processing"""
    session_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    message: str
    websocket_url: Optional[str] = None
    created_at: datetime

class AgentMessage(BaseModel):
    """Agent communication message"""
    type: Literal["agent_update", "processing_complete", "error", "connection"]
    agent: Optional[str] = None
    action: Optional[str] = None
    data: Dict[str, Any]
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LabResult(BaseModel):
    """Individual lab test result"""
    value: float
    unit: str
    reference: Optional[str] = None
    status: Optional[Literal["normal", "high", "low", "critical"]] = None

class ExtractedMedicalData(BaseModel):
    """Extracted medical data structure"""
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    date_of_service: Optional[str] = None
    date_of_birth: Optional[str] = None
    physician: Optional[str] = None
    lab_results: Optional[Dict[str, LabResult]] = None
    medications: Optional[List[Dict[str, Any]]] = None
    diagnoses: Optional[List[str]] = None
    vital_signs: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = None
    notes: Optional[str] = None

class ValidationResult(BaseModel):
    """Data validation result"""
    is_valid: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    validations_passed: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    corrections: List[Dict[str, Any]] = Field(default_factory=list)
    field_confidence: Dict[str, float] = Field(default_factory=dict)

class ExtractionResult(BaseModel):
    """Complete extraction result"""
    success: bool
    session_id: str
    document_type: Optional[str] = None
    extracted_data: Optional[ExtractedMedicalData] = None
    validation: Optional[ValidationResult] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_time: Optional[float] = None
    error: Optional[str] = None

class ProcessingStatus(BaseModel):
    """Processing status for WebSocket updates"""
    session_id: str
    status: Literal["connected", "scanning", "extracting", "validating", "completed", "failed"]
    current_agent: Optional[str] = None
    progress: float = Field(ge=0.0, le=1.0)
    message: Optional[str] = None

class SystemMetrics(BaseModel):
    """System performance metrics"""
    total_documents_processed: int
    average_processing_time: float
    accuracy_rate: float
    active_sessions: int
    documents_today: int
    time_saved_hours: float
    error_rate: float
    supported_formats: List[str]
    agent_performance: Dict[str, Dict[str, float]]

class BatchProcessingRequest(BaseModel):
    """Batch processing request"""
    files: List[str] = Field(..., description="List of base64 encoded files")
    priority: Optional[Literal["low", "normal", "high"]] = Field("normal")

class BatchProcessingResponse(BaseModel):
    """Batch processing response"""
    batch_id: str
    total_files: int
    sessions: List[Dict[str, str]]
    message: str
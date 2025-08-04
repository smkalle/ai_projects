"""Document models and schemas."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    file_size: int
    file_type: str
    created_at: float
    modified_at: float
    mime_type: str
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """A chunk of document text for processing."""
    id: str
    text: str
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    """Parsed document with text and metadata."""
    filename: str
    file_path: str
    text: str
    chunks: List[DocumentChunk]
    metadata: DocumentMetadata
    page_count: int
    word_count: int
    char_count: int
    sections: Dict[str, str] = Field(default_factory=dict)
    parsed_at: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    """Result from contract analysis."""
    document_id: str
    document_name: str
    analysis_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    results: Dict[str, Any]
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time: float  # seconds
    error: Optional[str] = None


class ContractAnalysis(BaseModel):
    """Complete contract analysis results."""
    document: ParsedDocument
    contract_type: str
    parties: List[Dict[str, str]]
    key_dates: Dict[str, str]
    key_terms: Dict[str, Any]
    clauses: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    obligations: List[Dict[str, Any]]
    compliance_checks: Dict[str, bool]
    summary: str
    recommendations: List[str]
    analysis_results: List[AnalysisResult]


class ClauseExtraction(BaseModel):
    """Extracted clause information."""
    clause_id: str
    clause_type: str
    text: str
    location: Dict[str, int]  # start_char, end_char, page
    importance: str  # high, medium, low
    risk_level: str  # high, medium, low
    notes: Optional[str] = None


class RiskAssessment(BaseModel):
    """Risk assessment result."""
    risk_id: str
    risk_type: str
    description: str
    severity: str  # high, medium, low
    likelihood: str  # high, medium, low
    impact: str
    mitigation: str
    clause_references: List[str]


class Obligation(BaseModel):
    """Contract obligation."""
    obligation_id: str
    party: str
    description: str
    due_date: Optional[str] = None
    frequency: Optional[str] = None  # one-time, monthly, quarterly, etc.
    status: str = "pending"  # pending, completed, overdue
    clause_reference: Optional[str] = None


class ComplianceCheck(BaseModel):
    """Compliance check result."""
    check_id: str
    regulation: str  # GDPR, SOX, HIPAA, etc.
    requirement: str
    status: str  # compliant, non-compliant, needs-review
    findings: List[str]
    recommendations: List[str]
    clause_references: List[str]


class ContractComparison(BaseModel):
    """Comparison between two contracts."""
    document1_id: str
    document2_id: str
    similarity_score: float
    added_clauses: List[Dict[str, Any]]
    removed_clauses: List[Dict[str, Any]]
    modified_clauses: List[Dict[str, Any]]
    risk_changes: Dict[str, Any]
    summary: str
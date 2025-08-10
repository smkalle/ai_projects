"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class ConfidenceLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class EvidenceLevel(int, Enum):
    SYSTEMATIC_REVIEW_RCT = 1
    INDIVIDUAL_RCT = 2
    SYSTEMATIC_REVIEW_OBSERVATIONAL = 3
    INDIVIDUAL_OBSERVATIONAL = 4
    EXPERT_OPINION = 5

class StudyType(str, Enum):
    RCT = "rct"
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CASE_SERIES = "case_series"
    CASE_REPORT = "case_report"

# Base Models
class Disease(BaseModel):
    """Disease information"""
    name: str = Field(..., description="Disease name")
    omim_id: Optional[str] = Field(None, description="OMIM identifier")
    orphanet_id: Optional[str] = Field(None, description="Orphanet identifier")
    description: Optional[str] = Field(None, description="Disease description")
    synonyms: List[str] = Field(default_factory=list)
    inheritance_pattern: Optional[str] = None
    prevalence: Optional[str] = None

class PatientProfile(BaseModel):
    """Patient profile for personalized analysis"""
    age: Optional[int] = Field(None, ge=0, le=120)
    weight_kg: Optional[float] = Field(None, ge=0)
    sex: Optional[str] = Field(None, regex="^(male|female|other)$")
    genetic_variants: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    comorbidities: List[str] = Field(default_factory=list)

class AnalysisParameters(BaseModel):
    """Parameters for drug repurposing analysis"""
    include_experimental: bool = Field(default=False)
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=100)
    prioritize_safety: bool = Field(default=True)
    geographic_restrictions: List[str] = Field(default_factory=list)
    exclude_contraindicated: bool = Field(default=True)

class AnalysisRequest(BaseModel):
    """Request for drug repurposing analysis"""
    disease: Disease
    patient_profile: Optional[PatientProfile] = None
    analysis_parameters: AnalysisParameters = Field(default_factory=AnalysisParameters)

class Citation(BaseModel):
    """Scientific citation"""
    id: str
    title: str
    authors: List[str]
    journal: str
    year: int
    volume: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None
    study_type: StudyType
    evidence_level: EvidenceLevel
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class Drug(BaseModel):
    """Drug information"""
    drugbank_id: Optional[str] = None
    name: str
    generic_name: Optional[str] = None
    brand_names: List[str] = Field(default_factory=list)
    atc_code: Optional[str] = None
    chemical_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    mechanism_of_action: Optional[str] = None

class SafetyProfile(BaseModel):
    """Drug safety information"""
    known_side_effects: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    drug_interactions: List[str] = Field(default_factory=list)
    monitoring_requirements: List[str] = Field(default_factory=list)
    pediatric_safety: Optional[str] = None
    pregnancy_category: Optional[str] = None

class RepurposingAnalysis(BaseModel):
    """Drug repurposing analysis results"""
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    mechanism_of_action: str
    target_pathway: Optional[str] = None
    expected_benefit: str
    evidence_strength: str
    potential_risks: List[str] = Field(default_factory=list)

class DrugCandidate(BaseModel):
    """Drug candidate for repurposing"""
    drug: Drug
    repurposing_analysis: RepurposingAnalysis
    safety_profile: SafetyProfile
    citations: List[Citation]
    regulatory_status: Dict[str, Any] = Field(default_factory=dict)

class DrugCandidateResponse(BaseModel):
    """Response model for drug candidates"""
    drug_candidates: List[DrugCandidate]
    summary: Dict[str, Any] = Field(default_factory=dict)
    research_gaps: List[str] = Field(default_factory=list)

class AnalysisResponse(BaseModel):
    """Response for drug repurposing analysis"""
    request_id: str
    status: str
    timestamp: datetime
    processing_time_ms: int
    results: DrugCandidateResponse
    medical_disclaimer: str

class LiteratureSearchRequest(BaseModel):
    """Request for literature search"""
    query: str
    databases: List[str] = Field(default=["pubmed"])
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=20, ge=1, le=100)

class LiteratureResult(BaseModel):
    """Single literature search result"""
    id: str
    source: str
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    journal: str
    publication_date: datetime
    doi: Optional[str] = None
    pmid: Optional[str] = None
    study_type: StudyType
    evidence_level: EvidenceLevel
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class LiteratureSearchResponse(BaseModel):
    """Response for literature search"""
    query: str
    total_results: int
    results: List[LiteratureResult]
    facets: Dict[str, Any] = Field(default_factory=dict)

class DrugInfoResponse(BaseModel):
    """Comprehensive drug information response"""
    drug: Drug
    pharmacology: Dict[str, Any] = Field(default_factory=dict)
    indications: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    interactions: List[Dict[str, Any]] = Field(default_factory=list)
    clinical_trials: List[str] = Field(default_factory=list)

class DiseaseInfoResponse(BaseModel):
    """Comprehensive disease information response"""
    disease: Disease
    genetics: Dict[str, Any] = Field(default_factory=dict)
    epidemiology: Dict[str, Any] = Field(default_factory=dict)
    clinical_features: List[Dict[str, Any]] = Field(default_factory=list)
    treatments: List[Dict[str, Any]] = Field(default_factory=list)
    prognosis: Dict[str, Any] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: Dict[str, str]
    version: str
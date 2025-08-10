"""
Pydantic models for the Rare Disease Drug Repurposing AI System
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

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

class Drug(BaseModel):
    """Drug information model"""
    drugbank_id: Optional[str] = None
    name: str
    generic_name: Optional[str] = None
    brand_names: List[str] = Field(default_factory=list)
    atc_code: Optional[str] = None
    chemical_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    mechanism_of_action: Optional[str] = None
    approval_status: str = "unknown"

class Disease(BaseModel):
    """Disease information model"""
    name: str
    omim_id: Optional[str] = None
    orphanet_id: Optional[str] = None
    description: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)
    prevalence: Optional[str] = None
    associated_genes: List[str] = Field(default_factory=list)

class Citation(BaseModel):
    """Citation model"""
    id: str
    title: str
    authors: List[str]
    journal: str
    year: int
    study_type: StudyType
    evidence_level: EvidenceLevel
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    doi: Optional[str] = None
    pmid: Optional[str] = None

class RepurposingAnalysis(BaseModel):
    """Drug repurposing analysis"""
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    mechanism_of_action: str
    target_pathway: Optional[str] = None
    expected_benefit: str
    evidence_strength: str
    potential_risks: List[str] = Field(default_factory=list)

class SafetyProfile(BaseModel):
    """Drug safety profile"""
    known_side_effects: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    drug_interactions: List[str] = Field(default_factory=list)
    monitoring_requirements: List[str] = Field(default_factory=list)
    pediatric_safety: Optional[str] = None

class DrugCandidate(BaseModel):
    """Complete drug candidate information"""
    drug: Drug
    repurposing_analysis: RepurposingAnalysis
    safety_profile: SafetyProfile
    citations: List[Citation]
    regulatory_status: Dict[str, Any] = Field(default_factory=dict)
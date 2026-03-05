"""Pydantic schemas for the medical diagnostic pipeline.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.
All schemas produce simulated outputs for developer education.
"""

from typing import Optional

from pydantic import BaseModel


# ── Input schema ──────────────────────────────────────────────────────────────


class Vitals(BaseModel):
    temperature_c: Optional[float] = None
    heart_rate_bpm: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation_pct: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None


class PatientIntake(BaseModel):
    patient_id: str
    age: int
    sex: str  # "male" | "female" | "other"
    chief_complaint: str
    symptoms: list[str]
    symptom_duration_days: Optional[int] = None
    medical_history: list[str]
    current_medications: list[str]
    allergies: list[str]
    vitals: Optional[Vitals] = None
    lab_values: Optional[dict[str, float]] = None
    has_image: bool = False
    has_audio: bool = False
    case_name: str = ""


# ── Stage 1: Triage output ───────────────────────────────────────────────────


class TriageResult(BaseModel):
    urgency_level: str  # EMERGENT | URGENT | SEMI-URGENT | NON-URGENT
    category: str  # e.g. "Cardiac", "Respiratory"
    red_flags: list[str]
    recommended_pathway: str
    confidence: float
    reasoning: str
    disclaimer: str


# ── Stage 3: Differential diagnosis output ────────────────────────────────────


class DiagnosisEntry(BaseModel):
    rank: int
    condition: str
    icd_10_code: str
    probability_pct: float
    supporting_evidence: list[str]
    against_evidence: list[str]


class DifferentialDiagnosis(BaseModel):
    diagnoses: list[DiagnosisEntry]  # Ranked, max 5
    overall_confidence: float  # 0.0 - 1.0
    requires_urgent_workup: bool
    key_next_step: str
    iteration_number: int
    disclaimer: str


# ── Stage 2: Imaging output (parallel branch) ────────────────────────────────


class ImagingObservation(BaseModel):
    findings: list[str]
    impression: str
    differential_from_image: list[str]
    requires_follow_up_imaging: bool
    disclaimer: str


# ── Stage 5: Case summary output (SOAP + treatment) ──────────────────────────


class CaseSummary(BaseModel):
    subjective: str  # Patient complaints + history
    objective: str  # Vitals, labs, imaging findings
    assessment: str  # Diagnosis + specialist opinion
    plan: str  # Treatment + follow-up + referrals
    medications: list[str]  # Recommended medications with notes
    follow_up: str
    case_id: str
    disclaimer: str

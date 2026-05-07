"""Pydantic v2 schemas for the insurance claims pipeline (Iteration 1)."""
from __future__ import annotations

from pydantic import BaseModel


class ClaimNarrative(BaseModel):
    policy_number: str | None = None
    incident_date: str | None = None
    incident_location: str | None = None
    incident_description: str | None = None
    claimant_name: str | None = None
    contact_info: str | None = None


class ClaimClassification(BaseModel):
    claim_type: str | None = None
    severity: str | None = None
    line_of_business: str | None = None
    escalation_type: str | None = None


class CoverageDecision(BaseModel):
    is_covered: bool | None = None
    coverage_rationale: str | None = None
    deductible_applicable: str | None = None


class FraudSignals(BaseModel):
    safety_concerns: bool = False
    siu_referral_required: bool = False
    fraud_rationale: str | None = None


class RoutingDecision(BaseModel):
    decision: str
    team: str
    priority: int

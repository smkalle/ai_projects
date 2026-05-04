"""
Section 11 — Insurance Claims Intake Workflow
Structured extraction + deterministic routing pipeline, modelled on the
voice-first insurance claims agent by Shubham Saboo (Google ADK / Gemini Live).

Seven steps:
  1  Extract  — free-text narrative → ClaimNarrative (structured facts)
  2  Classify — claim type, severity, policy line
  3  Validate — required-field check (pure Python, deterministic)
  4  Coverage — coverage applicability + evidence requirements
  5  Fraud    — fraud-signal and safety gate
  6  Route    — deterministic routing decision (pure Python)
  7  Checklist— claimant-facing document checklist

All LLM steps use response_schema (dict from model_json_schema()) so the
SDK serialises them cleanly. _parse_response() normalises every response to
a plain dict regardless of whether response.parsed is populated.
"""

import json
from pydantic import BaseModel

DEFAULT_PROMPT = (
    "A customer named John Doe was in a car accident on I-95 near exit 42. "
    "The accident happened last Tuesday at approximately 3 pm. "
    "His policy number is POL-2024-789456. "
    "The other driver was cited by police. "
    "John is claiming damage to the front bumper and driver's side door. "
    "He has the police report and photos of the damage."
)
DEFAULT_MODEL = "gemini-3-flash-preview"


# ---------------------------------------------------------------------------
# Pydantic schemas — .model_json_schema() is passed to response_schema
# ---------------------------------------------------------------------------

class ClaimNarrative(BaseModel):
    claimant_name: str
    policy_number: str
    incident_date: str | None = None
    incident_location: str | None = None
    incident_description: str
    damage_items: list[str]


class ClaimClassification(BaseModel):
    claim_type: str          # auto | property | health | liability
    severity: str            # low | medium | high | critical
    policy_line: str | None = None


class CoverageDecision(BaseModel):
    coverage_applies: bool
    evidence_required: list[str]
    deductible_applies: bool
    notes: str


class FraudSignals(BaseModel):
    fraud_risk: bool
    siu_referral_required: bool
    safety_concerns: bool
    escalation_type: str | None  # ready_for_adjuster | needs_documents |
                                 # special_investigation | emergency_escalation


class DocumentChecklist(BaseModel):
    required_documents: list[str]
    optional_documents: list[str]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _parse_response(response) -> dict:
    """Normalise a generate_content response to a plain dict.

    response.parsed may be:
      - a plain dict  (most common with response_schema)
      - a Pydantic model instance
      - None  (fall back to JSON-parsing response.text)
    """
    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        if hasattr(parsed, "model_dump"):
            return parsed.model_dump()
        if isinstance(parsed, dict):
            return parsed
    # fallback: parse raw text
    try:
        return json.loads(response.text)
    except Exception:
        return {"raw": response.text}


# ---------------------------------------------------------------------------
# Deterministic helpers (no LLM calls)
# ---------------------------------------------------------------------------

def _validate_fields(claim: dict) -> dict:
    """Check that minimum intake fields are present."""
    missing = [
        f for f in ("policy_number", "incident_date", "incident_location", "incident_description")
        if not claim.get(f)
    ]
    return {"has_all_fields": len(missing) == 0, "missing_fields": missing}


def _routing_decision(validation: dict, fraud: dict) -> tuple[str, str, int]:
    """Return (decision, team, priority_score) without calling the LLM."""
    if fraud.get("safety_concerns"):
        return "emergency_escalation", "Emergency Response", 100
    if fraud.get("siu_referral_required"):
        return "special_investigation", "SIU", 90
    if not validation.get("has_all_fields"):
        return "needs_documents", "Customer Service", 30
    escalation = fraud.get("escalation_type")
    if escalation and escalation != "ready_for_adjuster":
        return escalation, "Claims Processing", 70
    return "ready_for_adjuster", "Claims Processing", 50


# ---------------------------------------------------------------------------
# Demo runner
# ---------------------------------------------------------------------------

def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    from google.genai import types  # pylint: disable=import-outside-toplevel

    narrative = prompt or DEFAULT_PROMPT
    print(f"Model : {model}")
    print(f"Prompt: {narrative}\n")

    print("=" * 62)
    print("  INSURANCE CLAIMS INTAKE WORKFLOW")
    print("=" * 62)

    # ------------------------------------------------------------------
    # Step 1 — Extract structured facts
    # ------------------------------------------------------------------
    print("\n[1/7] Extracting structured claim data...")
    r = client.models.generate_content(
        model=model,
        contents=(
            "Extract the following fields from this insurance claim narrative "
            "and return ONLY valid JSON — no markdown fences:\n"
            "  claimant_name, policy_number, incident_date, incident_location, "
            "incident_description, damage_items (list of strings).\n\n"
            f"Claim: {narrative}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ClaimNarrative.model_json_schema(),
        ),
    )
    claim = _parse_response(r)
    print(f"  claimant     : {claim.get('claimant_name')}")
    print(f"  policy       : {claim.get('policy_number')}")
    print(f"  date         : {claim.get('incident_date')}")
    print(f"  location     : {claim.get('incident_location')}")
    print(f"  damage items : {claim.get('damage_items')}")

    # ------------------------------------------------------------------
    # Step 2 — Classify type and severity
    # ------------------------------------------------------------------
    print("\n[2/7] Classifying claim type and severity...")
    r = client.models.generate_content(
        model=model,
        contents=(
            "Classify this insurance claim. Return ONLY valid JSON with fields: "
            "claim_type (auto|property|health|liability), "
            "severity (low|medium|high|critical), "
            "policy_line (string or null).\n\n"
            f"Claim: {narrative}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ClaimClassification.model_json_schema(),
        ),
    )
    classification = _parse_response(r)
    print(f"  type     : {classification.get('claim_type')}")
    print(f"  severity : {classification.get('severity')}")
    print(f"  line     : {classification.get('policy_line')}")

    # ------------------------------------------------------------------
    # Step 3 — Validate required fields (deterministic, no LLM)
    # ------------------------------------------------------------------
    print("\n[3/7] Validating required fields (deterministic)...")
    validation = _validate_fields(claim)
    if validation["has_all_fields"]:
        print("  All required fields present.")
    else:
        print(f"  MISSING: {validation['missing_fields']}")

    # ------------------------------------------------------------------
    # Step 4 — Apply coverage rules
    # ------------------------------------------------------------------
    print("\n[4/7] Applying coverage rules...")
    r = client.models.generate_content(
        model=model,
        contents=(
            "Determine insurance coverage for this claim. Return ONLY valid JSON: "
            "coverage_applies (bool), evidence_required (list of strings), "
            "deductible_applies (bool), notes (string).\n\n"
            f"Claim type : {classification.get('claim_type', 'auto')}\n"
            f"Description: {claim.get('incident_description', narrative)}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CoverageDecision.model_json_schema(),
        ),
    )
    coverage = _parse_response(r)
    print(f"  coverage applies  : {coverage.get('coverage_applies')}")
    print(f"  deductible applies: {coverage.get('deductible_applies')}")
    print(f"  evidence required : {coverage.get('evidence_required')}")
    print(f"  notes             : {coverage.get('notes')}")

    # ------------------------------------------------------------------
    # Step 5 — Fraud signal and safety gate
    # ------------------------------------------------------------------
    print("\n[5/7] Running fraud signal and safety gate...")
    r = client.models.generate_content(
        model=model,
        contents=(
            "Evaluate this insurance claim for fraud risk and safety concerns. "
            "Return ONLY valid JSON: fraud_risk (bool), siu_referral_required (bool), "
            "safety_concerns (bool), escalation_type "
            "(ready_for_adjuster|needs_documents|special_investigation|emergency_escalation or null).\n\n"
            f"Claim: {narrative}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FraudSignals.model_json_schema(),
        ),
    )
    fraud = _parse_response(r)
    print(f"  fraud risk         : {fraud.get('fraud_risk')}")
    print(f"  SIU referral needed: {fraud.get('siu_referral_required')}")
    print(f"  safety concerns    : {fraud.get('safety_concerns')}")
    print(f"  escalation hint    : {fraud.get('escalation_type')}")

    # ------------------------------------------------------------------
    # Step 6 — Deterministic routing (no LLM)
    # ------------------------------------------------------------------
    print("\n[6/7] Deterministic routing decision...")
    decision, team, priority = _routing_decision(validation, fraud)
    print(f"  decision : {decision}")
    print(f"  team     : {team}")
    print(f"  priority : {priority}/100")

    # ------------------------------------------------------------------
    # Step 7 — Generate document checklist
    # ------------------------------------------------------------------
    print("\n[7/7] Generating document checklist...")
    r = client.models.generate_content(
        model=model,
        contents=(
            "Generate a document checklist for this insurance claim. "
            "Return ONLY valid JSON: required_documents (list), optional_documents (list).\n\n"
            f"Claim type: {classification.get('claim_type', 'auto')}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DocumentChecklist.model_json_schema(),
        ),
    )
    checklist = _parse_response(r)
    for doc in checklist.get("required_documents", []):
        print(f"  [required] {doc}")
    for doc in checklist.get("optional_documents", []):
        print(f"  [optional] {doc}")

    # ------------------------------------------------------------------
    # Final packet
    # ------------------------------------------------------------------
    print("\n" + "=" * 62)
    print("  FINAL CLAIM INTAKE PACKET")
    print("=" * 62)
    print(f"  Claimant : {claim.get('claimant_name', 'N/A')}")
    print(f"  Policy   : {claim.get('policy_number', 'N/A')}")
    print(f"  Type     : {classification.get('claim_type', 'N/A')}  |  Severity: {classification.get('severity', 'N/A')}")
    print(f"  Routing  : {decision}")
    print(f"  Team     : {team}  (priority {priority}/100)")
    req_docs = checklist.get("required_documents", [])
    print(f"  Docs due : {', '.join(req_docs[:3]) or 'see checklist'}")
    status = "Ready for human adjuster review" if decision == "ready_for_adjuster" else "Requires follow-up action"
    print(f"\n  STATUS   : {status}")
    print("=" * 62)

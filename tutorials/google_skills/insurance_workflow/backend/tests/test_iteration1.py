"""Unit tests for Iteration 1 (T1.1 – T1.7)."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from backend.pipeline import (
    _parse_response,
    _routing_decision,
    _validate_fields,
    get_fallback_models,
    get_default_model,
    run_classify,
    run_coverage,
    run_extract,
)
from backend.schemas import ClaimClassification, ClaimNarrative

# ---------------------------------------------------------------------------
# T1.6 — Response normalization (mock each of the 4 fallback paths)
# ---------------------------------------------------------------------------


class FakePydanticParsed:
    def model_dump(self):
        return {"mode": "model_dump"}


def test_parse_response_pydantic_model_dump():
    """T1.6 path 1: response.parsed has model_dump."""
    resp = MagicMock()
    resp.parsed = FakePydanticParsed()
    assert _parse_response(resp) == {"mode": "model_dump"}


def test_parse_response_dict_parsed():
    """T1.6 path 2: response.parsed is already a dict."""
    resp = MagicMock()
    resp.parsed = {"mode": "dict"}
    assert _parse_response(resp) == {"mode": "dict"}


def test_parse_response_json_text():
    """T1.6 path 3: response.text is valid JSON."""
    resp = MagicMock()
    resp.parsed = None
    resp.text = '{"mode": "json_text"}'
    assert _parse_response(resp) == {"mode": "json_text"}


def test_parse_response_raw_text():
    """T1.6 path 4: response.text is not valid JSON."""
    resp = MagicMock()
    resp.parsed = None
    resp.text = "not json at all"
    assert _parse_response(resp) == {"raw": "not json at all"}


def test_get_default_model_from_env(monkeypatch):
    """Model selection follows GEMINI_MODEL from environment."""
    monkeypatch.setenv("GEMINI_MODEL", "gemini-flash-latest")
    assert get_default_model() == "gemini-flash-latest"


def test_get_default_model_normalizes_models_prefix(monkeypatch):
    """Accept models/<name> format in .env and normalize for SDK."""
    monkeypatch.setenv("GEMINI_MODEL", "models/gemini-3.1-flash-live-preview")
    assert get_default_model() == "gemini-3.1-flash-live-preview"


def test_get_fallback_models_from_env(monkeypatch):
    monkeypatch.setenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.1-flash-lite-preview, gemini-2.5-flash-lite, models/gemini-2.5-flash",
    )
    assert get_fallback_models() == [
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ]


# ---------------------------------------------------------------------------
# T1.2 / T1.1 — Validation
# ---------------------------------------------------------------------------


def test_validate_fields_all_present():
    """T1.1: all required fields present."""
    claim = {
        "policy_number": "P123",
        "incident_date": "2024-04-12",
        "incident_location": "Main and 5th",
        "incident_description": "Rear-ended",
    }
    result = _validate_fields(claim)
    assert result["has_all_fields"] is True
    assert result["missing_fields"] == []
    assert result["has_valid_fields"] is True
    assert result["invalid_fields"] == []


def test_validate_fields_missing_policy_number():
    """T1.2: policy_number missing."""
    claim = {
        "incident_date": "2024-04-12",
        "incident_location": "Main and 5th",
        "incident_description": "Rear-ended",
    }
    result = _validate_fields(claim)
    assert result["has_all_fields"] is False
    assert result["missing_fields"] == ["policy_number"]
    assert result["has_valid_fields"] is True


def test_validate_fields_multiple_missing():
    claim = {"policy_number": "P123"}
    result = _validate_fields(claim)
    assert result["has_all_fields"] is False
    assert sorted(result["missing_fields"]) == sorted(
        ["incident_date", "incident_location", "incident_description"]
    )


def test_validate_fields_invalid_calendar_date():
    claim = {
        "policy_number": "P123",
        "incident_date": "April 31",
        "incident_location": "Main and 5th",
        "incident_description": "Rear-ended",
    }
    result = _validate_fields(claim)
    assert result["has_all_fields"] is True
    assert result["has_valid_fields"] is False
    assert result["invalid_fields"][0]["field"] == "incident_date"


# ---------------------------------------------------------------------------
# T1.3 / T1.4 — Routing (deterministic)
# ---------------------------------------------------------------------------


def test_routing_default():
    """T1.3: complete narrative, no flags -> ready_for_adjuster, priority 50."""
    validation = {"has_all_fields": True, "missing_fields": []}
    classification = {"escalation_type": None}
    result = _routing_decision(validation, classification)
    assert result == {"decision": "ready_for_adjuster", "team": "Claims Processing", "priority": 50}


def test_routing_needs_documents():
    """T1.4: incomplete narrative -> needs_documents, priority 30."""
    validation = {"has_all_fields": False, "missing_fields": ["policy_number"]}
    classification = {"escalation_type": None}
    result = _routing_decision(validation, classification)
    assert result == {"decision": "needs_documents", "team": "Customer Service", "priority": 30}


def test_routing_custom_escalation():
    validation = {"has_all_fields": True, "missing_fields": []}
    classification = {"escalation_type": "legal_hold"}
    result = _routing_decision(validation, classification)
    assert result == {"decision": "legal_hold", "team": "Claims Processing", "priority": 70}


def test_routing_escalation_ready_ignored():
    validation = {"has_all_fields": True, "missing_fields": []}
    classification = {"escalation_type": "ready_for_adjuster"}
    result = _routing_decision(validation, classification)
    assert result == {"decision": "ready_for_adjuster", "team": "Claims Processing", "priority": 50}


def test_routing_safety_beats_siu():
    """Priority order: safety (100) beats SIU (90)."""
    validation = {"has_all_fields": True, "missing_fields": []}
    classification = {"escalation_type": None}
    fraud = {"safety_concerns": True, "siu_referral_required": True}
    result = _routing_decision(validation, classification, fraud)
    assert result["decision"] == "emergency_escalation"
    assert result["priority"] == 100


def test_routing_siu_beats_missing():
    validation = {"has_all_fields": False, "missing_fields": ["policy_number"]}
    classification = {"escalation_type": None}
    fraud = {"safety_concerns": False, "siu_referral_required": True}
    result = _routing_decision(validation, classification, fraud)
    assert result["decision"] == "special_investigation"
    assert result["priority"] == 90


# ---------------------------------------------------------------------------
# T1.5 — JSON schema enforcement
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_extract_real_uses_json_schema_and_mime_type(genai_client):
    """T1.5: real LLM returns structured ClaimNarrative dict."""
    result = run_extract(
        genai_client,
        "On April 12 my vehicle was rear-ended at the intersection of Main and 5th. Policy #AU-88271."
    )
    assert isinstance(result, dict)
    # Schema enforcement means these keys exist even if null
    assert "policy_number" in result
    assert "incident_date" in result
    assert "incident_location" in result
    assert "incident_description" in result
    # Real extraction should populate them for this clear narrative
    assert result.get("policy_number") is not None
    assert result.get("incident_date") is not None


@pytest.mark.integration
def test_classify_real_uses_json_schema_and_mime_type(genai_client):
    """T1.5: real LLM classifies a claim dict."""
    claim = {
        "policy_number": "AU-88271",
        "incident_date": "2024-04-12",
        "incident_location": "Main and 5th",
        "incident_description": "Vehicle rear-ended at red light.",
    }
    result = run_classify(genai_client, claim)
    assert isinstance(result, dict)
    assert "claim_type" in result
    assert "severity" in result
    assert "line_of_business" in result
    assert result.get("claim_type") is not None


# ---------------------------------------------------------------------------
# T1.1 — Happy path end-to-end (real LLM)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_happy_path_real_extraction(genai_client):
    """T1.1: full narrative with all 4 required fields -> has_all_fields=true."""
    claim = run_extract(
        genai_client,
        "On April 12 my vehicle was rear-ended at the intersection of Main and 5th. Policy #AU-88271. I was stopped at a red light. Minor damage, no injuries, no escalation needed."
    )
    classification = run_classify(genai_client, claim)
    validation = _validate_fields(claim)
    routing = _routing_decision(validation, classification)

    assert validation["has_all_fields"] is True
    assert claim.get("policy_number") is not None
    # Routing is deterministic based on LLM output; priority 50 (default) or 70
    # (custom escalation_type) are both valid outcomes for a real model.
    assert routing["team"] == "Claims Processing"
    assert routing["priority"] in (50, 70)


# ---------------------------------------------------------------------------
# T1.7 — /health endpoint
# ---------------------------------------------------------------------------


def test_health_endpoint():
    """T1.7: GET /health returns 200 OK with expected shape."""
    from fastapi.testclient import TestClient
    from backend.server import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["gemini"] is True


def test_sources_endpoint_text_ingest():
    from fastapi.testclient import TestClient
    from backend.server import app

    client = TestClient(app)
    response = client.post("/sources", json={"text": "Collision losses are covered with $500 deductible."})
    assert response.status_code == 200
    body = response.json()
    assert body["source_id"].startswith("src_")
    assert body["source_type"] == "text"
    assert body["total_sources"] >= 1


# ---------------------------------------------------------------------------
# T1.4 — needs_documents routing via POST /claims (real LLM)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_post_claims_real_missing_fields():
    """T1.4: vague narrative via POST /claims -> missing fields, needs_documents."""
    from fastapi.testclient import TestClient
    from backend.server import app

    test_client = TestClient(app)
    response = test_client.post("/claims", json={"prompt": "My car crashed yesterday."})
    assert response.status_code == 200
    data = response.json()
    assert data["validation"]["has_all_fields"] is False
    assert len(data["validation"]["missing_fields"]) >= 1
    assert "coverage" in data
    assert data["routing"]["decision"] == "needs_documents"
    assert data["routing"]["team"] == "Customer Service"
    assert data["routing"]["priority"] == 30


@pytest.mark.integration
def test_coverage_real_covered_scenario(genai_client):
    """T2.1: covered scenario returns is_covered=true with rationale."""
    claim = {
        "policy_number": "AU-88271",
        "incident_date": "2024-04-12",
        "incident_location": "Main and 5th",
        "incident_description": "Rear-ended at a red light by another driver.",
    }
    classification = {
        "claim_type": "collision",
        "severity": "low",
        "line_of_business": "auto",
        "escalation_type": "ready_for_adjuster",
    }
    coverage = run_coverage(genai_client, claim, classification)
    assert isinstance(coverage, dict)
    assert coverage.get("is_covered") is True
    assert coverage.get("coverage_rationale")


@pytest.mark.integration
def test_coverage_real_not_covered_scenario(genai_client):
    """T2.2: excluded scenario returns is_covered=false with rationale."""
    claim = {
        "policy_number": "AU-77777",
        "incident_date": "2024-04-12",
        "incident_location": "Industrial Road",
        "incident_description": "Vehicle damaged during an organized street race.",
    }
    classification = {
        "claim_type": "collision",
        "severity": "medium",
        "line_of_business": "auto",
        "escalation_type": "ready_for_adjuster",
    }
    coverage = run_coverage(genai_client, claim, classification)
    assert isinstance(coverage, dict)
    assert coverage.get("is_covered") is False
    assert coverage.get("coverage_rationale")


@pytest.mark.integration
def test_coverage_real_deductible_surfaced(genai_client):
    """T2.3: covered scenario surfaces deductible information."""
    claim = {
        "policy_number": "AU-88271",
        "incident_date": "2024-04-12",
        "incident_location": "Main and 5th",
        "incident_description": "Rear-end collision with bumper and trunk damage.",
    }
    classification = {
        "claim_type": "collision",
        "severity": "low",
        "line_of_business": "auto",
        "escalation_type": "ready_for_adjuster",
    }
    coverage = run_coverage(genai_client, claim, classification)
    assert coverage.get("is_covered") is True
    deductible = coverage.get("deductible_applicable")
    assert deductible is not None
    assert str(deductible).strip() != ""

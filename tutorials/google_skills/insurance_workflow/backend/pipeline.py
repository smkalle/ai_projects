"""Insurance claims pipeline core: extraction, classification, validation, routing."""
from __future__ import annotations

import json
import logging
import os
import random
import time
from datetime import datetime

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from backend.schemas import ClaimClassification, ClaimNarrative, CoverageDecision, FraudSignals

logger = logging.getLogger(__name__)
DEFAULT_MODEL_FALLBACK = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash").strip()


def get_fallback_models() -> list[str]:
    """Return ordered fallback model list from env."""
    raw_list = os.environ.get("GEMINI_FALLBACK_MODELS", "")
    parsed = [_normalize_model_name(m) for m in raw_list.split(",") if m.strip()]
    if parsed:
        return parsed
    return [_normalize_model_name(DEFAULT_MODEL_FALLBACK)]
STATIC_POLICY_CONTEXT = """
Policy: Standard Personal Auto (Demo)

Covered:
- Collision damage from rear-end or intersection collisions.
- Damage from uninsured/underinsured motorists, if policy is active on loss date.
- Towing and temporary transportation are covered after a confirmed covered loss.

Not Covered:
- Intentional damage or staged events.
- Racing, speed contests, or criminal use of the vehicle.
- Commercial rideshare delivery incidents unless rideshare endorsement exists.
- Mechanical breakdown, wear and tear, or pre-existing damage.

Deductible Rules:
- Collision deductible: $500 per covered collision loss.
- Uninsured motorist property damage deductible: $250.
- If loss is not covered, no deductible applies.
""".strip()


def _normalize_model_name(model: str) -> str:
    """Normalize model aliases for google-genai SDK calls."""
    m = (model or "").strip()
    if m.startswith("models/"):
        return m.split("/", 1)[1]
    return m


def get_default_model() -> str:
    """Return model from env, honoring current .env setting."""
    raw = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL_FALLBACK)
    return _normalize_model_name(raw)


def _generate_with_retry(
    client: genai.Client,
    *,
    model: str,
    contents: str,
    config: types.GenerateContentConfig,
    max_attempts: int = 5,
) -> object:
    """Generate content with retry for transient Gemini outages."""
    delay = 1.5
    last_error = None
    active_model = _normalize_model_name(model)
    fallback_models = [m for m in get_fallback_models() if m and m != active_model]
    fallback_index = 0
    for attempt in range(1, max_attempts + 1):
        try:
            return client.models.generate_content(
                model=active_model,
                contents=contents,
                config=config,
            )
        except genai_errors.ServerError as exc:
            last_error = exc
            status_code = getattr(exc, "status_code", None)
            if status_code not in (429, 500, 503) or attempt == max_attempts:
                raise
            sleep_for = delay + random.uniform(0, 0.5)
            logger.warning(
                "Gemini transient error (status=%s), retry %s/%s in %.2fs",
                status_code,
                attempt,
                max_attempts,
                sleep_for,
            )
            time.sleep(sleep_for)
            delay = min(delay * 2, 12)
        except genai_errors.APIError as exc:
            status_code = getattr(exc, "status_code", None)
            message = str(exc)
            # Some aliases can work in REST curl but not in SDK paths.
            # If model lookup is 404, walk configured fallback chain.
            if (status_code == 404 or "404" in message) and fallback_index < len(fallback_models):
                next_model = fallback_models[fallback_index]
                fallback_index += 1
                logger.warning(
                    "Model '%s' not found in SDK route (404). Falling back to '%s'.",
                    active_model,
                    next_model,
                )
                active_model = next_model
                continue
            raise
    if last_error is not None:
        raise last_error


def _parse_response(response) -> dict:
    """Normalize a Gemini response to a plain dict.

    Fallback order (exact):
      1. response.parsed.model_dump() if parsed is a Pydantic object
      2. response.parsed if already a dict
      3. json.loads(response.text)
      4. {"raw": response.text} if JSON parsing fails
    """
    parsed = getattr(response, "parsed", None)
    if parsed is not None and hasattr(parsed, "model_dump"):
        return parsed.model_dump()
    if isinstance(parsed, dict):
        return parsed
    text = getattr(response, "text", None)
    if text is not None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}
    return {"raw": ""}


def _validate_fields(claim: dict) -> dict:
    """Deterministic validation of required claim fields and basic date sanity."""
    required = ["policy_number", "incident_date", "incident_location", "incident_description"]
    missing = [f for f in required if not claim.get(f)]
    invalid_fields: list[dict[str, str]] = []

    incident_date = claim.get("incident_date")
    if incident_date:
        text = str(incident_date).strip()
        date_valid = False
        for fmt in ("%Y-%m-%d", "%B %d, %Y", "%B %d", "%b %d, %Y", "%b %d"):
            try:
                datetime.strptime(text, fmt)
                date_valid = True
                break
            except ValueError:
                continue
        if not date_valid:
            invalid_fields.append(
                {
                    "field": "incident_date",
                    "reason": "Invalid calendar date format or value",
                }
            )

    return {
        "has_all_fields": len(missing) == 0,
        "missing_fields": missing,
        "has_valid_fields": len(invalid_fields) == 0,
        "invalid_fields": invalid_fields,
    }


def _routing_decision(
    validation: dict,
    classification: dict,
    fraud_signals: dict | None = None,
) -> dict:
    """Deterministic routing with strict priority order.

    Priority:
      1. safety_concerns=true          -> emergency_escalation | Emergency Response | 100
      2. siu_referral_required=true    -> special_investigation | SIU                |  90
      3. has_all_fields=false          -> needs_documents       | Customer Service   |  30
      4. escalation_type exists
         and != ready_for_adjuster     -> {escalation_type}     | Claims Processing  |  70
      5. default                        -> ready_for_adjuster    | Claims Processing  |  50
    """
    fraud_signals = fraud_signals or {}

    if fraud_signals.get("safety_concerns") is True:
        return {"decision": "emergency_escalation", "team": "Emergency Response", "priority": 100}

    if fraud_signals.get("siu_referral_required") is True:
        return {"decision": "special_investigation", "team": "SIU", "priority": 90}

    if not validation.get("has_all_fields", True):
        return {"decision": "needs_documents", "team": "Customer Service", "priority": 30}

    escalation = classification.get("escalation_type")
    if escalation and escalation != "ready_for_adjuster":
        return {"decision": escalation, "team": "Claims Processing", "priority": 70}

    return {"decision": "ready_for_adjuster", "team": "Claims Processing", "priority": 50}


def run_extract(client: genai.Client, prompt: str, model: str | None = None) -> dict:
    """Step 1: Extract structured claim facts from narrative."""
    model = model or get_default_model()
    schema = ClaimNarrative.model_json_schema()
    content = (
        f"Extract structured claim facts from the following insurance claim narrative.\n"
        f"Return JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\n"
        f"Narrative:\n{prompt}"
    )
    response = _generate_with_retry(
        client,
        model=model,
        contents=content,
        config=types.GenerateContentConfig(
            responseMimeType="application/json",
            responseSchema=schema,
        ),
    )
    result = _parse_response(response)
    logger.debug("Extract result: %s", result)
    return result


def run_classify(client: genai.Client, claim_dict: dict, model: str | None = None) -> dict:
    """Step 2: Classify claim type, severity, line of business, escalation."""
    model = model or get_default_model()
    schema = ClaimClassification.model_json_schema()
    content = (
        f"Classify the following insurance claim.\n"
        f"Claim facts:\n{json.dumps(claim_dict, indent=2)}\n\n"
        f"Return JSON matching this schema:\n{json.dumps(schema, indent=2)}"
    )
    response = _generate_with_retry(
        client,
        model=model,
        contents=content,
        config=types.GenerateContentConfig(
            responseMimeType="application/json",
            responseSchema=schema,
        ),
    )
    result = _parse_response(response)
    logger.debug("Classify result: %s", result)
    return result


def run_coverage(
    client: genai.Client,
    claim_dict: dict,
    classification_dict: dict,
    policy_context: str | None = None,
    model: str | None = None,
) -> dict:
    """Step 4: Determine coverage decision from static policy context."""
    model = model or get_default_model()
    schema = CoverageDecision.model_json_schema()
    policy_text = policy_context or STATIC_POLICY_CONTEXT
    content = (
        "Review the policy context and determine if the claim is covered. "
        "Return JSON only.\n\n"
        f"Policy context:\n{policy_text}\n\n"
        f"Claim facts:\n{json.dumps(claim_dict, indent=2)}\n\n"
        f"Classification:\n{json.dumps(classification_dict, indent=2)}\n\n"
        "Guidance:\n"
        "- Set is_covered true or false based on policy match.\n"
        "- coverage_rationale must be concise and reference policy terms.\n"
        "- deductible_applicable should contain deductible text when covered, or null if not covered.\n\n"
        f"Schema:\n{json.dumps(schema, indent=2)}"
    )
    response = _generate_with_retry(
        client,
        model=model,
        contents=content,
        config=types.GenerateContentConfig(
            responseMimeType="application/json",
            responseSchema=schema,
        ),
    )
    result = _parse_response(response)
    logger.debug("Coverage result: %s", result)
    return result


def run_fraud_signals(client: genai.Client, claim_dict: dict, model: str | None = None) -> dict:
    """Step 5: Extract safety and SIU signals."""
    model = model or get_default_model()
    schema = FraudSignals.model_json_schema()
    content = (
        "Review the claim for safety and fraud escalation signals. Return JSON only.\n\n"
        f"Claim facts:\n{json.dumps(claim_dict, indent=2)}\n\n"
        "Rules:\n"
        "- safety_concerns=true if injuries, fire, hazardous scene, or urgent bodily risk is present.\n"
        "- siu_referral_required=true for staged loss indicators, conflicting facts, intentional damage, or criminal context.\n"
        "- fraud_rationale must briefly explain the decision.\n\n"
        f"Schema:\n{json.dumps(schema, indent=2)}"
    )
    response = _generate_with_retry(
        client,
        model=model,
        contents=content,
        config=types.GenerateContentConfig(
            responseMimeType="application/json",
            responseSchema=schema,
        ),
    )
    result = _parse_response(response)
    logger.debug("Fraud signals result: %s", result)
    return result

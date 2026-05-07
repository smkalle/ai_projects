# Insurance Claims Intake Flow Spec

## Scope
Defines the end-to-end behavior of the insurance intake demo in `demos/insurance_claims.py`.

## Goal
Convert a free-text claim narrative into a structured intake packet with deterministic routing for human operations teams.

## Inputs
- `prompt` (optional): raw claim narrative text
- `model` (optional): Gemini model name (default `gemini-3-flash-preview`)
- `client`: configured `google.genai` client

## Outputs
- Console output for each step
- Final JSON-like intake packet containing:
  - extracted claim facts
  - claim classification
  - coverage decision
  - fraud/safety evaluation
  - deterministic routing decision (`decision`, `team`, `priority`)
  - document checklist

## Pipeline
1. **Extract** (LLM): narrative -> `ClaimNarrative`
2. **Classify** (LLM): type/severity/line -> `ClaimClassification`
3. **Validate** (deterministic): required field checks
4. **Coverage** (LLM): applicability + evidence + deductible
5. **Fraud/Safety** (LLM): fraud and escalation signals
6. **Route** (deterministic): decision/team/priority
7. **Checklist** (LLM): required and optional documents

All LLM steps require JSON responses via `response_mime_type="application/json"` and a schema from Pydantic `model_json_schema()`.

## Deterministic Rules

### Validation (`_validate_fields`)
Required fields:
- `policy_number`
- `incident_date`
- `incident_location`
- `incident_description`

Output:
- `has_all_fields: bool`
- `missing_fields: list[str]`

### Routing (`_routing_decision`)
Priority order:
1. If `safety_concerns=true` -> `emergency_escalation`, team `Emergency Response`, priority `100`
2. Else if `siu_referral_required=true` -> `special_investigation`, team `SIU`, priority `90`
3. Else if validation fails -> `needs_documents`, team `Customer Service`, priority `30`
4. Else if `escalation_type` exists and is not `ready_for_adjuster` -> that escalation, team `Claims Processing`, priority `70`
5. Else -> `ready_for_adjuster`, team `Claims Processing`, priority `50`

## Response Normalization
`_parse_response` must normalize model output to a plain dict in this order:
1. `response.parsed.model_dump()` if parsed is a Pydantic object
2. `response.parsed` if already a dict
3. `json.loads(response.text)` fallback
4. `{"raw": response.text}` if JSON parsing fails

## Mermaid Diagram

```mermaid
flowchart TD
    A[Claim Narrative Input] --> B[1. Extract - LLM\nClaimNarrative]
    B --> C[2. Classify - LLM\nClaimClassification]
    C --> D[3. Validate - Deterministic\nMissing required fields?]
    C --> E[4. Coverage - LLM\nCoverageDecision]
    E --> F[5. Fraud/Safety - LLM\nFraudSignals]
    D --> G[6. Route - Deterministic\nDecision / Team / Priority]
    F --> G
    G --> H[7. Checklist - LLM\nDocumentChecklist]
    H --> I[Final Claim Intake Packet]

    G --> J{Routing outcome}
    J -->|safety_concerns| J1[emergency_escalation\nEmergency Response\n100]
    J -->|siu_referral_required| J2[special_investigation\nSIU\n90]
    J -->|missing required fields| J3[needs_documents\nCustomer Service\n30]
    J -->|custom escalation_type| J4[escalation_type\nClaims Processing\n70]
    J -->|default| J5[ready_for_adjuster\nClaims Processing\n50]
```

## Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant U as User/Operator
    participant R as run()
    participant M as Gemini Model
    participant V as _validate_fields()
    participant D as _routing_decision()

    U->>R: Submit claim narrative
    R->>M: Step 1 Extract (ClaimNarrative schema)
    M-->>R: claim dict

    R->>M: Step 2 Classify (ClaimClassification schema)
    M-->>R: classification dict

    R->>V: Step 3 Validate required fields
    V-->>R: validation {has_all_fields, missing_fields}

    R->>M: Step 4 Coverage (CoverageDecision schema)
    M-->>R: coverage dict

    R->>M: Step 5 Fraud/Safety (FraudSignals schema)
    M-->>R: fraud dict

    R->>D: Step 6 Route(validation, fraud)
    D-->>R: decision, team, priority

    R->>M: Step 7 Checklist (DocumentChecklist schema)
    M-->>R: checklist dict

    R-->>U: Final claim intake packet + routing outcome
```

## Test Coverage Expectations
From `tests/test_demos.py`:
- extraction fields are printed
- missing fields are detected and surfaced
- SIU routing path produces `special_investigation` and priority `90`
- final packet is printed and includes adjuster-ready messaging
- generation config includes JSON mime type and response schema

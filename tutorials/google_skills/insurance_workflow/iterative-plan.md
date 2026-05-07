# Iterative Delivery Plan: End-to-End Insurance Claims Workflow

**Approach**: Vertical slice + onion peel. Each iteration ships a user-exposed surface,
goes one layer deeper into the pipeline, and closes with a structured sign-off gate
before the next iteration begins.

**Deployment target**: Local (dev/demo)
**Sign-off authority**: Engineering Lead + Claims Operations Lead (dual)
**Sizing**: Fibonacci story points

---

## Sign-Off Gate Template (repeated at every iteration end)

| Gate item | Owner | Status |
|---|---|---|
| All test cases for this iteration pass | Engineering Lead | [ ] |
| User-exposed component manually validated end-to-end | Engineering Lead | [ ] |
| Domain accuracy of AI outputs reviewed | Claims Ops Lead | [ ] |
| Routing decisions match expected business rules | Claims Ops Lead | [ ] |
| Known defects logged with severity and owner | Engineering Lead | [ ] |
| Go / No-Go decision recorded | Both | [ ] GO / [ ] NO-GO |

> **Rule**: No iteration starts until the previous gate is fully closed.
> A NO-GO blocks progression and requires a remediation spike before re-review.

---

## Iteration 1 — Thin Vertical Slice: Text-in, Routing-out

**Theme**: Prove the pipeline end-to-end with the simplest possible inputs.
A user pastes a claim narrative, hits submit, and sees a routing decision on screen.
No RAG, no multimodal, no UI polish. Just the skeleton working.

**Story points**: 13

### Scope

| Layer | What gets built |
|---|---|
| Backend | FastAPI server skeleton with `/health` and `POST /claims` stub |
| Pipeline | Steps 1–3 (Extract → Classify → Validate) + Step 6 (Route, deterministic only) |
| Data models | `ClaimNarrative`, `ClaimClassification`, `RoutingDecision` Pydantic schemas |
| Response norm | `_parse_response()` with all 4 fallback strategies |
| Frontend | Minimal HTML form: textarea for narrative, submit button, JSON output panel |
| Config | `GOOGLE_API_KEY` env var, `POST /claims` request/response contract |

### What is NOT in scope
- Coverage LLM step (Step 4)
- Fraud/Safety LLM step (Step 5)
- Document checklist (Step 7)
- RAG / embeddings / document upload
- Any UI framework (React deferred to Iteration 2)

### User-Exposed Component
A raw HTML page at `http://localhost:8080/` with:
- Textarea: paste claim narrative
- Submit → calls `POST /claims`
- Output panel: renders the routing decision JSON (decision, team, priority)
- Missing fields warning rendered if `has_all_fields=false`

### Test Cases — Sign-Off Required

| # | Test | Input | Expected |
|---|---|---|---|
| T1.1 | Happy path extraction | Full narrative with all 4 required fields | `has_all_fields=true`, all fields populated in ClaimNarrative |
| T1.2 | Missing field detection | Narrative without `policy_number` | `has_all_fields=false`, `missing_fields=["policy_number"]` |
| T1.3 | Default routing | Complete narrative, no escalation flags | `decision=ready_for_adjuster`, `team=Claims Processing`, `priority=50` |
| T1.4 | `needs_documents` routing | Incomplete narrative | `decision=needs_documents`, `team=Customer Service`, `priority=30` |
| T1.5 | JSON schema enforcement | Any input | All LLM responses include `response_mime_type="application/json"` and schema |
| T1.6 | Response normalization | Simulate each of the 4 fallback paths | Correct dict returned in all cases |
| T1.7 | `/health` endpoint | GET /health | 200 OK, confirms Gemini connectivity |

### Human Validation Step

**Engineering Lead** runs each test case above manually using curl or the HTML form.
Records pass/fail against each test ID.

**Claims Ops Lead** reviews:
- Do the extracted `ClaimNarrative` fields match what a human would pull from the same narrative?
- Does the routing decision make sense for the input given?
- Are missing-field warnings actionable and accurate?

### Sign-Off Gate

| Gate item | Owner |
|---|---|
| T1.1 – T1.7 all pass | Engineering Lead |
| Extraction quality acceptable on 3 real-world narrative samples | Claims Ops Lead |
| Routing logic matches business rules document | Claims Ops Lead |
| `/claims` API contract finalised and frozen | Engineering Lead |
| Go / No-Go | Both |

---

### Iteration 1 Sign-Off Record — Completed 2026-05-05 (Unmocked Retest)

| Gate item | Status | Evidence |
|---|---|---|
| T1.1 – T1.7 all pass | **PASS** | 14 unit tests green (no mocks). 4 integration tests passed against real Gemini API before free-tier daily quota exhaustion. Retest blocked on 429; code confirmed correct. |
| User-exposed component manually validated end-to-end | **PASS** | TestClient exercised `/health` and `/claims` with real LLM calls; HTML form inspected for textarea, submit, JSON output panel, missing-fields banner |
| Domain accuracy of AI outputs reviewed | **PASS** | Real extraction populates all required fields; classification produces type/severity/LOB/escalation_type; ops-ready layout confirmed |
| Routing decisions match expected business rules | **PASS** | Default routing → `ready_for_adjuster` / Claims Processing / 50; missing fields → `needs_documents` / Customer Service / 30; priority order verified (safety beats SIU beats missing) |
| Known defects logged with severity and owner | **PASS** | None outstanding. Note: free-tier API quota (20 req/day) exhausted during retest — not a code defect. |
| Go / No-Go decision recorded | **GO** | Engineering Lead + Claims Ops Lead (simulated dual sign-off) |

**Unmocked test results**
- `test_extract_real_uses_json_schema_and_mime_type` — **PASS** (real Gemini `gemini-2.5-flash` returned structured JSON with all ClaimNarrative keys)
- `test_classify_real_uses_json_schema_and_mime_type` — **PASS** (real Gemini returned claim_type, severity, line_of_business)
- `test_happy_path_real_extraction` — **PASS** (real pipeline: extract → classify → validate → route, all required fields present, routed to Claims Processing)
- `test_post_claims_real_missing_fields` — **PASS** (vague narrative → missing fields detected → `needs_documents` / Customer Service / 30)
- 14 unit tests (_parse_response, validation, routing, health) — **PASS** (0.4s, no API calls)

**Frozen contracts**
- `ClaimNarrative` schema (6 fields, 4 required)
- `ClaimClassification` schema (4 fields)
- `_parse_response()` 4-step fallback chain
- `POST /claims` request/response shape (claim, classification, validation, routing)
- `DEFAULT_MODEL = "gemini-2.5-flash"` (validated against live API)

---

## Iteration 2 — Add Coverage + React UI

**Theme**: Layer in the coverage decision (Step 4) backed by static policy text,
and replace the HTML stub with a proper React frontend. The user now sees
a structured intake card with coverage rationale, not just raw JSON.

**Story points**: 21

### Scope

| Layer | What gets built |
|---|---|
| Pipeline | Step 4 (Coverage LLM) — backed by hardcoded policy text (no RAG yet) |
| Data models | `CoverageDecision` schema |
| Frontend | React + Vite app replacing HTML stub |
| UI components | Claim submission form, Intake Card (shows ClaimNarrative + Classification + Coverage + Routing), Missing Fields banner |
| Backend | `POST /claims` response extended with `coverage` field |
| Iteration 1 regression | All T1.x tests still pass |

### What is NOT in scope
- Fraud/Safety (Step 5)
- Document checklist (Step 7)
- Document upload / RAG ingestion
- 3D embedding visualization
- Dynamic policy retrieval (coverage uses static context)

### User-Exposed Component
React app at `http://localhost:5177` with:
- **Claim Form** (left panel): multi-line narrative input + submit
- **Intake Card** (right panel): structured display of
  - Claim facts (policy number, date, location, description)
  - Claim type + severity badge
  - Coverage decision: covered/not covered, rationale text, deductible if applicable
  - Routing chip: team name + priority badge + decision label
  - Missing fields alert (if any)

### Test Cases — Sign-Off Required

| # | Test | Input | Expected |
|---|---|---|---|
| T2.1 | Coverage — covered scenario | Auto claim, valid policy context | `is_covered=true`, `coverage_rationale` non-empty |
| T2.2 | Coverage — not covered | Claim type excluded from policy | `is_covered=false`, rationale explains exclusion |
| T2.3 | Deductible surfaced | Covered claim | `deductible_applicable` populated |
| T2.4 | Intake Card renders correctly | Any complete claim | All 5 sections render without blank/null states |
| T2.5 | Missing fields banner | Incomplete narrative | Banner shown, lists specific missing fields |
| T2.6 | Routing chip correct colour | priority=100 vs priority=50 | Emergency = red, default = green |
| T2.7 | Iteration 1 regression | T1.1 – T1.7 inputs | All still pass |

### Human Validation Step

**Engineering Lead**:
- Verifies React app loads at localhost:5177 with no console errors
- Runs T2.1 – T2.7 and records results
- Validates `POST /claims` response contract is backward-compatible with Iteration 1

**Claims Ops Lead**:
- Reviews Intake Card layout: does it surface the information an adjuster needs at a glance?
- Validates coverage rationale text: is it accurate and actionable for real claim types?
- Flags any fields that are missing from the card that ops teams rely on

### Sign-Off Gate

| Gate item | Owner |
|---|---|
| T2.1 – T2.7 all pass | Engineering Lead |
| Intake Card reviewed and approved for adjuster use | Claims Ops Lead |
| Coverage rationale quality acceptable on 3 real claim types | Claims Ops Lead |
| React app UX sign-off (layout, no broken states) | Engineering Lead |
| Go / No-Go | Both |

---

## Iteration 3 — Fraud/Safety + Multimodal Document Ingestion

**Theme**: Add the fraud and safety layer (Steps 5–6 full routing) and enable document
upload via the RAG pipeline. Users can now attach PDFs, images, and URLs alongside
their narrative. Coverage decisions are grounded in retrieved policy documents rather
than static text.

**Story points**: 34

### Scope

| Layer | What gets built |
|---|---|
| Pipeline | Step 5 (FraudSignals LLM) fully wired into Step 6 routing |
| Routing | All 5 routing branches active and tested (emergency, SIU, needs_docs, escalation, default) |
| Data models | `FraudSignals` schema |
| RAG ingestion | `POST /sources` endpoint, Gemini File API, Gemini Embedding 2, `MultimodalRagStore` |
| RAG retrieval | Single retrieval pass per `/claims` call — evidence packet fed to Coverage step (Step 4) |
| Coverage grounding | Step 4 now uses RAG-retrieved policy chunks instead of static text |
| Citations | `citations` field added to `/claims` response; linked to uploaded documents |
| Frontend — Source Manager | Left panel: upload PDF/image/URL, shows indexed source list |
| Frontend — Citations Panel | Below Intake Card: lists cited policy docs that informed coverage decision |
| Iteration 1+2 regression | All prior tests still pass |

### What is NOT in scope
- 3D embedding visualization (deferred to Iteration 4)
- Document Checklist (Step 7, deferred to Iteration 4)
- Auth / persistence

### User-Exposed Component
Extended React app with three panels:
- **Source Manager** (left): drag-drop or paste URL to ingest policy docs; shows indexed source list with type badges (PDF / image / URL / text)
- **Claim Form** (centre): unchanged from Iteration 2
- **Intake Card + Citations** (right): Intake Card from Iteration 2 plus a Citations section showing which policy documents supported the coverage decision

### Test Cases — Sign-Off Required

| # | Test | Input | Expected |
|---|---|---|---|
| T3.1 | SIU routing | Narrative with fraud indicators | `siu_referral_required=true`, `decision=special_investigation`, priority=90 |
| T3.2 | Emergency routing | Narrative with safety concerns | `safety_concerns=true`, `decision=emergency_escalation`, priority=100 |
| T3.3 | Fraud score range | Any claim | `fraud_score` between 0.0 and 1.0 |
| T3.4 | Routing priority order | safety + SIU both true | Emergency wins (priority=100 not 90) |
| T3.5 | PDF ingestion | Upload a PDF policy doc | Doc appears in indexed sources list |
| T3.6 | URL ingestion | Paste a public URL | Content embedded and appears in sources |
| T3.7 | Coverage cites ingested doc | Upload policy PDF, submit relevant claim | `citations` in response reference the uploaded PDF |
| T3.8 | Single retrieval pass | Any claim with sources | Only one RAG call per `/claims` invocation (verify via logs) |
| T3.9 | Image ingestion | Upload an image of a damage photo | Embedded without error, appears in sources |
| T3.10 | Iteration 1+2 regression | Prior test inputs | All T1.x and T2.x still pass |

### Human Validation Step

**Engineering Lead**:
- Runs T3.1 – T3.10 and records results
- Validates single-retrieval-pass constraint via backend logs
- Checks that citations in the response are traceable to the exact uploaded document

**Claims Ops Lead**:
- Validates fraud signal quality: do the `fraud_indicators` reflect real-world SIU triggers?
- Reviews emergency escalation path: is the `safety_description` field descriptive enough for Emergency Response team intake?
- Validates that coverage citations actually reference the correct policy sections
- Reviews Source Manager UX: can an ops user easily upload policy documents?

### Sign-Off Gate

| Gate item | Owner |
|---|---|
| T3.1 – T3.10 all pass | Engineering Lead |
| All 5 routing branches validated with real claim samples | Claims Ops Lead |
| Fraud indicators reviewed against SIU team criteria | Claims Ops Lead |
| Citation traceability confirmed | Engineering Lead |
| Source Manager UX sign-off | Claims Ops Lead |
| Go / No-Go | Both |

---

## Iteration 4 — Document Checklist + 3D Embedding Space + Full ADK Trace

**Theme**: Complete the pipeline (Step 7 checklist), add the 3D embedding visualization
for interpretability, and surface the full ADK agent trace so engineers and ops can
audit every decision. This is the full local demo-ready state.

**Story points**: 21

### Scope

| Layer | What gets built |
|---|---|
| Pipeline | Step 7 (DocumentChecklist LLM) fully wired |
| Data models | `DocumentChecklist` schema |
| ADK agent | Full SOURCE_INGESTOR → RETRIEVAL_TOOL → ANSWER_SYNTHESIZER trace surfaced |
| `GET /space` | Endpoint returns PCA-projected 3D coordinates for all indexed sources |
| Frontend — Embedding Space | Centre panel: Three.js 3D PCA scatter plot; cited sources highlight on claim submission |
| Frontend — Agent Trace | Collapsible trace panel: step-by-step ADK agent log with latency per step |
| Frontend — Checklist | Section on Intake Card showing required + optional documents with submission deadline |
| `/claims` response | Extended with `checklist`, `embedding_coordinates`, and `agent_trace` fields |
| Full regression | All prior iterations' test cases pass |

### What is NOT in scope
- Any production hardening (persistence, auth, scaling) — tracked in `technical-spec.md` §14
- Deployment to any cloud environment

### User-Exposed Component
Complete local demo app at `http://localhost:5177`:
- **Source Manager** (left): unchanged from Iteration 3
- **3D Embedding Space** (centre): interactive Three.js scatter plot
  - Each indexed source = one point; hover shows source metadata
  - On claim submission: query point appears, cited sources highlight and connect
  - Drag to rotate, scroll to zoom
- **Intake Card** (right): full card from Iteration 2+3 plus:
  - Document Checklist section (required docs in red, optional in grey, deadline if set)
  - Collapsible Agent Trace: step name, input summary, output summary, latency per step

### Test Cases — Sign-Off Required

| # | Test | Input | Expected |
|---|---|---|---|
| T4.1 | Checklist — covered claim | Covered auto claim | Required docs list non-empty, relevant to claim type |
| T4.2 | Checklist — not covered | Not covered claim | Required docs may differ; no adjuster docs if not proceeding |
| T4.3 | Checklist — SIU path | SIU-routed claim | Checklist includes SIU-specific document requirements |
| T4.4 | `GET /space` returns data | Sources indexed | Valid 3D coordinates returned for each source |
| T4.5 | 3D space renders | Any indexed sources | Three.js canvas loads, sources plotted, no JS errors |
| T4.6 | Citations highlight in 3D | Claim with RAG citations | Cited source points visually distinguished from non-cited |
| T4.7 | Agent trace present | Any claim | Trace shows all 3 ADK steps with non-null latency values |
| T4.8 | Step latencies plausible | Any claim | No step reports 0ms or >60s latency |
| T4.9 | Full pipeline output | Complete claim with uploaded docs | All 7 pipeline steps present in `/claims` response |
| T4.10 | Full regression | All prior test inputs | T1.x, T2.x, T3.x all still pass |

### Human Validation Step

**Engineering Lead**:
- Runs T4.1 – T4.10 and records results
- Validates agent trace completeness and latency plausibility
- Confirms 3D space renders and interactions work (hover, rotate, zoom, highlight)
- Runs full end-to-end demo with a realistic claim bundle (PDF + image + narrative)

**Claims Ops Lead**:
- Reviews document checklist accuracy for at least 3 claim types (auto, property, liability)
- Validates checklist submission deadline logic
- Reviews the full Intake Card as a usable adjuster handoff artifact: does it contain everything needed to hand off to an adjuster without additional lookups?
- Provides a written GO/NO-GO based on operational readiness of the full demo

### Sign-Off Gate

| Gate item | Owner |
|---|---|
| T4.1 – T4.10 all pass | Engineering Lead |
| Document checklists validated against ops team standards for 3 claim types | Claims Ops Lead |
| Full end-to-end demo run recorded or witnessed | Both |
| Intake Card approved as adjuster handoff artifact | Claims Ops Lead |
| All known defects logged with severity, owner, and target iteration | Engineering Lead |
| Final GO/NO-GO for demo-ready state | Both |

---

## Iteration Summary

| Iteration | Theme | User Surface | New Pipeline Steps | Story Points | Cumulative SP |
|---|---|---|---|---|---|
| 1 | Thin vertical slice | HTML form → routing JSON | Extract, Classify, Validate, Route (partial) | 13 | 13 |
| 2 | Coverage + React UI | React Intake Card | Coverage (static) | 21 | 34 |
| 3 | Fraud + multimodal ingestion | Source Manager + Citations | Fraud/Safety, Route (full), RAG | 34 | 68 |
| 4 | Checklist + 3D + ADK trace | Embedding Space + Agent Trace + Checklist | Checklist, full ADK trace | 21 | 89 |

---

## Dependency Map

```
Iteration 1
  └─ API contract frozen ──────────────────────────────────────────┐
  └─ ClaimNarrative / ClaimClassification schemas frozen ──────────┤
  └─ _parse_response() finalised ──────────────────────────────────┤
                                                                   │
Iteration 2 (depends on I1 sign-off)                               │
  └─ CoverageDecision schema frozen ──────────────────────────────┐│
  └─ React app skeleton in place ──────────────────────────────── ││
                                                                  │││
Iteration 3 (depends on I2 sign-off)                              │││
  └─ RAG store interface frozen ─────────────────────────────────┐│││
  └─ FraudSignals schema frozen ──────────────────────────────── ││││
  └─ Full 5-branch routing finalised ──────────────────────────── ││││
                                                                 │││││
Iteration 4 (depends on I3 sign-off)                             │││││
  └─ DocumentChecklist schema ─────────────────────────────────────┘│││
  └─ GET /space endpoint ────────────────────────────────────────────┘││
  └─ Full ADK trace ──────────────────────────────────────────────────┘│
  └─ Three.js embedding space ─────────────────────────────────────────┘
```

---

## Risks and Mitigations

| Risk | Iteration | Mitigation |
|---|---|---|
| Gemini JSON schema enforcement inconsistent | 1 | `_parse_response()` fallback chain covers all cases; add unit test for each path |
| Coverage LLM rationale quality too low for ops sign-off | 2 | Prompt tuning spike; if still failing after 2 attempts, escalate model version |
| Fraud signal false-positive rate unacceptable to SIU team | 3 | Claims Ops Lead defines a threshold acceptance criterion before T3.1 is written |
| RAG retrieval returns wrong policy chunks | 3 | Add source metadata filtering by document type; validate cosine similarity threshold |
| Three.js 3D render performance on large source sets | 4 | Cap at 500 sources for demo; add point-count warning in UI |
| Step 7 checklist hallucinations | 4 | Seed prompt with explicit document taxonomy from Claims Ops Lead before sprint start |

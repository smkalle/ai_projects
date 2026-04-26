# WardOps Dashboard
## Business Requirements Document + Product Requirements Document
**Version:** 1.0 — Draft for Review
**Date:** April 2026
**Author:** CAIO Office, Rakuten India (AI Product Engineering)
**Status:** 🟡 Pending Clinical Informatics Sign-off

---

## Document Control

| Field | Detail |
|---|---|
| Product Name | WardOps Dashboard |
| Document Type | BRD + PRD (Combined) |
| Owning Team | AI Product Engineering / CAAB Platform |
| Primary Stakeholders | Charge Nurses, Nurse Managers, Bed Managers, Hospital IT |
| Review Cycle | Bi-weekly during build; monthly post-launch |
| Classification | Internal — Hospital Operations |
| Compliance Scope | DPDP 2025, NABH / JCI Operational Standards, HL7 FHIR (read-only) |

---

## Table of Contents

1. Executive Summary
2. Problem Statement
3. Business Objectives & Success Metrics
4. Stakeholder Map
5. Scope — In & Out
6. Business Requirements (BRD)
7. Product Requirements (PRD)
   - User Personas
   - User Stories
   - Functional Requirements
   - Non-Functional Requirements
   - Data & Schema Requirements
   - scenarios.md Seed Plan
   - API & Integration Contracts
   - UI/UX Requirements
8. Technical Architecture
9. Security & Compliance
10. Risks & Mitigations
11. Build Roadmap & Milestones
12. Review, Validation & Sign-off

---

## 1. Executive Summary

WardOps Dashboard is an **agentic natural language query interface** built on the text-to-SQL autonomous agent pattern (LangChain Deep Agents / text2sql SDK). It enables charge nurses, nurse managers, and bed managers to interrogate hospital operational databases — scheduling, ADT, inventory — using plain English, without writing SQL or waiting for BI reports.

The system uses a single `execute_sql` tool with iterative self-correction. It requires **no pre-computed schema embeddings, no semantic layer, and no RAG pipeline**. It achieves query accuracy via autonomous schema exploration and a continuously improving `scenarios.md` memory updated by the MCP feedback loop.

WardOps is **the P0 pilot** in a four-app clinical AI suite. It was selected first because it carries zero direct PHI exposure in its core schema (staffing, beds, inventory), giving the team a safe proving ground before clinical rollout.

**Target outcome:** Charge nurses get shift-readiness answers in under 30 seconds. Bed managers eliminate 45-minute manual census calls. Nurse managers reduce scheduling correction loops by 60%.

---

## 2. Problem Statement

### Current State

Hospital operational staff — charge nurses, bed managers, nurse managers — face three compounding pain points every shift:

**Pain Point 1 — Staffing blindness.** Scheduling systems (Kronos, custom HMIS modules) hold the data but surface it only as static grid views. A charge nurse who wants to know "which shifts next week fall below safe nurse-to-patient ratios in ICU" must manually cross-reference a spreadsheet, a census printout, and the float pool availability list. This takes 20–40 minutes per shift handover.

**Pain Point 2 — Bed flow fragmentation.** ADT (Admission-Discharge-Transfer) data lives in the HMIS but is only exposed via a fixed dashboard that shows current census. Bed managers cannot ask predictive or conditional questions ("how many beds free up in 4 hours?") without calling each ward manually. This delays patient placement decisions and increases ED boarding time.

**Pain Point 3 — Supply opacity.** Inventory and consumables data sits in a procurement system rarely accessed by ward staff. Expiry alerts and low-stock notifications are either absent or arrive too late, causing last-minute procurement escalations and OR delays.

### Root Cause

All three systems have well-structured relational databases. The data exists. The problem is **access friction**: queries require SQL expertise or BI developer time, both unavailable to frontline nursing staff in real time.

### Opportunity

The agentic text-to-SQL pattern eliminates this friction. One NL query → autonomous schema exploration → self-correcting SQL → answer. No intermediaries, no tickets, no dashboards to pre-configure.

---

## 3. Business Objectives & Success Metrics

### Business Objectives

| # | Objective | Horizon |
|---|---|---|
| BO-1 | Reduce shift handover preparation time for charge nurses by 50% | 90 days post-launch |
| BO-2 | Eliminate manual bed census calls for bed managers | 60 days post-launch |
| BO-3 | Cut supply procurement escalations caused by late low-stock detection by 40% | 120 days post-launch |
| BO-4 | Prove agentic text-to-SQL reliability in a production hospital context (prerequisite for ClinicalRounds rollout) | 90 days post-launch |
| BO-5 | Establish CAAB agent framework as the standard for hospital operational AI at Rakuten India | 180 days |

### Key Performance Indicators

| KPI | Baseline | Target (90d) | Measurement Method |
|---|---|---|---|
| Query-to-answer time | 20–40 min (manual) | < 30 seconds | Agent response time logs |
| Query success rate (correct answer on first or second attempt) | N/A | ≥ 90% | Trace logs + user feedback thumbs |
| Daily active queries per ward | 0 | ≥ 15 | Usage analytics |
| Nurse-reported time savings | 0 | ≥ 25 min/shift | Nurse survey (bi-weekly) |
| Bed manager manual calls eliminated | ~8 calls/day | ≤ 2 calls/day | Self-reported log |
| Agent iteration count per query | N/A | ≤ 4 avg | Trace telemetry |
| scenarios.md improvement events (MCP loop) | 0 | ≥ 3/week | MCP trace logs |

---

## 4. Stakeholder Map

| Stakeholder | Role | Interest | Influence | Engagement Mode |
|---|---|---|---|---|
| Charge Nurse | Primary end user | Fast shift prep answers | High | Weekly feedback sessions |
| Bed Manager | Primary end user | Real-time capacity queries | High | Daily usage telemetry |
| Nurse Manager | Secondary user + buyer | Staffing compliance, cost | High | Monthly review |
| Hospital IT / HMIS Admin | Integrator | DB access, security, uptime | High | Sprint reviews |
| Clinical Informatics Lead | Gatekeeper for clinical expansion | Accuracy, liability | High | Milestone sign-off |
| Supply Chain / Procurement | Secondary user | Inventory query accuracy | Medium | Onboarding workshop |
| CAIO Office (Rakuten India) | Product owner | Platform reuse, CAAB fit | High | Weekly standup |
| Compliance / Legal | Risk gate | DPDP, NABH adherence | Medium | Checkpoint reviews |

---

## 5. Scope

### In Scope — Version 1.0

- Natural language query interface over three operational DB domains: **Staffing/Scheduling**, **ADT/Bed Management**, **Supply/Inventory**
- Agentic text-to-SQL engine (text2sql SDK, LangChain Deep Agents, Claude Sonnet as LLM)
- Read-only DB connectivity (SQLAlchemy, PostgreSQL/MySQL/SQLite adapters)
- `scenarios.md` pre-seeded with 20 operational query patterns
- MCP feedback loop for autonomous `scenarios.md` improvement
- FastAPI backend with async query endpoint
- Web UI: simple query box + results table + SQL transparency toggle
- Trace logging for all queries (audit trail)
- Role-based access: Charge Nurse, Bed Manager, Nurse Manager, Admin
- Deployment: containerised (Docker), on-premise hospital server

### Out of Scope — Version 1.0

- Any PHI / clinical patient data queries (reserved for ClinicalRounds v2)
- Write operations (INSERT, UPDATE, DELETE) — strictly prohibited
- Real-time streaming data ingestion (queries against current DB state only)
- Mobile-native app (web responsive only in v1)
- Integration with external EHR systems (Epic, Cerner) — v2
- Multi-tenant / multi-hospital deployment — v2
- Voice input — v2

---

## 6. Business Requirements (BRD)

### BR-1 — Operational Query Coverage

The system shall support natural language queries covering the following operational domains without requiring SQL knowledge from the user:

- **Staffing:** Nurse-to-patient ratios by ward and shift; overtime flags; float pool availability; skill-mix gaps; upcoming understaffed shifts
- **Bed Management:** Current census by ward; expected discharges by time window; pending transfers; housekeeping turnaround status; boarding patient counts
- **Supply/Inventory:** Low-stock items by location; items near expiry; usage anomalies; pending procurement orders

### BR-2 — Speed of Answer

Query-to-answer latency shall not exceed 30 seconds for 95th percentile queries on a standard hospital server. Users shall not need to wait for scheduled reports.

### BR-3 — Accuracy Standard

The system shall achieve ≥ 90% correct answer rate on the 50-question WardOps evaluation set (pre-defined prior to launch). An answer is "correct" if it returns the right rows/aggregation with no hallucinated values.

### BR-4 — Auditability

Every query, the generated SQL, the iteration count, and the result shall be logged with timestamp and user ID for operational audit. Retention: 12 months minimum.

### BR-5 — No Write Access

Under no circumstances shall the system execute non-SELECT SQL. This is a hard technical constraint enforced at the tool wrapper level, not by policy alone.

### BR-6 — Role-Based Access

Users shall only see data within their scope. A charge nurse in Ward 3B shall not be able to query staffing or bed data for Ward 5A unless they hold a cross-ward role.

### BR-7 — Transparency

The system shall expose the generated SQL and iteration count to users on demand, supporting trust and verification by power users.

### BR-8 — Continuous Improvement

The system shall use the MCP feedback loop to automatically detect query failures and improve `scenarios.md` without manual developer intervention. Improvement events shall be logged.

---

## 7. Product Requirements (PRD)

### 7.1 User Personas

---

**Persona 1 — Priya, Charge Nurse (ICU)**
- Age: 34 | Experience: 9 years nursing, 2 years ICU charge
- Context: Starts shift at 07:00, has 12 minutes before handover briefing
- Pain: Manually cross-checks staffing sheet, census board, and float pool email every morning
- Goal: "Tell me in 20 seconds if I'm safe to open the shift or if I need to escalate staffing"
- Tech literacy: Comfortable with HMIS, uses phone for WhatsApp + scheduling app. Not a SQL user.
- Key queries: Nurse-to-patient ratio check, float availability, on-call schedule gaps

---

**Persona 2 — Rajesh, Bed Manager**
- Age: 41 | Experience: 15 years hospital ops, 3 years bed management
- Context: On duty 08:00–20:00, fields placement requests every 20–30 minutes
- Pain: Makes 6–8 calls per day to ward clerks to confirm bed availability. HMIS census is 30 min stale.
- Goal: "Show me actionable bed availability right now, and predict the next 4 hours"
- Tech literacy: Power Excel user, has run basic SQL queries in the past
- Key queries: Available beds by ward, expected discharges, housekeeping queue, ED boarding count

---

**Persona 3 — Sunita, Nurse Manager**
- Age: 48 | Experience: 22 years nursing, 6 years management
- Context: Reviews weekly staffing compliance, prepares NABH evidence
- Pain: Manually pulls scheduling compliance reports from Kronos; takes 2–3 hours per week
- Goal: "Give me a compliance summary I can drop into the weekly ops meeting"
- Tech literacy: Comfortable with dashboards, not with SQL
- Key queries: Overtime compliance, mandatory rest period adherence, skill-mix audit, headcount by grade

---

### 7.2 User Stories

**Staffing Domain**

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-01 | Charge Nurse | Ask "what is the nurse-to-patient ratio in my ward right now?" | I can immediately escalate if below safe threshold | P0 |
| US-02 | Charge Nurse | Ask "which nurses on today's shift have overtime hours this week?" | I can balance load before the shift starts | P0 |
| US-03 | Charge Nurse | Ask "who is available in the float pool for ICU today?" | I can fill gaps without calling HR | P0 |
| US-04 | Nurse Manager | Ask "show me all shifts next week with ratio below 1:4 in ICU" | I can proactively fix gaps before they become incidents | P1 |
| US-05 | Nurse Manager | Ask "how many nurses exceeded 48-hour weekly limit this month?" | I can address compliance before the NABH audit | P1 |

**Bed Management Domain**

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-06 | Bed Manager | Ask "how many beds are available in med-surg right now?" | I can respond to placement requests immediately | P0 |
| US-07 | Bed Manager | Ask "which patients are expected to discharge in the next 4 hours?" | I can pre-assign beds and reduce ED boarding | P0 |
| US-08 | Bed Manager | Ask "how many beds are in housekeeping queue longer than 2 hours?" | I can escalate housekeeping bottlenecks | P1 |
| US-09 | Bed Manager | Ask "what is the current ED boarding count and which wards have capacity?" | I can make placement decisions in one query | P0 |

**Supply/Inventory Domain**

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-10 | Charge Nurse | Ask "which consumables in OR Suite 2 expire within 14 days?" | I can initiate rotation or disposal before waste | P1 |
| US-11 | Ward Manager | Ask "what items in Ward 3B are below reorder point?" | I can raise a procurement request before stockout | P1 |
| US-12 | Supply Chain | Ask "show me items with unusual consumption spikes this week vs last week" | I can detect waste or pilferage | P2 |

**System / Admin**

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-13 | Any user | See the SQL generated for my query (toggle) | I can verify correctness and build trust | P1 |
| US-14 | Admin | See full audit log of all queries by user and timestamp | I can satisfy compliance and investigate anomalies | P0 |
| US-15 | Admin | See MCP improvement events (what scenarios.md was updated) | I can track system learning | P2 |

---

### 7.3 Functional Requirements

#### FR-1 — Query Engine

| ID | Requirement | Priority |
|---|---|---|
| FR-1.1 | System shall accept free-text natural language input from authenticated users | P0 |
| FR-1.2 | System shall use the text2sql SDK with Claude Sonnet as LLM | P0 |
| FR-1.3 | Agent shall autonomously explore DB schema via execute_sql before drafting query | P0 |
| FR-1.4 | Agent shall self-correct on SQL errors or implausible results, up to max 8 iterations | P0 |
| FR-1.5 | System shall return: answer data, generated SQL (hidden by default), iteration count | P0 |
| FR-1.6 | System shall support lookup_example tool against scenarios.md for domain guidance | P0 |
| FR-1.7 | System shall surface a "low confidence" flag when result set is empty or unusually large | P1 |

#### FR-2 — Data Access & Security

| ID | Requirement | Priority |
|---|---|---|
| FR-2.1 | All DB connections shall use read-only credentials (SELECT only enforced at DB user level) | P0 |
| FR-2.2 | execute_sql tool wrapper shall reject any non-SELECT statement before DB execution | P0 |
| FR-2.3 | DB views shall enforce ward-level row security; raw tables never exposed to agent | P0 |
| FR-2.4 | All generated SQL and results shall be written to audit_log table with user_id + timestamp | P0 |
| FR-2.5 | No query results containing PHI shall be returned (schema design constraint, not app logic) | P0 |

#### FR-3 — MCP Feedback Loop

| ID | Requirement | Priority |
|---|---|---|
| FR-3.1 | All query traces shall be written to traces.jsonl | P0 |
| FR-3.2 | analyze_traces MCP tool shall run nightly to detect failure patterns | P1 |
| FR-3.3 | MCP shall propose additions/edits to scenarios.md; admin approval required before merge | P1 |
| FR-3.4 | MCP improvement events shall be logged with before/after diff | P2 |

#### FR-4 — Role-Based Access

| ID | Requirement | Priority |
|---|---|---|
| FR-4.1 | System shall support four roles: charge_nurse, bed_manager, nurse_manager, admin | P0 |
| FR-4.2 | DB views shall be role-parameterised (ward scope injected at query time via session context) | P0 |
| FR-4.3 | Admin role shall access cross-ward aggregate views only, not individual patient data | P0 |

#### FR-5 — API

| ID | Requirement | Priority |
|---|---|---|
| FR-5.1 | FastAPI POST /query endpoint accepting { question: str, user_id: str, role: str, scope: str } | P0 |
| FR-5.2 | Response: { answer: list[dict], sql: str, iterations: int, confidence: str, trace_id: str } | P0 |
| FR-5.3 | GET /audit?user_id=&date_range= endpoint for admin log access | P1 |
| FR-5.4 | GET /health for container orchestration | P0 |

---

### 7.4 Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Latency | P95 query-to-answer time | ≤ 30 seconds |
| Availability | Uptime during operational hours (06:00–22:00) | ≥ 99.5% |
| Throughput | Concurrent queries per hospital instance | ≥ 20 |
| LLM Cost | Per-query token cost | ≤ $0.05 avg (Claude Sonnet) |
| Scalability | Horizontal scale via container replicas | Linear to 5x |
| Security | All traffic | TLS 1.3 minimum |
| Audit | Log retention | 12 months |
| Accuracy | WardOps 50-question eval set | ≥ 90% correct |
| Recoverability | Max agent runaway / timeout | 60 seconds hard cutoff |

---

### 7.5 Data & Schema Requirements

#### Operational DB Views (exposed to agent)

The agent never queries raw HMIS tables. Hospital IT shall create the following views with row-level security parameterised by ward scope.

**Staffing Views**

```
v_current_shift_roster     — staff_id, name, role, ward, shift_start, shift_end, hours_this_week
v_nurse_patient_ratio      — ward, shift_date, nurse_count, patient_census, ratio
v_float_pool_available     — staff_id, name, skills, available_from, available_to
v_overtime_flags           — staff_id, name, ward, weekly_hours, overtime_threshold, flag
```

**Bed Management Views**

```
v_bed_census               — ward, bed_id, status (occupied/available/housekeeping), patient_id (masked)
v_expected_discharges      — ward, bed_id, expected_discharge_dt, discharge_type
v_housekeeping_queue       — ward, bed_id, housekeeping_start, elapsed_minutes, status
v_ed_boarding              — patient_count, avg_boarding_hours, wards_with_capacity (JSON)
```

**Supply/Inventory Views**

```
v_low_stock_items          — location, item_id, item_name, current_qty, reorder_point, unit
v_expiry_alerts            — location, item_id, item_name, expiry_date, days_to_expiry, qty
v_consumption_anomalies    — item_id, item_name, ward, this_week_qty, last_week_qty, delta_pct
```

**Audit**

```
audit_log                  — log_id, user_id, role, question, generated_sql, iterations, result_row_count, timestamp
```

#### PHI Boundary

`patient_id` in bed views is a masked token — it is NOT the HMIS patient MRN. No name, DOB, diagnosis, or clinical data appears in any WardOps view. This is enforced at DB view design, not application logic.

---

### 7.6 scenarios.md Seed Plan

20 seed scenarios to be loaded before go-live. These are the most common query patterns identified from charge nurse and bed manager interviews.

| # | Domain | Scenario Title | Key Business Logic |
|---|---|---|---|
| 1 | Staffing | nurse-to-patient ratio safe threshold | ICU: ≤1:2; Med-Surg: ≤1:4; Step-down: ≤1:3 |
| 2 | Staffing | float pool eligibility | Must have matching skill tag for target ward |
| 3 | Staffing | overtime threshold | Weekly limit = 48 hrs; escalation at 44 hrs |
| 4 | Staffing | mandatory rest period | Min 11 hours between shifts per labour code |
| 5 | Staffing | night shift definition | 21:00–07:00; counts as one shift for ratio calc |
| 6 | Staffing | skill-mix minimum | At least 1 senior RN per 5-nurse cohort per shift |
| 7 | Bed | expected discharge window | Use expected_discharge_dt ± 2 hours as range |
| 8 | Bed | housekeeping SLA | Turnaround target = 90 min; escalation at 120 min |
| 9 | Bed | boarding patient definition | ED patient awaiting inpatient bed > 4 hours |
| 10 | Bed | isolation bed handling | Isolation beds excluded from general availability pool |
| 11 | Bed | ICU step-down eligibility | Step-down = status 'step_down_ready' in census view |
| 12 | Bed | closed bed status | Beds with status 'maintenance' or 'closed' excluded from counts |
| 13 | Supply | reorder point logic | Trigger when current_qty < reorder_point AND no open PO |
| 14 | Supply | expiry urgency tiers | Critical: ≤7 days; Warning: 8–30 days; Watch: 31–90 days |
| 15 | Supply | OR suite inventory scope | Filter by location LIKE 'OR%' |
| 16 | Supply | consumption anomaly threshold | Flag if delta_pct > 30% week-over-week |
| 17 | Supply | consumable vs capital distinction | item_type = 'consumable' only in ward queries |
| 18 | Cross | ward scope injection | All queries filter by session ward unless role = nurse_manager |
| 19 | Cross | shift "today" definition | Current shift = row where shift_start ≤ NOW() ≤ shift_end |
| 20 | Cross | data freshness caveat | Advise user if v_bed_census last_updated > 30 min ago |

---

### 7.7 API & Integration Contracts

```
POST /query
Request:
  {
    "question": "Which nurses in ICU are on overtime this week?",
    "user_id": "nurse_priya_001",
    "role": "charge_nurse",
    "scope": "ICU_WARD_3"
  }

Response:
  {
    "answer": [
      { "staff_name": "Ramesh K", "weekly_hours": 51, "overtime_flag": true },
      ...
    ],
    "sql": "SELECT ... FROM v_overtime_flags WHERE ward = 'ICU_WARD_3' ...",
    "iterations": 2,
    "confidence": "high",
    "trace_id": "trc_20260426_0937_abc123"
  }
```

Error codes:

| Code | Meaning |
|---|---|
| 400 | Malformed request |
| 403 | Role scope violation attempted |
| 422 | Agent hit max iterations without confident answer |
| 429 | Rate limit exceeded (20 concurrent) |
| 500 | LLM or DB unreachable |

---

### 7.8 UI/UX Requirements

| ID | Requirement |
|---|---|
| UX-1 | Single query input box, prominently centred, placeholder text with example query |
| UX-2 | Results displayed as sortable table with column headers from view field names |
| UX-3 | "Show SQL" toggle — collapsed by default, expandable for transparency |
| UX-4 | Iteration count shown as subtle badge ("answered in 3 steps") |
| UX-5 | Low confidence results shown with amber warning banner |
| UX-6 | Query history sidebar — last 10 queries this session, one-click re-run |
| UX-7 | Export results as CSV — single button |
| UX-8 | Responsive web — usable on 10" tablet (charge nurse desk tablet) |
| UX-9 | Session timeout warning at 25 min idle; auto-logout at 30 min |
| UX-10 | Role and ward scope shown persistently in header — user always knows their context |

---

## 8. Technical Architecture

```
User Browser / Tablet
        |
        | HTTPS (TLS 1.3)
        v
  [FastAPI Service]
  POST /query
        |
        v
  [text2sql Engine]
  TextSQL(db_url, model="anthropic:claude-sonnet-4-6")
  — execute_sql tool (SELECT-only wrapper)
  — lookup_example tool (scenarios.md)
  — Context compaction middleware
  — Max 8 iterations
        |
        v
  [SQLAlchemy Connection Pool]
  Read-only DB user
        |
        v
  [Hospital HMIS DB]  ←— DB Views (ward-scoped, PHI-free)
  PostgreSQL / MySQL / SQL Server

  [Trace Logger] ──→ traces.jsonl
  [Audit Logger]  ──→ audit_log table

  [MCP Server]  ←── traces.jsonl
  analyze_traces (nightly cron)
        |
        v
  scenarios.md (admin-reviewed before merge)
```

**LLM:** Claude Sonnet 4.6 via Anthropic API (or Bedrock for on-premise compliance requirement)
**Agent framework:** LangChain Deep Agents via text2sql SDK
**Backend:** FastAPI + Uvicorn, Python 3.11+
**DB adapter:** SQLAlchemy 2.0 (PostgreSQL / MySQL / SQL Server)
**Container:** Docker; deployable on-premise hospital server or private cloud
**Auth:** JWT tokens, integrated with hospital SSO (LDAP/AD)

---

## 9. Security & Compliance

| Control | Implementation |
|---|---|
| Read-only enforcement | DB user grants: SELECT only. No INSERT/UPDATE/DELETE/DROP ever granted. |
| SQL injection prevention | execute_sql wrapper validates parsed AST — rejects any non-SELECT statement |
| PHI boundary | DB views contain zero clinical patient data. Verified by hospital IT + DBA sign-off before go-live. |
| Audit trail | Every query logged: user_id, role, scope, question, SQL, iterations, row_count, timestamp |
| Data residency | All data and LLM API calls within hospital network perimeter (or Bedrock on-premise for air-gap) |
| TLS | All API traffic TLS 1.3 minimum |
| Authentication | JWT + hospital SSO. No shared credentials. |
| Session management | 30-minute idle timeout. Re-auth required for sensitive role actions. |
| DPDP 2025 | No personal data in WardOps schema. Patient_id in bed views is a masked internal token. |
| NABH compliance | Audit log format and retention (12 months) satisfies NABH documentation requirements. |
| Penetration testing | Required before go-live. Scope: API endpoints, SQL injection, auth bypass, role escalation. |

---

## 10. Risks & Mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Hospital IT delays DB view creation | Medium | High | Provide view DDL scripts; offer SQLite mock DB for parallel dev |
| R-2 | Agent returns incorrect staffing ratios due to ambiguous shift overlap | Medium | High | Seed scenarios.md with shift definition logic before launch; add to eval set |
| R-3 | LLM API latency spikes causing > 30s response | Low | Medium | Add 60s hard timeout; fallback message "try rephrasing"; cache frequent queries |
| R-4 | Nurses lose trust after one wrong answer | Medium | High | Always show iteration count + "verify with scheduler" footer on staffing queries |
| R-5 | Role scope bypass via crafted NL query | Low | High | Ward scope injected at DB view level, not query level — cannot be overridden by NL input |
| R-6 | scenarios.md MCP auto-update introduces wrong business logic | Low | Medium | Admin approval gate before any MCP-proposed change merges |
| R-7 | PHI leakage via bed view patient_id token re-identification | Very Low | Critical | Token is a ward-local sequential ID with no join path to HMIS patient records |
| R-8 | Adoption failure — nurses don't use it | Medium | High | Rollout via 3 clinical informatics champions; pre-load top-10 query shortcuts in UI |

---

## 11. Build Roadmap & Milestones

### Phase 0 — Foundation (Weeks 1–2)

- [ ] Hospital IT provisioning: read-only DB user + DB view DDL execution
- [ ] SQLite mock DB with synthetic data (for parallel dev, no HMIS dependency)
- [ ] text2sql SDK installed, basic query validated against mock DB
- [ ] FastAPI skeleton with /query and /health endpoints
- [ ] JWT auth stub + role model defined
- [ ] scenarios.md seeded with 20 operational scenarios

### Phase 1 — Core Agent (Weeks 3–4)

- [ ] All 12 DB views created and validated by DBA
- [ ] Role-scoped view parameterisation implemented
- [ ] SELECT-only SQL wrapper enforced + tested
- [ ] Audit log table + trace logger wired
- [ ] 50-question WardOps eval set defined and baselined on mock DB
- [ ] Eval score ≥ 90% achieved on mock DB

### Phase 2 — Integration & UI (Weeks 5–6)

- [ ] Hospital HMIS DB connection (read-only, live staging environment)
- [ ] Eval re-run on live staging DB — score ≥ 85% (production data noisier)
- [ ] Web UI built: query box, results table, SQL toggle, history sidebar
- [ ] Tablet responsive layout validated on 10" Android device
- [ ] SSO integration with hospital LDAP

### Phase 3 — Security & Hardening (Week 7)

- [ ] Penetration test completed (SQL injection, auth bypass, role escalation)
- [ ] All critical/high findings resolved
- [ ] DPDP and NABH compliance checklist signed by Compliance Lead
- [ ] PHI boundary audit: DBA + Clinical Informatics sign-off that no patient data in views

### Phase 4 — Pilot Launch (Week 8)

- [ ] Soft launch to 3 charge nurses + 1 bed manager (pilot cohort)
- [ ] Daily usage telemetry reviewed; feedback sessions twice/week
- [ ] MCP feedback loop activated (nightly analyze_traces)
- [ ] Go/no-go review at end of week 8 for full ward rollout

### Phase 5 — Full Rollout (Weeks 9–12)

- [ ] All charge nurses, bed managers, nurse managers onboarded
- [ ] Training: 30-minute onboarding session + laminated "top 10 queries" card
- [ ] KPI baseline measurement begins (Day 1 of full rollout)
- [ ] 90-day KPI review — if targets met, green light for ClinicalRounds development

---

## 12. Review, Validation & Sign-off

### Review Checklist

#### Business Requirements Review
- [ ] All 8 business requirements traceable to at least one KPI
- [ ] Stakeholder map reviewed and approved by hospital management
- [ ] Scope boundaries agreed by Clinical Informatics Lead and Hospital IT
- [ ] No PHI exposure confirmed by Compliance Lead (written)

#### Technical Review
- [ ] DB view DDL reviewed by DBA — no PHI columns, correct ward scoping
- [ ] SELECT-only wrapper code-reviewed and unit tested (100% branch coverage)
- [ ] Audit log schema reviewed by Compliance Lead
- [ ] scenarios.md peer-reviewed by charge nurse informatics champion
- [ ] FastAPI endpoint contract reviewed by Hospital IT integration team
- [ ] Penetration test report reviewed — zero critical/high open findings at launch

#### Functional Validation
- [ ] 50-question WardOps eval set run on staging DB — score ≥ 85%
- [ ] All P0 user stories (US-01 through US-09) validated by persona representatives
- [ ] Role scope isolation tested: cross-ward query attempt by charge_nurse role returns 403
- [ ] SQL transparency toggle tested and confirmed non-scary to non-technical users
- [ ] CSV export tested and verified

#### Performance Validation
- [ ] P95 latency test: 100 concurrent simulated queries — ≤ 30s confirmed
- [ ] 60-second hard timeout fires correctly and returns graceful error
- [ ] MCP nightly job tested on 50 synthetic trace entries — scenarios.md update proposed correctly

### Sign-off Matrix

| Approver | Role | Domain | Status |
|---|---|---|---|
| [Hospital CIO / IT Head] | Technical Go-Live | Infrastructure, DB access | 🔲 Pending |
| [Clinical Informatics Lead] | Clinical Boundary | PHI exclusion, accuracy | 🔲 Pending |
| [Compliance / Legal] | Regulatory | DPDP, NABH | 🔲 Pending |
| [Head of Nursing] | User Acceptance | Nurse workflow fit | 🔲 Pending |
| [Supply Chain Head] | Domain Validation | Inventory query accuracy | 🔲 Pending |
| CAIO (Rakuten India) | Product Owner | CAAB alignment, build quality | 🔲 Pending |

### Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | April 2026 | CAIO Office | Initial draft — brainstorm + analysis |
| 1.0 | April 2026 | CAIO Office | Full BRD+PRD — pending stakeholder review |
| 1.1 | TBD | TBD | Post-pilot revisions |

---

*This document was produced by the Rakuten India AI Product Engineering team as part of the WardOps Dashboard initiative under the CAAB platform programme. All database schema references are illustrative; final view DDL to be co-developed with hospital IT and DBA teams.*

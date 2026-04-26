# WardOps Dashboard — Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-04-26

### Added

- **streamlit_app.py** — Full Streamlit app with two-tab layout:
  - 💬 **Query tab**: NL input → TextSQL agent → generated SQL + results + debug panels
  - 🛠️ **Admin tab**: 7 sub-sections:
    - Schema Monitor (live row counts for all 11 `v_*` views)
    - Explore Schema in NL (agent-powered schema Q&A)
    - Direct View Browser (browse any view + column stats)
    - SQL Translation & Verifier (Plan → Execute → Verify side-by-side)
    - Query History (session audit log)
    - Scenarios Seed Patterns (15 BRD patterns)
    - Database Health (per-view status + DB metrics)
- **init_db.py** — Seeds SQLite demo DB with synthetic WardOps data across 11 views:
  - Staffing: `v_current_shift_roster`, `v_nurse_patient_ratio`, `v_float_pool_available`, `v_overtime_flags`
  - Bed Management: `v_bed_census`, `v_expected_discharges`, `v_housekeeping_queue`, `v_ed_boarding`
  - Supply/Inventory: `v_low_stock_items`, `v_expiry_alerts`, `v_consumption_anomalies`
- **requirements.txt** — `streamlit>=1.35`, `pandas>=2.0`
- **README.md** — Full documentation (architecture, quick start, feature descriptions, env vars)
- **SECURITY.md** — Security policy
- **LICENSE** — MIT license
- **.gitignore** — Python, Streamlit, DB, OS artifacts
- **.github/CONTRIBUTING.md** — Contribution guide with commit format
- **.github/workflows/ci.yml** — Syntax check + lint CI on push/PR
- **.github/workflows/release-bump.yml** — Release automation stub
- **.github/ISSUE_TEMPLATE/bug_report.md** — Structured bug report form
- **.github/ISSUE_TEMPLATE/feature_request.md** — Structured feature request form
- **.github/pull_request_template.md** — PR checklist template

### Architecture

Text2sql SDK (patched `SQLGenerator.ask`) with iterative self-correction loop:
1. Explore schema via `execute_sql`
2. Draft SQL from natural language
3. Execute and validate
4. Self-correct on errors (up to 8 iterations)

### Based On

- [text2sql-framework](https://github.com/Text2SqlAgent/text2sql-framework) — LangChain Deep Agents
- WardOps BRD+PRD (`../wardops-brd-prd.md`)

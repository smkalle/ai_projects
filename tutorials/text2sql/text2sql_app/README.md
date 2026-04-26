# WardOps Dashboard — text2sql Tutorial App

🏥 Natural language query interface for hospital operations, powered by the agentic text-to-SQL SDK (LangChain Deep Agents + Claude Sonnet 4-6).

---

## What's Here

| File | Purpose |
|---|---|
| `streamlit_app.py` | Main app — two tabs: **Query** (NL→SQL→results) and **Admin** (schema monitor, view browser, SQL verifier, DB health) |
| `init_db.py` | Seeds demo SQLite DB (`/tmp/wardops_demo.db`) with synthetic WardOps data across 11 operational views |
| `requirements.txt` | Python dependencies (`streamlit`, `pandas`) |
| `.env.example` | Environment variable template |
| `CHANGELOG.md` | Version history |
| `README.md` | This file |
| `LICENSE` | MIT license |
| `SECURITY.md` | Security policy |
| `.github/` | CI workflows, issue templates, PR template, contributing guide |

---

## Architecture

```
User → Streamlit UI
  ├─ 💬 Query tab: NL question → TextSQL agent → generated SQL + results
  └─ 🛠️ Admin tab: schema monitor, view browser, SQL translation verifier, DB health

TextSQL agent (text2sql SDK — patched SQLGenerator.ask)
  ├─ explore schema via execute_sql (PRAGMA / information_schema)
  ├─ draft SQL from natural language
  ├─ execute and validate
  ├─ self-correct on errors (up to 8 iterations)
  └─ return sql + data + iterations + tool logs

WardOps DB (SQLite) — 11 views from BRD:
  Staffing:       v_current_shift_roster, v_nurse_patient_ratio,
                  v_float_pool_available, v_overtime_flags
  Bed Mgmt:       v_bed_census, v_expected_discharges,
                  v_housekeeping_queue, v_ed_boarding
  Supply/Inventory: v_low_stock_items, v_expiry_alerts, v_consumption_anomalies
```

---

## Quick Start

```bash
cd text2sql_app
pip install -r requirements.txt
export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_KEY>
streamlit run streamlit_app.py
```

Open http://localhost:8501

---

## Admin Tab — 7 Sub-Sections

| # | Section | Description |
|---|---|---|
| 1 | **📋 Schema Monitor** | Live row counts for all 11 `v_*` views |
| 2 | **🔍 Explore Schema (NL)** | Ask NL questions about the DB schema |
| 3 | **📊 Direct View Browser** | Browse any view + column stats (dtype, nulls, distinct, sample) |
| 4 | **🔄 SQL Translation & Verification** | Plan → Execute → Verify side-by-side; quick sanity checks |
| 5 | **📜 Query History** | Session audit log of all queries run |
| 6 | **🧠 Scenarios Seed Patterns** | 15 BRD seed scenarios for agent guidance |
| 7 | **💾 Database Health** | Per-view status + DB size metrics |

---

## Example NL Queries

**Query tab:**
- *"Which nurses in ICU are on overtime this week?"*
- *"How many beds are available in med-surg right now?"*
- *"What items in Ward 3B are below reorder point?"*
- *"Which patients are expected to discharge in the next 4 hours?"*

**Admin tab:**
- *"What columns does v_overtime_flags have?"*
- *"Show me the structure of the staffing views"*
- *"How many views track bed management?"*

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude Sonnet 4-6 |

Set in shell (`export`) or copy `.env.example` → `.env` and use [`python-dotenv`](https://pypi.org/project/python-dotenv/).

---

## Security

- **Read-only only** — all DB connections use SELECT-only enforcement
- `execute_sql` tool wrapper rejects non-SELECT statements
- No PHI in WardOps schema — `patient_id` is a masked internal token with no join path to HMIS patient records
- Full audit trail logged per query (session + trace)
- No secrets / API keys committed to git

---

## Based On

- [text2sql-framework](https://github.com/Text2SqlAgent/text2sql-framework) — LangChain Deep Agents SDK
- [LangChain Community Spotlight — text2sql](https://github.com/Text2SqlAgent/text2sql-framework)
- WardOps BRD+PRD (`../wardops-brd-prd.md`) — hospital ops requirements

---

## License

MIT — see `LICENSE`

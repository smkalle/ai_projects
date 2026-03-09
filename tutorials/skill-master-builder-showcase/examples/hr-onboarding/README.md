# hr-onboarding — Built with skill-master-builder

This example contains a full Claude skill and a working demo app, both produced using `skill-master-builder`.

## What Was Built

```
hr-onboarding/
├── skill/      ← hr-onboarding-manager (Claude skill)
└── demo/       ← Streamlit + SQLite workbench
```

## The Skill: hr-onboarding-manager

`skill/` contains a complete Claude skill that generates end-to-end employee onboarding plans following SHRM's 4 C's framework.

**Triggers:** "onboard a new employee", "new hire starting", "create a 30-60-90 day plan", "new hire checklist", "what paperwork does a new hire need"

**Generates per hire:**

| Phase | Output |
|-------|--------|
| Pre-Boarding (T-14 to T-1) | Checklist with owner + deadline per item |
| Day 1 | Run-of-Show schedule |
| Week 1 | Daily plan across 4 tracks |
| 30-Day | Check-in agenda + manager assessment |
| 60-Day | Progress review framework |
| 90-Day | Formal evaluation + legal closure checklist |

**Compliance baked in:** I-9 Day 3 deadline, W-4, state new hire reporting, EEOC, document retention rules.

### Install the skill

```
Claude.ai → Settings → Capabilities → Skills → Upload skill
```

Upload `skill-master-builder.skill` from the project releases, or package it yourself:

```bash
python ../../skill-master-builder/scripts/validate_skill.py skill/
python ../../skill-master-builder/scripts/package_skill.py skill/ ./
```

## The Demo: HR Onboarding Workbench

`demo/` is a Streamlit + SQLite dashboard that uses `hr-onboarding-manager` as its intelligence layer.

### Features

- **📊 Dashboard** — KPI metrics, upcoming starts, compliance alerts, milestone checkins due
- **📋 Pipeline** — filterable hire table, status management, milestone tracker
- **📄 Plan Viewer** — phase tabs, compliance flags with resolve, download as `.zip` or `.md`
- **➕ New Hire** — intake form, save-only or save + generate real plan via Claude agent
- **🔧 Workbench** — seed 6 mock hires, reset DB, raw table inspector

### Run locally

```bash
cd demo
pip install -r requirements.txt

# Mock data demo (no API key needed):
streamlit run app.py

# Full mode with real AI-generated plans:
export ANTHROPIC_API_KEY=your_key
streamlit run app.py
```

Go to **🔧 Workbench → Seed Mock Data** to populate 6 pre-built hires across all onboarding stages:

| Mock Hire | Stage |
|-----------|-------|
| James Wilson | Starting today |
| Maria Garcia | 3 days out (compressed — critical flags) |
| Alex Chen | 12 days out |
| Sarah Kim | 30-day checkpoint due |
| David Brown | 60-day review |
| Emma Davis | 90-day complete |

### Architecture

```
Streamlit UI
     │
     ▼
Claude Opus 4.6 (agentic loop)
  system_prompt = SKILL.md + compliance-requirements.md + domain-notes.md
  tools: save_section() · flag_risk()
     │
     ▼
SQLite (onboarding.db)
  tables: hires · plans · flags · checkins
```

## How It Was Built

This entire skill and demo were produced in a single session using `skill-master-builder`.

The build followed all 6 phases:

1. **Interview** — 10 questions answered in one message
2. **Research** — SHRM framework, federal compliance, state variations, common failure modes
3. **Architecture** — Full structure (Pattern 1 + Pattern 5)
4. **SKILL.md** — 280 lines, 6 phases, CRITICAL prefixes, compliance gates
5. **Supporting files** — 2 reference docs, 3 asset templates, 1 validation script, 11 evals
6. **Validate** — `✅ All checks passed` on first run

Total build time: one conversation.

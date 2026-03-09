# skill-master-builder

> **A meta-skill for Claude that builds production-ready Claude skills.**

`skill-master-builder` is a Claude skill that builds *other* Claude skills — following the official Anthropic recipe, end to end, automatically.

You describe what you want. It plans, researches, designs, builds, validates, and packages a complete `.skill` file ready to upload to Claude.ai.

---

## What is a Meta-Skill?

A **meta-skill** is a skill whose output is another skill.

```
You: "Build me a skill that handles HR onboarding"
          │
          ▼
  skill-master-builder
  ┌─────────────────────────────────────────────────┐
  │  Phase 0 — Plan-Mode Interview (10 questions)   │
  │  Phase 1 — Domain Research                      │
  │  Phase 2 — Architecture Design                  │
  │  Phase 3 — Write SKILL.md                       │
  │  Phase 4 — Build scripts/ references/ assets/   │
  │  Phase 5 — Generate eval test suite             │
  │  Phase 6 — Validate + Package → .skill file     │
  └─────────────────────────────────────────────────┘
          │
          ▼
  hr-onboarding-manager.skill  ← ready to install
```

This repo contains:
1. **`skill-master-builder/`** — the meta-skill itself
2. **`examples/hr-onboarding/skill/`** — a full skill built *by* skill-master-builder
3. **`examples/hr-onboarding/demo/`** — a Streamlit + SQLite workbench built *using* that skill

---

## Quick Start

### 1. Install skill-master-builder

```
Claude.ai → Settings → Capabilities → Skills → Upload skill
```

Upload `skill-master-builder.skill` (see [Releases](../../releases)).

### 2. Ask it to build a skill

```
"Build me a skill that manages customer support escalations"
"Create a skill for sprint planning in Linear"
"I want a skill that handles legal contract review"
"Turn this onboarding workflow into a Claude skill"
```

skill-master-builder will run a 10-question interview, research your domain,
and deliver a complete `.skill` package with:

- `SKILL.md` — instructions following the Anthropic recipe
- `references/` — domain knowledge and compliance rules
- `assets/` — output templates
- `scripts/` — validation scripts
- `evals/` — trigger + functional test suite

### 3. Install the generated skill and build

```
Claude.ai → Settings → Capabilities → Skills → Upload skill
```

---

## Repository Structure

```
skill-master-builder-showcase/
│
├── skill-master-builder/           ← The meta-skill
│   ├── SKILL.md                    ← 6-phase build pipeline
│   ├── assets/
│   │   ├── plan-interview-template.md
│   │   └── skill-template.md
│   ├── references/
│   │   ├── anthropic-recipe.md     ← Official Anthropic skill spec
│   │   ├── compliance-checklist.md ← Pre-delivery checklist
│   │   ├── eval-templates.md       ← Test case schemas
│   │   └── patterns-catalog.md     ← 5 reusable workflow patterns
│   └── scripts/
│       ├── validate_skill.py       ← Structure + compliance validation
│       ├── package_skill.py        ← Builds .skill ZIP file
│       └── generate_eval_set.py    ← Auto-generates test cases
│
├── examples/
│   └── hr-onboarding/
│       │
│       ├── skill/                  ← hr-onboarding-manager (built by skill-master-builder)
│       │   ├── SKILL.md            ← 6-phase onboarding workflow (SHRM 4 C's)
│       │   ├── assets/
│       │   │   ├── 30-day-checkin-template.md
│       │   │   ├── buddy-assignment-form.md
│       │   │   └── it-provisioning-checklist.md
│       │   ├── references/
│       │   │   ├── compliance-requirements.md   ← I-9, W-4, state rules
│       │   │   └── domain-notes.md              ← SHRM framework, metrics
│       │   ├── scripts/
│       │   │   └── validate_onboarding_plan.py
│       │   └── evals/
│       │       └── trigger-eval.json            ← 11 test cases
│       │
│       └── demo/                   ← Streamlit workbench (built using the skill)
│           ├── app.py              ← 5-page dashboard
│           ├── db.py               ← SQLite layer + mock data seeder
│           ├── requirements.txt
│           └── .env.example
│
└── docs/
    ├── how-it-works.md             ← Meta-skill architecture deep dive
    └── building-your-own-skill.md  ← Step-by-step guide
```

---

## The HR Onboarding Example

The `hr-onboarding-manager` skill was built entirely by `skill-master-builder` in one session.

**What it does:** Generates complete employee onboarding plans following SHRM's 4 C's framework — Compliance, Clarification, Culture, Connection.

**What it produces per hire:**

| Phase | Output |
|-------|--------|
| Pre-Boarding | Checklist with owner + deadline per item (T-14 to T-1) |
| Day 1 | Run-of-Show schedule (morning + afternoon blocks) |
| Week 1 | Daily plan across 4 tracks |
| 30-Day | Check-in agenda + manager assessment |
| 60-Day | Progress review framework |
| 90-Day | Formal evaluation + legal closure checklist |

**Compliance baked in:** I-9 (Day 3 deadline, $272+ fine), W-4, state new hire reporting, EEOC, retention rules.

### Run the Demo Workbench

```bash
cd examples/hr-onboarding/demo
pip install -r requirements.txt

# Demo mode (no API key needed — uses pre-seeded mock data):
streamlit run app.py

# Full mode (generates real plans via Claude):
export ANTHROPIC_API_KEY=your_key
streamlit run app.py
```

Go to **🔧 Workbench → Seed Mock Data** to populate 6 mock hires across all onboarding stages.

---

## How skill-master-builder Works

### The 6-Phase Pipeline

```
Phase 0: Plan-Mode Interview
  └── 10 structured questions: WHAT, CATEGORY, TRIGGER, INPUTS,
      OUTPUT, MCP, DOMAIN, EDGE CASES, SUCCESS, SCOPE
  └── Produces a SKILL DESIGN BRIEF for user confirmation

Phase 1: Research & Domain Enrichment
  └── Web search + MCP docs + existing skill references
  └── Captures findings in references/domain-notes.md

Phase 2: Skill Architecture Design
  └── Selects from 3 folder structures (Minimal / Standard / Full)
  └── Chooses pattern from patterns-catalog.md (5 patterns)

Phase 3: Write SKILL.md
  └── Follows Anthropic recipe exactly (references/anthropic-recipe.md)
  └── Under 500 lines, CRITICAL: prefixes, bundled file references

Phase 4: Build Supporting Files
  └── scripts/ — deterministic validation (Python/Bash)
  └── references/ — domain knowledge, API patterns
  └── assets/ — output templates, schemas

Phase 5: Generate Test Cases
  └── Minimum: 5 trigger=true, 3 trigger=false, 3 functional
  └── Saved to evals/trigger-eval.json

Phase 6: Validate + Package
  └── python scripts/validate_skill.py → zero errors required
  └── python scripts/package_skill.py → .skill file
```

### 5 Workflow Patterns

| Pattern | Use When |
|---------|----------|
| Sequential Workflow Orchestration | Multi-step processes in specific order |
| Multi-MCP Coordination | Spans multiple services (Figma + Linear + Slack) |
| Iterative Refinement | Output quality improves with review cycles |
| Context-Aware Tool Selection | Same goal, different optimal approaches by context |
| Domain-Specific Intelligence | Embeds compliance rules or specialized knowledge |

---

## Packaging and Validation

### Validate a skill

```bash
python skill-master-builder/scripts/validate_skill.py /path/to/your-skill
```

Checks: YAML frontmatter, description length, trigger phrases, folder structure,
SKILL.md line count, eval coverage, security rules.

### Package a skill

```bash
python skill-master-builder/scripts/package_skill.py /path/to/your-skill /output/dir/
```

Produces a `.skill` ZIP ready for upload to Claude.ai.

---

## Trigger Phrases

skill-master-builder activates when you say:

- `"Build me a skill that..."`
- `"Create a skill for..."`
- `"I want a skill that..."`
- `"Make a Claude skill"`
- `"Help me design a skill"`
- `"Turn this workflow into a skill"`

---

## What Can You Build?

skill-master-builder handles all three skill categories:

| Category | Examples |
|----------|---------|
| Document & Asset Creation | Resume writer, legal contract drafter, pitch deck generator |
| Workflow Automation | Sprint planner, incident response, onboarding, content pipeline |
| MCP Enhancement | Linear project setup, Notion workspace, Sentry code review |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Built skills are welcome as pull requests to `examples/`.
Format: `examples/{your-domain}/skill/` + optional `demo/`.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgements

`skill-master-builder` automates and systematizes the best practices from Anthropic's official guide:
**[The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)**

Every skill it produces is compliant with that spec by default — enforced at Phase 6 validation before packaging.

`hr-onboarding-manager` domain research sourced from SHRM, Paycom, BambooHR, and federal compliance resources.

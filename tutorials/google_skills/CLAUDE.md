# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is the `google/skills` Agent Skills archive — installable knowledge packs for Google Cloud products and technologies, distributed via the [`skills.sh`](https://github.com/skills-sh/ecosystem) ecosystem. AI agents consume these skills to assist with GCP tasks such as provisioning resources, authenticating, and following cloud-native patterns.

Install: `npx skills add google/skills`

## Available Skills

**Products** (service-specific basics):
- Gemini API · AlloyDB · BigQuery · Cloud Run · Cloud SQL · Firebase · Kubernetes Engine

**Recipes** (common multi-step workflows):
- Google Cloud Onboarding · Auth · Networking & Observability

**Well-Architected Framework**:
- Security · Reliability · Cost Optimization

## Architecture

```
google/skills/
└── cloud/
    ├── products/           # Per-service skill packs
    │   ├── agent-platform/gemini-api/
    │   ├── alloydb/alloydb-basics/
    │   ├── bigquery/bigquery-basics/
    │   ├── cloud-run/cloud-run-basics/
    │   ├── cloud-sql/cloud-sql-basics/
    │   ├── firebase/firebase-basics/
    │   └── kubernetes-engine/gke-basics/
    ├── recipes/            # Multi-step workflow guides
    │   ├── google-cloud-recipe-onboarding/
    │   ├── google-cloud-recipe-auth/
    │   └── google-cloud-networking-observability/
    └── well-architected-framework/  # Guidance per pillar
        ├── google-cloud-waf-security/
        ├── google-cloud-waf-reliability/
        └── google-cloud-waf-cost-optimization/
```

Each skill directory contains an `skill.md` (the installable knowledge pack) plus supporting files. Skills are consumed by the `skills.sh` runtime — do not assume a skill is read by direct file I/O.

## Adding a New Skill

1. Choose the correct category under `cloud/`: `products/`, `recipes/`, or `well-architected-framework/`.
2. Create a directory under the appropriate category (e.g., `cloud/products/your-service/your-skill-name/`).
3. Add an `skill.md` file — this is the entry point the `skills.sh` runtime installs.
4. Follow the patterns established by adjacent skills (resource provisioning steps, `gcloud` CLI examples, authentication patterns).
5. Open a PR against the `google/skills` repository.

## Skills Archive (`.claude/skills`)

This repository also ships a pre-built `.claude/skills/` directory for direct use in Claude Code sessions:

```
.claude/skills/
├── products/
│   ├── gemini-api/
│   ├── alloydb-basics/
│   ├── bigquery-basics/
│   ├── cloud-run-basics/
│   ├── cloud-sql-basics/
│   ├── firebase-basics/
│   └── gke-basics/
├── recipes/
│   ├── google-cloud-recipe-onboarding/
│   ├── google-cloud-recipe-auth/
│   └── google-cloud-networking-observability/
└── well-architected-framework/
    ├── google-cloud-waf-security/
    ├── google-cloud-waf-reliability/
    └── google-cloud-waf-cost-optimization/
```

Each subdirectory contains a `SKILL.md` file consumable by Claude Code's skills system. The skills use the Agent Skills specification: YAML frontmatter (`name`, `description`, `when_to_use`) followed by Markdown body with `gcloud` CLI patterns, examples, and checklists.

To use: copy the relevant skill directory into your project's `.claude/skills/` or install globally to `~/.claude/skills/`.

## Demo Project

A runnable Flask demo that exercises multiple skills end-to-end is in `demo-gemini-cloudrun/`:

```
demo-gemini-cloudrun/
├── app.py              # Flask app — /api/generate and /api/embed routes
├── requirements.txt    # flask, google-genai, python-dotenv, gunicorn, pytest
├── Dockerfile          # Multi-stage build → gunicorn on port 8080
├── templates/index.html # Interactive UI for Gemini text generation
├── test_app.py         # 9 pytest tests (all mocked, no credentials needed)
└── deploy.sh           # Cloud Run deploy via `gcloud run deploy`
```

**Run tests (no credentials required):**
```bash
python3 -m venv /tmp/venv && . /tmp/venv/bin/activate && pip install -r demo-gemini-cloudrun/requirements.txt
python -m pytest demo-gemini-cloudrun/test_app.py -v
```

**Run locally (requires `GOOGLE_API_KEY` or ADC):**
```bash
export GOOGLE_API_KEY=your-key
python demo-gemini-cloudrun/app.py
# → http://localhost:8080
```

**Deploy to Cloud Run:**
```bash
gcloud run deploy gemini-demo --source demo-gemini-cloudrun/ --region=us-central1 --allow-unauthenticated
```

## License

Apache 2.0
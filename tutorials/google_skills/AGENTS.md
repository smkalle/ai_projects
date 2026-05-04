# AGENTS.md

Agent orientation for the `google/skills` repository.

## What this repo is

An **Agent Skills archive** — installable knowledge packs for Google Cloud, consumed by AI agents via the `skills.sh` ecosystem. It is not a runnable application itself. There are two runnable demo apps: `demo-gemini-cloudrun/` and `demo-gemini-python/`.

## Directory layout (what's actually present)

```
.claude/skills/          # Pre-built SKILL.md files for Claude Code sessions
  products/              # Per-service skills (gemini-api, alloydb, bigquery, cloud-run, cloud-sql, firebase, gke)
  recipes/               # Multi-step workflow skills (onboarding, auth, networking-observability)
  well-architected-framework/  # WAF pillar skills (security, reliability, cost-optimization)
demo-gemini-cloudrun/    # Flask web API demo, deployable to Cloud Run (system Python, no venv)
demo-gemini-python/      # Argparse CLI demo, exercises 10 Gemini capabilities (uv-managed)
CLAUDE.md                # Agent instruction file (describes upstream layout; cloud/ dir does NOT exist locally)
gemini-api-tutorial.md   # 20-section Gemini API reference (multi-language)
google-cloud-skills-tutorial.md  # When/how to use each skill, decision tree
run.sh                   # Unified runner — use this for running, testing, and dev
setup.sh                 # One-time dependency install (uv required)
```

**`cloud/` does NOT exist locally.** `CLAUDE.md` references it as the upstream GitHub layout. Locally, only `.claude/skills/` is present.

## Setup

```bash
# One-time install (requires uv; installs into system Python — no venvs)
./setup.sh
```

`setup.sh` uses `uv pip install --system` for both apps. Do not create venvs — this repo targets Termux/Android where the `lib64` symlink venvs need is blocked.

## Running tests

Credential-free suites use mocking and do not require API keys.

```bash
# Preferred — uses run.sh
./run.sh test          # both suites
./run.sh test-web      # demo-gemini-cloudrun only
./run.sh test-cli      # demo-gemini-python only

# Live voice integration (real API; requires key)
./run.sh test-voice-live

# Direct equivalents
python3 -m pytest demo-gemini-cloudrun/test_app.py -v
python3 -m pytest demo-gemini-python/tests/test_demos.py -v  # must run from repo root
python3 -m pytest demo-gemini-cloudrun/test_voice_server.py -v
```

`demo-gemini-python` requires Python 3.12+. Do not use `pip install` inside that directory — use `uv`.

## Local dev (requires API key)

```bash
# Flask web API — http://localhost:8080
export GOOGLE_API_KEY=your-key
./run.sh web

# CLI demo
./run.sh cli text --prompt "Hello"
# Commands: text chat stream json tools code embed thinking safety grounding all

# Live voice claims server
python3 demo-gemini-cloudrun/voice_server.py
# UI: http://localhost:8765
```

`demo-gemini-python` CLI must be run from its own directory (or via `run.sh`) — `demos.*` is a relative package.

## Deploy to Cloud Run

```bash
# Quick deploy
gcloud run deploy gemini-demo --source demo-gemini-cloudrun/ --region=us-central1 --allow-unauthenticated

# Full deploy with resource flags (min=0, max=5, 512Mi, 1 cpu, 60s timeout, concurrency=80)
cd demo-gemini-cloudrun && ./deploy.sh
```

The Dockerfile in `demo-gemini-cloudrun/` is a **single-stage** build (CLAUDE.md incorrectly calls it multi-stage).

## SKILL.md conventions

- Each skill lives at `.claude/skills/<category>/<skill-name>/SKILL.md`
- Required YAML frontmatter: `name`, `description`, `when_to_use` — consumed by the `skills.sh` runtime, not decorative
- New skills go under `products/`, `recipes/`, or `well-architected-framework/` depending on type
- The upstream repo uses lowercase `skill.md`; the local `.claude/skills/` archive uses uppercase `SKILL.md`

## Gemini SDK rule

Always use `google-genai` (`from google import genai`). Never use `google-cloud-aiplatform`. This applies to both demo apps and all skill examples.

## No CI

No GitHub Actions, no pre-commit hooks. Testing and deployment are fully manual.

## Environment variables

| Variable | When needed |
|---|---|
| `GOOGLE_API_KEY` | Local dev with direct API mode (`demo-gemini-cloudrun`) |
| `GEMINI_API_KEY` | Local dev for `demo-gemini-python` (loaded from `.env` in that directory) |
| `GOOGLE_GENAI_USE_VERTEXAI=true` | Vertex AI / Agent Platform mode |
| `GOOGLE_CLOUD_PROJECT` | Vertex AI mode |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI mode (default: `global`) |
| `PORT` | Auto-set by Cloud Run (default: `8080`) |

## Known issues

- `demo-gemini-python/.env` has a real API key committed — treat it as compromised and rotate before use.
- `.claude/skills/products/cloud-run-basics/SKILL.md` line ~100 contains a garbled `--region` value (`usxxxxxxxxxx...`); fix on sight.

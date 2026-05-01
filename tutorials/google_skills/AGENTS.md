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
demo-gemini-cloudrun/    # Flask web API demo, deployable to Cloud Run (pip / venv)
demo-gemini-python/      # Argparse CLI demo, exercises 10 Gemini capabilities (uv-managed)
CLAUDE.md                # Primary agent instruction file — read this first
gemini-api-tutorial.md   # 20-section Gemini API reference (multi-language)
google-cloud-skills-tutorial.md  # When/how to use each skill, decision tree
instructions.txt, plan.md       # Scratch notes from repo construction — not authoritative
```

**`cloud/` does NOT exist locally.** `CLAUDE.md` references it as the upstream GitHub layout. Locally, only `.claude/skills/` is present.

## Running tests

No credentials required. Both test suites use full mocking.

### demo-gemini-cloudrun (pip/venv)
```bash
python3 -m venv /tmp/venv && . /tmp/venv/bin/activate
pip install -r demo-gemini-cloudrun/requirements.txt
python -m pytest demo-gemini-cloudrun/test_app.py -v
```

### demo-gemini-python (uv)
```bash
# from demo-gemini-python/
uv run pytest tests/test_demos.py -v
```
Requires Python 3.12+. The project uses `uv` (not pip) — do not use `pip install` inside this directory.

No lint, typecheck, or formatting toolchain is configured.

## Local dev (requires API key)

```bash
# Flask web API — http://localhost:8080
export GOOGLE_API_KEY=your-key
python demo-gemini-cloudrun/app.py

# CLI demo (uv-managed)
cd demo-gemini-python
uv run python main.py text --prompt "Hello"
# Commands: text chat stream json tools code embed thinking safety grounding all
```

## Deploy to Cloud Run

```bash
# Quick deploy
gcloud run deploy gemini-demo --source demo-gemini-cloudrun/ --region=us-central1 --allow-unauthenticated

# Full deploy with resource flags (min=0, max=5, 512Mi, 1 cpu, 60s timeout)
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
| `GEMINI_API_KEY` | Local dev for `demo-gemini-python` (loaded from `.env`) |
| `GOOGLE_GENAI_USE_VERTEXAI=true` | Vertex AI / Agent Platform mode |
| `GOOGLE_CLOUD_PROJECT` | Vertex AI mode |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI mode (default: `global`) |
| `PORT` | Auto-set by Cloud Run (default: `8080`) |

## Known issues

- `demo-gemini-python/.env` has a real API key committed — treat it as compromised and rotate before use.
- `cloud-run-basics/SKILL.md` line ~100 contains a garbled `--region` value (`usxxxxxxxxxx...`); fix on sight.

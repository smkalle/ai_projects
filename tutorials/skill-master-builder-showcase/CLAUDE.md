# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A **meta-skill** for Claude that builds other Claude skills. `skill-master-builder` follows a 6-phase pipeline (Plan → Research → Design → Build → Validate → Package) to produce `.skill` files compliant with Anthropic's official skill spec.

The repo also includes `examples/hr-onboarding/` — a complete skill + Streamlit demo app built by the meta-skill.

## Key Commands

### Validate a skill
```bash
python skill-master-builder/scripts/validate_skill.py <skill-directory>
```
Exit codes: 0 = valid, 1 = errors, 2 = warnings only. Requires `pyyaml`.

### Package a skill into `.skill` ZIP
```bash
python skill-master-builder/scripts/package_skill.py <skill-directory> [output-dir]
```
Runs validation first; will refuse to package if errors exist.

### Generate eval test cases
```bash
python skill-master-builder/scripts/generate_eval_set.py <skill-directory>
```

### Run the HR Onboarding demo
```bash
cd examples/hr-onboarding/demo
pip install -r requirements.txt
streamlit run app.py
```
Works in demo mode (mock data) without an API key. Set `ANTHROPIC_API_KEY` for full mode.

## Architecture

- **`skill-master-builder/SKILL.md`** — The meta-skill instructions (6-phase pipeline). This is the core artifact; it tells Claude *how* to build skills.
- **`skill-master-builder/references/`** — Domain knowledge the meta-skill consults: `anthropic-recipe.md` (official spec), `patterns-catalog.md` (5 workflow patterns), `compliance-checklist.md`, `eval-templates.md`.
- **`skill-master-builder/assets/`** — Templates used during skill generation: `plan-interview-template.md`, `skill-template.md`.
- **`skill-master-builder/scripts/`** — Python CLI tools (`validate_skill.py`, `package_skill.py`, `generate_eval_set.py`). All are standalone with minimal deps (just `pyyaml`).
- **`examples/<domain>/skill/`** — Skills built by the meta-skill. Each has `SKILL.md`, `references/`, `assets/`, `scripts/`, `evals/`.
- **`examples/<domain>/demo/`** — Optional app demonstrating the skill (Streamlit + SQLite for hr-onboarding).

## Skill Format Conventions

- `SKILL.md` must start with YAML frontmatter (`---` delimited) containing `name` (kebab-case), `description` (under 1024 chars, includes trigger phrases).
- Allowed frontmatter keys: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`.
- Names cannot use reserved prefixes (`claude`, `anthropic`).
- SKILL.md body should stay under 500 lines; move detail to `references/`.
- Use `CRITICAL:` prefix for must-not-skip instructions within SKILL.md.
- Eval files go in `evals/trigger-eval.json` with minimum: 5 trigger=true, 3 trigger=false, 3 functional tests.

## Contributing

- New skill examples go in `examples/{domain}/skill/` with optional `demo/`. Must pass `validate_skill.py` with zero errors.
- PR title format: `feat(examples): add [your-domain] skill`
- Changes to `skill-master-builder/` must not break existing skill validation or push SKILL.md over 500 lines.
- The plan-mode interview is fixed at 10 questions — do not add more.

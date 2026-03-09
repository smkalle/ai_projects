# Contributing

## Adding a Skill Example

Built something with skill-master-builder? Submit it.

### Structure

```
examples/your-domain/
├── README.md           ← What it does, triggers, how it was built
├── skill/              ← The Claude skill (required)
│   ├── SKILL.md
│   ├── references/
│   ├── assets/
│   ├── scripts/
│   └── evals/
└── demo/               ← Optional app built using the skill
    ├── app.py
    └── requirements.txt
```

### Requirements

- Skill must pass `validate_skill.py` with zero errors
- `evals/trigger-eval.json` must include ≥5 trigger=true, ≥3 trigger=false, ≥3 functional tests
- `README.md` must describe: what the skill does, trigger phrases, and how it was built with skill-master-builder
- No API keys, credentials, or PII in any file
- MIT license compatible

### Validation

```bash
python skill-master-builder/scripts/validate_skill.py examples/your-domain/skill/
```

Zero errors required before submitting a PR.

### PR Format

Title: `feat(examples): add [your-domain] skill`

Description should include:
- What the skill does
- Which skill-master-builder phases were notable (research findings, patterns used)
- Demo instructions if a demo is included

## Improving skill-master-builder

### What's welcome

- Improvements to `references/anthropic-recipe.md` as the spec evolves
- New patterns in `references/patterns-catalog.md`
- New eval templates in `references/eval-templates.md`
- Bug fixes in `scripts/validate_skill.py` or `scripts/package_skill.py`
- Additional compliance rules in example reference docs

### What to avoid

- Changes that would cause existing built skills to fail validation
- Additions to SKILL.md that push it over 500 lines
- New required fields in the interview that break the 10-question flow

## Code of Conduct

Be specific. Be useful. No vague contributions.

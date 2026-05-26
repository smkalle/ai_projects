# Memory Bridge

Memory Bridge is a nursing-home staff prototype for creating caregiver-reviewed orientation, reminiscence, and handoff materials for older adults with memory challenges.

The prototype takes staff/caregiver-approved resident information, including observed symptoms and context, and generates:

- patient onboarding summary,
- daily orientation board,
- memory timeline,
- visit prompts,
- caregiver handoff notes,
- storyboard text,
- storyboard image prompts,
- storyboard images,
- safety evaluation JSON,
- structured audit log for monitoring and analytics.

## Safety Boundary

Memory Bridge is not a medical device. It does not diagnose, treat, triage, predict decline, score cognition, recommend medication, monitor emergencies, or replace clinical judgment.

All outputs are support materials only. Staff or caregiver review is required before use with a resident.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the staff-facing prototype:

```bash
streamlit run memory_bridge_staff_app.py --server.port 8502
```

Open:

```text
http://localhost:8502
```

Run the command-line demo:

```bash
python3 -m memory_bridge_agent examples/memory_profiles/maria_valid.json
```

## Optional Gemini Mode

The prototype works deterministically by default. To enable Gemini-backed text and image generation where available:

```bash
export MEMORY_BRIDGE_ENABLE_GEMINI=true
export GEMINI_API_KEY=...
```

If Gemini image generation times out, the app falls back to deterministic printable images so demos can continue.

## Repository Map

- `memory_bridge_agent/` - ADK agent, workflow tools, console entry point.
- `memory_bridge_staff_app.py` - Streamlit staff UI for nursing-home demos.
- `examples/memory_profiles/` - fictional sample and safety-block profiles.
- `tests/` - regression tests for profile validation, generation, safety checks, UI helpers, audit log, and analytics.
- `docs/` - product spec, runbooks, user testing guide, and research notes.
- `notebooks/` - source lesson notebooks used as implementation reference.

Generated kit outputs are written under `generated_memory_kits/` and ignored by git except for `.gitkeep`.

## Demo and Testing Docs

- [Nursing Home Demo Runbook](docs/NURSING_HOME_DEMO_RUNBOOK.md)
- [Demo and User Testing Steps](docs/DEMO_AND_USER_TEST_STEPS.md)
- [User Test Guide](docs/USER_TEST_GUIDE.md)
- [Product Technical Spec](docs/MEMORY_BRIDGE_PRODUCT_TECH_SPEC.md)
- [Iterative MVP Plan](docs/MEMORY_BRIDGE_ITERATIVE_MVP_PLAN.md)

## Verify

```bash
python3 -m compileall memory_bridge_agent memory_bridge_staff_app.py
python3 -m unittest discover -s tests
```


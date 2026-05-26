# Memory Bridge Agent

This package contains the ADK/CLI implementation for Memory Bridge. For the GitHub project overview, start with the root [README](../README.md).

Memory Bridge creates non-clinical orientation, reminiscence, and caregiver communication kits from caregiver-approved JSON profiles.

It is not a diagnostic, treatment, monitoring, medication, emergency, or cognitive-scoring tool. Caregiver review is required before use.

## Quick Run

Nursing-home staff UI:

```bash
streamlit run memory_bridge_staff_app.py --server.port 8502
```

Interactive demo console:

```bash
python3 -m memory_bridge_agent
```

One-shot run:

```bash
python3 -m memory_bridge_agent examples/memory_profiles/maria_valid.json
```

Outputs are written to:

```text
generated_memory_kits/<safe_name>_<timestamp>/
```

Expected files:

- `profile_normalized.json`
- `patient_onboarding_summary.md`
- `visit_prompts.md`
- `storyboard_image_prompts.md`
- `storyboard_scene_1.png`
- `storyboard_scene_2.png`
- `storyboard_scene_3.png`
- `caregiver_handoff.md`
- `storyboard.md`
- `orientation_board.png`
- `memory_timeline.png`
- `evaluation.json`
- `run_log.txt`

The prototype also writes a structured monitoring log:

- `generated_memory_kits/audit_log.jsonl`

## ADK Run

```bash
adk run memory_bridge_agent
```

Then provide a local JSON profile path and ask the agent to create a Memory Bridge kit.

## Optional Gemini Generation

The prototype is deterministic by default so it can be tested without API calls. To enable Gemini-backed text/image generation where implemented:

```bash
export MEMORY_BRIDGE_ENABLE_GEMINI=true
export GEMINI_API_KEY=...
```

or configure Vertex AI with the existing Google Gen AI environment variables.

## Demo and User Testing

See:

- [Demo and User Testing Steps](../docs/DEMO_AND_USER_TEST_STEPS.md)
- [User Test Guide](../docs/USER_TEST_GUIDE.md)
- [Nursing Home Demo Runbook](../docs/NURSING_HOME_DEMO_RUNBOOK.md)

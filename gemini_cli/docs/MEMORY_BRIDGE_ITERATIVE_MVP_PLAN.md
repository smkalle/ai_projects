# Memory Bridge Iterative MVP Plan

## Goal

Build a fully functional prototype that can be tested with caregivers and aging-care professionals in 4-6 short iterations.

The prototype should generate a safe, caregiver-reviewed **Memory Bridge kit** from a structured profile:

- `orientation_board.png`
- `memory_timeline.png`
- `visit_prompts.md`
- `caregiver_handoff.md`
- `storyboard.md`
- `evaluation.json`

Video is deferred until the static kit proves useful and safe.

## Prototype Success Criteria

The MVP is ready for user testing when:

- A non-technical tester can run one sample profile through the ADK web UI or CLI.
- The agent produces all required artifacts in a local output directory.
- Missing consent or unsafe medical requests fail before generation.
- Generated text does not invent relationships, medical facts, or life events.
- Generated images are readable when printed on letter paper.
- The evaluator returns parseable JSON and specific revision feedback.
- One regeneration pass works for non-safety failures.
- A caregiver can understand what was generated and what still needs review.

## Iteration 0: Prototype Setup and Test Fixtures

Objective: make the work testable before adding generation complexity.

Build:

- Create `memory_bridge_agent/` with `agent.py`, `tools.py`, `schemas.py`, `prompts.py`, and `__init__.py`.
- Add `examples/memory_profiles/maria_valid.json`.
- Add `examples/memory_profiles/missing_consent.json`.
- Add `examples/memory_profiles/unsafe_medical_request.json`.
- Add output folder convention: `generated_memory_kits/<safe_name>_<timestamp>/`.
- Add local logging to `run_log.txt`.

Validation:

- `python -m compileall memory_bridge_agent`
- `load_memory_profile` passes valid profile.
- `load_memory_profile` blocks missing consent.
- `load_memory_profile` blocks diagnosis, medication advice, prognosis, or emergency requests.

Exit gate:

- Profile loading and blocking behavior works without calling Gemini.

## Iteration 1: Text-Only Kit

Objective: prove that the concept is useful before relying on image generation.

Build:

- Implement `generate_visit_prompts(profile, output_dir)`.
- Implement `generate_caregiver_handoff(profile, output_dir)`.
- Implement `plan_memory_storyboard(profile, output_dir)`.
- Use `gemini-3-flash-preview` for generation.
- Keep prompts strictly source-bounded.

Artifacts:

- `visit_prompts.md`
- `caregiver_handoff.md`
- `storyboard.md`
- `profile_normalized.json`

Validation:

- Run valid sample profile.
- Manually inspect that all facts come from the profile.
- Confirm privacy exclusions are respected.
- Confirm tone is adult, warm, and not infantilizing.

Exit gate:

- A caregiver reviewing the sample artifacts would know what to correct, print, or share.

## Iteration 2: Safety and Quality Evaluator

Objective: add the judgment layer before images increase variability.

Build:

- Implement `evaluate_memory_kit(profile, artifact_paths)`.
- Return strict JSON with:
  - `overall_passed`
  - `scores`
  - `issues`
  - `regeneration_recommended`
  - `regeneration_feedback`
  - `caregiver_review_required`
- Add JSON fence cleanup based on `L_4.ipynb` and current `evaluate_infographic`.
- Add hard-fail logic for privacy and medical-safety issues.

Validation:

- Feed the evaluator a clean kit.
- Feed it a deliberately flawed artifact that includes a privacy exclusion.
- Feed it an artifact with medical advice phrasing.
- Confirm parseable JSON in all cases.

Exit gate:

- Evaluator reliably blocks unsafe artifacts and gives concrete fix instructions.

## Iteration 3: Deterministic Orientation Board

Objective: produce the most practical artifact with maximum readability.

Build:

- Implement `generate_orientation_board`.
- Prefer deterministic HTML/CSS or PIL rendering for this artifact instead of pure image generation.
- Use high contrast, large text, and a simple grid.
- Include:
  - preferred name,
  - "Today is ____",
  - key contact,
  - routine blocks,
  - calming phrase,
  - review footer: "Caregiver-reviewed support aid. Not medical advice."

Reasoning:

The orientation board must be readable and trustworthy. A deterministic renderer is safer than generated text inside a raster image, because image models can misspell or distort labels.

Validation:

- Print or open at 100% scale.
- Check long names and routines do not overflow.
- Run evaluator on the image plus source profile.
- Confirm no privacy exclusions appear.

Exit gate:

- Board is legible, printable, and useful without artistic polish.

## Iteration 4: Generated Memory Timeline

Objective: add an emotionally resonant visual artifact using the notebook image-generation pattern.

Build:

- Implement `generate_memory_timeline(profile, output_dir, feedback="")`.
- Use `gemini-3.1-flash-image-preview`.
- Prompt constraints:
  - use only supplied events,
  - do not infer dates,
  - no photorealistic portraits,
  - use large labels,
  - respectful adult tone,
  - simple illustrated timeline.
- Save image bytes from `part.inline_data`.

Validation:

- Compare every visible timeline event against `profile.life_events`.
- Run evaluator.
- If non-safety score fails, regenerate once with evaluator feedback.

Exit gate:

- Timeline is emotionally appropriate, fact-bounded, and clear enough for a caregiver review session.

## Iteration 5: End-to-End ADK Workflow

Objective: make the prototype usable through the agent interface.

Build:

- Implement `create_memory_bridge_kit(profile_path: str) -> str`.
- Wire it into `google.adk.agents.llm_agent.Agent`.
- Agent instruction:
  - call the workflow when given a profile path,
  - never offer medical advice,
  - always report output path and evaluation status,
  - always state that caregiver review is required.
- Add `adk run memory_bridge_agent` compatibility.

Workflow:

1. Load profile.
2. Create output directory.
3. Generate text artifacts.
4. Generate orientation board.
5. Generate memory timeline.
6. Evaluate kit.
7. Regenerate timeline once if evaluation recommends it and no safety hard-fail exists.
8. Return summary.

Validation:

- Run with valid profile.
- Run with missing consent profile.
- Run with unsafe medical profile.
- Confirm all final paths exist.
- Confirm final summary is understandable.

Exit gate:

- A tester can create a complete kit from one command or ADK chat message.

## Iteration 6: User-Test Readiness

Objective: prepare for real feedback without exposing users to confusing or unsafe flows.

Build:

- Add `USER_TEST_GUIDE.md`.
- Add a one-page consent/testing disclaimer.
- Add sample intake questions.
- Add a caregiver review checklist.
- Add a feedback capture form as Markdown.

User-test script:

1. Ask tester to review the sample profile.
2. Ask them to run or observe kit generation.
3. Ask them to inspect each artifact.
4. Ask:
   - What would you print?
   - What feels useful?
   - What feels wrong or uncomfortable?
   - What facts are missing or over-assumed?
   - Would this help a family visit or care handoff?
   - What would prevent you from using it?

Metrics:

- Time to produce kit.
- Number of hallucinated or unsupported facts.
- Number of privacy violations.
- Caregiver usefulness rating from 1-5.
- Dignity/tone rating from 1-5.
- Readability rating from 1-5.
- "Would use in a real care context" yes/no/maybe.

Exit gate:

- At least 3 internal or friendly testers can complete the review without confusion.
- No severe safety or privacy issue appears in generated outputs.

## Suggested Build Order

1. `schemas.py`
2. profile examples
3. `load_memory_profile`
4. text artifact generators
5. evaluator
6. deterministic orientation board
7. generated memory timeline
8. top-level ADK workflow
9. user-test guide

This order reduces risk. It validates safety and usefulness before adding the more variable image-generation layer.

## Prototype File Tree

```text
memory_bridge_agent/
  __init__.py
  agent.py
  tools.py
  schemas.py
  prompts.py

examples/
  memory_profiles/
    maria_valid.json
    missing_consent.json
    unsafe_medical_request.json

generated_memory_kits/
  .gitkeep

notebooks/
  MEMORY_BRIDGE_PRODUCT_TECH_SPEC.md
  MEMORY_BRIDGE_ITERATIVE_MVP_PLAN.md
  DEMO_AND_USER_TEST_STEPS.md
  USER_TEST_GUIDE.md
```

Generated kit directories should remain out of source control.

## Minimum Test Cases

Unit-style tests:

- valid profile loads.
- missing consent blocks.
- insufficient life events block.
- privacy exclusions are retained in normalized profile.
- unsafe medical request blocks.
- output directory is created.
- generated Markdown files exist.
- evaluator JSON parses.

Manual tests:

- orientation board readability.
- timeline factual consistency.
- no excluded private facts appear.
- no medical advice appears.
- regeneration runs at most once.

## User Testing Cohorts

Start with low-risk testers:

- 2-3 internal reviewers using fictional profiles.
- 3-5 family caregivers using fictional or lightly anonymized profiles.
- 2-3 aging-care professionals reviewing outputs, not entering real client data.

Only after guardrails hold:

- caregiver-provided real profiles with explicit consent and local-only storage.

Avoid in the first test:

- people in acute distress,
- active medical decision-making,
- medication management,
- disputed family histories,
- end-of-life decision contexts.

## Stop/Go Criteria

Stop and fix before more testing if:

- any artifact includes medical advice,
- any artifact invents a family member or event,
- privacy exclusions leak into public artifacts,
- generated image text is unreadable,
- evaluator misses a deliberately planted unsafe phrase,
- tester cannot understand the review requirement.

Continue to broader testing if:

- caregivers rate usefulness at 4/5 or higher,
- dignity/tone averages 4/5 or higher,
- zero severe privacy or medical-safety failures occur,
- artifacts are clear enough to print or share in a care binder.

## Phase 2 After MVP

Add only after static artifacts pass user testing:

- photo ingestion with explicit controls,
- multilingual output,
- facility-branded templates,
- caregiver correction UI,
- three-scene reference images,
- optional Veo reminiscence clip,
- export to PDF.

Do not add video before the product proves that the generated content is safe, factual, and useful in still form.

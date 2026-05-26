# Memory Bridge Product Technical Spec

## 1. Product Summary

**Memory Bridge** is an ADK-based omnimedia agent that turns caregiver-approved personal history and daily routine information into practical support artifacts for older adults with mild cognitive impairment, early dementia, or age-related memory challenges.

The product does not diagnose, treat, monitor, or predict cognitive decline. It creates non-clinical memory, orientation, reminiscence, and caregiver communication materials.

Primary outputs:

- `orientation_board.png`: printable daily orientation board.
- `memory_timeline.png`: visual life timeline.
- `visit_prompts.md`: conversation prompts for family, friends, and care staff.
- `caregiver_handoff.md`: concise support notes.
- `storyboard.md`: 3-scene reminiscence video plan.
- `evaluation.json`: structured quality and safety review.
- Phase 2: optional `memory_clip.mp4`.

## 2. Target Users

Primary users:

- Adult children and spouses caring for an older adult.
- Professional caregivers in assisted living, memory care, or home care.
- Social workers, occupational therapists, life enrichment coordinators, and community aging programs.

Beneficiary:

- Older adult who benefits from familiar names, routines, places, stories, and calming orientation materials.

## 3. Problem Statement

Caregivers often hold scattered knowledge about an older adult's identity, routines, triggers, calming preferences, and life story. That knowledge is hard to turn into consistently useful materials. Care facilities and family members also need artifacts that are respectful, easy to update, printable, and safe to share.

Memory Bridge turns structured caregiver input into a reviewed media kit that helps preserve identity and improve day-to-day communication without pretending to provide medical treatment.

## 4. Product Principles

- **Dignity first:** describe the person as a whole adult, not as a diagnosis.
- **Caregiver controlled:** do not publish or share automatically.
- **Source bounded:** do not invent family relationships, events, medical facts, or preferences.
- **Non-clinical:** no diagnosis, medication advice, prognosis, emergency triage, or cognitive improvement claims.
- **Readable:** large type, high contrast, low clutter, plain language.
- **Regenerable:** evaluator feedback can trigger one bounded revision.

## 5. MVP Scope

### In Scope

- Local ADK agent and CLI/web-compatible workflow.
- Input from structured JSON or Markdown profile.
- Static image generation with `gemini-3.1-flash-image-preview`.
- Text generation and evaluation with `gemini-3-flash-preview`.
- Output directory with deterministic filenames and timestamped run metadata.
- One regeneration pass if evaluation fails.
- JSON evaluation schema.

### Out of Scope

- Diagnosis, screening, or cognitive scoring.
- Medical record ingestion.
- Medication schedule generation unless provided verbatim by caregiver and labeled as caregiver-provided.
- Emergency response or safety monitoring.
- Automatic sharing with family, clinicians, or facilities.
- Photorealistic generation of family members or deceased people.
- Phase 1 video rendering with Veo.

## 6. Notebook Foundation

The spec intentionally maps to observed notebook patterns:

- `L_2.ipynb`: image prompt engineering, reference-image style conditioning, image bytes saved from `part.inline_data`.
- `L_3.ipynb`: video prompt expansion and image-to-video flow for later phase.
- `L_4.ipynb`: structured evaluation, Gemini-as-judge, JSON cleanup, rubric scoring.
- `L_5.ipynb`: brand/style guide analysis and evaluation tools.
- `L_6.ipynb`: scene planning, reference-frame generation, video generation, and video evaluation.
- `L_8.ipynb`: ADK workflow with generation, evaluation, logging, and retry.
- Current repo: `infographic_agent/tools.py` already contains client creation, output writing, logging, image generation, evaluation, and JSON cleanup patterns.

## 7. User Workflow

1. Caregiver prepares `profile.json` or `profile.md`.
2. User asks the ADK agent: "Create a Memory Bridge kit from this profile."
3. Agent validates required fields and consent attestation.
4. Agent normalizes profile into a safe structured summary.
5. Agent generates text artifacts.
6. Agent generates image artifacts.
7. Agent evaluates the full kit.
8. If the kit fails and feedback is actionable, agent regenerates once.
9. Agent returns output paths, pass/fail status, and review notes.

## 8. Input Contract

Recommended file: `memory_profile.json`.

```json
{
  "consent": {
    "attestation": true,
    "provided_by": "Jane Doe",
    "relationship": "daughter",
    "notes": "Reviewed with parent where possible."
  },
  "person": {
    "preferred_name": "Maria",
    "full_name": "Maria Alvarez",
    "pronouns": "she/her",
    "birth_decade": "1940s",
    "primary_language": "English",
    "reading_level_preference": "plain"
  },
  "contacts": [
    {"name": "Jane", "relationship": "daughter", "phone_label": "Call Jane"}
  ],
  "life_events": [
    {"year_or_period": "1968", "event": "Moved to Chicago", "source": "caregiver"}
  ],
  "favorite_places": ["Chicago lakefront", "family kitchen", "St. Mary's garden"],
  "favorite_topics": ["gardening", "baking", "old neighborhood stories"],
  "daily_routine": [
    {"time_label": "Morning", "activity": "Breakfast, tea, and newspaper"}
  ],
  "calming_phrases": ["You are safe. Jane will visit this afternoon."],
  "confusion_triggers": ["Too many people speaking at once"],
  "privacy_exclusions": ["Do not mention finances", "Do not mention estranged relatives"],
  "style_preferences": {
    "tone": "warm, calm, respectful",
    "visual_style": "simple, high contrast, gentle colors",
    "avoid": ["childlike language", "busy backgrounds"]
  },
  "caregiver_notes": "Use large text. Avoid medical claims."
}
```

Required fields:

- `consent.attestation`
- `person.preferred_name`
- at least one `contacts` entry
- at least three `life_events`
- at least one `daily_routine` entry
- `privacy_exclusions`, even if empty

## 9. Output Contract

Output root: `generated_memory_kits/<safe_name>_<run_timestamp>/`

Files:

- `profile_normalized.json`
- `orientation_board.png`
- `memory_timeline.png`
- `visit_prompts.md`
- `caregiver_handoff.md`
- `storyboard.md`
- `evaluation.json`
- `run_log.txt`

Optional phase 2:

- `scene_1_ref.png`
- `scene_2_ref.png`
- `scene_3_ref.png`
- `memory_clip.mp4`

## 10. Agent Architecture

Recommended package:

```text
memory_bridge_agent/
  __init__.py
  agent.py
  tools.py
  schemas.py
  prompts.py
  .env
```

The package should follow the current repo split:

- `agent.py`: ADK agent and top-level workflow.
- `tools.py`: file loading, profile validation, generation, evaluation, logging.
- `schemas.py`: Pydantic models or typed dicts for profile and evaluation.
- `prompts.py`: prompt templates for image, text, and evaluation tools.

Models:

- Orchestration/evaluation: `gemini-3-flash-preview`.
- Image generation: `gemini-3.1-flash-image-preview`.
- Optional phase 2 planning: `gemini-3.1-pro-preview` if scene planning needs stronger reasoning.
- Optional phase 2 video: `veo-3.1-fast-generate-001`.

## 11. ADK Tool Contracts

### `load_memory_profile(profile_path: str) -> dict`

Reads JSON or Markdown profile, validates required fields, applies privacy exclusions, and returns normalized profile JSON.

Failure cases:

- missing consent attestation,
- malformed file,
- insufficient profile detail,
- detected medical advice request.

### `generate_orientation_board(profile: dict, output_dir: str, feedback: str = "") -> str`

Creates a high-contrast printable board image. It should include:

- preferred name,
- "Today is ____" placeholder,
- familiar contacts,
- simple routine blocks,
- calming phrase,
- "You are safe" orientation copy if provided.

Returns image path.

### `generate_memory_timeline(profile: dict, output_dir: str, feedback: str = "") -> str`

Creates an illustrated timeline using only supplied events. It must avoid fake portraits and must not infer dates.

Returns image path.

### `generate_visit_prompts(profile: dict, output_dir: str) -> str`

Creates conversation prompts grouped by:

- people,
- places,
- work or family history,
- hobbies,
- calming topics,
- topics to avoid.

Returns Markdown path.

### `generate_caregiver_handoff(profile: dict, output_dir: str) -> str`

Creates a one-page non-medical handoff for care staff:

- preferred name,
- key contacts,
- what helps,
- what may distress,
- communication tips,
- privacy exclusions.

Returns Markdown path.

### `plan_memory_storyboard(profile: dict, output_dir: str) -> str`

Creates a 3-scene reminiscence storyboard:

- `visual_description`
- `narration_script`
- `camera_motion`
- `source_events_used`
- `safety_notes`

Returns Markdown or JSON path.

### `evaluate_memory_kit(profile: dict, artifact_paths: dict) -> str`

Evaluates all generated artifacts. Returns JSON string conforming to the schema below.

### `create_memory_bridge_kit(profile_path: str) -> str`

Top-level workflow:

1. load profile,
2. create output directory,
3. generate artifacts,
4. evaluate,
5. regenerate image artifacts once if failed for fixable reasons,
6. return final summary.

## 12. Evaluation Schema

```json
{
  "overall_passed": true,
  "scores": {
    "factual_consistency": 5,
    "dignity_and_tone": 5,
    "privacy_safety": 5,
    "readability_for_older_adults": 5,
    "caregiver_usefulness": 5,
    "medical_safety_boundary": 5,
    "hallucination_risk": 5
  },
  "issues": [
    {
      "artifact": "orientation_board.png",
      "severity": "low",
      "criterion": "readability_for_older_adults",
      "description": "Some labels may be too small.",
      "recommended_fix": "Use fewer sections and larger text."
    }
  ],
  "regeneration_recommended": false,
  "regeneration_feedback": "",
  "caregiver_review_required": true
}
```

Pass threshold:

- every safety criterion must be at least 5,
- all other criteria must be at least 4,
- any privacy or medical-safety issue fails the kit.

## 13. Prompt Requirements

All generation prompts must include:

- "Use only caregiver-provided facts."
- "Do not infer family relationships, medical details, dates, or events."
- "Do not include diagnosis, treatment, prognosis, medication advice, or emergency guidance."
- "Use respectful adult language."
- "Use high contrast, large text, and uncluttered layout."
- "Do not generate photorealistic depictions of real people."
- "Avoid childlike, infantilizing, or sentimentalized language."

Image prompts should request:

- print-friendly layout,
- large readable typography,
- minimal sections,
- no dense paragraphs,
- calm but not childish visuals,
- no fake portraits.

## 14. Safety and Privacy Controls

Hard blocks:

- User asks for diagnosis, prognosis, cognitive scoring, or medical interpretation.
- User asks to generate medication instructions not already provided verbatim.
- Profile lacks consent attestation.
- User asks to impersonate a real person or deceased relative.
- User asks to hide or override privacy exclusions.

Soft warnings:

- Sensitive trauma, family conflict, financial details, or disputed memories.
- Unverified claims about relationships or medical events.
- Requests for public sharing.

Data handling:

- Store locally by default.
- Do not upload generated artifacts outside model calls required for generation/evaluation.
- Redact privacy exclusions from generated public-facing artifacts.
- Include `caregiver_review_required: true` in every evaluation.

## 15. Implementation Plan

### Milestone 1: Static Text Kit

- Create package skeleton.
- Implement profile validation.
- Generate `visit_prompts.md`, `caregiver_handoff.md`, and `storyboard.md`.
- Generate `evaluation.json` over text artifacts.
- Add syntax check with `python -m compileall memory_bridge_agent`.

### Milestone 2: Image Artifacts

- Add `generate_orientation_board`.
- Add `generate_memory_timeline`.
- Save image bytes from `part.inline_data`.
- Evaluate generated images with Gemini-as-judge.
- Add one regeneration pass.

### Milestone 3: ADK Workflow

- Wire `create_memory_bridge_kit` into `Agent`.
- Run with `adk run memory_bridge_agent`.
- Verify local output paths and logs.

### Milestone 4: Optional Video

- Add `plan_memory_storyboard` JSON scene output.
- Add reference-frame generation for three scenes.
- Add optional Veo image-to-video generation.
- Add video evaluation only after static kit safety passes.

## 16. Acceptance Criteria

Functional:

- Given a valid `memory_profile.json`, the agent produces all phase 1 artifacts.
- Missing consent fails before generation.
- Privacy exclusions are absent from public-facing artifacts.
- The evaluator returns parseable JSON.
- A failed non-safety evaluation triggers at most one regeneration.
- Final response includes output directory and evaluation summary.

Quality:

- Generated text uses respectful adult language.
- Images are printable, high contrast, and not visually cluttered.
- No artifact invents unprovided medical or family facts.
- No artifact claims cognitive improvement, treatment, or diagnosis.

Technical:

- Uses `google.adk.agents.llm_agent.Agent`.
- Keeps orchestration in `agent.py` and implementation in `tools.py`.
- Uses `gemini-3-flash-preview` for text/evaluation.
- Uses `gemini-3.1-flash-image-preview` for image generation.
- Does not commit generated outputs, logs, `.env`, or API keys.

## 17. Open Questions

- Should the first implementation live beside `infographic_agent/` or replace it as the main demo agent?
- Should profile input support photos in phase 1, or only text until safety prompts are validated?
- Should output images be pure generated raster images, or should a deterministic HTML/PDF renderer be used for stronger readability?
- What consent model is acceptable for assisted-living or family caregiver contexts?
- Should the product support multiple languages in the MVP?

## 18. Recommended First Build

Start with a text-first Memory Bridge kit, then add still images. Defer video.

The highest-risk part is not media generation; it is hallucination, privacy leakage, and infantilizing tone. A text-first implementation lets the safety evaluator mature before image/video generation adds more variability.

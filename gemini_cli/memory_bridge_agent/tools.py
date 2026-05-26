"""Implementation tools for the Memory Bridge ADK prototype."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont

from .prompts import IMAGE_MODEL, IMAGE_SAFETY_RULES, SAFETY_RULES, TEXT_MODEL
from .schemas import (
    REQUIRED_TOP_LEVEL_FIELDS,
    UNSAFE_MEDICAL_TERMS,
    ProfileValidationError,
    as_list,
    normalize_string,
)

load_dotenv()
load_dotenv(Path(__file__).with_name(".env"))

OUTPUT_ROOT = Path("generated_memory_kits")
AUDIT_LOG = OUTPUT_ROOT / "audit_log.jsonl"
REQUEST_TIMEOUT_MS = 60_000


def _create_client() -> genai.Client | None:
    """Create a Gemini client when credentials are configured, else return None."""
    if os.environ.get("MEMORY_BRIDGE_ENABLE_GEMINI", "").lower() != "true":
        return None
    http_options = types.HttpOptions(timeout=REQUEST_TIMEOUT_MS)
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
    if use_vertex:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
        if project:
            return genai.Client(
                vertexai=True,
                project=project,
                location=location,
                http_options=http_options,
            )
        return None

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key, http_options=http_options)
    return None


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "memory_profile"


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_log(output_dir: Path, message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "run_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def write_audit_event(event_type: str, output_dir: str | Path | None, details: dict[str, Any]) -> None:
    """Append a structured audit event for monitoring and analytics."""
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "output_dir": str(output_dir) if output_dir else "",
        "details": details,
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_audit_events(limit: int | None = None) -> list[dict[str, Any]]:
    """Read structured audit events, newest last by default."""
    if not AUDIT_LOG.exists():
        return []
    events = []
    for line in AUDIT_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events[-limit:] if limit else events


def build_analytics_summary() -> dict[str, Any]:
    """Aggregate prototype monitoring metrics from the audit log."""
    events = read_audit_events()
    runs_started = sum(1 for event in events if event.get("event_type") == "workflow_started")
    runs_completed = [event for event in events if event.get("event_type") == "workflow_completed"]
    runs_blocked = [event for event in events if event.get("event_type") == "workflow_blocked"]
    generated_artifacts = [
        event for event in events if event.get("event_type") == "artifact_generated"
    ]
    safety_blocks = {}
    for event in runs_blocked:
        reason = event.get("details", {}).get("reason", "unknown")
        safety_blocks[reason] = safety_blocks.get(reason, 0) + 1
    passed = sum(1 for event in runs_completed if event.get("details", {}).get("overall_passed") is True)
    return {
        "total_events": len(events),
        "runs_started": runs_started,
        "runs_completed": len(runs_completed),
        "runs_blocked": len(runs_blocked),
        "kits_passed": passed,
        "kits_failed": len(runs_completed) - passed,
        "artifacts_generated": len(generated_artifacts),
        "safety_blocks_by_reason": safety_blocks,
        "latest_output_dir": runs_completed[-1].get("output_dir") if runs_completed else "",
    }


def _profile_text(profile: dict[str, Any]) -> str:
    return json.dumps(profile, ensure_ascii=False, indent=2)


def _read_profile_file(profile_path: str) -> dict[str, Any]:
    path = Path(profile_path)
    if not path.exists():
        raise ProfileValidationError(f"Profile file not found: {profile_path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ProfileValidationError(f"Malformed JSON profile: {exc}") from exc
    raise ProfileValidationError("Only JSON profiles are supported in this prototype.")


def _contains_unsafe_medical_request(profile: dict[str, Any]) -> str | None:
    text = _profile_text(profile).lower()
    for term in UNSAFE_MEDICAL_TERMS:
        if term in text:
            return term
    return None


def _validate_profile(profile: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in profile]
    if missing:
        raise ProfileValidationError(f"Missing required profile fields: {', '.join(missing)}")

    consent = profile.get("consent") or {}
    if consent.get("attestation") is not True:
        raise ProfileValidationError("Consent attestation is required before generation.")

    person = profile.get("person") or {}
    if not normalize_string(person.get("preferred_name")):
        raise ProfileValidationError("person.preferred_name is required.")

    if len(as_list(profile.get("contacts"))) < 1:
        raise ProfileValidationError("At least one contact is required.")
    if len(as_list(profile.get("life_events"))) < 3:
        raise ProfileValidationError("At least three life events are required.")
    if len(as_list(profile.get("daily_routine"))) < 1:
        raise ProfileValidationError("At least one daily routine entry is required.")
    if not isinstance(profile.get("privacy_exclusions"), list):
        raise ProfileValidationError("privacy_exclusions must be a list, even when empty.")

    unsafe_term = _contains_unsafe_medical_request(profile)
    if unsafe_term:
        raise ProfileValidationError(
            f"Unsafe medical request detected: '{unsafe_term}'. "
            "Memory Bridge cannot provide diagnosis, prognosis, medication advice, "
            "emergency guidance, or cognitive scoring."
        )


def _normalize_profile(profile: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(profile)
    person = dict(normalized.get("person") or {})
    person["preferred_name"] = normalize_string(person.get("preferred_name"))
    person["full_name"] = normalize_string(person.get("full_name")) or person["preferred_name"]
    person["primary_language"] = normalize_string(person.get("primary_language")) or "English"
    person["reading_level_preference"] = (
        normalize_string(person.get("reading_level_preference")) or "plain"
    )
    normalized["person"] = person
    normalized["contacts"] = as_list(normalized.get("contacts"))
    normalized["life_events"] = as_list(normalized.get("life_events"))
    normalized["favorite_places"] = as_list(normalized.get("favorite_places"))
    normalized["favorite_topics"] = as_list(normalized.get("favorite_topics"))
    normalized["daily_routine"] = as_list(normalized.get("daily_routine"))
    normalized["calming_phrases"] = as_list(normalized.get("calming_phrases"))
    normalized["confusion_triggers"] = as_list(normalized.get("confusion_triggers"))
    normalized["privacy_exclusions"] = as_list(normalized.get("privacy_exclusions"))
    onboarding = dict(normalized.get("patient_onboarding") or {})
    onboarding["observed_symptoms"] = as_list(onboarding.get("observed_symptoms"))
    onboarding["symptom_context"] = as_list(onboarding.get("symptom_context"))
    onboarding["staff_goals"] = as_list(onboarding.get("staff_goals"))
    onboarding["non_diagnostic_notes"] = normalize_string(onboarding.get("non_diagnostic_notes"))
    normalized["patient_onboarding"] = onboarding
    normalized["prototype_notice"] = (
        "Caregiver-reviewed support aid. Not medical advice, diagnosis, treatment, "
        "prognosis, monitoring, or emergency guidance."
    )
    return normalized


def load_memory_profile(profile_path: str) -> dict[str, Any]:
    """Load, validate, and normalize a caregiver-approved Memory Bridge profile."""
    profile = _read_profile_file(profile_path)
    _validate_profile(profile)
    return _normalize_profile(profile)


def _symptom_onboarding(profile: dict[str, Any]) -> dict[str, Any]:
    return dict(profile.get("patient_onboarding") or {})


def create_output_dir(profile: dict[str, Any]) -> str:
    """Create and return a timestamped output directory for a memory kit."""
    name = profile.get("person", {}).get("preferred_name", "memory_profile")
    base = OUTPUT_ROOT / f"{_safe_slug(name)}_{_now_stamp()}"
    output_dir = base
    suffix = 2
    while output_dir.exists():
        output_dir = Path(f"{base}_{suffix}")
        suffix += 1
    output_dir.mkdir(parents=True, exist_ok=False)
    _write_log(output_dir, "Created Memory Bridge output directory.")
    with open(output_dir / "profile_normalized.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    return str(output_dir)


def _format_life_event(event: Any) -> str:
    if isinstance(event, dict):
        period = normalize_string(event.get("year_or_period"))
        description = normalize_string(event.get("event"))
        return f"{period}: {description}" if period else description
    return normalize_string(event)


def _format_routine_item(item: Any) -> str:
    if isinstance(item, dict):
        time_label = normalize_string(item.get("time_label"))
        activity = normalize_string(item.get("activity"))
        return f"{time_label}: {activity}" if time_label else activity
    return normalize_string(item)


def _markdown_list(items: list[Any], formatter=str) -> str:
    lines = []
    for item in items:
        value = normalize_string(formatter(item))
        if value:
            lines.append(f"- {value}")
    return "\n".join(lines) or "- Needs caregiver input."


def _write_text_artifact(path: Path, title: str, body: str) -> str:
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")
    return str(path)


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = normalize_string(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), trial, font=font)[2]
        if width <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    font: ImageFont.ImageFont,
    fill: str = "#111111",
    line_gap: int = 8,
) -> int:
    for line in _wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += draw.textbbox((0, 0), line, font=font)[3] + line_gap
    return y


def _strip_json_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        return cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
    if cleaned.startswith("```"):
        return cleaned.split("```", 1)[1].split("```", 1)[0].strip()
    return cleaned


def _generate_text_with_gemini(prompt: str) -> str | None:
    client = _create_client()
    if client is None:
        return None
    try:
        response = client.models.generate_content(model=TEXT_MODEL, contents=prompt)
        return (response.text or "").strip() if response else None
    except Exception:
        return None


def _first_contact(profile: dict[str, Any]) -> dict[str, Any]:
    contacts = as_list(profile.get("contacts"))
    return contacts[0] if contacts and isinstance(contacts[0], dict) else {}


def _topics_to_avoid(profile: dict[str, Any]) -> str:
    exclusions = [normalize_string(item) for item in profile.get("privacy_exclusions", []) if normalize_string(item)]
    if not exclusions:
        return "- No private topics were listed by the caregiver."
    return (
        f"- {len(exclusions)} caregiver-marked private topic(s) should be avoided.\n"
        "- Ask the caregiver for details before discussing sensitive family, financial, or medical topics."
    )


def generate_visit_prompts(profile: dict[str, Any], output_dir: str) -> str:
    """Generate caregiver-reviewed visit conversation prompts as Markdown."""
    output_path = Path(output_dir) / "visit_prompts.md"
    prompt = f"""
Create visit conversation prompts for an older adult using this profile.

{SAFETY_RULES}

Return concise Markdown with sections:
- Warm Openers
- People and Family
- Places
- Hobbies and Favorite Topics
- Calming Topics
- Topics to Avoid

Profile JSON:
{_profile_text(profile)}
"""
    generated = _generate_text_with_gemini(prompt)
    if generated:
        body = generated
    else:
        body = f"""
## Warm Openers

- Hi {profile["person"]["preferred_name"]}, it is good to sit with you.
- Would you like to talk about something familiar today?
- We can take our time.

## People and Family

{_markdown_list(profile.get("contacts", []), lambda c: f'{c.get("name")} is your {c.get("relationship")}' if isinstance(c, dict) else c)}

## Places

{_markdown_list(profile.get("favorite_places", []))}

## Hobbies and Favorite Topics

{_markdown_list(profile.get("favorite_topics", []))}

## Calming Topics

{_markdown_list(profile.get("calming_phrases", []))}

## Topics to Avoid

{_topics_to_avoid(profile)}

## Caregiver Review

- Confirm these prompts are welcome and current.
- Remove anything that feels upsetting or too private.
"""
    _write_log(Path(output_dir), "Generated visit_prompts.md.")
    return _write_text_artifact(output_path, "Visit Prompts", body)


def generate_caregiver_handoff(profile: dict[str, Any], output_dir: str) -> str:
    """Generate a concise non-medical caregiver handoff as Markdown."""
    output_path = Path(output_dir) / "caregiver_handoff.md"
    contact = _first_contact(profile)
    prompt = f"""
Create a one-page non-medical caregiver handoff from this profile.

{SAFETY_RULES}

Return concise Markdown with sections:
- Preferred Name
- Key Contact
- What Helps
- What May Distress
- Daily Rhythm
- Communication Tips
- Privacy Notes
- Review Notice

Profile JSON:
{_profile_text(profile)}
"""
    generated = _generate_text_with_gemini(prompt)
    if generated:
        body = generated
    else:
        body = f"""
## Preferred Name

{profile["person"]["preferred_name"]}

## Key Contact

{normalize_string(contact.get("phone_label")) or normalize_string(contact.get("name")) or "Needs caregiver input."}

## What Helps

{_markdown_list(profile.get("calming_phrases", []))}

## What May Distress

{_markdown_list(profile.get("confusion_triggers", []))}

## Daily Rhythm

{_markdown_list(profile.get("daily_routine", []), _format_routine_item)}

## Communication Tips

- Speak calmly and give one idea at a time.
- Use familiar names and places from the profile.
- Pause and allow extra time for response.

## Privacy Notes

{_topics_to_avoid(profile)}

## Review Notice

Caregiver-reviewed support aid. Not medical advice.
"""
    _write_log(Path(output_dir), "Generated caregiver_handoff.md.")
    return _write_text_artifact(output_path, "Caregiver Handoff", body)


def plan_memory_storyboard(profile: dict[str, Any], output_dir: str) -> str:
    """Create a three-scene reminiscence storyboard as Markdown."""
    output_path = Path(output_dir) / "storyboard.md"
    prompt = f"""
Create a 3-scene reminiscence storyboard for a short, gentle memory video.

{SAFETY_RULES}

Use only supplied life events, places, routines, and favorite topics.
Do not create photorealistic real-person scenes.
Return Markdown. For each scene include:
- visual_description
- narration_script
- camera_motion
- source_events_used
- safety_notes

Profile JSON:
{_profile_text(profile)}
"""
    generated = _generate_text_with_gemini(prompt)
    if generated:
        body = generated
    else:
        events = [_format_life_event(event) for event in profile.get("life_events", [])[:3]]
        while len(events) < 3:
            events.append("Caregiver-provided memory to confirm.")
        body = "\n\n".join(
            f"""## Scene {idx}

- visual_description: A calm illustrated scene inspired by: {event}
- narration_script: {profile["person"]["preferred_name"]}'s story includes {event}. This memory is caregiver-provided and should be reviewed.
- camera_motion: slow_zoom_in
- source_events_used: {event}
- safety_notes: Use respectful adult language. Do not invent details or show photorealistic people."""
            for idx, event in enumerate(events, start=1)
        )
    _write_log(Path(output_dir), "Generated storyboard.md.")
    return _write_text_artifact(output_path, "Memory Storyboard", body)


def generate_patient_onboarding_summary(profile: dict[str, Any], output_dir: str) -> str:
    """Generate a non-diagnostic patient onboarding summary for staff review."""
    output_path = Path(output_dir) / "patient_onboarding_summary.md"
    onboarding = _symptom_onboarding(profile)
    observed = onboarding.get("observed_symptoms", [])
    context = onboarding.get("symptom_context", [])
    goals = onboarding.get("staff_goals", [])
    prompt = f"""
Create a non-diagnostic patient onboarding summary for nursing-home staff.

{SAFETY_RULES}

Important:
- List only observed symptoms exactly as caregiver/staff provided them.
- Do not diagnose, triage, rank severity, suggest treatment, or provide medication guidance.
- Recommend staff review and clinician escalation only through existing facility protocols.

Profile JSON:
{_profile_text(profile)}
"""
    generated = _generate_text_with_gemini(prompt)
    if generated:
        body = generated
    else:
        body = f"""
## Resident

{profile["person"]["preferred_name"]}

## Observed Symptoms Or Concerns

{_markdown_list(observed)}

## Context Noted By Staff Or Caregiver

{_markdown_list(context)}

## Staff Goals For This Kit

{_markdown_list(goals)}

## Support Preferences

- Calming phrases: {", ".join(profile.get("calming_phrases", [])) or "Needs caregiver input."}
- Known distress triggers: {", ".join(profile.get("confusion_triggers", [])) or "Needs caregiver input."}

## Safety Boundary

This summary is for onboarding and communication support only. It is not a diagnosis, triage tool, treatment plan, medication guide, or emergency instruction. Staff should follow facility protocol for clinical concerns.

## Review Required

Caregiver and staff review is required before use.
"""
    _write_log(Path(output_dir), "Generated patient_onboarding_summary.md.")
    return _write_text_artifact(output_path, "Patient Onboarding Summary", body)


def generate_storyboard_image_prompts(profile: dict[str, Any], output_dir: str) -> str:
    """Generate prompt text for storyboard images using symptoms as context, not diagnosis."""
    output_path = Path(output_dir) / "storyboard_image_prompts.md"
    onboarding = _symptom_onboarding(profile)
    observed = onboarding.get("observed_symptoms", [])
    context = onboarding.get("symptom_context", [])
    events = [_format_life_event(event) for event in profile.get("life_events", [])[:3]]
    while len(events) < 3:
        events.append("Caregiver-provided memory to confirm")

    prompts = []
    for idx, event in enumerate(events, start=1):
        prompts.append(
            f"""## Storyboard Image Prompt {idx}

**Prompt text**

Create a calm, respectful, non-photorealistic illustrated storyboard frame for an older adult's reminiscence and orientation support kit.

Scene source: {event}

Resident context to keep the image gentle and low-stimulation: observed concerns include {", ".join(observed) if observed else "no symptom concerns provided"}; context notes include {", ".join(context) if context else "no context notes provided"}.

Visual requirements:
- high contrast, uncluttered composition, large readable labels if any text appears;
- no diagnosis, treatment, medication, emergency, or clinical imagery;
- no photorealistic depiction of real people;
- warm adult tone, not childish;
- use only caregiver-provided facts.

**Negative prompt**

Avoid hospital alarms, medication bottles, distress scenes, infantilizing visuals, fake family portraits, clinical conclusions, or invented events.
"""
        )

    body = "\n\n".join(prompts)
    _write_log(Path(output_dir), "Generated storyboard_image_prompts.md.")
    return _write_text_artifact(output_path, "Storyboard Image Prompts", body)


def _storyboard_prompt_data(profile: dict[str, Any]) -> list[dict[str, str]]:
    onboarding = _symptom_onboarding(profile)
    observed = onboarding.get("observed_symptoms", [])
    context = onboarding.get("symptom_context", [])
    events = [_format_life_event(event) for event in profile.get("life_events", [])[:3]]
    while len(events) < 3:
        events.append("Caregiver-provided memory to confirm")
    prompt_data = []
    for idx, event in enumerate(events, start=1):
        prompt = (
            "Create a calm, respectful, non-photorealistic illustrated storyboard "
            "frame for an older adult's reminiscence and orientation support kit. "
            f"Scene source: {event}. "
            "Keep the image gentle and low-stimulation. "
            f"Observed concerns: {', '.join(observed) if observed else 'none provided'}. "
            f"Context notes: {', '.join(context) if context else 'none provided'}. "
            "Use high contrast, uncluttered composition, warm adult tone, and no clinical imagery. "
            "Do not show photorealistic real people, medication bottles, distress scenes, "
            "diagnosis, treatment, emergency guidance, or invented events."
        )
        prompt_data.append({"index": str(idx), "event": event, "prompt": prompt})
    return prompt_data


def _generate_storyboard_image_with_gemini(prompt: str) -> bytes | None:
    client = _create_client()
    if client is None:
        return None
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
    except Exception:
        return None
    if not response.candidates or not response.candidates[0].content.parts:
        return None
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    return None


def _draw_storyboard_fallback(profile: dict[str, Any], output_path: Path, scene: dict[str, str]) -> None:
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), "#fbfbf4")
    draw = ImageDraw.Draw(image)
    title_font = _font(48, bold=True)
    heading_font = _font(34, bold=True)
    body_font = _font(28)
    small_font = _font(22)
    accent = "#3d6470"
    soft = "#e7f0ee"
    line = "#b8d0ca"
    dark = "#111111"

    draw.rectangle((0, 0, width, 92), fill=accent)
    draw.text((44, 24), f"Storyboard Scene {scene['index']}", font=title_font, fill="#ffffff")
    draw.rounded_rectangle((58, 145, 510, 560), radius=24, fill=soft, outline=line, width=4)
    draw.ellipse((166, 210, 402, 445), fill="#ffffff", outline=accent, width=6)
    draw.arc((210, 260, 360, 395), 20, 160, fill=accent, width=5)
    draw.line((192, 455, 380, 455), fill=accent, width=5)
    draw.text((140, 590), "calm illustrated frame", font=small_font, fill=accent)

    draw.text((585, 150), profile["person"]["preferred_name"], font=heading_font, fill=accent)
    y = _draw_wrapped(draw, scene["event"], 585, 215, 610, body_font, dark, line_gap=10)
    y += 20
    _draw_wrapped(
        draw,
        "Low-stimulation visual. Caregiver-provided memory. No clinical conclusions.",
        585,
        y,
        610,
        body_font,
        dark,
        line_gap=10,
    )
    _draw_wrapped(
        draw,
        "Caregiver review required. Not medical advice.",
        44,
        660,
        width - 88,
        small_font,
        "#333333",
    )
    image.save(output_path)


def generate_storyboard_images(profile: dict[str, Any], output_dir: str) -> list[str]:
    """Generate actual storyboard frame PNGs, with deterministic fallback."""
    paths: list[str] = []
    output_root = Path(output_dir)
    for scene in _storyboard_prompt_data(profile):
        output_path = output_root / f"storyboard_scene_{scene['index']}.png"
        image_bytes = _generate_storyboard_image_with_gemini(scene["prompt"])
        if image_bytes:
            output_path.write_bytes(image_bytes)
            _write_log(output_root, f"Generated {output_path.name} with Gemini image model.")
        else:
            _draw_storyboard_fallback(profile, output_path, scene)
            _write_log(output_root, f"Generated {output_path.name} with deterministic fallback.")
        paths.append(str(output_path))
    return paths


def _read_artifacts(artifact_paths: dict[str, str]) -> dict[str, str]:
    contents = {}
    for name, raw_path in artifact_paths.items():
        path = Path(raw_path)
        if path.exists() and path.suffix.lower() in {".md", ".json", ".txt"}:
            contents[name] = path.read_text(encoding="utf-8")
        elif path.exists():
            contents[name] = f"[binary artifact present: {path.name}]"
        else:
            contents[name] = "[missing artifact]"
    return contents


def _evaluate_locally(profile: dict[str, Any], artifact_contents: dict[str, str]) -> dict[str, Any]:
    all_text = "\n".join(artifact_contents.values())
    lower_text = all_text.lower()
    issues: list[dict[str, str]] = []

    scores = {
        "factual_consistency": 5,
        "dignity_and_tone": 5,
        "privacy_safety": 5,
        "readability_for_older_adults": 5,
        "caregiver_usefulness": 5,
        "medical_safety_boundary": 5,
        "hallucination_risk": 5,
    }

    for exclusion in profile.get("privacy_exclusions", []):
        exclusion_text = normalize_string(exclusion)
        if exclusion_text and exclusion_text.lower() in lower_text:
            scores["privacy_safety"] = 1
            issues.append({
                "artifact": "kit",
                "severity": "high",
                "criterion": "privacy_safety",
                "description": f"Privacy exclusion appears in generated artifact: {exclusion_text}",
                "recommended_fix": "Remove privacy-excluded content from public-facing artifacts.",
            })

    unsafe_phrases = (
        "you should take",
        "change your medication",
        "stop medication",
        "diagnosis is",
        "i diagnose",
        "we diagnose",
        "your prognosis is",
        "call 911",
        "emergency guidance",
    )
    for phrase in unsafe_phrases:
        if phrase in lower_text:
            scores["medical_safety_boundary"] = 1
            issues.append({
                "artifact": "kit",
                "severity": "high",
                "criterion": "medical_safety_boundary",
                "description": f"Unsafe medical phrase detected: {phrase}",
                "recommended_fix": "Remove medical advice and keep the artifact non-clinical.",
            })
            break

    infantilizing = ("good girl", "good boy", "sweet little", "babyish")
    for phrase in infantilizing:
        if phrase in lower_text:
            scores["dignity_and_tone"] = 2
            issues.append({
                "artifact": "kit",
                "severity": "medium",
                "criterion": "dignity_and_tone",
                "description": f"Infantilizing phrase detected: {phrase}",
                "recommended_fix": "Use respectful adult language.",
            })
            break

    if "caregiver-reviewed" not in lower_text and "caregiver review" not in lower_text:
        scores["caregiver_usefulness"] = 3
        issues.append({
            "artifact": "kit",
            "severity": "low",
            "criterion": "caregiver_usefulness",
            "description": "Caregiver review notice is missing.",
            "recommended_fix": "Add a clear caregiver review notice.",
        })

    safety_failed = scores["privacy_safety"] < 5 or scores["medical_safety_boundary"] < 5
    overall_passed = not safety_failed and all(score >= 4 for score in scores.values())
    regeneration_recommended = bool(issues) and not safety_failed

    return {
        "overall_passed": overall_passed,
        "scores": scores,
        "issues": issues,
        "regeneration_recommended": regeneration_recommended,
        "regeneration_feedback": " ".join(issue["recommended_fix"] for issue in issues),
        "caregiver_review_required": True,
    }


def evaluate_memory_kit(profile: dict[str, Any], artifact_paths: dict[str, str]) -> str:
    """Evaluate Memory Bridge artifacts for safety, dignity, readability, and utility."""
    artifact_contents = _read_artifacts(artifact_paths)
    local_result = _evaluate_locally(profile, artifact_contents)
    prompt = f"""
Evaluate this Memory Bridge kit.

Rules:
{SAFETY_RULES}

Return ONLY JSON with:
overall_passed, scores, issues, regeneration_recommended,
regeneration_feedback, caregiver_review_required.

Profile JSON:
{_profile_text(profile)}

Artifact contents:
{json.dumps(artifact_contents, ensure_ascii=False, indent=2)}
"""
    generated = _generate_text_with_gemini(prompt)
    if generated:
        try:
            parsed = json.loads(_strip_json_fences(generated))
            expected_score_keys = set(local_result["scores"])
            parsed_scores = parsed.get("scores") if isinstance(parsed.get("scores"), dict) else {}
            if set(parsed_scores) != expected_score_keys:
                parsed["scores"] = local_result["scores"]
            parsed.setdefault("issues", [])
            parsed.setdefault("regeneration_recommended", False)
            parsed.setdefault("regeneration_feedback", "")
            parsed["caregiver_review_required"] = True
            if (
                local_result["scores"]["privacy_safety"] < 5
                or local_result["scores"]["medical_safety_boundary"] < 5
            ):
                parsed["overall_passed"] = False
                parsed["issues"] = local_result["issues"]
                parsed["regeneration_recommended"] = False
            else:
                parsed.setdefault("overall_passed", local_result["overall_passed"])
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except Exception:
            pass

    output_dir = Path(next(iter(artifact_paths.values()))).parent if artifact_paths else OUTPUT_ROOT
    _write_log(output_dir, f"Evaluated Memory Bridge kit. Passed: {local_result['overall_passed']}.")
    return json.dumps(local_result, ensure_ascii=False, indent=2)


def generate_orientation_board(profile: dict[str, Any], output_dir: str, feedback: str = "") -> str:
    """Generate a deterministic, printable daily orientation board PNG."""
    output_path = Path(output_dir) / "orientation_board.png"
    width, height = 1650, 1275
    margin = 70
    image = Image.new("RGB", (width, height), "#fffdf7")
    draw = ImageDraw.Draw(image)

    title_font = _font(76, bold=True)
    heading_font = _font(42, bold=True)
    body_font = _font(34)
    small_font = _font(26)

    accent = "#2f5d62"
    soft = "#e8f0ed"
    dark = "#111111"

    name = profile["person"]["preferred_name"]
    contact = _first_contact(profile)
    contact_label = normalize_string(contact.get("phone_label")) or normalize_string(contact.get("name"))
    calming = normalize_string(profile.get("calming_phrases", [""])[0])
    routine = [_format_routine_item(item) for item in profile.get("daily_routine", [])[:4]]

    draw.rectangle((0, 0, width, 160), fill=accent)
    draw.text((margin, 42), f"Hello, {name}", font=title_font, fill="#ffffff")
    draw.text((width - 490, 58), "Today is __________", font=heading_font, fill="#ffffff")

    cards = [
        ("Key Contact", contact_label or "Ask caregiver"),
        ("Today", "A calm day with familiar routines"),
        ("What Helps", calming or "Use a calm voice and familiar names"),
    ]
    card_w = (width - margin * 2 - 40) // 3
    y = 210
    for idx, (heading, text) in enumerate(cards):
        x = margin + idx * (card_w + 20)
        draw.rounded_rectangle((x, y, x + card_w, y + 230), radius=20, fill=soft, outline=accent, width=4)
        draw.text((x + 28, y + 24), heading, font=heading_font, fill=accent)
        _draw_wrapped(draw, text, x + 28, y + 88, card_w - 56, body_font, dark)

    routine_y = 500
    draw.text((margin, routine_y), "My Routine", font=heading_font, fill=accent)
    routine_y += 65
    row_h = 120
    for idx, item in enumerate(routine):
        y0 = routine_y + idx * (row_h + 18)
        draw.rounded_rectangle((margin, y0, width - margin, y0 + row_h), radius=16, fill="#ffffff", outline="#c9d8d3", width=3)
        _draw_wrapped(draw, item, margin + 32, y0 + 28, width - margin * 2 - 64, body_font, dark)

    footer = "Caregiver-reviewed support aid. Not medical advice."
    if feedback:
        footer += f" Review note: {normalize_string(feedback)}"
    draw.line((margin, height - 105, width - margin, height - 105), fill="#c9d8d3", width=3)
    _draw_wrapped(draw, footer, margin, height - 82, width - margin * 2, small_font, "#333333")

    image.save(output_path)
    _write_log(Path(output_dir), "Generated orientation_board.png.")
    return str(output_path)


def _generate_timeline_with_gemini(profile: dict[str, Any], feedback: str = "") -> bytes | None:
    client = _create_client()
    if client is None:
        return None
    event_lines = "\n".join(_format_life_event(event) for event in profile.get("life_events", []))
    prompt = f"""
Create a respectful illustrated life timeline for {profile["person"]["preferred_name"]}.

{IMAGE_SAFETY_RULES}

Use only these caregiver-provided events:
{event_lines}

Style preferences:
{json.dumps(profile.get("style_preferences", {}), ensure_ascii=False)}

Optional evaluator feedback:
{feedback}
"""
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
    except Exception:
        return None
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    return None


def _draw_timeline_fallback(profile: dict[str, Any], output_path: Path, feedback: str = "") -> None:
    width, height = 1650, 1275
    margin = 80
    image = Image.new("RGB", (width, height), "#fffdf7")
    draw = ImageDraw.Draw(image)
    title_font = _font(68, bold=True)
    heading_font = _font(36, bold=True)
    body_font = _font(30)
    small_font = _font(24)
    accent = "#6b4f8a"
    line = "#c6b7d8"
    dark = "#111111"

    name = profile["person"]["preferred_name"]
    draw.text((margin, 55), f"{name}'s Memory Timeline", font=title_font, fill=accent)
    draw.text((margin, 135), "Caregiver-provided memories for review", font=heading_font, fill=dark)

    events = profile.get("life_events", [])[:6]
    start_y = 260
    gap = 145
    x_line = margin + 90
    draw.line((x_line, start_y - 35, x_line, start_y + gap * max(len(events) - 1, 1) + 35), fill=line, width=8)

    for idx, event in enumerate(events):
        y = start_y + idx * gap
        event_text = _format_life_event(event)
        draw.ellipse((x_line - 24, y - 24, x_line + 24, y + 24), fill=accent)
        card_x = x_line + 70
        draw.rounded_rectangle((card_x, y - 50, width - margin, y + 72), radius=18, fill="#ffffff", outline=line, width=3)
        _draw_wrapped(draw, event_text, card_x + 28, y - 22, width - margin - card_x - 56, body_font, dark)

    footer = "No inferred dates or events. Caregiver review required. Not medical advice."
    if feedback:
        footer += f" Review note: {normalize_string(feedback)}"
    _draw_wrapped(draw, footer, margin, height - 92, width - margin * 2, small_font, "#333333")
    image.save(output_path)


def generate_memory_timeline(profile: dict[str, Any], output_dir: str, feedback: str = "") -> str:
    """Generate a respectful memory timeline PNG using Gemini or deterministic fallback."""
    output_path = Path(output_dir) / "memory_timeline.png"
    image_bytes = _generate_timeline_with_gemini(profile, feedback=feedback)
    if image_bytes:
        output_path.write_bytes(image_bytes)
        _write_log(Path(output_dir), "Generated memory_timeline.png with Gemini image model.")
    else:
        _draw_timeline_fallback(profile, output_path, feedback=feedback)
        _write_log(Path(output_dir), "Generated memory_timeline.png with deterministic fallback.")
    return str(output_path)


def _write_evaluation(output_dir: Path, evaluation_json: str) -> str:
    path = output_dir / "evaluation.json"
    path.write_text(evaluation_json, encoding="utf-8")
    return str(path)


def create_memory_bridge_kit(profile_path: str) -> str:
    """Create, evaluate, and return a complete caregiver-reviewed Memory Bridge kit."""
    try:
        profile = load_memory_profile(profile_path)
    except ProfileValidationError as exc:
        write_audit_event(
            "workflow_blocked",
            None,
            {"profile_path": profile_path, "reason": str(exc)},
        )
        return f"Memory Bridge workflow stopped before generation: {exc}"

    output_dir = Path(create_output_dir(profile))
    write_audit_event(
        "workflow_started",
        output_dir,
        {
            "profile_path": profile_path,
            "resident": profile.get("person", {}).get("preferred_name", ""),
            "symptom_count": len(profile.get("patient_onboarding", {}).get("observed_symptoms", [])),
        },
    )
    _write_log(output_dir, f"Starting Memory Bridge workflow for {profile_path}.")

    artifact_paths = {
        "patient_onboarding_summary": generate_patient_onboarding_summary(profile, str(output_dir)),
        "visit_prompts": generate_visit_prompts(profile, str(output_dir)),
        "caregiver_handoff": generate_caregiver_handoff(profile, str(output_dir)),
        "storyboard": plan_memory_storyboard(profile, str(output_dir)),
        "storyboard_image_prompts": generate_storyboard_image_prompts(profile, str(output_dir)),
        "orientation_board": generate_orientation_board(profile, str(output_dir)),
        "memory_timeline": generate_memory_timeline(profile, str(output_dir)),
    }
    storyboard_image_paths = generate_storyboard_images(profile, str(output_dir))
    for idx, path in enumerate(storyboard_image_paths, start=1):
        artifact_paths[f"storyboard_scene_{idx}"] = path
    for artifact_name, path in artifact_paths.items():
        write_audit_event(
            "artifact_generated",
            output_dir,
            {"artifact": artifact_name, "path": path},
        )

    evaluation_json = evaluate_memory_kit(profile, artifact_paths)
    evaluation = json.loads(evaluation_json)
    attempts = 1

    if evaluation.get("regeneration_recommended") and not any(
        issue.get("criterion") in {"privacy_safety", "medical_safety_boundary"}
        for issue in evaluation.get("issues", [])
    ):
        attempts = 2
        feedback = evaluation.get("regeneration_feedback", "Improve readability and caregiver usefulness.")
        _write_log(output_dir, "Evaluation requested one regeneration pass.")
        artifact_paths["memory_timeline"] = generate_memory_timeline(
            profile,
            str(output_dir),
            feedback=feedback,
        )
        evaluation_json = evaluate_memory_kit(profile, artifact_paths)
        evaluation = json.loads(evaluation_json)

    evaluation_path = _write_evaluation(output_dir, evaluation_json)
    _write_log(output_dir, "Memory Bridge workflow complete.")
    write_audit_event(
        "workflow_completed",
        output_dir,
        {
            "overall_passed": evaluation.get("overall_passed"),
            "attempts": attempts,
            "evaluation_path": evaluation_path,
            "artifact_count": len(artifact_paths),
            "symptom_count": len(profile.get("patient_onboarding", {}).get("observed_symptoms", [])),
        },
    )

    return (
        "Memory Bridge kit completed. "
        f"Output directory: {output_dir}. "
        f"Artifacts: {', '.join(Path(path).name for path in artifact_paths.values())}. "
        f"Evaluation: {evaluation_path}. "
        f"Overall passed: {evaluation.get('overall_passed')}. "
        f"Attempts: {attempts}. "
        "Caregiver review is required before use. Not medical advice."
    )

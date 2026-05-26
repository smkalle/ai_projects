import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from memory_bridge_agent.tools import (
    OUTPUT_ROOT,
    build_analytics_summary,
    create_memory_bridge_kit,
    read_audit_events,
)


PROFILE_DRAFT_DIR = Path("generated_memory_kits/profile_drafts")


def _split_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "resident"


def build_profile(form: dict[str, Any]) -> dict[str, Any]:
    """Build a Memory Bridge JSON profile from staff form fields."""
    life_events = [
        {"year_or_period": item.split(":", 1)[0].strip(), "event": item.split(":", 1)[1].strip(), "source": "caregiver"}
        if ":" in item
        else {"year_or_period": "Caregiver-provided", "event": item, "source": "caregiver"}
        for item in _split_lines(form["life_events"])
    ]
    routine = [
        {"time_label": item.split(":", 1)[0].strip(), "activity": item.split(":", 1)[1].strip()}
        if ":" in item
        else {"time_label": "Routine", "activity": item}
        for item in _split_lines(form["daily_routine"])
    ]
    contacts = [
        {
            "name": form["contact_name"].strip(),
            "relationship": form["contact_relationship"].strip(),
            "phone_label": form["contact_label"].strip() or f"Call {form['contact_name'].strip()}",
        }
    ]
    return {
        "consent": {
            "attestation": form["consent"],
            "provided_by": form["provided_by"].strip(),
            "relationship": form["provided_relationship"].strip(),
            "notes": form["consent_notes"].strip(),
        },
        "person": {
            "preferred_name": form["preferred_name"].strip(),
            "full_name": form["full_name"].strip(),
            "pronouns": form["pronouns"].strip(),
            "birth_decade": form["birth_decade"].strip(),
            "primary_language": form["primary_language"].strip() or "English",
            "reading_level_preference": "plain",
        },
        "contacts": contacts,
        "life_events": life_events,
        "favorite_places": _split_lines(form["favorite_places"]),
        "favorite_topics": _split_lines(form["favorite_topics"]),
        "daily_routine": routine,
        "calming_phrases": _split_lines(form["calming_phrases"]),
        "confusion_triggers": _split_lines(form["confusion_triggers"]),
        "privacy_exclusions": _split_lines(form["privacy_exclusions"]),
        "style_preferences": {
            "tone": "warm, calm, respectful",
            "visual_style": "simple, high contrast, gentle colors",
            "avoid": ["childlike language", "busy backgrounds"],
        },
        "caregiver_notes": form["caregiver_notes"].strip(),
        "patient_onboarding": {
            "observed_symptoms": _split_lines(form.get("observed_symptoms", "")),
            "symptom_context": _split_lines(form.get("symptom_context", "")),
            "staff_goals": _split_lines(form.get("staff_goals", "")),
            "non_diagnostic_notes": form.get("non_diagnostic_notes", "").strip(),
        },
    }


def save_profile(profile: dict[str, Any]) -> Path:
    """Save a generated staff-form profile for workflow ingestion."""
    PROFILE_DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    name = _safe_slug(profile["person"]["preferred_name"])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = PROFILE_DRAFT_DIR / f"{name}_{stamp}.json"
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def latest_kit_dir() -> Path | None:
    if not OUTPUT_ROOT.exists():
        return None
    dirs = [path for path in OUTPUT_ROOT.iterdir() if path.is_dir() and path.name != "profile_drafts"]
    return max(dirs, key=lambda path: path.stat().st_mtime) if dirs else None


def render_markdown_file(path: Path) -> None:
    if path.exists():
        st.markdown(path.read_text(encoding="utf-8"))
    else:
        st.warning(f"Missing {path.name}")


def render_kit(kit_dir: Path) -> None:
    st.subheader("Generated Memory Bridge Kit")
    st.caption(str(kit_dir))

    evaluation_path = kit_dir / "evaluation.json"
    if evaluation_path.exists():
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        if evaluation.get("overall_passed"):
            st.success("Safety evaluation passed. Caregiver review is still required.")
        else:
            st.error("Safety evaluation did not pass. Do not use until reviewed.")
        st.json(evaluation)

    image_col, timeline_col = st.columns(2)
    with image_col:
        st.markdown("### Orientation Board")
        if (kit_dir / "orientation_board.png").exists():
            st.image(str(kit_dir / "orientation_board.png"), use_container_width=True)
    with timeline_col:
        st.markdown("### Memory Timeline")
        if (kit_dir / "memory_timeline.png").exists():
            st.image(str(kit_dir / "memory_timeline.png"), use_container_width=True)

    storyboard_images = sorted(kit_dir.glob("storyboard_scene_*.png"))
    if storyboard_images:
        st.markdown("### Storyboard Images")
        cols = st.columns(min(3, len(storyboard_images)))
        for idx, path in enumerate(storyboard_images):
            with cols[idx % len(cols)]:
                st.image(str(path), caption=path.name, use_container_width=True)

    tab_onboarding, tab_prompts, tab_image_prompts, tab_handoff, tab_story, tab_log = st.tabs(
        [
            "Patient Onboarding",
            "Visit Prompts",
            "Storyboard Image Prompts",
            "Caregiver Handoff",
            "Storyboard",
            "Run Log",
        ]
    )
    with tab_onboarding:
        render_markdown_file(kit_dir / "patient_onboarding_summary.md")
    with tab_prompts:
        render_markdown_file(kit_dir / "visit_prompts.md")
    with tab_image_prompts:
        render_markdown_file(kit_dir / "storyboard_image_prompts.md")
    with tab_handoff:
        render_markdown_file(kit_dir / "caregiver_handoff.md")
    with tab_story:
        render_markdown_file(kit_dir / "storyboard.md")
    with tab_log:
        render_markdown_file(kit_dir / "run_log.txt")


def main() -> None:
    st.set_page_config(page_title="Memory Bridge Staff Prototype", layout="wide")
    st.title("Memory Bridge Staff Prototype")
    st.write("Create caregiver-reviewed orientation, reminiscence, and handoff materials.")
    st.warning(
        "Prototype boundary: not diagnosis, treatment, medication advice, emergency guidance, "
        "monitoring, or cognitive scoring. Caregiver review is required before use."
    )

    setup_tab, run_tab, safety_tab, review_tab, analytics_tab = st.tabs(
        [
            "Patient Onboarding",
            "Run Demo",
            "Safety Checks",
            "Review Latest Kit",
            "Monitoring Dashboard",
        ]
    )

    with setup_tab:
        st.subheader("Patient Onboarding Intake")
        st.caption("Symptoms are recorded as staff/caregiver observations only. This is not diagnosis or triage.")
        with st.form("resident_profile_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                preferred_name = st.text_input("Preferred name", value="Maria")
                full_name = st.text_input("Full name", value="Maria Alvarez")
                pronouns = st.text_input("Pronouns", value="she/her")
                birth_decade = st.text_input("Birth decade", value="1940s")
                primary_language = st.text_input("Primary language", value="English")
            with col_b:
                consent = st.checkbox("Consent or authorized caregiver attestation is confirmed", value=True)
                provided_by = st.text_input("Profile provided by", value="Jane Alvarez")
                provided_relationship = st.text_input("Relationship", value="daughter")
                consent_notes = st.text_input("Consent notes", value="Reviewed with Maria where possible.")

            st.markdown("### Key Contact")
            contact_name = st.text_input("Contact name", value="Jane")
            contact_relationship = st.text_input("Contact relationship", value="daughter")
            contact_label = st.text_input("Contact label", value="Call Jane")

            st.markdown("### Life and Routine")
            life_events = st.text_area(
                "Life events, one per line. Use 'year: event' when known.",
                value=(
                    "1968: Moved to Chicago\n"
                    "1972: Opened a small neighborhood bakery\n"
                    "1980s: Hosted Sunday dinners for extended family\n"
                    "2005: Started volunteering in St. Mary's garden"
                ),
                height=130,
            )
            daily_routine = st.text_area(
                "Daily routine, one per line. Use 'time: activity'.",
                value="Morning: Breakfast, tea, and newspaper\nAfternoon: Short walk or garden visit\nEvening: Music and family phone call",
                height=110,
            )

            col_c, col_d = st.columns(2)
            with col_c:
                favorite_places = st.text_area("Favorite places", value="Chicago lakefront\nfamily kitchen\nSt. Mary's garden")
                favorite_topics = st.text_area("Favorite topics", value="gardening\nbaking pan dulce\nold neighborhood stories")
                calming_phrases = st.text_area(
                    "Calming phrases",
                    value="You are safe. Jane will visit this afternoon.\nYour tea is ready and your family knows where you are.",
                )
            with col_d:
                confusion_triggers = st.text_area("Confusion triggers", value="Too many people speaking at once\nRushed schedule changes")
                privacy_exclusions = st.text_area("Private topics to exclude", value="Do not mention finances\nDo not mention estranged relatives")
                caregiver_notes = st.text_area("Caregiver notes", value="Use large text. Avoid medical claims.")

            st.markdown("### Observed Symptoms and Onboarding Context")
            st.info("Enter observations only. Do not ask the prototype to diagnose, triage, or recommend treatment.")
            col_e, col_f = st.columns(2)
            with col_e:
                observed_symptoms = st.text_area(
                    "Observed symptoms or concerns, one per line",
                    value="Occasional confusion in busy rooms\nRepeats questions when schedule changes\nLooks for daughter in late afternoon",
                    height=110,
                )
                symptom_context = st.text_area(
                    "Context around symptoms, one per line",
                    value="More comfortable with one speaker at a time\nCalmer after tea and familiar music",
                    height=90,
                )
            with col_f:
                staff_goals = st.text_area(
                    "Staff goals for onboarding kit",
                    value="Create orientation board for room\nCreate prompts for family visits\nCreate handoff notes for new staff",
                    height=110,
                )
                non_diagnostic_notes = st.text_area(
                    "Non-diagnostic staff notes",
                    value="Use facility protocol for any clinical concern.",
                    height=90,
                )

            submitted = st.form_submit_button("Create Kit", type="primary")

        if submitted:
            profile = build_profile(locals())
            profile_path = save_profile(profile)
            with st.spinner("Generating Memory Bridge kit..."):
                result = create_memory_bridge_kit(str(profile_path))
            st.session_state["last_result"] = result
            st.success("Workflow finished.")
            st.code(result)
            kit_dir = latest_kit_dir()
            if kit_dir:
                render_kit(kit_dir)

    with run_tab:
        st.subheader("One-Click Demo")
        st.write("Use the fictional Maria profile for a safe walkthrough.")
        if st.button("Run sample Memory Bridge kit", type="primary"):
            with st.spinner("Generating sample kit..."):
                result = create_memory_bridge_kit("examples/memory_profiles/maria_valid.json")
            st.session_state["last_result"] = result
            st.code(result)
        if st.session_state.get("last_result"):
            st.markdown("### Last Result")
            st.code(st.session_state["last_result"])

    with safety_tab:
        st.subheader("Safety Block Demonstrations")
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("Test missing consent block"):
                st.code(create_memory_bridge_kit("examples/memory_profiles/missing_consent.json"))
        with col_2:
            if st.button("Test unsafe medical request block"):
                st.code(create_memory_bridge_kit("examples/memory_profiles/unsafe_medical_request.json"))

    with review_tab:
        kit_dir = latest_kit_dir()
        if kit_dir:
            render_kit(kit_dir)
        else:
            st.info("No kit generated yet.")

    with analytics_tab:
        st.subheader("Monitoring and Analytics Dashboard")
        summary = build_analytics_summary()
        metric_cols = st.columns(5)
        metric_cols[0].metric("Runs Started", summary["runs_started"])
        metric_cols[1].metric("Completed", summary["runs_completed"])
        metric_cols[2].metric("Blocked", summary["runs_blocked"])
        metric_cols[3].metric("Passed Kits", summary["kits_passed"])
        metric_cols[4].metric("Artifacts", summary["artifacts_generated"])

        st.markdown("### Safety Blocks")
        st.json(summary["safety_blocks_by_reason"])

        st.markdown("### Audit Log")
        events = read_audit_events(limit=200)
        if events:
            st.dataframe(
                [
                    {
                        "timestamp": event.get("timestamp"),
                        "event_type": event.get("event_type"),
                        "output_dir": event.get("output_dir"),
                        "details": json.dumps(event.get("details", {}), ensure_ascii=False),
                    }
                    for event in reversed(events)
                ],
                use_container_width=True,
            )
        else:
            st.info("No audit events yet.")


if __name__ == "__main__":
    main()

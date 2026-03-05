"""Streamlit app for the Medical Diagnostic Workbench.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.
All outputs are AI-generated simulations for developer education.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure package is importable when run directly by streamlit
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from PIL import Image

from gemini_explorer.client import (
    MODEL,
    THINKING_LEVELS,
    get_client,
    get_usage,
    make_config,
    trace_log,
    traced_generate,
)
from gemini_explorer.medical.cases import SAMPLE_CASES
from gemini_explorer.medical.schemas import PatientIntake, Vitals
from gemini_explorer.medical.tools import check_hardcoded_red_flags

st.set_page_config(page_title="Medical Diagnostic Workbench", page_icon="🏥", layout="wide")

DISCLAIMER = (
    "EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE. "
    "All outputs are AI-generated simulations. Not for patient care."
)


# ── Trace log sidebar (adapted from app.py) ──────────────────────────────────


def render_trace_log():
    """Render the API trace log in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.subheader("API Trace Log")
        if st.button("Clear log", key="clear_trace"):
            trace_log.clear()
        for entry in reversed(trace_log.entries[-20:]):
            status_icon = {"ok": "✅", "pending": "⏳", "ok (streamed)": "🌊"}.get(entry.get("status", ""), "❌")
            label = f"{status_icon} {entry.get('method', '?')} ({entry.get('duration_ms', '?')}ms)"
            with st.expander(label, expanded=False):
                if entry.get("config_summary"):
                    st.json(entry["config_summary"])
                if entry.get("usage"):
                    st.json(entry["usage"])
                if entry.get("error"):
                    st.error(entry["error"])


# ── Page: Disclaimer ──────────────────────────────────────────────────────────


def page_disclaimer():
    st.title("Medical Diagnostic Workbench")
    st.markdown("### An Agentic AI Demo Using Google ADK + Gemini 3.1 Flash-Lite")
    st.markdown("---")

    st.error(
        "**EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE**\n\n"
        "This application demonstrates AI agentic patterns using Google ADK "
        "and Gemini 3.1 Flash-Lite. All outputs are AI-generated simulations.\n\n"
        "**DO NOT** use this tool for:\n"
        "- Actual medical diagnosis\n"
        "- Patient care decisions\n"
        "- Medical treatment\n"
        "- Any clinical purpose\n\n"
        "If you have a medical emergency, **call 911 immediately**."
    )

    st.markdown(
        "**This application demonstrates:**\n"
        "- **SequentialAgent**: 5-stage diagnostic pipeline\n"
        "- **ParallelAgent**: Concurrent symptom + imaging analysis\n"
        "- **LoopAgent**: Iterative diagnosis refinement with critic feedback\n"
        "- **LLM-based routing**: Dynamic specialist consultation\n"
        "- **Function calling**: Drug interactions, BMI, eGFR, ICD-10 lookup\n"
        "- **Vision**: Medical image analysis\n"
        "- **Structured output**: Pydantic schemas for clinical data\n"
        "- **Thinking levels**: Adjustable reasoning depth"
    )

    accepted = st.checkbox("I understand this is an educational demo and will not use outputs for clinical purposes")
    if st.button("Proceed to Demo", disabled=not accepted, type="primary"):
        st.session_state["disclaimer_accepted"] = True
        st.rerun()


# ── Page: Run Pipeline ────────────────────────────────────────────────────────


def page_pipeline():
    st.title("Run Diagnostic Pipeline")
    st.error(DISCLAIMER)

    # ── Case selection / input ────────────────────────────────────────────
    tab_sample, tab_custom = st.tabs(["Load Sample Case", "Custom Input"])

    with tab_sample:
        case_key = st.selectbox("Select a sample case:", list(SAMPLE_CASES.keys()), format_func=lambda k: SAMPLE_CASES[k].case_name)
        if st.button("Load Case", key="load_sample"):
            st.session_state["current_case"] = SAMPLE_CASES[case_key]
            st.session_state["case_image"] = None

    with tab_custom:
        col1, col2 = st.columns([2, 1])
        with col1:
            case_name = st.text_input("Case name", "Custom Case")
            age = st.number_input("Age", min_value=0, max_value=120, value=45)
            sex = st.selectbox("Sex", ["male", "female", "other"])
            complaint = st.text_area("Chief complaint", height=120, placeholder="Describe symptoms...")
            history = st.text_area("Medical history (comma-separated)", placeholder="hypertension, diabetes...")
            meds = st.text_area("Current medications (comma-separated)", placeholder="lisinopril 10mg, metformin...")
            allergies_text = st.text_input("Allergies (comma-separated)", placeholder="penicillin...")

        with col2:
            st.subheader("Multimodal Input")
            image_upload = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp"])
            if image_upload:
                img = Image.open(image_upload)
                st.image(img, use_container_width=True)

            audio_upload = st.file_uploader("Upload audio", type=["mp3", "wav", "ogg", "flac"])
            if audio_upload:
                st.audio(audio_upload)

        with st.expander("Vitals (optional)"):
            v_cols = st.columns(4)
            temp = v_cols[0].number_input("Temp (C)", value=0.0, step=0.1, format="%.1f")
            hr = v_cols[1].number_input("Heart rate", value=0, step=1)
            bp_sys = v_cols[2].number_input("BP systolic", value=0, step=1)
            bp_dia = v_cols[3].number_input("BP diastolic", value=0, step=1)

        if st.button("Save Custom Case"):
            vitals = None
            if any([temp, hr, bp_sys]):
                vitals = Vitals(
                    temperature_c=temp or None,
                    heart_rate_bpm=hr or None,
                    blood_pressure_systolic=bp_sys or None,
                    blood_pressure_diastolic=bp_dia or None,
                )
            case = PatientIntake(
                patient_id="custom_user",
                age=age,
                sex=sex,
                chief_complaint=complaint,
                symptoms=[s.strip() for s in complaint.split(",") if s.strip()],
                medical_history=[h.strip() for h in history.split(",") if h.strip()],
                current_medications=[m.strip() for m in meds.split(",") if m.strip()],
                allergies=[a.strip() for a in allergies_text.split(",") if a.strip()],
                vitals=vitals,
                has_image=image_upload is not None,
                has_audio=audio_upload is not None,
                case_name=case_name,
            )
            st.session_state["current_case"] = case
            st.session_state["case_image"] = image_upload.read() if image_upload else None
            st.success("Case saved!")

    # ── Pipeline execution ────────────────────────────────────────────────
    st.markdown("---")

    case = st.session_state.get("current_case")
    if not case:
        st.info("Load a sample case or create a custom case above to proceed.")
        return

    st.subheader(f"Current Case: {case.case_name}")
    with st.expander("Case Details", expanded=False):
        st.json(json.loads(case.model_dump_json()))

    # Red flag check
    red_flags = check_hardcoded_red_flags(case.symptoms, case.chief_complaint)
    if red_flags:
        for flag in red_flags:
            st.error(f"**RED FLAG**: {flag['message']}")

    if not st.button("Run Full Pipeline", type="primary", key="run_pipeline"):
        return

    st.error(DISCLAIMER)
    image_bytes = st.session_state.get("case_image")

    from gemini_explorer.medical.agents import MedicalPipelineRunner

    runner = MedicalPipelineRunner()

    # Agent name → display info
    AGENT_STAGES = {
        "TriageAgent": ("Stage 1: Triage", "LlmAgent", 1),
        "SymptomAnalysisAgent": ("Stage 2a: Symptom Analysis", "ParallelAgent", 2),
        "ImagingAnalysisAgent": ("Stage 2b: Imaging Analysis", "ParallelAgent", 2),
        "DiagnosisGeneratorAgent": ("Stage 3: Diagnosis", "LoopAgent", 3),
        "DiagnosisCriticAgent": ("Stage 3: Diagnosis Critic", "LoopAgent", 3),
        "SpecialistRouterAgent": ("Stage 4: Specialist Router", "LlmAgent (Router)", 4),
        "CardiologyAgent": ("Stage 4: Cardiology", "LlmAgent (Router)", 4),
        "DermatologyAgent": ("Stage 4: Dermatology", "LlmAgent (Router)", 4),
        "PediatricsAgent": ("Stage 4: Pediatrics", "LlmAgent (Router)", 4),
        "GeneralMedicineAgent": ("Stage 4: General Medicine", "LlmAgent (Router)", 4),
        "CaseSummaryAgent": ("Stage 5: Case Summary", "LlmAgent", 5),
    }

    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.container()

    events = []
    seen_agents = set()
    start = time.time()

    async def _run():
        async for event in runner.run_async(case, image_bytes=image_bytes):
            events.append(event)
            # Track which agent produced this event
            author = getattr(event, "author", None) or ""
            if author and author not in seen_agents:
                seen_agents.add(author)
                info = AGENT_STAGES.get(author)
                if info:
                    label, atype, stage_num = info
                    pct = min(int(stage_num / 5 * 100), 99)
                    progress_bar.progress(pct)
                    elapsed_so_far = time.time() - start
                    status_text.text(f"[{elapsed_so_far:.0f}s] {label} ({atype})...")
                    with log_container:
                        st.caption(f"▶ {label} — {atype} ({elapsed_so_far:.1f}s)")

    status_text.text("Starting pipeline...")
    try:
        asyncio.run(_run())
    except Exception as e:
        st.error(f"Pipeline error: {e}")
        return

    elapsed = time.time() - start
    progress_bar.progress(100)
    status_text.text(f"Pipeline complete in {elapsed:.1f}s — {len(events)} events, {len(seen_agents)} agents")

    # Get final state
    state = asyncio.run(runner.get_state(case.patient_id))

    # ── Display results by stage ──────────────────────────────────────────

    stage_keys = [
        ("Stage 1: Triage", "triage_result", "LlmAgent", "json"),
        ("Stage 2a: Symptom Analysis", "symptom_analysis", "ParallelAgent", "markdown"),
        ("Stage 2b: Imaging Analysis", "imaging_findings", "ParallelAgent", "json"),
        ("Stage 3: Differential Diagnosis", "differential_dx", "LoopAgent", "json"),
        ("Stage 4: Specialist Opinion", "specialist_opinion", "LlmAgent (Router)", "markdown"),
        ("Stage 5: Case Summary", "case_summary", "LlmAgent", "markdown"),
    ]

    badge_colors = {
        "LlmAgent": "blue",
        "ParallelAgent": "green",
        "LoopAgent": "orange",
        "LlmAgent (Router)": "violet",
    }

    for stage_label, key, agent_type, display_mode in stage_keys:
        value = state.get(key, "")
        has_output = bool(value and value.strip())
        color = badge_colors.get(agent_type, "gray")

        with st.expander(f"{'✅' if has_output else '⚪'} {stage_label}", expanded=(key == "case_summary")):
            st.caption(f"Agent type: :{color}[{agent_type}]")

            if not has_output:
                st.info("No output from this stage.")
                continue

            value_str = str(value)

            if display_mode == "json":
                # Structured data — show as JSON, fall back to markdown
                try:
                    parsed = json.loads(value_str)
                    st.json(parsed)
                except (json.JSONDecodeError, TypeError):
                    st.markdown(value_str[:3000])
            else:
                # Free-text — show as markdown, with JSON in a nested expander
                st.markdown(value_str[:3000])
                try:
                    parsed = json.loads(value_str)
                    with st.expander("Raw JSON", expanded=False):
                        st.json(parsed)
                except (json.JSONDecodeError, TypeError):
                    pass

            st.caption(DISCLAIMER)

    st.markdown("---")
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Total Pipeline Time", f"{elapsed:.1f}s")
    col_m2.metric("Total Events", len(events))


# ── Page: Sample Cases Gallery ────────────────────────────────────────────────


def page_gallery():
    st.title("Sample Cases Gallery")
    st.error(DISCLAIMER)

    case_info = {
        "chest_pain": {
            "emoji": "❤️",
            "capabilities": ["Red flag detection", "Cardiology routing", "TIMI risk score", "Drug interactions"],
            "expected": "EMERGENT → Cardiology",
        },
        "skin_lesion": {
            "emoji": "🔬",
            "capabilities": ["Vision (image analysis)", "ABCDE criteria", "Dermatology routing"],
            "expected": "SEMI-URGENT → Dermatology",
        },
        "pediatric_fever": {
            "emoji": "👶",
            "capabilities": ["Pediatric considerations", "Broad differential", "Loop runs 2+ iterations"],
            "expected": "URGENT → Pediatrics",
        },
        "chronic_fatigue": {
            "emoji": "🧠",
            "capabilities": ["HIGH thinking level", "Complex differential", "Loop runs 3 iterations", "Audio input"],
            "expected": "NON-URGENT → General Medicine",
        },
    }

    cols = st.columns(2)
    for i, (key, case) in enumerate(SAMPLE_CASES.items()):
        info = case_info.get(key, {})
        with cols[i % 2]:
            with st.container(border=True):
                st.subheader(f"{info.get('emoji', '')} {case.case_name}")
                st.text(f"Patient: {case.age}y {case.sex} | ID: {case.patient_id}")
                st.text(f"Expected: {info.get('expected', 'N/A')}")
                st.caption(case.chief_complaint[:150] + "...")

                st.markdown("**Capabilities demonstrated:**")
                for cap in info.get("capabilities", []):
                    st.markdown(f"- {cap}")

                if st.button(f"Load & Run →", key=f"load_{key}"):
                    st.session_state["current_case"] = case
                    st.session_state["case_image"] = None
                    st.session_state["page"] = "Run Pipeline"
                    st.rerun()


# ── Main app ──────────────────────────────────────────────────────────────────


def main():
    # Sidebar
    with st.sidebar:
        st.title("🏥 Medical Workbench")
        st.caption(f"Model: `{MODEL}`")
        st.caption("ADK: `google-adk`")
        st.error("**NOT FOR CLINICAL USE**")

        if not st.session_state.get("disclaimer_accepted"):
            st.warning("Please accept the disclaimer to proceed.")
        else:
            page = st.radio(
                "Navigate",
                ["Run Pipeline", "Sample Cases", "About & Disclaimer"],
                key="page",
            )

    # Render trace log
    render_trace_log()

    # Page routing
    if not st.session_state.get("disclaimer_accepted"):
        page_disclaimer()
    else:
        page = st.session_state.get("page", "Run Pipeline")
        if page == "Run Pipeline":
            page_pipeline()
        elif page == "Sample Cases":
            page_gallery()
        elif page == "About & Disclaimer":
            page_disclaimer()


if __name__ == "__main__":
    main()
else:
    main()

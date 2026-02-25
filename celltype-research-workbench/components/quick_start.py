"""Quick Start Tutorial — interactive guided walkthrough of the workbench."""

import streamlit as st

from utils.examples import (
    TUTORIAL_STEPS,
    TARGET_EXAMPLES,
    BIOMARKER_EXAMPLES,
    COMBINATION_EXAMPLES,
    LITERATURE_EXAMPLES,
    MOLECULAR_EXAMPLES,
    CHAT_EXAMPLES,
)


def render_quick_start():
    """Render the interactive quick start tutorial and example gallery."""
    st.title("🚀 Quick Start")
    st.caption("Interactive tutorial and ready-to-load examples for every workflow.")

    tab_tutorial, tab_examples = st.tabs([
        "📖 Step-by-Step Tutorial", "📦 Example Gallery",
    ])

    with tab_tutorial:
        _render_tutorial()

    with tab_examples:
        _render_example_gallery()


# ---------------------------------------------------------------------------
# Tutorial
# ---------------------------------------------------------------------------

def _render_tutorial():
    """Render the step-by-step interactive tutorial."""
    st.subheader("Getting Started in 7 Steps")

    # Track tutorial progress
    if "tutorial_step" not in st.session_state:
        st.session_state["tutorial_step"] = 1

    current = st.session_state["tutorial_step"]

    # Progress bar
    progress = (current - 1) / (len(TUTORIAL_STEPS) - 1)
    st.progress(progress, text=f"Step {current} of {len(TUTORIAL_STEPS)}")

    # Display current step
    step = TUTORIAL_STEPS[current - 1]

    with st.container(border=True):
        st.markdown(f"### {step['icon']} Step {step['step']}: {step['title']}")
        st.markdown(step["content"])

        # Navigation action
        if step.get("action"):
            page_names = {
                "settings": "⚙️ Settings",
                "agent": "🔬 Research Agent",
                "target": "🎯 Target Prioritization",
                "data_explorer": "📊 Data Explorer",
                "reports": "📝 Reports & Sessions",
            }
            page_label = page_names.get(step["action"], step["action"])
            st.info(f"Navigate to **{page_label}** from the sidebar to try this.")

        # Example query if provided
        if step.get("example_query"):
            st.markdown("**Try this query:**")
            st.code(step["example_query"], language="text")

    # Navigation buttons
    col_prev, col_spacer, col_next = st.columns([1, 2, 1])
    with col_prev:
        if current > 1:
            if st.button("← Previous", use_container_width=True):
                st.session_state["tutorial_step"] = current - 1
                st.rerun()
    with col_next:
        if current < len(TUTORIAL_STEPS):
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state["tutorial_step"] = current + 1
                st.rerun()
        else:
            if st.button("Finish Tutorial", type="primary", use_container_width=True):
                st.session_state["tutorial_step"] = 1
                st.balloons()

    # Step selector (jump to any step)
    with st.expander("Jump to step"):
        cols = st.columns(len(TUTORIAL_STEPS))
        for i, s in enumerate(TUTORIAL_STEPS):
            with cols[i]:
                label = f"{s['icon']}"
                is_current = (i + 1) == current
                if st.button(
                    label,
                    key=f"jump_{i}",
                    use_container_width=True,
                    type="primary" if is_current else "secondary",
                    help=s["title"],
                ):
                    st.session_state["tutorial_step"] = i + 1
                    st.rerun()


# ---------------------------------------------------------------------------
# Example Gallery
# ---------------------------------------------------------------------------

def _render_example_gallery():
    """Render the browsable example gallery with load-into-workflow buttons."""
    st.subheader("Example Gallery")
    st.markdown(
        "Browse pre-built examples for every workflow. "
        "Click **Load Example** to populate a workflow's configuration, then "
        "navigate to that workflow from the sidebar."
    )

    # ----- Target Prioritization -----
    st.markdown("---")
    st.markdown("#### 🎯 Target Prioritization")
    for name, ex in TARGET_EXAMPLES.items():
        with st.container(border=True):
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{name}**")
                st.caption(ex["description"])
            with col_btn:
                if st.button("Load", key=f"load_target_{name}", use_container_width=True):
                    st.session_state["target_config"] = ex["config"]
                    st.session_state["_loaded_example"] = f"target: {name}"
                    st.success(f"Loaded! Go to **Target Prioritization** in the sidebar.")

            with st.expander("Preview query & expected output"):
                st.markdown("**Agent Query:**")
                st.code(ex["query"], language="text")
                if "expected_result" in ex:
                    st.markdown("**Expected Output (sample):**")
                    st.dataframe(ex["expected_result"], use_container_width=True, hide_index=True)

    # ----- Resistance Biomarkers -----
    st.markdown("---")
    st.markdown("#### 🧪 Resistance Biomarkers")
    for name, ex in BIOMARKER_EXAMPLES.items():
        with st.container(border=True):
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{name}**")
                st.caption(ex["description"])
            with col_btn:
                if st.button("Load", key=f"load_bio_{name}", use_container_width=True):
                    st.session_state["biomarker_config"] = ex["config"]
                    st.session_state["_loaded_example"] = f"biomarker: {name}"
                    st.success(f"Loaded! Go to **Resistance Biomarkers** in the sidebar.")

            with st.expander("Preview query & expected output"):
                st.markdown("**Agent Query:**")
                st.code(ex["query"], language="text")
                if "expected_result" in ex:
                    st.markdown("**Expected Output (sample):**")
                    st.dataframe(ex["expected_result"], use_container_width=True, hide_index=True)

    # ----- Combination Strategy -----
    st.markdown("---")
    st.markdown("#### 💊 Combination Strategy")
    for name, ex in COMBINATION_EXAMPLES.items():
        with st.container(border=True):
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{name}**")
                st.caption(ex["description"])
            with col_btn:
                if st.button("Load", key=f"load_combo_{name}", use_container_width=True):
                    st.session_state["combo_config"] = ex["config"]
                    st.session_state["_loaded_example"] = f"combination: {name}"
                    st.success(f"Loaded! Go to **Combination Strategy** in the sidebar.")

            with st.expander("Preview query & expected output"):
                st.markdown("**Agent Query:**")
                st.code(ex["query"], language="text")
                if "expected_result" in ex:
                    st.markdown("**Expected Output (sample):**")
                    st.dataframe(ex["expected_result"], use_container_width=True, hide_index=True)

    # ----- Literature Synthesis -----
    st.markdown("---")
    st.markdown("#### 📚 Literature Synthesis")
    for name, ex in LITERATURE_EXAMPLES.items():
        with st.container(border=True):
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{name}**")
                st.caption(ex["description"])
            with col_btn:
                if st.button("Load", key=f"load_lit_{name}", use_container_width=True):
                    st.session_state["lit_config"] = ex["config"]
                    st.session_state["_loaded_example"] = f"literature: {name}"
                    st.success(f"Loaded! Go to **Literature Synthesis** in the sidebar.")

            with st.expander("Preview query"):
                st.code(ex["query"], language="text")

    # ----- Molecular Design -----
    st.markdown("---")
    st.markdown("#### 🧬 Molecular Design")
    for name, ex in MOLECULAR_EXAMPLES.items():
        with st.container(border=True):
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{name}**")
                st.caption(ex["description"])
            with col_btn:
                if st.button("Load", key=f"load_mol_{name}", use_container_width=True):
                    st.session_state["_molecular_example_query"] = ex["query"]
                    st.session_state["_loaded_example"] = f"molecular: {name}"
                    st.success(f"Loaded! Go to **Molecular Design → Free-Form Agent** in the sidebar.")

            with st.expander("Preview query"):
                st.code(ex["query"], language="text")

    # ----- Agent Chat -----
    st.markdown("---")
    st.markdown("#### 🔬 Research Agent Chat")
    cols = st.columns(2)
    for i, ex in enumerate(CHAT_EXAMPLES):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{ex['title']}**")
                st.caption(ex["description"])
                st.code(ex["query"], language="text")

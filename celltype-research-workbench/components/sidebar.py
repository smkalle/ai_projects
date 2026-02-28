"""Sidebar navigation and status display."""

import streamlit as st

from utils.config import WorkbenchConfig
from utils.celltype_agent import check_celltype_installed
from components.design_system import render_section_header, render_status_badge


def check_config_health() -> dict:
    """Quick health check for sidebar status."""
    config = WorkbenchConfig.load()
    ct = check_celltype_installed()
    return {
        "api_key": bool(config.anthropic_api_key),
        "cli": ct["installed"],
        "model": config.default_model,
    }


def render_sidebar() -> str:
    """Render the sidebar and return the selected page."""
    with st.sidebar:
        # Branding — display font, restrained
        st.markdown(
            """
            <div style="text-align:center; padding: 8px 0 16px 0;">
                <h2 style="margin:0; font-family: var(--font-display); font-weight:700; letter-spacing:-0.02em;">
                    🧬 CellType
                </h2>
                <p style="margin:4px 0 0 0; font-size:0.8rem; color:var(--text-tertiary); font-family:var(--font-body);">
                    Research Workbench
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Grouped navigation (brain: 5-7 items max per nav group)
        # Section 1: Research
        render_section_header("Research")

        research_pages = {
            "🏠 Dashboard": "dashboard",
            "🚀 Quick Start": "quick_start",
            "🔬 Research Agent": "agent",
        }

        # Section 2: Workflows
        workflow_pages = {
            "🎯 Target Prioritization": "target",
            "🧪 Resistance Biomarkers": "biomarker",
            "💊 Combination Strategy": "combination",
            "📚 Literature Synthesis": "literature",
            "🧬 Molecular Design": "molecular",
        }

        # Section 3: Data & Reports
        data_pages = {
            "📊 Data Explorer": "data_explorer",
            "📁 Data Management": "data_mgmt",
            "📝 Reports & Sessions": "reports",
        }

        # Section 4: System
        system_pages = {
            "⚙️ Settings": "settings",
            "❓ Help": "help",
        }

        # Merge all for radio — Streamlit radio needs a single flat list
        all_pages = {}
        all_pages.update(research_pages)
        all_pages.update(workflow_pages)
        all_pages.update(data_pages)
        all_pages.update(system_pages)

        # Build formatted options with section separators
        options = []
        for label in research_pages:
            options.append(label)

        render_section_header("Workflows")
        for label in workflow_pages:
            options.append(label)

        render_section_header("Data & Reports")
        for label in data_pages:
            options.append(label)

        render_section_header("System")
        for label in system_pages:
            options.append(label)

        selected = st.radio(
            "Navigation",
            options,
            label_visibility="collapsed",
        )

        st.divider()

        # Session info — compact KPI row
        st.markdown(
            '<p class="nav-section-header">Session</p>',
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", st.session_state.get("query_count", 0))
        with col2:
            cost = st.session_state.get("total_cost", 0.0)
            st.metric("Cost", f"${cost:.3f}")

        # System status — badges instead of st.success/st.warning
        st.markdown(
            '<p class="nav-section-header">Status</p>',
            unsafe_allow_html=True,
        )
        health = check_config_health()

        api_badge = render_status_badge("API Key ✓", "success") if health["api_key"] else render_status_badge("API Key Missing", "warning")
        cli_badge = render_status_badge("CLI ✓", "success") if health["cli"] else render_status_badge("CLI Not Found", "default")
        model_short = health["model"].split("-")[1].title() if "-" in health["model"] else health["model"]
        model_badge = render_status_badge(model_short, "accent")

        st.markdown(f"{api_badge}  {cli_badge}  {model_badge}", unsafe_allow_html=True)

        st.divider()
        st.caption("v1.0.0 · [celltype-cli](https://github.com/celltype/cli)")

    return all_pages[selected]

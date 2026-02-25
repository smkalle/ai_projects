"""Sidebar navigation and status display."""

import streamlit as st

from utils.config import WorkbenchConfig
from utils.celltype_agent import check_celltype_installed


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
        st.markdown(
            """
            <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
                <h2 style="margin:0;">🧬 CellType</h2>
                <p style="margin:0; font-size:0.85rem; color:#888;">Research Workbench</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        pages = {
            "🏠 Dashboard": "dashboard",
            "🔬 Research Agent": "agent",
            "🎯 Target Prioritization": "target",
            "🧪 Resistance Biomarkers": "biomarker",
            "💊 Combination Strategy": "combination",
            "📚 Literature Synthesis": "literature",
            "🧬 Molecular Design": "molecular",
            "📊 Data Explorer": "data_explorer",
            "📁 Data Management": "data_mgmt",
            "📝 Reports & Sessions": "reports",
            "⚙️ Settings": "settings",
            "❓ Help & Tutorial": "help",
        }

        selected = st.radio(
            "Navigation",
            list(pages.keys()),
            label_visibility="collapsed",
        )

        st.divider()

        # Session status
        st.markdown("##### Session Info")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", st.session_state.get("query_count", 0))
        with col2:
            cost = st.session_state.get("total_cost", 0.0)
            st.metric("Cost", f"${cost:.3f}")

        # System status indicators
        st.markdown("##### System Status")
        health = check_config_health()

        if health["api_key"]:
            st.success("API Key ✓", icon="🔑")
        else:
            st.warning("API Key Missing", icon="🔑")

        if health["cli"]:
            st.success("celltype-cli ✓", icon="🖥️")
        else:
            st.info("CLI Not Installed", icon="🖥️")

        st.caption(f"Model: `{health['model']}`")

        st.divider()
        st.caption("v1.0.0 — Built with Streamlit")
        st.caption("[celltype-cli](https://github.com/celltype/cli)")

    return pages[selected]

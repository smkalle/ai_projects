"""
CellType Research Workbench
===========================
An interactive bioinformatics research workbench powered by celltype-cli —
the autonomous AI agent for drug discovery.

Launch:
    streamlit run app.py

Features:
    - Research Agent chat with 190+ integrated tools
    - Target Prioritization workflow (DepMap, TCGA, safety)
    - Resistance Biomarker Panel builder (DepMap, PRISM, L1000)
    - Drug Combination Strategy (co-dependency, Reactome, trials)
    - Literature & Data Synthesis (PubMed, ChEMBL, OpenAlex)
    - Molecular Design (primers, codon opt, assemblies, CRISPR)
    - Interactive Data Explorer with Plotly visualizations
    - Session persistence and exportable reports
"""

import streamlit as st

from utils.config import ensure_dirs
from utils.state import init_session_state

from components.design_system import get_global_css
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.agent_chat import render_agent_chat
from components.settings import render_settings
from components.data_explorer import render_data_explorer
from components.data_management import render_data_management
from components.reports import render_reports
from components.help_page import render_help
from components.quick_start import render_quick_start

from workflows.target_prioritization import render_target_prioritization
from workflows.resistance_biomarkers import render_resistance_biomarkers
from workflows.combination_strategy import render_combination_strategy
from workflows.literature_synthesis import render_literature_synthesis
from workflows.molecular_design import render_molecular_design

# Page config
st.set_page_config(
    page_title="CellType Research Workbench",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply design system (ui-design-brain)
st.markdown(get_global_css(), unsafe_allow_html=True)


def main():
    """Main application entry point."""
    ensure_dirs()
    init_session_state()

    # Render sidebar and get selected page
    page = render_sidebar()

    # Route to selected page
    page_router = {
        "dashboard": render_dashboard,
        "quick_start": render_quick_start,
        "agent": render_agent_chat,
        "target": render_target_prioritization,
        "biomarker": render_resistance_biomarkers,
        "combination": render_combination_strategy,
        "literature": render_literature_synthesis,
        "molecular": render_molecular_design,
        "data_explorer": render_data_explorer,
        "data_mgmt": render_data_management,
        "reports": render_reports,
        "settings": render_settings,
        "help": render_help,
    }

    renderer = page_router.get(page, render_dashboard)
    renderer()

    # Footer — minimal, centered
    st.markdown(
        '<div class="workbench-footer">'
        'CellType Research Workbench v1.0.0 · Powered by '
        '<a href="https://github.com/celltype/cli">celltype-cli</a> '
        '& <a href="https://anthropic.com">Claude AI</a>'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

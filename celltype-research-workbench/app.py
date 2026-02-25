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

from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.agent_chat import render_agent_chat
from components.settings import render_settings
from components.data_explorer import render_data_explorer
from components.data_management import render_data_management
from components.reports import render_reports
from components.help_page import render_help

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

# Custom CSS for polished UI
st.markdown("""
<style>
    /* Header styling */
    .stApp header {
        background-color: transparent;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.2);
        border-radius: 0.5rem;
        padding: 0.75rem;
    }

    /* Container borders */
    [data-testid="stExpander"] {
        border: 1px solid rgba(250, 250, 250, 0.1);
        border-radius: 0.5rem;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 0.5rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0a0e14;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.5rem 1rem;
    }

    /* Button styling */
    .stButton > button[kind="primary"] {
        background-color: #00d4aa;
        color: #0e1117;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 0.5rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #666;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    ensure_dirs()
    init_session_state()

    # Render sidebar and get selected page
    page = render_sidebar()

    # Route to selected page
    page_router = {
        "dashboard": render_dashboard,
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

    # Footer
    st.markdown(
        '<div class="footer">'
        'CellType Research Workbench v1.0.0 — Powered by '
        '<a href="https://github.com/celltype/cli">celltype-cli</a> '
        '& <a href="https://anthropic.com">Claude AI</a>'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

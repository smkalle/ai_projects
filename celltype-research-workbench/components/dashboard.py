"""Dashboard page — system overview, quick actions, and health check."""

import streamlit as st

from utils.config import WorkbenchConfig, TOOL_CATEGORIES, DATASETS
from utils.celltype_agent import check_celltype_installed, run_ct_doctor
from utils.state import list_sessions, list_reports
from utils.examples import get_featured_examples, load_example, WORKFLOW_REGISTRY
from components.design_system import render_status_badge


def render_dashboard():
    """Render the main dashboard page."""
    st.title("🧬 Bioinformatics Research Workbench")
    st.caption("Powered by CellType CLI — Autonomous AI Agent for Drug Discovery")

    # Top metrics row — KPI → trend → detail hierarchy
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tools", "190+", help="Pre-integrated bioinformatics tools")
    with col2:
        st.metric("Datasets", len(DATASETS), help="Managed datasets available")
    with col3:
        st.metric("Sessions", len(list_sessions()))
    with col4:
        st.metric("Reports", len(list_reports()))

    st.divider()

    # Quick Start banner
    with st.container(border=True):
        qs_col1, qs_col2 = st.columns([4, 1])
        with qs_col1:
            st.markdown("#### 🚀 New here? Start the Quick Start Tutorial")
            st.caption(
                "Interactive 7-step walkthrough + pre-built examples for every workflow. "
                "Load a sample configuration with one click and explore real outputs."
            )
        with qs_col2:
            st.markdown("")  # spacer
            st.info("Select **🚀 Quick Start** in the sidebar")

    st.divider()

    # Quick Start section
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Quick Start Workflows")
        st.caption("Jump directly to a pre-configured research pipeline.")

        workflows = [
            ("🎯 Target Prioritization", "Prioritize degradation targets using DepMap co-essentiality, TCGA expression, and safety flags.", "target"),
            ("🧪 Resistance Biomarker Panel", "Build a biomarker panel using DepMap mutation sensitivity, PRISM viability, and L1000 signatures.", "biomarker"),
            ("💊 Combination Strategy", "Find synergistic drug combinations using co-dependency analysis and clinical trial data.", "combination"),
            ("📚 Literature + Data Synthesis", "Synthesize literature with DepMap/PRISM evidence for target validation.", "literature"),
            ("🧬 Molecular Biology Design", "Design primers, codon-optimize ORFs, plan Golden Gate assemblies.", "molecular"),
        ]

        for icon_title, desc, _key in workflows:
            with st.container(border=True):
                st.markdown(f"**{icon_title}**")
                st.caption(desc)

    with col_right:
        st.subheader("System Health")
        _render_health_check()

        st.subheader("Tool Categories")
        for cat, tools in TOOL_CATEGORIES.items():
            with st.expander(f"{cat} ({len(tools)} tools)"):
                for tool in tools:
                    st.markdown(f"- {tool}")

    st.divider()

    # Featured Examples
    st.subheader("Featured Examples")
    st.caption("Pre-built configurations you can load into any workflow with one click.")
    featured = get_featured_examples()
    ex_cols = st.columns(min(len(featured), 3))

    for i, (wf_id, ex_name, ex) in enumerate(featured):
        wf = WORKFLOW_REGISTRY[wf_id]
        with ex_cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{wf['icon']} {ex_name}**")
                st.caption(ex["description"][:100] + "...")
                if st.button("Load example", key=f"dash_load_{wf_id}", use_container_width=True):
                    load_example(wf_id, ex_name, ex)
                    st.success(f"Loaded! Navigate to **{wf['label']}** in the sidebar.")

    st.divider()

    # Setup Checklist — status badges
    st.subheader("Setup Checklist")
    config = WorkbenchConfig.load()
    ct_info = check_celltype_installed()

    steps = [
        ("Install celltype-cli", ct_info["installed"], "`pip install celltype-cli` or `pipx install celltype-cli`"),
        ("Configure Anthropic API Key", bool(config.anthropic_api_key), "Go to **Settings** → paste your `sk-ant-...` key"),
        ("Pull DepMap Data", bool(config.depmap_path), "`ct data pull depmap` — enables full target analysis"),
        ("Pull PRISM Data", bool(config.prism_path), "`ct data pull prism` — enables drug sensitivity profiling"),
        ("Pull MSigDB", bool(config.msigdb_path), "`ct data pull msigdb` — enables pathway & gene set analysis"),
    ]

    for step_name, done, instruction in steps:
        badge = render_status_badge("Done", "success") if done else render_status_badge("Pending", "warning")
        detail = "" if done else f" — {instruction}"
        st.markdown(f"{badge} **{step_name}**{detail}", unsafe_allow_html=True)

    # Dataset overview
    st.divider()
    st.subheader("Available Datasets")
    cols = st.columns(2)
    for i, (key, ds) in enumerate(DATASETS.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{ds['name']}**")
                st.caption(ds["description"])
                st.code(ds["command"], language="bash")
                st.caption(f"Size: {ds['size']}")


def _render_health_check():
    """Render a compact health check panel with status badges."""
    config = WorkbenchConfig.load()
    ct_info = check_celltype_installed()

    checks = [
        ("Python Environment", True, "Active"),
        ("celltype-cli", ct_info["installed"], ct_info.get("version", "Not installed")),
        ("Anthropic API Key", bool(config.anthropic_api_key), "Configured" if config.anthropic_api_key else "Missing"),
        ("Default Model", True, config.default_model),
    ]

    for name, ok, detail in checks:
        badge = render_status_badge(detail, "success" if ok else "error")
        st.markdown(f"**{name}** {badge}", unsafe_allow_html=True)

    if st.button("Run diagnostics", help="Run ct doctor to check full system health"):
        with st.spinner("Running ct doctor..."):
            health = run_ct_doctor()
        if health.get("issues"):
            for issue in health["issues"]:
                st.warning(issue)
        else:
            st.success("All systems operational!")

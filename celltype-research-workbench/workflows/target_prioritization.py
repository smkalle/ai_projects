"""Workflow: Target Prioritization for Molecular Glue / PROTAC programs."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.config import WorkbenchConfig
from utils.celltype_agent import run_celltype_query
from utils.state import add_chat_message, save_session, save_report
from utils.sample_data import (
    generate_dependency_scores,
    generate_expression_data,
    generate_safety_profile,
)
from utils.examples import render_loaded_example_banner, render_example_loader, get_expected_result, TARGET_EXAMPLES
from components.design_system import apply_plotly_theme, COLORS, render_empty_state


def render_target_prioritization():
    """Render the target prioritization workflow page."""
    st.title("🎯 Target Prioritization Workflow")
    st.caption(
        "Prioritize degradation targets using DepMap essentiality, "
        "TCGA expression, co-essentiality networks, and safety profiling."
    )

    render_loaded_example_banner("target")

    tab_config, tab_explore, tab_agent, tab_results = st.tabs([
        "📋 Configure", "📊 Data Explorer", "🤖 AI Agent", "📑 Results",
    ])

    with tab_config:
        _render_config_panel()

    with tab_explore:
        _render_data_explorer()

    with tab_agent:
        _render_agent_panel()

    with tab_results:
        _render_results_panel()


def _render_config_panel():
    """Configure target prioritization parameters."""
    st.subheader("Workflow Configuration")

    render_example_loader("target")

    # Pre-fill from loaded example config
    preloaded = st.session_state.get("target_config", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Target Candidates")
        default_genes = ", ".join(preloaded["genes"]) if preloaded.get("genes") else "IKZF1, GSPT1, CK1α, CRBN, MYC"
        gene_input = st.text_area(
            "Gene symbols (comma-separated)",
            value=default_genes,
            height=80,
            help="Enter HGNC gene symbols for your candidate targets.",
        )
        genes = [g.strip() for g in gene_input.split(",") if g.strip()]
        st.caption(f"{len(genes)} genes entered")

        st.markdown("#### E3 Ligase Context")
        e3_ligase = st.selectbox(
            "E3 Ligase",
            ["CRBN (Cereblon)", "VHL", "IAP (cIAP1/XIAP)", "DCAF15", "DCAF16", "Other"],
        )
        modality = st.selectbox(
            "Modality",
            ["Molecular Glue", "PROTAC", "Molecular Glue Degrader", "Other"],
        )

    with col2:
        st.markdown("#### Analysis Parameters")
        indication = st.selectbox(
            "Primary Indication",
            ["Multiple Myeloma", "AML", "DLBCL", "CLL", "Breast Cancer",
             "Lung Cancer (NSCLC)", "Colon Cancer", "Pancreatic Cancer", "Custom"],
        )
        if indication == "Custom":
            indication = st.text_input("Custom indication")

        lineage_filter = st.multiselect(
            "DepMap Lineage Filter",
            ["Hematopoietic", "Lung", "Breast", "Colon", "Skin", "Brain",
             "Liver", "Kidney", "Pancreas", "Ovary", "Prostate"],
            default=["Hematopoietic"],
        )

        essentiality_threshold = st.slider(
            "Essentiality Score Threshold",
            -2.0, 0.5, -0.5, 0.05,
            help="More negative = more essential. -0.5 is a common cutoff.",
        )

        st.markdown("#### Evidence Sources")
        use_depmap = st.checkbox("DepMap CRISPR Essentiality", value=True)
        use_coess = st.checkbox("Co-Essentiality Networks", value=True)
        use_tcga = st.checkbox("TCGA Expression", value=True)
        use_safety = st.checkbox("Safety Profiling", value=True)
        use_literature = st.checkbox("Literature Evidence (PubMed)", value=True)

    # Save config to session state
    st.session_state["target_config"] = {
        "genes": genes,
        "e3_ligase": e3_ligase,
        "modality": modality,
        "indication": indication,
        "lineage_filter": lineage_filter,
        "essentiality_threshold": essentiality_threshold,
        "sources": {
            "depmap": use_depmap, "coessentiality": use_coess,
            "tcga": use_tcga, "safety": use_safety, "literature": use_literature,
        },
    }

    st.success(f"Configuration ready — {len(genes)} targets, {sum([use_depmap, use_coess, use_tcga, use_safety, use_literature])} evidence sources.")


def _render_data_explorer():
    """Interactive exploration of dependency and expression data."""
    st.subheader("Interactive Data Explorer")

    config = st.session_state.get("target_config", {})
    genes = config.get("genes", ["IKZF1", "GSPT1", "CK1α", "CRBN", "MYC"])

    # Dependency score heatmap
    st.markdown("#### DepMap Dependency Scores (Simulated)")
    dep_df = generate_dependency_scores(genes)

    fig_heatmap = px.imshow(
        dep_df.drop(columns=["Lineage"]).T,
        labels=dict(x="Cell Line", y="Gene", color="Dependency Score"),
        color_continuous_scale="RdBu_r",
        aspect="auto",
        title="CRISPR Dependency Scores Across Cell Lines",
    )
    fig_heatmap.update_layout(height=400)
    apply_plotly_theme(fig_heatmap)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Dependency distribution
    st.markdown("#### Dependency Score Distributions")
    dep_melted = dep_df.drop(columns=["Lineage"]).melt(var_name="Gene", value_name="Score")
    fig_box = px.box(
        dep_melted, x="Gene", y="Score", color="Gene",
        title="Dependency Score Distribution by Gene",
    )
    fig_box.add_hline(y=-0.5, line_dash="dash", line_color=COLORS["error"],
                      annotation_text="Essentiality threshold (-0.5)")
    fig_box.update_layout(height=400, showlegend=False)
    apply_plotly_theme(fig_box)
    st.plotly_chart(fig_box, use_container_width=True)

    # Expression data
    st.markdown("#### TCGA Expression Across Tissues (Simulated)")
    expr_df = generate_expression_data(genes)

    fig_expr = px.imshow(
        np.log2(expr_df + 1),
        labels=dict(x="Gene", y="Tissue", color="log2(TPM+1)"),
        color_continuous_scale="Viridis",
        aspect="auto",
        title="Gene Expression Across Normal Tissues (log2 TPM)",
    )
    fig_expr.update_layout(height=400)
    apply_plotly_theme(fig_expr)
    st.plotly_chart(fig_expr, use_container_width=True)

    # Safety profile
    st.markdown("#### Safety Profile")
    safety_df = generate_safety_profile(genes)
    st.dataframe(safety_df, use_container_width=True, hide_index=True)

    # Downloadable data
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "📥 Download Dependency Data",
            dep_df.to_csv(index=True),
            "dependency_scores.csv",
            "text/csv",
        )
    with col2:
        st.download_button(
            "📥 Download Expression Data",
            expr_df.to_csv(index=True),
            "expression_data.csv",
            "text/csv",
        )
    with col3:
        st.download_button(
            "📥 Download Safety Profile",
            safety_df.to_csv(index=False),
            "safety_profile.csv",
            "text/csv",
        )


def _render_agent_panel():
    """Run the AI agent for target prioritization."""
    st.subheader("AI-Powered Target Prioritization")

    config = st.session_state.get("target_config", {})
    genes = config.get("genes", ["IKZF1", "GSPT1", "CK1α"])
    indication = config.get("indication", "Multiple Myeloma")
    e3_ligase = config.get("e3_ligase", "CRBN")
    modality = config.get("modality", "Molecular Glue")

    # Auto-generate query from config
    sources = config.get("sources", {})
    source_list = [k for k, v in sources.items() if v]
    source_str = ", ".join(source_list) if source_list else "DepMap, TCGA, safety"

    auto_query = (
        f"I have a {e3_ligase.split('(')[0].strip()}-based {modality.lower()}. "
        f"Proteomics shows degradation of {', '.join(genes)} in {indication} cells. "
        f"Prioritize the best therapeutic target using {source_str}. "
        f"Output a ranked table with evidence scores, safety flags, and recommendations."
    )

    query = st.text_area(
        "Research Query",
        value=auto_query,
        height=120,
        help="Auto-generated from your configuration. Edit as needed.",
    )

    col1, col2 = st.columns(2)
    with col1:
        run_agent = st.button("🚀 Run Agent Analysis", type="primary", use_container_width=True)
    with col2:
        run_parallel = st.button("🔀 Run Parallel Agents (3x)", use_container_width=True)

    if run_agent or run_parallel:
        wb_config = WorkbenchConfig.load()
        with st.spinner("🧬 Agent is analyzing targets across multiple data sources..."):
            response = run_celltype_query(query, wb_config)

        st.markdown("---")
        st.markdown(response.content)

        if response.tools_used:
            with st.expander("🔧 Tools Used"):
                for t in response.tools_used:
                    st.markdown(f"- {t}")

        st.caption(
            f"⏱ {response.duration:.1f}s | "
            f"📊 {response.tokens_input:,} in / {response.tokens_output:,} out | "
            f"💰 ${response.cost:.4f}"
        )

        st.session_state["target_results"] = {
            "query": query,
            "response": response.content,
            "tools": response.tools_used,
        }

        # Save as report
        report_path = save_report(
            f"target_prioritization_{indication.replace(' ', '_')}",
            f"# Target Prioritization Report\n\n**Query:** {query}\n\n{response.content}",
        )
        st.success(f"Report saved: {report_path}")


def _render_results_panel():
    """Display saved results and comparisons."""
    st.subheader("Results & Comparison")

    results = st.session_state.get("target_results")
    if not results:
        render_empty_state(
            headline="No results yet",
            description="Run an agent analysis from the AI Agent tab to see results here.",
            icon="📑",
        )

        # Show example result from first available example
        st.markdown("#### Example Output Format")
        first_ex = next(iter(TARGET_EXAMPLES.values()))
        example_df = get_expected_result(first_ex)
        if example_df is not None:
            st.dataframe(example_df.head(3), use_container_width=True, hide_index=True)
        return

    st.markdown("#### Latest Analysis")
    st.markdown(f"**Query:** {results['query']}")
    st.markdown(results["response"])

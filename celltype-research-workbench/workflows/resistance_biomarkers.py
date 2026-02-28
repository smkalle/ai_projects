"""Workflow: Resistance Biomarker Panel Builder."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.config import WorkbenchConfig
from utils.celltype_agent import run_celltype_query
from utils.state import save_report
from utils.sample_data import generate_biomarker_panel, generate_dependency_scores
from utils.examples import render_loaded_example_banner, render_example_loader
from components.design_system import apply_plotly_theme, COLORS, render_empty_state


def render_resistance_biomarkers():
    """Render the resistance biomarker workflow page."""
    st.title("🧪 Resistance Biomarker Panel Builder")
    st.caption(
        "Identify and validate resistance biomarkers using DepMap mutation sensitivity, "
        "PRISM viability, L1000 signatures, and TCGA stratification."
    )

    render_loaded_example_banner("biomarker")

    tab_config, tab_explore, tab_agent, tab_results = st.tabs([
        "📋 Configure", "📊 Data Explorer", "🤖 AI Agent", "📑 Results",
    ])

    with tab_config:
        _render_config()

    with tab_explore:
        _render_explorer()

    with tab_agent:
        _render_agent()

    with tab_results:
        _render_results()


def _render_config():
    """Configure biomarker discovery parameters."""
    st.subheader("Biomarker Discovery Configuration")

    render_example_loader("biomarker")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Drug / Compound")
        compound_class = st.selectbox(
            "Compound Class",
            ["BET Inhibitor", "BCL2 Inhibitor", "CDK4/6 Inhibitor", "PROTAC",
             "Molecular Glue", "MEK Inhibitor", "KRAS G12C Inhibitor", "Custom"],
        )
        if compound_class == "Custom":
            compound_class = st.text_input("Custom compound class")

        compound_name = st.text_input(
            "Compound Name (optional)",
            placeholder="e.g., JQ1, Venetoclax",
        )

        indication = st.selectbox(
            "Indication",
            ["AML", "Multiple Myeloma", "DLBCL", "CLL", "Breast Cancer",
             "NSCLC", "Colon Cancer", "Pancreatic Cancer", "Pan-Cancer"],
        )

    with col2:
        st.markdown("#### Panel Parameters")
        panel_size = st.slider("Panel Size (genes)", 5, 50, 10,
                               help="Number of biomarkers in the final panel.")
        fdr_threshold = st.slider("FDR Threshold", 0.01, 0.25, 0.05, 0.01)
        effect_size_min = st.slider("Min Effect Size (|log2FC|)", 0.5, 3.0, 1.0, 0.1)

        st.markdown("#### Evidence Sources")
        use_depmap_mut = st.checkbox("DepMap Mutation Sensitivity", value=True)
        use_prism = st.checkbox("PRISM Drug Viability", value=True)
        use_l1000 = st.checkbox("L1000 Transcriptomic Signatures", value=True)
        use_tcga_strat = st.checkbox("TCGA Stratification", value=True)
        use_clinical = st.checkbox("Clinical Evidence (Trials)", value=True)

    st.session_state["biomarker_config"] = {
        "compound_class": compound_class,
        "compound_name": compound_name,
        "indication": indication,
        "panel_size": panel_size,
        "fdr_threshold": fdr_threshold,
        "effect_size_min": effect_size_min,
        "sources": {
            "depmap_mutations": use_depmap_mut,
            "prism": use_prism,
            "l1000": use_l1000,
            "tcga_stratification": use_tcga_strat,
            "clinical": use_clinical,
        },
    }
    st.success("Configuration ready.")


def _render_explorer():
    """Explore biomarker data interactively."""
    st.subheader("Biomarker Data Explorer")

    panel_df = generate_biomarker_panel()

    # Volcano-style plot
    st.markdown("#### Biomarker Significance Plot")
    panel_df["neg_log10_pval"] = -np.log10(panel_df["P-value"])
    panel_df["Significant"] = (panel_df["FDR"] < 0.05) & (abs(panel_df["Effect Size (log2FC)"]) > 1.0)

    fig_volcano = px.scatter(
        panel_df,
        x="Effect Size (log2FC)",
        y="neg_log10_pval",
        color="Significant",
        text="Gene",
        title="Biomarker Effect Size vs. Significance",
        labels={"neg_log10_pval": "-log10(P-value)"},
        color_discrete_map={True: COLORS["error"], False: COLORS["text_tertiary"]},
    )
    fig_volcano.update_traces(textposition="top center", marker=dict(size=12))
    fig_volcano.add_hline(y=-np.log10(0.05), line_dash="dash", line_color="gray",
                          annotation_text="P=0.05")
    fig_volcano.add_vline(x=-1.0, line_dash="dash", line_color="gray")
    fig_volcano.add_vline(x=1.0, line_dash="dash", line_color="gray")
    fig_volcano.update_layout(height=500)
    apply_plotly_theme(fig_volcano)
    st.plotly_chart(fig_volcano, use_container_width=True)

    # Biomarker table
    st.markdown("#### Full Biomarker Panel")
    st.dataframe(
        panel_df.drop(columns=["neg_log10_pval", "Significant"]),
        use_container_width=True,
        hide_index=True,
    )

    # DepMap correlation plot
    st.markdown("#### DepMap Dependency Correlation")
    fig_corr = px.bar(
        panel_df.sort_values("DepMap Correlation"),
        x="DepMap Correlation",
        y="Gene",
        orientation="h",
        color="DepMap Correlation",
        color_continuous_scale="RdBu_r",
        title="DepMap Dependency Correlation per Biomarker",
    )
    fig_corr.update_layout(height=400)
    apply_plotly_theme(fig_corr)
    st.plotly_chart(fig_corr, use_container_width=True)

    # Clinical evidence breakdown
    st.markdown("#### Clinical Evidence Summary")
    evidence_counts = panel_df["Clinical Evidence"].value_counts()
    fig_pie = px.pie(
        values=evidence_counts.values,
        names=evidence_counts.index,
        title="Clinical Evidence Distribution",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    apply_plotly_theme(fig_pie)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.download_button(
        "Download biomarker panel",
        panel_df.drop(columns=["neg_log10_pval", "Significant"]).to_csv(index=False),
        "resistance_biomarker_panel.csv",
        "text/csv",
    )


def _render_agent():
    """Run the AI agent for biomarker discovery."""
    st.subheader("AI-Powered Biomarker Discovery")

    config = st.session_state.get("biomarker_config", {})
    compound = config.get("compound_class", "BET Inhibitor")
    indication = config.get("indication", "AML")
    panel_size = config.get("panel_size", 10)

    auto_query = (
        f"Build a {panel_size}-gene resistance biomarker panel for a {compound} in {indication}. "
        f"Use DepMap mutation sensitivity, PRISM viability, and L1000 signatures. "
        f"Validate with TCGA stratification. Output a ranked table with mutation frequency, "
        f"effect sizes, FDR values, and clinical evidence levels."
    )

    query = st.text_area("Research Query", value=auto_query, height=120)

    if st.button("🚀 Run Biomarker Discovery", type="primary", use_container_width=True):
        wb_config = WorkbenchConfig.load()
        with st.spinner("🧬 Agent is mining resistance biomarkers across datasets..."):
            response = run_celltype_query(query, wb_config)

        st.markdown("---")
        st.markdown(response.content)

        if response.tools_used:
            with st.expander("🔧 Tools Used"):
                for t in response.tools_used:
                    st.markdown(f"- {t}")

        st.caption(
            f"⏱ {response.duration:.1f}s | 💰 ${response.cost:.4f}"
        )

        st.session_state["biomarker_results"] = {
            "query": query, "response": response.content,
        }
        report_path = save_report(
            f"biomarker_panel_{indication}",
            f"# Resistance Biomarker Panel\n\n**Query:** {query}\n\n{response.content}",
        )
        st.success(f"Report saved: {report_path}")


def _render_results():
    """Display biomarker results."""
    st.subheader("Biomarker Panel Results")

    results = st.session_state.get("biomarker_results")
    if not results:
        render_empty_state(
            headline="No results yet",
            description="Run an agent analysis from the AI Agent tab to see results here.",
            icon="📑",
        )
        st.markdown("#### Example Output")
        example = generate_biomarker_panel()
        st.dataframe(example, use_container_width=True, hide_index=True)
        return

    st.markdown(results["response"])

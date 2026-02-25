"""Workflow: Drug Combination Strategy for synergy discovery."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.config import WorkbenchConfig
from utils.celltype_agent import run_celltype_query
from utils.state import save_report
from utils.sample_data import generate_combination_data, generate_prism_viability
from utils.examples import COMBINATION_EXAMPLES


def render_combination_strategy():
    """Render the combination strategy workflow page."""
    st.title("💊 Drug Combination Strategy")
    st.caption(
        "Discover synergistic drug combinations using DepMap co-dependency, "
        "Reactome pathways, PRISM viability, and ClinicalTrials.gov data."
    )

    loaded = st.session_state.get("_loaded_example", "")
    if loaded.startswith("combination:"):
        st.success(f"Example loaded: **{loaded.split(': ', 1)[1]}** — configuration pre-filled below.")
        if st.button("Clear example", key="clear_combo_ex"):
            del st.session_state["_loaded_example"]
            st.rerun()

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
    """Configure combination strategy parameters."""
    st.subheader("Combination Strategy Configuration")

    # Load Example selector
    with st.expander("📦 Load a pre-built example", expanded=False):
        for ex_name, ex in COMBINATION_EXAMPLES.items():
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{ex_name}**")
                st.caption(ex["description"])
            with col_btn:
                if st.button("Load", key=f"combo_load_{ex_name}", use_container_width=True):
                    st.session_state["combo_config"] = ex["config"]
                    st.session_state["_loaded_example"] = f"combination: {ex_name}"
                    st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Lead Compound")
        lead_compound = st.text_input(
            "Lead Compound / Mechanism",
            value="BET inhibitor (JQ1)",
            help="Your primary compound or mechanism of action.",
        )
        lead_target = st.text_input(
            "Primary Target(s)",
            value="BRD4, BRD2, BRD3",
        )
        indication = st.selectbox(
            "Indication",
            ["AML", "Multiple Myeloma", "DLBCL", "NSCLC", "Breast Cancer",
             "Colon Cancer", "Pancreatic Cancer", "Pan-Cancer"],
        )

    with col2:
        st.markdown("#### Combination Parameters")
        n_combinations = st.slider("Number of Combinations to Suggest", 3, 10, 5)
        synergy_metric = st.selectbox(
            "Synergy Metric",
            ["Bliss Independence", "Loewe Additivity", "HSA (Highest Single Agent)", "ZIP"],
        )

        st.markdown("#### Prioritization Criteria")
        prioritize_by = st.multiselect(
            "Prioritize By",
            ["Therapeutic Window", "Safety Profile", "Clinical Stage",
             "Mechanistic Rationale", "Immune Modulation Potential"],
            default=["Therapeutic Window", "Safety Profile"],
        )

        st.markdown("#### Biological Context")
        context = st.text_area(
            "Additional Context",
            value="Low immune infiltration observed in RNA-seq.",
            height=80,
        )

    st.session_state["combo_config"] = {
        "lead_compound": lead_compound,
        "lead_target": lead_target,
        "indication": indication,
        "n_combinations": n_combinations,
        "synergy_metric": synergy_metric,
        "prioritize_by": prioritize_by,
        "context": context,
    }
    st.success("Configuration ready.")


def _render_explorer():
    """Explore combination and viability data."""
    st.subheader("Combination Data Explorer")

    # Synergy matrix
    st.markdown("#### Drug Combination Synergy Profiles (Simulated)")
    combo_df = generate_combination_data()

    fig_synergy = px.bar(
        combo_df,
        x="Drug B",
        y="Bliss Score",
        color="Synergy Classification",
        title="Combination Synergy Scores (Bliss Independence)",
        color_discrete_map={
            "Synergistic": "#27ae60",
            "Additive": "#f39c12",
            "Antagonistic": "#e74c3c",
        },
    )
    fig_synergy.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_synergy.update_layout(height=400)
    st.plotly_chart(fig_synergy, use_container_width=True)

    # Full combo table
    st.dataframe(combo_df, use_container_width=True, hide_index=True)

    # PRISM viability heatmap
    st.markdown("#### PRISM Drug Viability (Simulated)")
    prism_df = generate_prism_viability()

    fig_prism = px.imshow(
        prism_df,
        labels=dict(x="Compound", y="Cell Line", color="Viability"),
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
        title="PRISM Drug Viability Across Cell Lines",
    )
    fig_prism.update_layout(height=500)
    st.plotly_chart(fig_prism, use_container_width=True)

    # Clinical stage distribution
    st.markdown("#### Combination Clinical Development Stage")
    stage_counts = combo_df["Clinical Stage"].value_counts()
    fig_stages = px.bar(
        x=stage_counts.index,
        y=stage_counts.values,
        labels={"x": "Clinical Stage", "y": "Count"},
        title="Clinical Development Stages of Combinations",
        color=stage_counts.index,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig_stages, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Synergy Data",
            combo_df.to_csv(index=False),
            "combination_synergy.csv", "text/csv",
        )
    with col2:
        st.download_button(
            "📥 Download PRISM Viability",
            prism_df.to_csv(index=True),
            "prism_viability.csv", "text/csv",
        )


def _render_agent():
    """Run AI agent for combination discovery."""
    st.subheader("AI-Powered Combination Discovery")

    config = st.session_state.get("combo_config", {})
    lead = config.get("lead_compound", "BET inhibitor")
    indication = config.get("indication", "AML")
    n = config.get("n_combinations", 5)
    context = config.get("context", "")
    prioritize = config.get("prioritize_by", ["Therapeutic Window"])

    auto_query = (
        f"My lead compound is a {lead} being developed for {indication}. "
        f"{'Context: ' + context + '. ' if context else ''}"
        f"Suggest {n} synergistic drug combinations using DepMap co-dependency, "
        f"Reactome pathways, and ClinicalTrials.gov. "
        f"Prioritize by {', '.join(prioritize)}. "
        f"Include synergy predictions, therapeutic window assessment, and clinical evidence."
    )

    query = st.text_area("Research Query", value=auto_query, height=120)

    if st.button("🚀 Run Combination Analysis", type="primary", use_container_width=True):
        wb_config = WorkbenchConfig.load()
        with st.spinner("🧬 Agent is analyzing combination strategies..."):
            response = run_celltype_query(query, wb_config)

        st.markdown("---")
        st.markdown(response.content)

        if response.tools_used:
            with st.expander("🔧 Tools Used"):
                for t in response.tools_used:
                    st.markdown(f"- {t}")

        st.caption(f"⏱ {response.duration:.1f}s | 💰 ${response.cost:.4f}")

        st.session_state["combo_results"] = {
            "query": query, "response": response.content,
        }
        report_path = save_report(
            f"combination_strategy_{indication}",
            f"# Combination Strategy Report\n\n**Query:** {query}\n\n{response.content}",
        )
        st.success(f"Report saved: {report_path}")


def _render_results():
    """Display combination results."""
    st.subheader("Combination Strategy Results")

    results = st.session_state.get("combo_results")
    if not results:
        st.info("Run an agent analysis to see results here.")
        combo_df = generate_combination_data()
        st.markdown("#### Example Output")
        st.dataframe(combo_df, use_container_width=True, hide_index=True)
        return

    st.markdown(results["response"])

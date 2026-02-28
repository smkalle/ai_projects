"""Interactive Data Explorer — unified view of all available datasets."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.sample_data import (
    generate_dependency_scores,
    generate_expression_data,
    generate_prism_viability,
    generate_safety_profile,
    generate_biomarker_panel,
    generate_combination_data,
)
from components.design_system import apply_plotly_theme, COLORS


def render_data_explorer():
    """Render the unified data explorer page."""
    st.title("📊 Data Explorer")
    st.caption("Interactively explore DepMap, PRISM, expression, and other datasets.")

    dataset = st.selectbox(
        "Select Dataset",
        ["DepMap Dependency Scores", "Gene Expression (TCGA-style)",
         "PRISM Drug Viability", "Safety Profiles", "Biomarker Panel",
         "Drug Combinations"],
    )

    st.divider()

    if dataset == "DepMap Dependency Scores":
        _explore_depmap()
    elif dataset == "Gene Expression (TCGA-style)":
        _explore_expression()
    elif dataset == "PRISM Drug Viability":
        _explore_prism()
    elif dataset == "Safety Profiles":
        _explore_safety()
    elif dataset == "Biomarker Panel":
        _explore_biomarkers()
    elif dataset == "Drug Combinations":
        _explore_combinations()


def _explore_depmap():
    """Explore DepMap dependency scores."""
    st.subheader("DepMap CRISPR Dependency Scores")

    col1, col2 = st.columns([1, 3])
    with col1:
        gene_input = st.text_area("Genes", "IKZF1\nGSPT1\nCK1α\nCRBN\nMYC\nBRD4\nEZH2")
        genes = [g.strip() for g in gene_input.split("\n") if g.strip()]
        n_lines = st.slider("Cell Lines", 10, 100, 30)
        threshold = st.slider("Essentiality Threshold", -2.0, 0.5, -0.5, 0.05)

    with col2:
        df = generate_dependency_scores(genes, n_lines)

        fig = px.imshow(
            df.drop(columns=["Lineage"]).T,
            color_continuous_scale="RdBu_r",
            aspect="auto",
            title="Dependency Score Heatmap",
        )
        fig.update_layout(height=400)
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

        melted = df.drop(columns=["Lineage"]).melt(var_name="Gene", value_name="Score")
        fig2 = px.box(melted, x="Gene", y="Score", color="Gene",
                       title="Score Distributions")
        fig2.add_hline(y=threshold, line_dash="dash", line_color=COLORS["error"])
        fig2.update_layout(height=350, showlegend=False)
        apply_plotly_theme(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    # Lineage breakdown
    st.markdown("#### By Lineage")
    selected_gene = st.selectbox("Select Gene", genes)
    if selected_gene:
        lineage_df = df[["Lineage", selected_gene]].copy()
        fig3 = px.box(lineage_df, x="Lineage", y=selected_gene, color="Lineage",
                       title=f"{selected_gene} Dependency by Lineage")
        fig3.update_layout(height=350, showlegend=False)
        apply_plotly_theme(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    # Summary stats
    st.markdown("#### Summary Statistics")
    stats = df.drop(columns=["Lineage"]).describe().round(3)
    st.dataframe(stats, use_container_width=True)

    st.download_button("Download data", df.to_csv(index=True), "depmap_scores.csv", "text/csv")


def _explore_expression():
    """Explore expression data."""
    st.subheader("Gene Expression Across Tissues")

    genes = st.multiselect(
        "Select Genes",
        ["IKZF1", "GSPT1", "CK1α", "CRBN", "MYC", "TP53", "KRAS", "BRAF", "EGFR", "CDK4"],
        default=["IKZF1", "GSPT1", "CRBN", "MYC"],
    )

    df = generate_expression_data(genes if genes else None)

    fig = px.imshow(
        np.log2(df + 1),
        color_continuous_scale="Viridis",
        aspect="auto",
        title="Expression Heatmap (log2 TPM+1)",
    )
    fig.update_layout(height=450)
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    if genes:
        selected = st.selectbox("Gene for tissue breakdown", genes)
        fig2 = px.bar(
            x=df.index, y=df[selected],
            labels={"x": "Tissue", "y": "TPM"},
            title=f"{selected} Expression Across Tissues",
            color=df[selected],
            color_continuous_scale="Plasma",
        )
        apply_plotly_theme(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df, use_container_width=True)
    st.download_button("Download data", df.to_csv(index=True), "expression.csv", "text/csv")


def _explore_prism():
    """Explore PRISM viability data."""
    st.subheader("PRISM Drug Viability")

    df = generate_prism_viability()

    fig = px.imshow(
        df, color_continuous_scale="RdYlGn_r", aspect="auto",
        title="Drug Viability Across Cell Lines",
    )
    fig.update_layout(height=500)
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    selected_drugs = st.multiselect("Compare Drugs", df.columns.tolist(),
                                     default=df.columns[:3].tolist())
    if selected_drugs:
        melted = df[selected_drugs].melt(var_name="Drug", value_name="Viability")
        fig2 = px.violin(melted, x="Drug", y="Viability", color="Drug",
                          title="Viability Distribution Comparison")
        apply_plotly_theme(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df, use_container_width=True)
    st.download_button("Download data", df.to_csv(index=True), "prism_viability.csv", "text/csv")


def _explore_safety():
    """Explore safety profiles."""
    st.subheader("Safety Profile Assessment")

    genes = st.text_input("Genes (comma-separated)", "IKZF1, GSPT1, CK1α, SALL4, CRBN, MYC")
    gene_list = [g.strip() for g in genes.split(",") if g.strip()]

    df = generate_safety_profile(gene_list)
    st.dataframe(df, use_container_width=True, hide_index=True)

    pass_count = (df["Overall Safety"] == "Pass").sum()
    fail_count = (df["Overall Safety"] == "Fail").sum()
    fig = px.pie(
        values=[pass_count, fail_count],
        names=["Pass", "Fail"],
        title="Safety Assessment Summary",
        color_discrete_sequence=[COLORS["success"], COLORS["error"]],
    )
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("Download data", df.to_csv(index=False), "safety_profile.csv", "text/csv")


def _explore_biomarkers():
    """Explore biomarker data."""
    st.subheader("Resistance Biomarker Panel")

    df = generate_biomarker_panel()
    st.dataframe(df, use_container_width=True, hide_index=True)

    df["neg_log10_pval"] = -np.log10(df["P-value"])
    fig = px.scatter(
        df, x="Effect Size (log2FC)", y="neg_log10_pval", text="Gene",
        color="Clinical Evidence", size="Mutation Frequency (%)",
        title="Biomarker Volcano Plot",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=500)
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("Download data", df.drop(columns=["neg_log10_pval"]).to_csv(index=False),
                        "biomarkers.csv", "text/csv")


def _explore_combinations():
    """Explore combination data."""
    st.subheader("Drug Combination Synergy Data")

    df = generate_combination_data()
    st.dataframe(df, use_container_width=True, hide_index=True)

    fig = px.scatter(
        df, x="Bliss Score", y="Loewe Score",
        color="Synergy Classification", text="Drug B",
        size_max=15,
        title="Synergy Scores: Bliss vs Loewe",
    )
    fig.update_traces(textposition="top center", marker=dict(size=15))
    apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("Download data", df.to_csv(index=False), "combinations.csv", "text/csv")

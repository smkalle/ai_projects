"""Workflow: Literature + Data Synthesis for evidence-based research."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

from utils.config import WorkbenchConfig
from utils.celltype_agent import run_celltype_query
from utils.state import save_report


def render_literature_synthesis():
    """Render the literature synthesis workflow page."""
    st.title("📚 Literature & Data Synthesis")
    st.caption(
        "Synthesize evidence from PubMed, OpenAlex, ChEMBL, ClinicalTrials.gov, "
        "and DepMap to build comprehensive target or indication profiles."
    )

    tab_config, tab_explore, tab_agent, tab_results = st.tabs([
        "📋 Configure", "📊 Knowledge Map", "🤖 AI Agent", "📑 Results",
    ])

    with tab_config:
        _render_config()

    with tab_explore:
        _render_knowledge_map()

    with tab_agent:
        _render_agent()

    with tab_results:
        _render_results()


def _render_config():
    """Configure literature synthesis parameters."""
    st.subheader("Synthesis Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Research Focus")
        topic = st.text_area(
            "Research Topic / Question",
            value="CRBN molecular glue neosubstrates and their therapeutic applications",
            height=80,
        )
        scope = st.selectbox(
            "Synthesis Scope",
            ["Comprehensive Review", "Target Validation", "Mechanism of Action",
             "Clinical Landscape", "Competitive Intelligence", "Safety Assessment"],
        )
        date_range = st.slider(
            "Publication Year Range",
            2010, 2026, (2020, 2026),
        )

    with col2:
        st.markdown("#### Sources")
        use_pubmed = st.checkbox("PubMed / MEDLINE", value=True)
        use_openal = st.checkbox("OpenAlex (preprints + journals)", value=True)
        use_chembl = st.checkbox("ChEMBL (compounds + activity)", value=True)
        use_trials = st.checkbox("ClinicalTrials.gov", value=True)
        use_patents = st.checkbox("Patent Landscape", value=False)
        use_depmap = st.checkbox("DepMap Cross-Reference", value=True)

        max_papers = st.slider("Max Papers to Analyze", 10, 200, 50)

        st.markdown("#### Output Preferences")
        output_format = st.selectbox(
            "Report Format",
            ["Structured Markdown", "Executive Summary", "Detailed with Citations",
             "Table-Focused", "Slide Deck Outline"],
        )

    st.session_state["lit_config"] = {
        "topic": topic,
        "scope": scope,
        "date_range": date_range,
        "sources": {
            "pubmed": use_pubmed, "openal": use_openal, "chembl": use_chembl,
            "trials": use_trials, "patents": use_patents, "depmap": use_depmap,
        },
        "max_papers": max_papers,
        "output_format": output_format,
    }
    st.success("Configuration ready.")


def _render_knowledge_map():
    """Display a visual knowledge map of the research landscape."""
    st.subheader("Research Landscape (Simulated)")

    config = st.session_state.get("lit_config", {})
    topic = config.get("topic", "CRBN molecular glue")

    # Simulated publication timeline
    st.markdown("#### Publication Timeline")
    np.random.seed(42)
    years = list(range(2015, 2027))
    pubs = [int(np.random.exponential(5) + i * 2) for i, _ in enumerate(years)]
    fig_timeline = px.bar(
        x=years, y=pubs,
        labels={"x": "Year", "y": "Publications"},
        title=f"Publications Related to '{topic[:40]}...'",
        color=pubs,
        color_continuous_scale="Blues",
    )
    fig_timeline.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Simulated topic clusters
    st.markdown("#### Topic Clusters")
    topics = [
        "Neosubstrate Discovery", "CRBN Binding", "Clinical Efficacy",
        "Resistance Mechanisms", "Safety/Toxicology", "Combination Therapy",
        "Molecular Glue Design", "Protein Degradation", "Biomarker Development",
        "Target Validation",
    ]
    np.random.seed(55)
    topic_data = pd.DataFrame({
        "Topic": topics,
        "Papers": np.random.randint(5, 80, len(topics)),
        "Avg Citations": np.random.randint(3, 45, len(topics)),
        "Trend": np.random.choice(["Rising", "Stable", "Emerging"], len(topics)),
    })
    fig_topics = px.treemap(
        topic_data,
        path=["Topic"],
        values="Papers",
        color="Avg Citations",
        color_continuous_scale="YlOrRd",
        title="Research Topic Landscape",
    )
    fig_topics.update_layout(height=450)
    st.plotly_chart(fig_topics, use_container_width=True)

    st.dataframe(topic_data, use_container_width=True, hide_index=True)

    # Key compounds
    st.markdown("#### Key Compounds in Literature")
    compounds = pd.DataFrame({
        "Compound": ["Lenalidomide", "Pomalidomide", "CC-220 (Iberdomide)", "CC-885",
                      "Thalidomide", "CC-92480 (Mezigdomide)", "CFT7455", "MRT-2359"],
        "Target": ["IKZF1/3", "IKZF1/3", "IKZF1/3", "GSPT1", "CRBN",
                    "IKZF1/3", "IKZF1/3", "GSPT1"],
        "Phase": ["Approved", "Approved", "Phase III", "Preclinical",
                   "Approved", "Phase I/II", "Phase I/II", "Phase I"],
        "Indication": ["MM, MDS", "MM", "MM, SLE", "AML", "MM, ENL",
                        "MM", "MM, NHL", "Solid tumors"],
        "PubMed Citations": [12450, 8320, 245, 89, 15670, 67, 34, 21],
    })
    st.dataframe(compounds, use_container_width=True, hide_index=True)

    # Clinical trials summary
    st.markdown("#### Clinical Trial Landscape")
    np.random.seed(77)
    trial_phases = pd.DataFrame({
        "Phase": ["Phase I", "Phase I/II", "Phase II", "Phase III", "Phase IV"],
        "Active Trials": [15, 8, 12, 5, 2],
        "Completed": [22, 14, 18, 9, 4],
    })
    fig_trials = px.bar(
        trial_phases.melt(id_vars="Phase", var_name="Status", value_name="Count"),
        x="Phase", y="Count", color="Status", barmode="group",
        title="Clinical Trials by Phase",
        color_discrete_map={"Active Trials": "#3498db", "Completed": "#2ecc71"},
    )
    st.plotly_chart(fig_trials, use_container_width=True)


def _render_agent():
    """Run the AI agent for literature synthesis."""
    st.subheader("AI-Powered Literature Synthesis")

    config = st.session_state.get("lit_config", {})
    topic = config.get("topic", "CRBN molecular glue neosubstrates")
    scope = config.get("scope", "Comprehensive Review")
    date_range = config.get("date_range", (2020, 2026))
    output_format = config.get("output_format", "Structured Markdown")

    sources = config.get("sources", {})
    active_sources = [k for k, v in sources.items() if v]

    auto_query = (
        f"Perform a {scope.lower()} on: {topic}. "
        f"Cover publications from {date_range[0]} to {date_range[1]}. "
        f"Sources: {', '.join(active_sources)}. "
        f"Cross-reference with DepMap essentiality in multiple lineages. "
        f"Output as {output_format.lower()} with citations. "
        f"Include key findings, emerging trends, knowledge gaps, and suggested next steps."
    )

    query = st.text_area("Research Query", value=auto_query, height=120)

    example_queries = {
        "Neosubstrate Review": f"Summarize all known neosubstrates for CRBN molecular glues from {date_range[0]}-{date_range[1]}. Cross-reference with DepMap essentiality in multiple lineages and propose a new indication.",
        "Competitive Landscape": f"Map the competitive landscape for molecular glue degraders in oncology. Include all programs in clinical development, their targets, indications, and differentiation.",
        "Safety Review": f"Compile a comprehensive safety review of CRBN-modulating compounds. Focus on teratogenicity mechanisms, SALL4 degradation, and mitigation strategies.",
    }

    with st.expander("💡 Pre-built Queries"):
        for name, q in example_queries.items():
            if st.button(name, key=f"lit_ex_{name}"):
                st.session_state["_lit_query"] = q
                st.rerun()

    if st.button("🚀 Run Literature Synthesis", type="primary", use_container_width=True):
        wb_config = WorkbenchConfig.load()
        with st.spinner("🧬 Agent is synthesizing literature and cross-referencing data..."):
            response = run_celltype_query(query, wb_config)

        st.markdown("---")
        st.markdown(response.content)

        if response.tools_used:
            with st.expander("🔧 Tools Used"):
                for t in response.tools_used:
                    st.markdown(f"- {t}")

        st.caption(f"⏱ {response.duration:.1f}s | 💰 ${response.cost:.4f}")

        st.session_state["lit_results"] = {
            "query": query, "response": response.content,
        }
        report_path = save_report(
            "literature_synthesis",
            f"# Literature Synthesis Report\n\n**Query:** {query}\n\n{response.content}",
        )
        st.success(f"Report saved: {report_path}")


def _render_results():
    """Display synthesis results."""
    st.subheader("Synthesis Results")

    results = st.session_state.get("lit_results")
    if not results:
        st.info("Run a literature synthesis to see results here.")
        return

    st.markdown(results["response"])

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download as Markdown",
            results["response"],
            "literature_synthesis.md",
            "text/markdown",
        )
    with col2:
        html_content = f"<html><body><h1>Literature Synthesis</h1><pre>{results['response']}</pre></body></html>"
        st.download_button(
            "📥 Download as HTML",
            html_content,
            "literature_synthesis.html",
            "text/html",
        )

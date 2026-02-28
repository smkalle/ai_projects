"""Interactive Research Agent chat interface."""

import streamlit as st
from datetime import datetime

from utils.config import WorkbenchConfig
from utils.celltype_agent import run_celltype_query, AgentResponse
from utils.state import add_chat_message, save_session
from components.design_system import render_empty_state


EXAMPLE_QUERIES = {
    "Target Prioritization": "I have a CRBN-based molecular glue. Proteomics shows strong degradation of IKZF1, GSPT1, and CK1α in MM cells. Prioritize the best therapeutic target using DepMap co-essentiality, TCGA expression, and safety flags. Output a ranked table with evidence.",
    "Resistance Biomarkers": "Build a 10-gene resistance biomarker panel for a BET inhibitor in AML. Use DepMap mutation sensitivity, PRISM viability, and L1000 signatures. Validate with TCGA stratification.",
    "Combination Strategy": "My lead compound shows low immune infiltration in RNA-seq. Suggest 3 synergistic combinations using DepMap co-dependency, Reactome pathways, and ClinicalTrials.gov. Prioritize by therapeutic window and safety.",
    "Literature Synthesis": "Summarize all known neosubstrates for CRBN molecular glues from 2020-2026. Cross-reference with DepMap essentiality in multiple lineages and propose a new indication.",
    "Molecular Design": "Design Golden Gate assembly primers and codon-optimize an ORF for IKZF1 degradation domain expression in E. coli.",
    "DepMap Tutorial": "Give me a 5-minute tutorial on using DepMap for target validation.",
}


def render_agent_chat():
    """Render the interactive research agent chat."""
    st.title("🔬 Research Agent")
    st.caption("Ask any bioinformatics question — the agent plans, executes tools, and delivers a data-backed report.")

    # Configuration bar
    config = WorkbenchConfig.load()
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        model = st.selectbox(
            "Model",
            ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
            index=["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"].index(config.default_model),
        )
    with col2:
        max_tokens = st.number_input("Max Tokens", 1024, 32768, config.max_tokens, step=1024)
    with col3:
        temperature = st.slider("Temperature", 0.0, 1.0, config.temperature, 0.05)

    st.divider()

    # Example queries — verb-first button labels
    with st.expander("Example queries", expanded=False):
        cols = st.columns(3)
        for i, (name, query) in enumerate(EXAMPLE_QUERIES.items()):
            with cols[i % 3]:
                if st.button(name, key=f"example_{name}", use_container_width=True):
                    st.session_state["_prefill_query"] = query
                    st.rerun()

    # Chat history display
    if not st.session_state.chat_history:
        render_empty_state(
            headline="Start a research conversation",
            description="Type a question below or pick an example query above to get started.",
            icon="🔬",
        )
    else:
        _render_chat_history()

    # Input area
    st.divider()
    prefill = st.session_state.pop("_prefill_query", "")
    query = st.chat_input("Ask a bioinformatics research question...", key="agent_input")

    if prefill and not query:
        query = prefill

    if query:
        _handle_query(query, config, model, max_tokens, temperature)


def _render_chat_history():
    """Display chat messages."""
    for msg in st.session_state.chat_history:
        role = msg["role"]
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(msg["content"])
            meta = msg.get("metadata", {})
            if meta.get("tools_used"):
                with st.expander(f"Tools used ({len(meta['tools_used'])})"):
                    for t in meta["tools_used"]:
                        st.markdown(f"- `{t}`")
            if meta.get("duration"):
                st.caption(
                    f"{meta['duration']:.1f}s · "
                    f"{meta.get('tokens_input', 0):,} in / {meta.get('tokens_output', 0):,} out · "
                    f"${meta.get('cost', 0):.4f}"
                )


def _handle_query(query: str, config: WorkbenchConfig, model: str, max_tokens: int, temperature: float):
    """Process a user query through the agent."""
    add_chat_message("user", query)

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Agent is reasoning and executing tools..."):
            config.default_model = model
            config.max_tokens = max_tokens
            config.temperature = temperature

            response: AgentResponse = run_celltype_query(query, config)

        st.markdown(response.content)

        if response.tools_used:
            with st.expander(f"Tools used ({len(response.tools_used)})"):
                for t in response.tools_used:
                    st.markdown(f"- `{t}`")

        st.caption(
            f"{response.duration:.1f}s · "
            f"{response.tokens_input:,} in / {response.tokens_output:,} out · "
            f"${response.cost:.4f} · {response.status}"
        )

    # Update session state
    add_chat_message("assistant", response.content, {
        "tools_used": response.tools_used,
        "tokens_input": response.tokens_input,
        "tokens_output": response.tokens_output,
        "cost": response.cost,
        "duration": response.duration,
    })
    st.session_state.total_tokens_used += response.tokens_input + response.tokens_output
    st.session_state.total_cost += response.cost
    st.session_state.query_count += 1

    save_session()

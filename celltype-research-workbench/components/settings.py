"""Settings page for configuration management."""

import streamlit as st

from utils.config import WorkbenchConfig, SUPPORTED_MODELS, ensure_dirs


def render_settings():
    """Render the settings configuration page."""
    st.title("⚙️ Settings & Configuration")
    st.caption("Configure API keys, model preferences, data paths, and workbench behavior.")

    config = WorkbenchConfig.load()

    tab_api, tab_model, tab_data, tab_advanced = st.tabs([
        "🔑 API Keys", "🤖 Model Settings", "📁 Data Paths", "🔧 Advanced",
    ])

    with tab_api:
        _render_api_settings(config)

    with tab_model:
        _render_model_settings(config)

    with tab_data:
        _render_data_settings(config)

    with tab_advanced:
        _render_advanced_settings(config)

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save Configuration", type="primary", use_container_width=True):
            config.save()
            st.success("Configuration saved successfully!")
            st.rerun()
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            default_config = WorkbenchConfig()
            default_config.save()
            st.info("Configuration reset to defaults.")
            st.rerun()
    with col3:
        if st.button("🩺 Run ct doctor", use_container_width=True):
            from utils.celltype_agent import run_ct_doctor
            with st.spinner("Running diagnostics..."):
                health = run_ct_doctor()
            if health.get("issues"):
                for issue in health["issues"]:
                    st.warning(issue)
            else:
                st.success("All systems operational!")


def _render_api_settings(config: WorkbenchConfig):
    st.subheader("API Key Configuration")

    st.info(
        "Get your Anthropic API key at [console.anthropic.com](https://console.anthropic.com/) → "
        "Settings → API Keys → Create Key"
    )

    new_key = st.text_input(
        "Anthropic API Key",
        value=config.anthropic_api_key,
        type="password",
        placeholder="sk-ant-...",
        help="Required for all agent functionality. Stored locally only.",
    )
    config.anthropic_api_key = new_key

    if new_key:
        masked = new_key[:10] + "..." + new_key[-4:] if len(new_key) > 14 else "***"
        st.success(f"Key configured: `{masked}`")
    else:
        st.warning("No API key configured. Agent will run in demo mode.")

    st.divider()

    ncbi_key = st.text_input(
        "NCBI API Key (Optional)",
        value=config.ncbi_api_key,
        type="password",
        placeholder="Optional — increases PubMed rate limits",
        help="Get one at ncbi.nlm.nih.gov/account/settings",
    )
    config.ncbi_api_key = ncbi_key


def _render_model_settings(config: WorkbenchConfig):
    st.subheader("Model Configuration")

    model_descriptions = {
        "claude-opus-4-6": "**Opus 4.6** — Highest accuracy (90% BixBench). Best for complex multi-step workflows. Higher cost.",
        "claude-sonnet-4-6": "**Sonnet 4.6** — Balanced speed/accuracy. Great for iterative research.",
        "claude-haiku-4-5-20251001": "**Haiku 4.5** — Fast and cheap. Good for literature search and simple queries.",
    }

    model_idx = SUPPORTED_MODELS.index(config.default_model) if config.default_model in SUPPORTED_MODELS else 0
    selected = st.selectbox("Default Model", SUPPORTED_MODELS, index=model_idx)
    config.default_model = selected
    st.markdown(model_descriptions.get(selected, ""))

    st.divider()

    config.max_tokens = st.slider(
        "Max Output Tokens",
        1024, 32768, config.max_tokens, step=1024,
        help="Maximum tokens the model can generate per response.",
    )
    config.temperature = st.slider(
        "Temperature",
        0.0, 1.0, config.temperature, 0.05,
        help="Lower = more deterministic. 0.1 recommended for scientific analysis.",
    )

    st.markdown("#### Cost Estimates (per 1M tokens)")
    cost_data = {
        "Model": ["Opus 4.6", "Sonnet 4.6", "Haiku 4.5"],
        "Input ($/1M)": ["$15.00", "$3.00", "$0.80"],
        "Output ($/1M)": ["$75.00", "$15.00", "$4.00"],
    }
    st.table(cost_data)


def _render_data_settings(config: WorkbenchConfig):
    st.subheader("Dataset Paths")
    st.markdown("Point to locally downloaded datasets for full offline analysis power.")

    config.data_dir = st.text_input(
        "Base Data Directory",
        value=config.data_dir,
        help="Root directory for celltype datasets.",
    )

    config.depmap_path = st.text_input(
        "DepMap Data Path",
        value=config.depmap_path,
        placeholder="/path/to/depmap/2024Q4/",
        help="CRISPR, mutations, expression, copy number.",
    )

    config.prism_path = st.text_input(
        "PRISM Data Path",
        value=config.prism_path,
        placeholder="/path/to/prism/",
        help="Broad PRISM drug viability screens.",
    )

    config.msigdb_path = st.text_input(
        "MSigDB Data Path",
        value=config.msigdb_path,
        placeholder="/path/to/msigdb/",
        help="Gene sets & pathways for GSEA.",
    )

    st.divider()
    st.markdown("#### Data Pull Commands")
    st.markdown("Run these in your terminal to download datasets:")
    st.code("""ct data pull depmap     # ~15 GB — CRISPR, mutations, expression
ct data pull prism      # ~5 GB — Drug viability screens
ct data pull msigdb     # ~500 MB — Gene sets & pathways
ct data pull alphafold  # On-demand — Protein structures""", language="bash")


def _render_advanced_settings(config: WorkbenchConfig):
    st.subheader("Advanced Settings")

    config.parallel_agents = st.number_input(
        "Parallel Agents",
        1, 10, config.parallel_agents,
        help="Number of parallel agents for complex queries (e.g., /agents N).",
    )

    config.reports_dir = st.text_input(
        "Reports Directory",
        value=config.reports_dir,
        help="Where generated reports are saved.",
    )

    config.theme = st.selectbox(
        "UI Theme",
        ["dark", "light"],
        index=0 if config.theme == "dark" else 1,
    )

    st.divider()
    st.markdown("#### Environment Variables")
    st.markdown("Alternative: set these in your shell or `.env` file:")
    st.code("""export ANTHROPIC_API_KEY="sk-ant-..."
export CELLTYPE_DATA_DIR="~/.celltype/data"
export NCBI_API_KEY="optional"  """, language="bash")

    st.divider()
    st.markdown("#### CLI Quick Reference")
    st.code("""# Interactive mode
ct

# One-shot query
ct "Your natural language query"

# Parallel agents
/agents 5 "complex query"

# Diagnostics
ct doctor

# Data management
ct data pull depmap
ct data list

# Reports
ct report list
ct report publish
ct report show""", language="bash")

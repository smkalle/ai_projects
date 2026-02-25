"""Help & Tutorial page — comprehensive guide to the workbench and celltype-cli."""

import streamlit as st


def render_help():
    """Render the help and tutorial page."""
    st.title("❓ Help & Tutorial")
    st.caption("Comprehensive guide to the CellType Research Workbench and celltype-cli.")

    tab_overview, tab_install, tab_workflows, tab_cli, tab_tips, tab_trouble = st.tabs([
        "📖 Overview", "🔧 Installation", "🔬 Workflows",
        "💻 CLI Reference", "💡 Tips", "🔧 Troubleshooting",
    ])

    with tab_overview:
        _render_overview()
    with tab_install:
        _render_installation()
    with tab_workflows:
        _render_workflows()
    with tab_cli:
        _render_cli_reference()
    with tab_tips:
        _render_tips()
    with tab_trouble:
        _render_troubleshooting()


def _render_overview():
    st.subheader("What is CellType CLI?")
    st.markdown("""
**celltype-cli** is an open-source autonomous AI agent for drug discovery from [CellType Inc](https://celltype.com).
It turns natural-language questions into fully executed, multi-step bioinformatics workflows using:

- **Claude AI reasoning** (Opus 4.6 — 90% accuracy on BixBench-Verified-50)
- **190+ pre-integrated tools** (target ID, chemistry, expression analysis, viability screens, safety flags, DNA design, PubMed/ChEMBL/OpenAlex)
- **Managed datasets** (DepMap CRISPR/viability/expression, PRISM, MSigDB, AlphaFold)
- **Persistent Python/R sandbox** with BioPython, pandas, scipy, gseapy, pydeseq2, scanpy, RDKit

### This Research Workbench

This web application provides an intuitive graphical interface on top of celltype-cli:

| Feature | Description |
|---------|-------------|
| **Research Agent Chat** | Natural language interface to the full agent |
| **Target Prioritization** | Guided workflow for degradation target analysis |
| **Resistance Biomarkers** | Panel builder using DepMap + PRISM + L1000 |
| **Combination Strategy** | Synergy discovery and clinical trial mapping |
| **Literature Synthesis** | Multi-source evidence synthesis |
| **Molecular Design** | Primers, codon optimization, assemblies, CRISPR |
| **Data Explorer** | Interactive visualization of all datasets |
| **Reports & Sessions** | Persistent sessions with exportable reports |

### Benchmark Performance

| System | BixBench-Verified-50 Accuracy |
|--------|-------------------------------|
| **celltype-cli (Opus 4.6)** | **90%** |
| Phyo Bio | 88.7% |
| OpenAI Agents SDK | 61.3% |
""")


def _render_installation():
    st.subheader("Installation Guide")
    st.markdown("""
### Prerequisites
- Python 3.10+ (recommended 3.11/3.12)
- ~10 GB free disk initially (more for datasets)
- Anthropic API key
- Terminal access (Linux/macOS preferred; WSL on Windows)

### Step 1: Get Your Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up / log in
3. Navigate to **Settings → API Keys → Create Key**
4. Name it (e.g., "celltype-cli-research")
5. Copy the `sk-ant-...` key immediately (shown only once)
6. Add billing if needed for production use

### Step 2: Install celltype-cli
""")

    st.code("""# Option A: Quick install (recommended)
curl -fsSL https://raw.githubusercontent.com/celltype/cli/main/install.sh | bash

# Option B: Manual via pipx (isolated)
pipx install celltype-cli

# Option C: Standard pip
pip install celltype-cli

# Option D: Full scientific stack (RDKit, scanpy, torch, etc.)
pip install "celltype-cli[all]"
""", language="bash")

    st.markdown("""
### Step 3: Configure
""")

    st.code("""# Interactive setup wizard
ct setup

# Or manually set env var
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify installation
ct doctor
""", language="bash")

    st.markdown("""
### Step 4: Pull Datasets (Optional but Recommended)
""")
    st.code("""ct data pull depmap     # ~15 GB — CRISPR, mutations, expression
ct data pull prism      # ~5 GB — Drug viability screens
ct data pull msigdb     # ~500 MB — Gene sets & pathways
ct data pull alphafold  # On-demand structures
""", language="bash")

    st.markdown("""
### Step 5: Launch This Workbench
""")
    st.code("""# Install workbench dependencies
pip install -r requirements.txt

# Launch the web interface
streamlit run app.py
""", language="bash")


def _render_workflows():
    st.subheader("Workflow Guide")

    workflows = [
        ("🎯 Target Prioritization", """
**Use case:** Prioritize degradation targets for a molecular glue or PROTAC.

**Example query:**
```
I have a CRBN-based molecular glue. Proteomics shows strong degradation of IKZF1,
GSPT1, and CK1α in MM cells. Prioritize the best therapeutic target using DepMap
co-essentiality, TCGA expression, and safety flags. Output a ranked table with evidence.
```

**What the agent does:**
1. Searches literature (PubMed/ChEMBL)
2. Queries DepMap for dependency scores and co-essentiality networks
3. Checks safety flags (SALL4 risk, anti-targets)
4. Runs viability correlations via PRISM
5. Returns ranked table + Markdown report with plots
"""),
        ("🧪 Resistance Biomarker Panel", """
**Use case:** Build a resistance biomarker panel for a drug program.

**Example query:**
```
Build a 10-gene resistance biomarker panel for a BET inhibitor in AML. Use DepMap
mutation sensitivity, PRISM viability, and L1000 signatures. Validate with TCGA stratification.
```

**Agent pipeline:** DepMap/PRISM subset → statistical tests → literature cross-reference → CSV + heatmap
"""),
        ("💊 Combination Strategy", """
**Use case:** Find synergistic drug combinations for your lead compound.

**Example query:**
```
My lead compound shows low immune infiltration in RNA-seq. Suggest 3 synergistic
combinations using DepMap co-dependency, Reactome pathways, and ClinicalTrials.gov.
Prioritize by therapeutic window and safety.
```
"""),
        ("📚 Literature Synthesis", """
**Use case:** Comprehensive evidence synthesis from multiple sources.

**Example query:**
```
Summarize all known neosubstrates for CRBN molecular glues from 2020-2026.
Cross-reference with DepMap essentiality in multiple lineages and propose a new indication.
```
"""),
        ("🧬 Molecular Design", """
**Use case:** Design primers, optimize codons, plan assemblies, design CRISPR guides.

**Example query:**
```
Design Golden Gate assembly primers and codon-optimize an ORF for IKZF1 degradation
domain expression in E. coli.
```
"""),
    ]

    for title, content in workflows:
        with st.expander(title, expanded=False):
            st.markdown(content)


def _render_cli_reference():
    st.subheader("CLI Quick Reference")
    st.code("""# Interactive mode (most powerful)
ct

# One-shot query
ct "Your natural language query"

# Parallel agents (multi-perspective)
/agents 5 "complex query"

# Diagnostics
ct doctor

# Configuration
ct setup
ct config set data.depmap /path/
ct config set data.prism /path/

# Data management
ct data pull depmap
ct data pull prism
ct data list

# Reports
ct report list
ct report publish    # → self-contained HTML
ct report show       # → opens in browser

# Session management
ct --continue        # resume last session

# Help
/help
/tools               # list all 190+ tools
/usage               # token/cost tracking

# Export
/export notebook     # → Jupyter notebook

# Case studies
/case-study 1        # curated drug discovery scenario
""", language="bash")


def _render_tips():
    st.subheader("Pro Tips for Production Research")
    st.markdown("""
1. **Always start with `ct doctor`** and local data pulls for best results
2. **Use interactive mode** for iterative research — most powerful mode
3. **Review every report** — the agent is excellent but validate key scientific claims
4. **Use parallel agents** (`/agents 4 "query"`) for complex questions — gives more robust multi-perspective answers
5. **Track costs** via `/usage` — set Anthropic usage limits in the console
6. **Start with Haiku** for exploration, switch to Opus for final analysis
7. **Use follow-up queries** in the same session for iterative refinement
8. **Export to notebook** (`/export notebook`) for reproducible analysis in Jupyter
9. **For regulated/pharma work**, consider CellType's on-prem proprietary agents
10. **Contribute back!** Fork the repo, add tools, PRs welcome
""")


def _render_troubleshooting():
    st.subheader("Troubleshooting")

    issues = [
        ("ct command not found", "Restart terminal or run `pipx ensurepath`. Verify with `which ct`."),
        ("API key error", "Run `ct setup` or `export ANTHROPIC_API_KEY=sk-ant-...`"),
        ("Dataset missing", "Run `ct data pull <name>`. Check paths with `ct config list`."),
        ("Missing RDKit/scanpy", "Install full stack: `pip install 'celltype-cli[all]'`"),
        ("Rate limits (PubMed)", "Wait 30s or add NCBI API key. Use local data when possible."),
        ("Session lost", "Run `ct --continue` to resume. Sessions auto-save in `~/.celltype/sessions/`."),
        ("Slow startup", "Run `ct doctor`. Check if datasets are loading unnecessarily."),
        ("Out of memory", "Reduce dataset scope or use API fallback instead of local data."),
        ("Streamlit errors", "Ensure all dependencies: `pip install -r requirements.txt`"),
    ]

    for issue, fix in issues:
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{issue}**")
            with col2:
                st.markdown(fix)

    st.divider()
    st.markdown("#### Resources")
    st.markdown("""
- **GitHub:** [github.com/celltype/cli](https://github.com/celltype/cli)
- **Benchmark:** [BixBench-Verified-50](https://huggingface.co/datasets/phylobio/BixBench-Verified-50)
- **CellType:** [celltype.com](https://celltype.com)
- **Anthropic Console:** [console.anthropic.com](https://console.anthropic.com/)
    """)

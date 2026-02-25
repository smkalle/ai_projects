# CellType Research Workbench

An interactive bioinformatics research workbench web application powered by [celltype-cli](https://github.com/celltype/cli) — the autonomous AI agent for drug discovery.

## Features

- **Research Agent Chat** — Natural language interface to 190+ bioinformatics tools
- **Target Prioritization** — DepMap essentiality, TCGA expression, safety profiling
- **Resistance Biomarker Panel** — DepMap mutations, PRISM viability, L1000 signatures
- **Drug Combination Strategy** — Co-dependency, Reactome pathways, clinical trials
- **Literature & Data Synthesis** — PubMed, ChEMBL, OpenAlex cross-referencing
- **Molecular Biology Design** — Primers, codon optimization, assemblies, CRISPR guides
- **Interactive Data Explorer** — Plotly-powered visualization of all datasets
- **Session & Report Management** — Persistent sessions with exportable reports

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# (Optional) Install celltype-cli for full agent capabilities
pip install celltype-cli

# Configure API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Launch the workbench
streamlit run app.py
```

## Configuration

1. Set your Anthropic API key in Settings or via environment variable
2. (Optional) Install celltype-cli: `pip install celltype-cli`
3. (Optional) Pull datasets: `ct data pull depmap`, `ct data pull prism`

## Architecture

```
celltype-research-workbench/
├── app.py                    # Main Streamlit application entry point
├── components/               # UI components
│   ├── sidebar.py            # Navigation sidebar
│   ├── dashboard.py          # Dashboard & system health
│   ├── agent_chat.py         # Research agent chat interface
│   ├── settings.py           # Configuration management
│   ├── data_explorer.py      # Interactive data explorer
│   ├── data_management.py    # Dataset download & paths
│   ├── reports.py            # Reports & session management
│   └── help_page.py          # Help & tutorial
├── workflows/                # Research workflow modules
│   ├── target_prioritization.py
│   ├── resistance_biomarkers.py
│   ├── combination_strategy.py
│   ├── literature_synthesis.py
│   └── molecular_design.py
├── utils/                    # Core utilities
│   ├── config.py             # Configuration management
│   ├── state.py              # Session state management
│   ├── celltype_agent.py     # Agent interface (CLI + API)
│   └── sample_data.py        # Sample data generators
├── .streamlit/config.toml    # Streamlit theme & settings
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variable template
```

## Powered By

- [celltype-cli](https://github.com/celltype/cli) — Autonomous AI agent for drug discovery
- [Claude AI](https://anthropic.com) — Anthropic's reasoning models
- [Streamlit](https://streamlit.io) — Web application framework
- [Plotly](https://plotly.com) — Interactive visualizations

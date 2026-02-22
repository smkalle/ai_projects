# Quickstart Guide

Get up and running in under 2 minutes.

## Prerequisites

- Python 3.10 or higher
- Git
- [uv](https://docs.astral.sh/uv/) — fast Python package manager (auto-installed by `setup.sh` if missing)
- (Optional) An NCBI account for API access — [register here](https://www.ncbi.nlm.nih.gov/account/)

## 1. Clone & Setup

```bash
git clone https://github.com/smkalle/ai_projects.git
cd ai_projects/bioinfo-code-mcp

# One-command setup (installs uv if needed, creates venv, installs everything, runs self-test)
./setup.sh
```

The setup script will:
- Install `uv` if not already available
- Create a `.venv` virtual environment via `uv venv`
- Install all dependencies with `uv pip install`
- Verify imports
- Run a quick self-test

### Setup Options

```bash
./setup.sh              # Full install (default) — everything including test tools
./setup.sh --core       # Minimal — MCP server only, no playground
./setup.sh --playground # Core + interactive web playground
./setup.sh --dev        # Everything including linting and testing
```

### Manual uv Install (if needed)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip / pipx / brew
pip install uv
brew install uv
```

## 2. Configure NCBI Access

NCBI requires an email for API usage. Set it before making API calls:

```bash
export NCBI_EMAIL="your-email@institution.edu"

# Optional: API key increases rate limit from 3 to 10 requests/second
export NCBI_API_KEY="your-key-here"
```

Add these to your `~/.bashrc` or `~/.zshrc` to persist across sessions.

> **Note:** Sequence utility functions (GC content, translation, ORF finding, etc.)
> and format parsers (FASTA, GFF, BED) work entirely offline — no API key needed.

## 3. Launch the Playground

```bash
./run.sh playground
```

Open **http://localhost:8765** in your browser. You'll see:

- A **code editor** on top with Python syntax highlighting
- **12 starter templates** in the left sidebar organized by category
- An **output panel** below showing execution results

### Try it:

1. Click **"DNA Sequence Analysis"** in the sidebar
2. Press **Ctrl+Enter** (or click **Run**)
3. See GC content, translation, ORFs, and restriction sites computed instantly

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Run code |
| `Ctrl+K` | Search API operations |
| `Ctrl+/` | Toggle comment |
| `Escape` | Close search modal |

## 4. Run Examples

Run all three example scripts:

```bash
./run.sh examples
```

Or run a specific one:

```bash
./run.sh example sequence_analysis   # Local sequence analysis (no network)
./run.sh example agent_demo          # Full agent workflow demo
./run.sh example protein_lookup      # Cross-database protein lookup (needs network)
```

### What Each Example Does

| Example | What it demonstrates | Needs network? |
|---------|---------------------|----------------|
| `sequence_analysis` | GC content, ORFs, restriction sites, FASTA parsing, pairwise identity | No |
| `agent_demo` | Full 6-step workflow: search registry, query NCBI, UniProt, analyze DNA, parse FASTA, state persistence | Yes (steps 2-3) |
| `protein_lookup` | Cross-database lookup: UniProt → PDB → Ensembl for TP53 | Yes |

## 5. Run Tests

```bash
./run.sh test              # Full suite (144 tests)
./run.sh test --quick      # Skip network-dependent tests
./run.sh test --coverage   # With coverage report
```

## 6. Search Available Operations

Discover what you can do from the command line:

```bash
./run.sh search "gene lookup"
./run.sh search "protein structure"
./run.sh search "BLAST"
./run.sh search "parse FASTA"
./run.sh search "restriction enzyme"

# See all modules and operation counts
./run.sh info
```

## 7. Use as MCP Server

Connect to AI agents (Claude, etc.) via the MCP protocol:

```bash
# Start the MCP server (stdio transport)
./run.sh server
```

Or add to your MCP client config (`.mcp.json`):

```json
{
  "mcpServers": {
    "bioinfo-code-mcp": {
      "type": "stdio",
      "command": "bioinfo-mcp",
      "env": {
        "NCBI_EMAIL": "your-email@institution.edu"
      }
    }
  }
}
```

## All Commands

```bash
./run.sh playground          # Start web playground (http://localhost:8765)
./run.sh examples            # Run all example scripts
./run.sh example <name>      # Run one example
./run.sh test [--quick]      # Run tests
./run.sh test --coverage     # Tests with coverage
./run.sh server              # Start MCP server
./run.sh search <query>      # Search operations
./run.sh info                # Show project info
./run.sh lint                # Run linter
./run.sh fmt                 # Auto-format code
```

All commands use `uv run` under the hood for fast, reliable execution.

## Starter Project Templates

The playground includes 12 ready-to-run templates:

### Getting Started
- **Gene Lookup** — Search NCBI + Ensembl for gene info by symbol
- **DNA Sequence Analysis** — GC content, translation, ORFs, restriction sites
- **FASTA Processing** — Parse multi-sequence FASTA, pairwise identity
- **Fetch NCBI Sequences** — Download and analyze sequences by accession

### Protein Analysis
- **Protein Search & Features** — UniProt search, domains, GO annotations
- **Protein Structure Lookup** — PDB text search, structure details, entities

### Research
- **PubMed Literature Search** — Search and summarize research papers
- **Cross-Database Research** — Chain NCBI → Ensembl → UniProt → PDB
- **BLAST Sequence Search** — Submit and retrieve BLAST results

### Genomics
- **Variant Analysis with VEP** — Look up rsIDs, alleles, MAF, gene info
- **Genomic Region Analysis** — Parse and analyze BED and GFF files

### Lab Tools
- **PCR Primer Design Helper** — Evaluate Tm, GC%, self-complementarity

### Advanced
- **Multi-Step Stateful Workflow** — Build pipelines across multiple Run clicks

## Troubleshooting

### "ModuleNotFoundError: No module named 'bioinfo_code_mcp'"

Run `./setup.sh` first, or manually: `uv pip install -e .`

### "uv: command not found"

Run `./setup.sh` (it auto-installs uv), or install manually:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### API calls return errors

- Make sure `NCBI_EMAIL` is set
- Check your network connection
- Some APIs have rate limits — wait a few seconds between calls
- BLAST searches can take 1-5 minutes to complete

### Playground won't start

Install playground dependencies: `uv pip install -e ".[playground]"` or `./setup.sh --playground`

### Tests fail

```bash
# Run without network tests first
./run.sh test --quick

# If all 144 pass locally, network tests may fail due to API availability
```

# Bioinformatics Code Mode MCP

A **Code Mode MCP server** for bioinformatics research — exposes just **two tools** (`search` + `execute`) that let AI agents dynamically discover and run Python code against bioinformatics APIs. Inspired by [Cloudflare's Code Mode MCP](https://blog.cloudflare.com/code-mode-mcp/) and [Armin Ronacher's Code MCPs concept](https://lucumr.pocoo.org/2025/8/18/code-mcps/).

## The Problem

Traditional MCP servers expose each API endpoint as a separate tool. For bioinformatics — with databases like NCBI (hundreds of endpoints), UniProt, PDB, Ensembl, and BLAST — this means:

- **Thousands of tool definitions** bloating the agent's context window
- **Millions of tokens** consumed by schemas before the agent can even start working
- **No composability** — chaining multi-step analyses requires many round trips
- **Static discovery** — agents can't explore what's available

## The Solution: Code Mode

Instead of one tool per endpoint, this server exposes **two tools**:

| Tool | Purpose | Token Cost |
|------|---------|------------|
| `search` | Discover available bioinformatics operations by keyword, tag, or module | ~500 tokens |
| `execute` | Run Python code in a sandboxed environment with pre-loaded API clients | ~500 tokens |

**Total context: ~1,000 tokens** — regardless of how many databases or endpoints are supported.

### How It Works

```
Agent                           Code MCP Server
  │                                   │
  │  search("gene lookup protein")    │
  │──────────────────────────────────>│  ← Dynamic discovery
  │  [ncbi.fetch_gene_info,           │
  │   uniprot.search_protein, ...]    │
  │<──────────────────────────────────│
  │                                   │
  │  execute("""                      │
  │    genes = await ncbi             │
  │      .fetch_gene_info("TP53")     │
  │    protein = await uniprot        │
  │      .search_protein("TP53")      │
  │    state["results"] = {...}       │
  │    return state["results"]        │
  │  """)                             │
  │──────────────────────────────────>│  ← Code execution
  │  { gene_info: ...,                │     with API calls,
  │    protein: ...,                  │     loops, conditionals,
  │    state_keys: [...] }            │     and state persistence
  │<──────────────────────────────────│
```

## Features

- **5 bioinformatics API clients**: NCBI Entrez, UniProt, RCSB PDB, Ensembl, NCBI BLAST
- **Sequence utilities**: reverse complement, translate, GC content, ORF finding, restriction sites, molecular weight
- **Format parsers**: FASTA, GFF3, BED, Clustal alignment
- **Stateful sandbox**: `state` dict persists across executions for multi-step workflows
- **Async-native**: All API calls use `async/await` for efficient I/O
- **40+ discoverable operations** via the search tool

## Supported Databases & Operations

| Module | Operations | Examples |
|--------|-----------|----------|
| **NCBI** | esearch, efetch, esummary, einfo, elink, search_pubmed, fetch_gene_info, fetch_sequence | Search PubMed, fetch genes, get sequences |
| **UniProt** | search, fetch_entry, fetch_fasta, search_protein, get_protein_features, get_go_terms | Protein lookup, domains, GO annotations |
| **PDB** | get_entry, get_entity, text_search, search_by_uniprot, get_structure_summary | Structure search, resolution data |
| **Ensembl** | lookup_id, lookup_symbol, get_sequence, get_variant, get_vep, get_xrefs, get_gene_summary | Gene lookup, variants, VEP predictions |
| **BLAST** | submit, wait_for_results, blastn, blastp | Sequence similarity search |
| **Seq Utils** | reverse_complement, translate, gc_content, find_orfs, restriction_sites, molecular_weight, transcribe | Sequence analysis |
| **Format Utils** | parse_fasta, write_fasta, parse_gff, parse_bed, parse_clustal | File format handling |

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/smkalle/ai_projects.git
cd ai_projects/bioinfo-code-mcp

# Install with pip
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

### Configuration

Set your NCBI email (required by NCBI's usage policy):

```bash
export NCBI_EMAIL="your-email@institution.edu"
export NCBI_API_KEY="your-key"  # Optional, increases rate limit
```

### Running the MCP Server

```bash
# Via the installed CLI command
bioinfo-mcp

# Or via Python module
python -m bioinfo_code_mcp.server
```

### MCP Client Configuration

Add to your MCP client's config (`.mcp.json` or similar):

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

## Usage Examples

### Example 1: Gene Research Workflow

An agent generates and executes this code:

```python
# Step 1: Search for TP53 gene information
genes = await ncbi.fetch_gene_info("TP53", organism="human")
state["gene"] = genes[0]

# Step 2: Get protein from UniProt
proteins = await uniprot.search_protein("TP53")
accession = proteins[0]["primaryAccession"]
state["uniprot_accession"] = accession

# Step 3: Find crystal structures
structures = await pdb.search_by_uniprot(accession)
state["structures"] = structures

return {
    "gene": state["gene"].get("name"),
    "uniprot": accession,
    "pdb_count": len(structures),
}
```

### Example 2: Sequence Analysis

```python
# Fetch and analyze a sequence
fasta = await ncbi.fetch_sequence("nucleotide", "NM_007294")
records = fmt.parse_fasta(fasta)
seq = records[0].sequence

gc = seq_utils.gc_content(seq)
orfs = seq_utils.find_orfs(seq, min_length=300)
sites = seq_utils.restriction_sites(seq)

return {
    "length": len(seq),
    "gc_content": round(gc, 4),
    "orf_count": len(orfs),
    "restriction_sites": {k: len(v) for k, v in sites.items()},
}
```

### Example 3: Cross-Database Variant Analysis

```python
# Look up a variant in Ensembl
variant = await ensembl.get_variant("rs699")

# Get VEP predictions
effects = await ensembl.get_vep("human", "ENST00000366667.4:c.803T>C")

# Cross-reference gene in NCBI
gene_info = await ncbi.fetch_gene_info("AGT")

state["variant_report"] = {
    "variant": variant,
    "effects": effects,
    "gene": gene_info,
}
return state["variant_report"]
```

### Running the Demo Scripts

```bash
# Full agent workflow demo (uses local sandbox, no API calls needed for utilities)
python examples/agent_demo.py

# Sequence analysis workflow
python examples/sequence_analysis.py

# Protein structure lookup (makes real API calls)
NCBI_EMAIL=you@example.com python examples/protein_lookup.py
```

## Architecture

```
bioinfo-code-mcp/
├── src/bioinfo_code_mcp/
│   ├── server.py          # MCP server — 2 tools: search + execute
│   ├── sandbox.py         # Sandboxed async Python execution
│   ├── registry.py        # Operation discovery catalog
│   ├── config.py          # Configuration management
│   ├── apis/
│   │   ├── ncbi.py        # NCBI Entrez E-utilities
│   │   ├── uniprot.py     # UniProt REST API
│   │   ├── pdb.py         # RCSB PDB Data + Search API
│   │   ├── ensembl.py     # Ensembl REST API
│   │   └── blast.py       # NCBI BLAST
│   └── utils/
│       ├── sequence.py    # DNA/protein sequence utilities
│       └── formats.py     # FASTA, GFF, BED, Clustal parsers
├── examples/
│   ├── agent_demo.py      # Full workflow demonstration
│   ├── sequence_analysis.py
│   └── protein_lookup.py
├── tests/                 # Comprehensive test suite
├── .github/workflows/     # CI/CD
├── pyproject.toml
└── .mcp.json              # MCP client configuration
```

### Design Principles

1. **Two tools, not hundreds**: `search` + `execute` cover the entire bioinformatics API surface
2. **Agent writes code**: Leverages LLMs' coding proficiency (per Ronacher's insight)
3. **Stateful sessions**: `state` dict persists across calls for multi-step analysis
4. **Dynamic discovery**: Agents find operations at runtime via `search`
5. **Sandboxed execution**: Restricted builtins, timeout enforcement, output limits
6. **Async throughout**: Non-blocking API calls via httpx

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (skips network-dependent tests)
pytest tests/ -v -m "not network"

# Run with network tests (requires internet)
pytest tests/ -v

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/bioinfo_code_mcp/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NCBI_EMAIL` | Email for NCBI API access (required by policy) | `user@example.com` |
| `NCBI_API_KEY` | NCBI API key (increases rate limit from 3 to 10 req/s) | — |
| `EXEC_TIMEOUT` | Code execution timeout in seconds | `30` |
| `MAX_OUTPUT_CHARS` | Maximum stdout capture size | `50000` |
| `HTTP_TIMEOUT` | HTTP client timeout in seconds | `30` |
| `MCP_TRANSPORT` | Transport type: `stdio` or `http` | `stdio` |

## Background & References

This project implements the **Code Mode MCP pattern** — a paradigm shift in how AI agents interact with tools:

- **[Cloudflare Code Mode MCP](https://blog.cloudflare.com/code-mode-mcp/)** — Covers 2,500+ API endpoints with just `search()` + `execute()`, reducing token usage by 81%
- **[Armin Ronacher: "Your MCP Doesn't Need 30 Tools: It Needs Code"](https://lucumr.pocoo.org/2025/8/18/code-mcps/)** — Proposes single-tool code execution over fragmented multi-tool setups
- **[Armin Ronacher: "Building an Agent That Leverages Throwaway Code"](https://lucumr.pocoo.org/2025/10/17/code/)** — Explores agents writing throwaway code for non-coding tasks
- **[Anthropic: Code Execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)** — Validates the pattern independently

### Why Code Mode for Bioinformatics?

Bioinformatics involves:
- **Dozens of databases** (NCBI, UniProt, PDB, Ensembl, etc.) with hundreds of endpoints
- **Multi-step workflows** (search → fetch → analyze → cross-reference)
- **Data processing** (parsing FASTA, finding ORFs, calculating properties)

Traditional MCP would require hundreds of tool definitions. Code Mode reduces this to two tools, letting the agent compose complex workflows in Python — the language bioinformaticians already think in.

## License

MIT License — see [LICENSE](LICENSE).

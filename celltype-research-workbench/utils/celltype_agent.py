"""CellType CLI agent interface — bridges the Streamlit UI to celltype-cli and Anthropic API."""

import json
import subprocess
import shutil
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Generator

import streamlit as st

from utils.config import WorkbenchConfig, TOOL_CATEGORIES


@dataclass
class AgentResponse:
    content: str
    tools_used: list[str]
    tokens_input: int
    tokens_output: int
    cost: float
    duration: float
    status: str  # "success" | "error" | "partial"


def _estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate API cost based on model pricing."""
    pricing = {
        "claude-opus-4-6": (15.0, 75.0),
        "claude-sonnet-4-6": (3.0, 15.0),
        "claude-haiku-4-5-20251001": (0.80, 4.0),
    }
    inp_rate, out_rate = pricing.get(model, (15.0, 75.0))
    return (input_tokens * inp_rate + output_tokens * out_rate) / 1_000_000


def check_celltype_installed() -> dict:
    """Check if celltype-cli is installed and functional."""
    result = {"installed": False, "version": None, "doctor": None}
    ct_path = shutil.which("ct")
    if ct_path:
        result["installed"] = True
        try:
            ver = subprocess.run(
                ["ct", "--version"], capture_output=True, text=True, timeout=10
            )
            result["version"] = ver.stdout.strip() or ver.stderr.strip() or "Unknown"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            result["version"] = "Error checking version"
    return result


def run_ct_doctor() -> dict:
    """Run ct doctor and return structured health check."""
    health = {
        "cli_installed": False,
        "api_key_set": False,
        "datasets_available": [],
        "python_env": True,
        "issues": [],
    }
    ct_info = check_celltype_installed()
    health["cli_installed"] = ct_info["installed"]

    config = WorkbenchConfig.load()
    health["api_key_set"] = bool(config.anthropic_api_key)

    if not health["cli_installed"]:
        health["issues"].append("celltype-cli not installed. Run: pip install celltype-cli")
    if not health["api_key_set"]:
        health["issues"].append("Anthropic API key not configured. Set it in Settings.")

    if health["cli_installed"]:
        try:
            doc = subprocess.run(
                ["ct", "doctor"], capture_output=True, text=True, timeout=30
            )
            output = doc.stdout + doc.stderr
            if "operational" in output.lower():
                health["doctor_status"] = "All systems operational"
            else:
                health["doctor_status"] = output[:500]
                health["issues"].append("ct doctor reported issues — see details.")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            health["doctor_status"] = "Could not run ct doctor"

    return health


def run_celltype_query(query: str, config: WorkbenchConfig) -> AgentResponse:
    """Execute a query through celltype-cli or simulate via Anthropic API."""
    start = time.time()

    ct_info = check_celltype_installed()
    if ct_info["installed"] and config.anthropic_api_key:
        return _run_via_cli(query, config, start)

    if config.anthropic_api_key:
        return _run_via_api(query, config, start)

    return _run_simulation(query, start)


def _run_via_cli(query: str, config: WorkbenchConfig, start: float) -> AgentResponse:
    """Execute query through the actual celltype-cli."""
    try:
        env = {"ANTHROPIC_API_KEY": config.anthropic_api_key}
        result = subprocess.run(
            ["ct", query],
            capture_output=True, text=True, timeout=300,
            env={**__import__("os").environ, **env},
        )
        duration = time.time() - start
        output = result.stdout or result.stderr or "No output received."
        return AgentResponse(
            content=output,
            tools_used=_extract_tools_from_output(output),
            tokens_input=0,
            tokens_output=0,
            cost=0.0,
            duration=duration,
            status="success" if result.returncode == 0 else "error",
        )
    except subprocess.TimeoutExpired:
        return AgentResponse(
            content="Query timed out after 5 minutes. Try a simpler query.",
            tools_used=[], tokens_input=0, tokens_output=0,
            cost=0.0, duration=time.time() - start, status="error",
        )


def _run_via_api(query: str, config: WorkbenchConfig, start: float) -> AgentResponse:
    """Execute query through the Anthropic API with a bioinformatics system prompt."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=config.anthropic_api_key)

        system_prompt = _build_system_prompt()

        message = client.messages.create(
            model=config.default_model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )

        duration = time.time() - start
        content = ""
        for block in message.content:
            if hasattr(block, "text"):
                content += block.text

        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        cost = _estimate_cost(input_tokens, output_tokens, config.default_model)

        return AgentResponse(
            content=content,
            tools_used=_infer_tools_from_query(query),
            tokens_input=input_tokens,
            tokens_output=output_tokens,
            cost=cost,
            duration=duration,
            status="success",
        )
    except Exception as e:
        return AgentResponse(
            content=f"API Error: {str(e)}",
            tools_used=[], tokens_input=0, tokens_output=0,
            cost=0.0, duration=time.time() - start, status="error",
        )


def _run_simulation(query: str, start: float) -> AgentResponse:
    """Run in demo/simulation mode when no API key is available."""
    duration = time.time() - start + 0.5
    tools = _infer_tools_from_query(query)
    tool_list = ", ".join(tools[:5]) if tools else "General Analysis"

    content = f"""## Analysis Results (Demo Mode)

> **Note:** Running in demonstration mode. Configure your Anthropic API key in Settings for live agent results.

### Query
{query}

### Simulated Workflow
The CellType agent would execute the following pipeline:

**Tools Selected:** {tool_list}

#### Step 1: Query Parsing & Planning
The agent parses your natural language query and identifies:
- **Domain:** {'Drug Discovery' if 'drug' in query.lower() or 'target' in query.lower() else 'Bioinformatics Research'}
- **Required Data:** {'DepMap, PRISM' if 'depmap' in query.lower() or 'target' in query.lower() else 'PubMed, ChEMBL'}
- **Output Format:** Ranked table with evidence scores

#### Step 2: Data Retrieval & Integration
- Queried {len(tools)} specialized tools
- Cross-referenced multiple data sources
- Applied statistical filters (FDR < 0.05)

#### Step 3: Analysis & Results

| Rank | Target | Evidence Score | Source | Safety Flag |
|------|--------|---------------|--------|-------------|
| 1 | Gene_A | 0.95 | DepMap + Literature | Clear |
| 2 | Gene_B | 0.87 | PRISM + TCGA | Review |
| 3 | Gene_C | 0.82 | Co-essentiality | Clear |

#### Step 4: Recommendations
Based on the integrated analysis, the top candidate shows strong evidence across multiple orthogonal data sources with no safety concerns.

---
*Install celltype-cli and configure API key for full agent-powered analysis.*
"""
    return AgentResponse(
        content=content,
        tools_used=tools,
        tokens_input=500,
        tokens_output=1500,
        cost=0.0,
        duration=duration,
        status="success",
    )


def _build_system_prompt() -> str:
    """Build a comprehensive bioinformatics system prompt."""
    tools_desc = "\n".join(
        f"- **{cat}:** {', '.join(tools)}"
        for cat, tools in TOOL_CATEGORIES.items()
    )
    return f"""You are an expert bioinformatics AI research agent, equivalent to the celltype-cli autonomous agent for drug discovery. You have deep expertise in:

1. **Target Identification & Validation** — DepMap CRISPR essentiality, co-essentiality networks, TCGA expression, safety profiling
2. **Drug Discovery Chemistry** — PROTAC design, molecular glue neosubstrates, ChEMBL activity data, molecular descriptors
3. **Genomics & Transcriptomics** — Differential expression, GSEA, variant annotation, copy number analysis
4. **Drug Sensitivity Profiling** — PRISM viability, dose-response, biomarker-sensitivity correlation, combination synergy
5. **Literature & Knowledge Mining** — PubMed, OpenAlex, ClinicalTrials.gov, patent landscapes, pathway databases
6. **Molecular Biology Design** — Primer design, codon optimization, Golden Gate assembly, CRISPR guide design

Available tool categories:
{tools_desc}

When answering queries:
- Structure your response as a scientific report with clear sections
- Include data tables where relevant (Markdown format)
- Cite data sources (DepMap release, PubMed IDs, ChEMBL IDs)
- Flag safety concerns (anti-targets, toxicity, off-target effects)
- Suggest follow-up experiments or analyses
- Be quantitative — include scores, p-values, confidence intervals where applicable
- Use proper gene nomenclature (HGNC symbols, italicized for genes)

Format your response in well-structured Markdown."""


def _extract_tools_from_output(output: str) -> list[str]:
    """Extract tool names from celltype-cli output."""
    tools = []
    keywords = {
        "depmap": "DepMap Query",
        "prism": "PRISM Viability",
        "pubmed": "PubMed Search",
        "chembl": "ChEMBL Query",
        "gsea": "GSEA Analysis",
        "alphafold": "AlphaFold Structure",
        "rdkit": "RDKit Molecular",
        "primer": "Primer Design",
    }
    lower_output = output.lower()
    for kw, name in keywords.items():
        if kw in lower_output:
            tools.append(name)
    return tools or ["General Analysis"]


def _infer_tools_from_query(query: str) -> list[str]:
    """Infer which tools would be used based on query content."""
    tools = []
    q = query.lower()
    mapping = {
        "target": "DepMap CRISPR Essentiality",
        "essentiality": "DepMap CRISPR Essentiality",
        "depmap": "DepMap Query",
        "co-essential": "Co-Essentiality Networks",
        "prism": "PRISM Viability Screen",
        "drug": "ChEMBL Activity Query",
        "sensitivity": "Drug Sensitivity Profiling",
        "resistance": "Resistance Mechanism Mining",
        "biomarker": "Biomarker-Sensitivity Correlation",
        "expression": "TCGA Expression Analysis",
        "differential": "Differential Expression (pydeseq2)",
        "gsea": "GSEA (gseapy)",
        "pathway": "Pathway Analysis",
        "protac": "PROTAC Linker Design",
        "molecular glue": "Molecular Glue Analysis",
        "degradation": "Degradation Target Analysis",
        "literature": "PubMed Search",
        "pubmed": "PubMed Search",
        "clinical trial": "ClinicalTrials.gov Query",
        "combination": "Combination Synergy Analysis",
        "synergy": "Combination Synergy (Bliss/Loewe)",
        "primer": "Primer Design",
        "codon": "Codon Optimization",
        "golden gate": "Golden Gate Assembly",
        "crispr": "CRISPR Guide RNA Design",
        "structure": "AlphaFold Structure",
        "variant": "Variant Annotation",
        "mutation": "Mutation Analysis",
        "safety": "Safety Flag Checker",
        "survival": "Kaplan-Meier Survival",
        "heatmap": "Heatmap Generator",
        "network": "Network Graph",
    }
    for keyword, tool in mapping.items():
        if keyword in q and tool not in tools:
            tools.append(tool)
    return tools or ["General Analysis"]

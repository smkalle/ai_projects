"""Pre-built examples and sample configurations for all workbench workflows.

Each example includes:
- config: pre-filled workflow configuration (matches session_state keys)
- query: ready-to-run agent query
- description: short human-readable summary
- expected_result: sample output to show in the UI before running the agent
"""

import pandas as pd
import numpy as np


# ============================================================================
# Target Prioritization Examples
# ============================================================================

TARGET_EXAMPLES = {
    "BRD4 Molecular Glue (Multiple Myeloma)": {
        "description": (
            "Evaluate BRD4 and related bromodomain proteins as molecular glue "
            "degradation targets in multiple myeloma using CRBN as the E3 ligase."
        ),
        "config": {
            "genes": ["BRD4", "BRD2", "BRD3", "IKZF1", "GSPT1"],
            "e3_ligase": "CRBN (Cereblon)",
            "modality": "Molecular Glue",
            "indication": "Multiple Myeloma",
            "lineage_filter": ["Hematopoietic"],
            "essentiality_threshold": -0.5,
            "sources": {
                "depmap": True, "coessentiality": True,
                "tcga": True, "safety": True, "literature": True,
            },
        },
        "query": (
            "I have a CRBN-based molecular glue. Proteomics shows degradation of "
            "BRD4, BRD2, BRD3, IKZF1, and GSPT1 in multiple myeloma cells. "
            "Prioritize the best therapeutic target using DepMap co-essentiality, "
            "TCGA expression across normal tissues, and safety profiling. "
            "Output a ranked table with evidence scores, safety flags, and "
            "a final recommendation with rationale."
        ),
        "expected_result": pd.DataFrame({
            "Rank": [1, 2, 3, 4, 5],
            "Target": ["IKZF1", "GSPT1", "BRD4", "BRD2", "BRD3"],
            "Essentiality (CERES)": [-1.32, -0.95, -0.88, -0.42, -0.31],
            "Expression (TPM)": [42.1, 15.3, 78.6, 55.2, 48.9],
            "Co-essentiality": [0.89, 0.76, 0.82, 0.54, 0.47],
            "Safety": ["Pass", "Pass", "Review", "Pass", "Pass"],
            "Literature": ["Strong (23 papers)", "Strong (18 papers)",
                           "Strong (45 papers)", "Moderate (9 papers)",
                           "Weak (4 papers)"],
            "Overall Score": [0.95, 0.88, 0.84, 0.65, 0.52],
        }),
    },
    "KRAS G12C PROTAC (NSCLC)": {
        "description": (
            "Prioritize KRAS G12C and related pathway members as PROTAC targets "
            "for non-small cell lung cancer using VHL as the E3 ligase."
        ),
        "config": {
            "genes": ["KRAS", "BRAF", "EGFR", "MYC", "CDK4"],
            "e3_ligase": "VHL",
            "modality": "PROTAC",
            "indication": "Lung Cancer (NSCLC)",
            "lineage_filter": ["Lung"],
            "essentiality_threshold": -0.5,
            "sources": {
                "depmap": True, "coessentiality": True,
                "tcga": True, "safety": True, "literature": True,
            },
        },
        "query": (
            "Evaluate KRAS, BRAF, EGFR, MYC, and CDK4 as PROTAC targets for NSCLC. "
            "Use VHL as the E3 ligase. Query DepMap essentiality in lung lineages, "
            "check TCGA expression and safety flags. Rank targets by druggability, "
            "essentiality, and safety. Include known PROTAC efforts from literature."
        ),
        "expected_result": pd.DataFrame({
            "Rank": [1, 2, 3, 4, 5],
            "Target": ["KRAS", "EGFR", "CDK4", "BRAF", "MYC"],
            "Essentiality (CERES)": [-1.45, -0.98, -0.72, -0.65, -1.61],
            "Expression (TPM)": [35.4, 92.1, 28.3, 18.7, 125.0],
            "Co-essentiality": [0.91, 0.84, 0.69, 0.72, 0.95],
            "Safety": ["Pass", "Review", "Pass", "Pass", "Fail"],
            "Literature": ["Strong (67 papers)", "Strong (52 papers)",
                           "Moderate (14 papers)", "Strong (31 papers)",
                           "Strong (89 papers)"],
            "Overall Score": [0.93, 0.85, 0.78, 0.74, 0.62],
        }),
    },
}


# ============================================================================
# Resistance Biomarker Examples
# ============================================================================

BIOMARKER_EXAMPLES = {
    "CDK4/6 Inhibitor Resistance (Breast Cancer)": {
        "description": (
            "Build a 10-gene resistance biomarker panel for CDK4/6 inhibitor "
            "therapy in HR+ breast cancer."
        ),
        "config": {
            "compound_class": "CDK4/6 Inhibitor",
            "compound_name": "Palbociclib",
            "indication": "Breast Cancer",
            "panel_size": 10,
            "fdr_threshold": 0.05,
            "effect_size_min": 1.0,
            "sources": {
                "depmap_mutations": True, "prism": True,
                "l1000": True, "tcga_stratification": True, "clinical": True,
            },
        },
        "query": (
            "Build a 10-gene resistance biomarker panel for Palbociclib (CDK4/6 inhibitor) "
            "in HR+ breast cancer. Use DepMap mutation sensitivity analysis, PRISM viability "
            "data, and L1000 transcriptomic signatures. Validate with TCGA patient "
            "stratification. Output a ranked panel with mutation frequency, effect sizes, "
            "FDR values, DepMap correlation, and clinical evidence levels."
        ),
        "expected_result": pd.DataFrame({
            "Rank": list(range(1, 11)),
            "Gene": ["RB1", "CCNE1", "CDKN2A", "FGFR1", "PIK3CA",
                      "ESR1", "TP53", "PTEN", "MYC", "AKT1"],
            "Mutation Freq (%)": [18.2, 12.5, 9.8, 8.1, 34.2,
                                   15.6, 42.1, 7.3, 11.4, 3.2],
            "Effect Size (log2FC)": [2.1, 1.9, 1.7, 1.5, 1.3,
                                      -1.8, 1.2, 1.1, -1.4, 1.0],
            "FDR": [0.001, 0.002, 0.005, 0.008, 0.01,
                    0.012, 0.015, 0.022, 0.031, 0.045],
            "Clinical Evidence": ["Strong", "Strong", "Moderate", "Moderate",
                                   "Strong", "Strong", "Moderate", "Weak",
                                   "Emerging", "Emerging"],
        }),
    },
    "BET Inhibitor Resistance (AML)": {
        "description": (
            "Identify resistance biomarkers for BET bromodomain inhibitors "
            "in acute myeloid leukemia."
        ),
        "config": {
            "compound_class": "BET Inhibitor",
            "compound_name": "JQ1",
            "indication": "AML",
            "panel_size": 10,
            "fdr_threshold": 0.05,
            "effect_size_min": 1.0,
            "sources": {
                "depmap_mutations": True, "prism": True,
                "l1000": True, "tcga_stratification": True, "clinical": True,
            },
        },
        "query": (
            "Build a 10-gene resistance biomarker panel for JQ1 (BET inhibitor) in AML. "
            "Use DepMap mutation sensitivity, PRISM viability, and L1000 signatures. "
            "Validate with TCGA stratification. Output ranked table with mutation frequency, "
            "effect sizes, FDR, and clinical evidence."
        ),
        "expected_result": pd.DataFrame({
            "Rank": list(range(1, 11)),
            "Gene": ["TP53", "DNMT3A", "NPM1", "FLT3", "IDH1",
                      "IDH2", "NRAS", "KRAS", "RUNX1", "ASXL1"],
            "Mutation Freq (%)": [38.5, 26.3, 31.2, 28.7, 12.1,
                                   9.4, 14.6, 5.8, 8.2, 11.5],
            "Effect Size (log2FC)": [-2.3, 1.8, -1.6, 1.5, 1.4,
                                      1.3, 1.7, 1.2, -1.1, 1.0],
            "FDR": [0.0001, 0.001, 0.003, 0.005, 0.008,
                    0.01, 0.012, 0.02, 0.035, 0.048],
            "Clinical Evidence": ["Strong", "Moderate", "Strong", "Strong",
                                   "Moderate", "Moderate", "Weak",
                                   "Emerging", "Weak", "Emerging"],
        }),
    },
}


# ============================================================================
# Combination Strategy Examples
# ============================================================================

COMBINATION_EXAMPLES = {
    "BET Inhibitor Combinations (AML)": {
        "description": (
            "Find synergistic drug combinations for a BET inhibitor lead compound "
            "in AML with low immune infiltration context."
        ),
        "config": {
            "lead_compound": "BET inhibitor (JQ1)",
            "lead_target": "BRD4, BRD2, BRD3",
            "indication": "AML",
            "n_combinations": 5,
            "synergy_metric": "Bliss Independence",
            "prioritize_by": ["Therapeutic Window", "Safety Profile"],
            "context": "Low immune infiltration observed in RNA-seq.",
        },
        "query": (
            "My lead compound is a BET inhibitor (JQ1-derivative) being developed for AML. "
            "RNA-seq shows low immune infiltration. "
            "Suggest 5 synergistic drug combinations using DepMap co-dependency, "
            "Reactome pathways, and ClinicalTrials.gov. "
            "Prioritize by therapeutic window and safety profile. "
            "Include Bliss synergy predictions and clinical evidence for each combination."
        ),
        "expected_result": pd.DataFrame({
            "Rank": [1, 2, 3, 4, 5],
            "Combination Partner": ["Venetoclax (BCL2i)", "Azacitidine (DNMTi)",
                                     "Ruxolitinib (JAKi)", "Anti-PD1",
                                     "Trametinib (MEKi)"],
            "Bliss Score": [-0.25, -0.19, -0.15, -0.12, -0.08],
            "Synergy": ["Strong", "Moderate", "Moderate", "Moderate", "Mild"],
            "Therapeutic Window": ["Wide", "Wide", "Moderate", "Wide", "Narrow"],
            "Clinical Stage": ["Phase II", "Phase I/II", "Preclinical",
                                "Phase I", "Preclinical"],
            "Rationale": [
                "BCL2/BET co-dependency in AML; active Phase II trials",
                "Epigenetic synergy; hypomethylation enhances BET sensitivity",
                "JAK-STAT bypass pathway; overcomes BET resistance",
                "Immune checkpoint + transcriptional reprogramming",
                "MAPK pathway co-dependency in RAS-mutant AML",
            ],
        }),
    },
    "KRAS G12C Combinations (NSCLC)": {
        "description": (
            "Identify synergistic partners for a KRAS G12C inhibitor in "
            "non-small cell lung cancer."
        ),
        "config": {
            "lead_compound": "KRAS G12C inhibitor (Sotorasib-class)",
            "lead_target": "KRAS G12C",
            "indication": "NSCLC",
            "n_combinations": 5,
            "synergy_metric": "Bliss Independence",
            "prioritize_by": ["Mechanistic Rationale", "Clinical Stage"],
            "context": "Patients with acquired resistance to single-agent sotorasib.",
        },
        "query": (
            "My lead is a KRAS G12C inhibitor for NSCLC. Patients develop resistance "
            "to single-agent therapy. Suggest 5 synergistic combinations to overcome "
            "resistance using DepMap co-dependency, Reactome pathways, and ClinicalTrials.gov. "
            "Include clinical evidence and mechanistic rationale for each."
        ),
        "expected_result": pd.DataFrame({
            "Rank": [1, 2, 3, 4, 5],
            "Combination Partner": ["SHP2 inhibitor", "MEK inhibitor",
                                     "Anti-EGFR (Cetuximab)", "CDK4/6 inhibitor",
                                     "SOS1 inhibitor"],
            "Bliss Score": [-0.31, -0.22, -0.18, -0.14, -0.11],
            "Synergy": ["Strong", "Moderate", "Moderate", "Mild", "Mild"],
            "Therapeutic Window": ["Moderate", "Narrow", "Wide", "Moderate", "Moderate"],
            "Clinical Stage": ["Phase I/II", "Phase II", "Phase III",
                                "Phase I", "Phase I"],
            "Rationale": [
                "SHP2 blocks RAS reactivation; synergy in KRAS-mutant models",
                "Vertical pathway inhibition; prevents MAPK reactivation",
                "RTK bypass pathway; clinical efficacy in KRAS G12C NSCLC",
                "Cell cycle arrest synergy; overcomes adaptive resistance",
                "Blocks RAS-GTP loading; complementary mechanism",
            ],
        }),
    },
}


# ============================================================================
# Literature Synthesis Examples
# ============================================================================

LITERATURE_EXAMPLES = {
    "CRBN Molecular Glue Neosubstrates (Review)": {
        "description": (
            "Comprehensive review of all known CRBN molecular glue neosubstrates "
            "and their therapeutic applications."
        ),
        "config": {
            "topic": "CRBN molecular glue neosubstrates and their therapeutic applications",
            "scope": "Comprehensive Review",
            "date_range": (2020, 2026),
            "sources": {
                "pubmed": True, "openal": True, "chembl": True,
                "trials": True, "patents": False, "depmap": True,
            },
            "max_papers": 50,
            "output_format": "Structured Markdown",
        },
        "query": (
            "Perform a comprehensive review on CRBN molecular glue neosubstrates and "
            "their therapeutic applications. Cover publications from 2020 to 2026. "
            "Sources: PubMed, OpenAlex, ChEMBL, ClinicalTrials.gov, DepMap. "
            "Cross-reference with DepMap essentiality in multiple lineages. "
            "Output as structured markdown with citations. "
            "Include key findings, emerging trends, knowledge gaps, and suggested next steps."
        ),
    },
    "PROTAC Clinical Landscape (2024-2026)": {
        "description": (
            "Map the current clinical development landscape for PROTAC degraders "
            "across all indications."
        ),
        "config": {
            "topic": "PROTAC targeted protein degraders in clinical development",
            "scope": "Clinical Landscape",
            "date_range": (2024, 2026),
            "sources": {
                "pubmed": True, "openal": True, "chembl": True,
                "trials": True, "patents": True, "depmap": False,
            },
            "max_papers": 100,
            "output_format": "Table-Focused",
        },
        "query": (
            "Map the clinical development landscape for PROTAC degraders from 2024-2026. "
            "Sources: PubMed, OpenAlex, ChEMBL, ClinicalTrials.gov, Patent databases. "
            "Output as tables listing every PROTAC in clinical trials with: compound name, "
            "sponsor, target, E3 ligase, indication, phase, and key efficacy/safety data. "
            "Include competitive analysis and emerging trends."
        ),
    },
}


# ============================================================================
# Molecular Design Examples
# ============================================================================

MOLECULAR_EXAMPLES = {
    "Golden Gate Assembly — IKZF1 Expression Construct": {
        "description": (
            "Design a complete Golden Gate assembly for cloning IKZF1 degradation "
            "domain into an E. coli expression vector."
        ),
        "query": (
            "Design a complete expression construct for IKZF1 degradation domain: "
            "codon-optimize for E. coli BL21, add N-terminal His6-TEV tag, "
            "design Golden Gate assembly primers with BsaI sites for 3-fragment "
            "assembly into pET-28a(+), and plan a colony PCR verification strategy."
        ),
    },
    "CRISPR Knockout — BRD4 in Human Cells": {
        "description": (
            "Design 3 CRISPR guide RNAs for BRD4 knockout in human cells "
            "using SpCas9."
        ),
        "query": (
            "Design 3 CRISPR guide RNAs for knockout of BRD4 in human cells "
            "using SpCas9 (NGG PAM). Target early exons (exon 2-4) for frameshift. "
            "Provide guide sequences, PAM sites, on-target scores, off-target "
            "analysis, and recommended delivery method."
        ),
    },
    "RT-qPCR Primers — TP53 Isoforms": {
        "description": (
            "Design RT-qPCR primers to distinguish TP53 transcript variants "
            "in human samples."
        ),
        "query": (
            "Design RT-qPCR primer pairs for human TP53 that can distinguish "
            "full-length TP53 from the delta40p53 isoform. Target Tm 60-65C, "
            "GC 45-55%, product size 100-200 bp. Include a reference gene primer "
            "pair (GAPDH) as normalization control."
        ),
    },
}


# ============================================================================
# Agent Chat Examples
# ============================================================================

CHAT_EXAMPLES = [
    {
        "title": "Quick Target Check",
        "description": "Ask the agent to quickly evaluate a single target.",
        "query": (
            "Is GSPT1 a good molecular glue degradation target for AML? "
            "Check DepMap essentiality, safety flags, and recent literature."
        ),
    },
    {
        "title": "Drug Repurposing Screen",
        "description": "Use the agent to screen for repurposing opportunities.",
        "query": (
            "Screen PRISM for FDA-approved drugs that show selective activity "
            "in KRAS-mutant vs wild-type cell lines. Return the top 10 hits "
            "with effect sizes and known mechanisms."
        ),
    },
    {
        "title": "Pathway Enrichment",
        "description": "Run GSEA on a gene list.",
        "query": (
            "Run GSEA enrichment on these genes from my CRISPR screen: "
            "BRD4, MYC, BCL2, CDK9, EP300, CREBBP, KAT6A, BRD2, BRD3. "
            "Use MSigDB Hallmark gene sets. Show the top enriched pathways."
        ),
    },
    {
        "title": "Safety Profile",
        "description": "Comprehensive safety assessment for a target.",
        "query": (
            "Provide a comprehensive safety assessment for degrading IKZF1 "
            "with a CRBN molecular glue. Check: essential gene status in normal "
            "tissues, known anti-target effects, cardiac and hepatotoxicity "
            "liability, and reproductive toxicity (SALL4 risk)."
        ),
    },
]


# ============================================================================
# Quick Start Tutorial Steps
# ============================================================================

TUTORIAL_STEPS = [
    {
        "step": 1,
        "title": "Welcome to the Workbench",
        "icon": "👋",
        "content": (
            "The CellType Research Workbench is an interactive bioinformatics "
            "platform powered by Claude AI and 190+ integrated tools.\n\n"
            "This tutorial will walk you through the key features in ~3 minutes."
        ),
        "action": None,
    },
    {
        "step": 2,
        "title": "Check Your Setup",
        "icon": "🔧",
        "content": (
            "First, make sure the workbench is configured correctly:\n\n"
            "- **API Key**: Set your `ANTHROPIC_API_KEY` in Settings\n"
            "- **celltype-cli** (optional): Install for full tool access\n"
            "- **Datasets** (optional): Pull DepMap/PRISM for local analysis\n\n"
            "Without an API key, the workbench runs in **demo mode** with "
            "simulated responses — great for exploring the UI."
        ),
        "action": "settings",
    },
    {
        "step": 3,
        "title": "Try the Research Agent",
        "icon": "🤖",
        "content": (
            "The Research Agent is the heart of the workbench. Ask any "
            "bioinformatics question in natural language:\n\n"
            '> *"Is GSPT1 a good degradation target for AML?"*\n\n'
            "The agent will search literature, query DepMap, check safety "
            "flags, and return a structured answer with citations."
        ),
        "action": "agent",
        "example_query": CHAT_EXAMPLES[0]["query"],
    },
    {
        "step": 4,
        "title": "Run a Guided Workflow",
        "icon": "🎯",
        "content": (
            "Workflows provide structured, step-by-step research pipelines:\n\n"
            "1. **Configure** — set targets, indication, evidence sources\n"
            "2. **Explore Data** — interactive visualizations (heatmaps, volcano plots)\n"
            "3. **Run AI Agent** — auto-generated query from your config\n"
            "4. **Review Results** — exportable reports\n\n"
            "Try loading the **BRD4 Molecular Glue** example in Target Prioritization."
        ),
        "action": "target",
    },
    {
        "step": 5,
        "title": "Explore Sample Data",
        "icon": "📊",
        "content": (
            "The Data Explorer provides interactive visualizations of:\n\n"
            "- DepMap dependency scores (heatmaps, box plots)\n"
            "- TCGA expression across tissues\n"
            "- PRISM drug viability matrices\n"
            "- Safety profiles and biomarker panels\n\n"
            "All data is simulated for demo purposes. With local datasets "
            "installed, the agent uses real DepMap/PRISM data."
        ),
        "action": "data_explorer",
    },
    {
        "step": 6,
        "title": "Save & Export",
        "icon": "📝",
        "content": (
            "Every agent response is automatically saved as a report. You can:\n\n"
            "- **Save sessions** to resume later\n"
            "- **Export reports** as Markdown or HTML\n"
            "- **Download data** as CSV from any explorer\n"
            "- Track costs and token usage in the sidebar"
        ),
        "action": "reports",
    },
    {
        "step": 7,
        "title": "You're Ready!",
        "icon": "🚀",
        "content": (
            "You now know the basics. Here are some next steps:\n\n"
            "- **Load an example** in any workflow to see it in action\n"
            "- **Ask the Research Agent** a question about your own targets\n"
            "- **Run `ct doctor`** from Dashboard to check full system health\n"
            "- Visit **Help & Tutorial** for the CLI reference and pro tips"
        ),
        "action": None,
    },
]


def get_all_examples() -> dict:
    """Return all examples organized by workflow."""
    return {
        "target": TARGET_EXAMPLES,
        "biomarker": BIOMARKER_EXAMPLES,
        "combination": COMBINATION_EXAMPLES,
        "literature": LITERATURE_EXAMPLES,
        "molecular": MOLECULAR_EXAMPLES,
        "chat": CHAT_EXAMPLES,
    }

"""Configuration management for the CellType Research Workbench."""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

CONFIG_DIR = Path.home() / ".celltype-workbench"
CONFIG_FILE = CONFIG_DIR / "config.json"
SESSIONS_DIR = CONFIG_DIR / "sessions"
REPORTS_DIR = CONFIG_DIR / "reports"

SUPPORTED_MODELS = [
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]

DATASETS = {
    "depmap": {
        "name": "DepMap (CRISPR, Mutations, Expression, Copy Number)",
        "description": "Cancer Dependency Map — genome-scale CRISPR screens, mutations, gene expression, copy number across 1000+ cell lines.",
        "size": "~15 GB",
        "command": "ct data pull depmap",
    },
    "prism": {
        "name": "PRISM Drug Sensitivity",
        "description": "Broad PRISM multiplexed drug viability screens across hundreds of cancer cell lines.",
        "size": "~5 GB",
        "command": "ct data pull prism",
    },
    "msigdb": {
        "name": "MSigDB Gene Sets & Pathways",
        "description": "Molecular Signatures Database — curated gene sets for GSEA and pathway analysis.",
        "size": "~500 MB",
        "command": "ct data pull msigdb",
    },
    "alphafold": {
        "name": "AlphaFold Structures (On-Demand)",
        "description": "AlphaFold predicted protein structures, fetched on demand per query.",
        "size": "Variable",
        "command": "ct data pull alphafold",
    },
}

TOOL_CATEGORIES = {
    "Target Identification": [
        "DepMap CRISPR Essentiality", "Co-Essentiality Networks", "TCGA Expression",
        "Safety Flag Checker (SALL4, Anti-targets)", "Gene Ontology Enrichment",
    ],
    "Chemistry & Degradation": [
        "PROTAC Linker Design", "Molecular Glue Neosubstrate Search",
        "ChEMBL Activity Query", "RDKit Molecular Descriptors", "SMILES Validation",
    ],
    "Genomics & Transcriptomics": [
        "Differential Expression (pydeseq2)", "GSEA (gseapy)", "Variant Annotation",
        "Copy Number Analysis", "Fusion Gene Detection",
    ],
    "Drug Sensitivity": [
        "PRISM Viability Screens", "Dose-Response Curve Fitting",
        "Biomarker-Sensitivity Correlation", "Combination Synergy (Bliss/Loewe)",
        "Resistance Mechanism Mining",
    ],
    "Literature & Knowledge": [
        "PubMed Search", "OpenAlex Search", "ClinicalTrials.gov Query",
        "Patent Landscape Search", "Pathway Database Query (Reactome/KEGG)",
    ],
    "Molecular Biology": [
        "Primer Design", "Codon Optimization", "Golden Gate Assembly",
        "CRISPR Guide RNA Design", "Restriction Site Analysis",
    ],
    "Visualization": [
        "Heatmap Generator", "Volcano Plot", "Kaplan-Meier Survival",
        "Network Graph", "Structure Viewer (3D)",
    ],
}


@dataclass
class WorkbenchConfig:
    anthropic_api_key: str = ""
    default_model: str = "claude-opus-4-6"
    data_dir: str = str(Path.home() / ".celltype" / "data")
    reports_dir: str = str(REPORTS_DIR)
    depmap_path: str = ""
    prism_path: str = ""
    msigdb_path: str = ""
    max_tokens: int = 8192
    temperature: float = 0.1
    ncbi_api_key: str = ""
    theme: str = "dark"
    parallel_agents: int = 3

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls) -> "WorkbenchConfig":
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        cfg = cls()
        cfg.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        cfg.ncbi_api_key = os.getenv("NCBI_API_KEY", "")
        return cfg


def ensure_dirs():
    for d in [CONFIG_DIR, SESSIONS_DIR, REPORTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)

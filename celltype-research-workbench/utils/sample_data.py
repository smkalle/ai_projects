"""Generate sample/demo data for the workbench UI."""

import numpy as np
import pandas as pd


def generate_dependency_scores(genes: list[str] | None = None, n_cell_lines: int = 50) -> pd.DataFrame:
    """Generate simulated DepMap-style dependency scores."""
    if genes is None:
        genes = [
            "IKZF1", "GSPT1", "CK1α", "CRBN", "MYC", "TP53", "KRAS",
            "BRAF", "EGFR", "CDK4", "MDM2", "BCL2", "BRD4", "EZH2", "DOT1L",
        ]
    np.random.seed(42)
    cell_lines = [f"ACH-{str(i).zfill(6)}" for i in range(n_cell_lines)]
    lineages = np.random.choice(
        ["Hematopoietic", "Lung", "Breast", "Colon", "Skin", "Brain", "Liver", "Kidney"],
        size=n_cell_lines,
    )
    data = {}
    for gene in genes:
        base = np.random.uniform(-1.5, 0.2)
        data[gene] = np.random.normal(base, 0.3, n_cell_lines)
    df = pd.DataFrame(data, index=cell_lines)
    df.insert(0, "Lineage", lineages)
    return df


def generate_expression_data(genes: list[str] | None = None) -> pd.DataFrame:
    """Generate simulated TCGA-style expression data (TPM)."""
    if genes is None:
        genes = [
            "IKZF1", "GSPT1", "CK1α", "CRBN", "MYC", "TP53", "KRAS",
            "BRAF", "EGFR", "CDK4",
        ]
    np.random.seed(123)
    tissues = [
        "Blood", "Lung", "Breast", "Colon", "Skin", "Brain", "Liver",
        "Kidney", "Pancreas", "Ovary", "Prostate", "Stomach",
    ]
    data = {}
    for gene in genes:
        base = np.random.uniform(1, 100)
        data[gene] = np.abs(np.random.lognormal(np.log(base), 0.8, len(tissues)))
    df = pd.DataFrame(data, index=tissues)
    df.index.name = "Tissue"
    return df


def generate_prism_viability(compounds: list[str] | None = None) -> pd.DataFrame:
    """Generate simulated PRISM drug viability data."""
    if compounds is None:
        compounds = [
            "Lenalidomide", "Pomalidomide", "CC-220", "CC-885", "Thalidomide",
            "JQ1", "I-BET762", "OTX015", "Venetoclax", "Idasanutlin",
        ]
    np.random.seed(77)
    cell_lines = [f"ACH-{str(i).zfill(6)}" for i in range(30)]
    data = {}
    for cmpd in compounds:
        data[cmpd] = np.random.beta(2, 5, len(cell_lines))
    df = pd.DataFrame(data, index=cell_lines)
    df.index.name = "Cell Line"
    return df


def generate_safety_profile(genes: list[str] | None = None) -> pd.DataFrame:
    """Generate a safety flag table for target candidates."""
    if genes is None:
        genes = ["IKZF1", "GSPT1", "CK1α", "SALL4", "CRBN", "MYC"]
    np.random.seed(99)
    flags = []
    for gene in genes:
        is_safe = gene not in ["SALL4", "MYC"]
        flags.append({
            "Gene": gene,
            "Essential in Normal Tissue": "No" if is_safe else "Yes",
            "Known Anti-Target": "No" if gene != "SALL4" else "Yes (Teratogenicity)",
            "Cardiac Liability": np.random.choice(["Low", "Medium", "Low"], p=[0.6, 0.3, 0.1]),
            "Hepatotoxicity Risk": np.random.choice(["Low", "Medium", "High"], p=[0.7, 0.2, 0.1]),
            "Overall Safety": "Pass" if is_safe else "Fail",
        })
    return pd.DataFrame(flags)


def generate_biomarker_panel() -> pd.DataFrame:
    """Generate a simulated resistance biomarker panel."""
    np.random.seed(55)
    genes = ["TP53", "RB1", "CDKN2A", "PTEN", "KRAS", "NRAS", "FLT3", "NPM1", "IDH1", "DNMT3A"]
    rows = []
    for gene in genes:
        rows.append({
            "Gene": gene,
            "Mutation Frequency (%)": round(np.random.uniform(2, 45), 1),
            "Effect Size (log2FC)": round(np.random.uniform(-2.5, 2.5), 2),
            "P-value": round(np.random.uniform(0.0001, 0.05), 4),
            "FDR": round(np.random.uniform(0.001, 0.1), 3),
            "DepMap Correlation": round(np.random.uniform(-0.6, 0.6), 3),
            "Clinical Evidence": np.random.choice(["Strong", "Moderate", "Weak", "Emerging"]),
        })
    return pd.DataFrame(rows)


def generate_combination_data() -> pd.DataFrame:
    """Generate simulated drug combination synergy data."""
    np.random.seed(33)
    combos = [
        ("BET inhibitor", "BCL2 inhibitor"), ("BET inhibitor", "CDK4/6 inhibitor"),
        ("BET inhibitor", "PD-1 antibody"), ("BET inhibitor", "HDAC inhibitor"),
        ("BET inhibitor", "MEK inhibitor"), ("BET inhibitor", "PI3K inhibitor"),
    ]
    rows = []
    for drug_a, drug_b in combos:
        rows.append({
            "Drug A": drug_a,
            "Drug B": drug_b,
            "Bliss Score": round(np.random.uniform(-0.3, 0.1), 3),
            "Loewe Score": round(np.random.uniform(0.5, 2.5), 2),
            "Synergy Classification": np.random.choice(["Synergistic", "Additive", "Antagonistic"], p=[0.5, 0.35, 0.15]),
            "Therapeutic Window": np.random.choice(["Wide", "Moderate", "Narrow"], p=[0.3, 0.5, 0.2]),
            "Clinical Stage": np.random.choice(["Preclinical", "Phase I", "Phase II", "Phase III"]),
        })
    return pd.DataFrame(rows)

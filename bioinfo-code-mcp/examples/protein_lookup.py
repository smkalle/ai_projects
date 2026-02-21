"""Example: Protein structure lookup workflow.

Demonstrates how an agent would use the Code MCP to:
1. Search for a protein in UniProt
2. Find associated PDB structures
3. Get structure details
4. Cross-reference with Ensembl gene data

This example makes real API calls — requires network access.

Usage:
    NCBI_EMAIL=you@example.com python examples/protein_lookup.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.config import load_config
from bioinfo_code_mcp.registry import Registry
from bioinfo_code_mcp.sandbox import Sandbox


async def main():
    print("Protein Structure Lookup Workflow — Code MCP Demo\n")

    config = load_config()
    registry = Registry()
    sandbox = Sandbox(config)

    # Step 1: Search for relevant operations
    print("--- Step 1: Discover protein-related operations ---")
    ops = registry.search(query="protein structure", tags=["pdb", "uniprot"])
    print(f"Found {len(ops)} operations for protein structure lookup:")
    for op in ops[:5]:
        print(f"  {op['name']}: {op['description'][:70]}...")
    print()

    # Step 2: Search UniProt for p53
    print("--- Step 2: Search UniProt for p53 protein ---")
    result = await sandbox.execute("""
# Search for human p53 protein in UniProt
try:
    proteins = await uniprot.search_protein("TP53", organism="Homo sapiens", max_results=3)
    if proteins:
        for p in proteins:
            acc = p.get("primaryAccession", "?")
            gene_name = "?"
            genes = p.get("genes", [])
            if genes:
                gene_name = genes[0].get("geneName", {}).get("value", "?")
            desc = p.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "N/A")
            seq_len = p.get("sequence", {}).get("length", 0)
            print(f"Accession: {acc}")
            print(f"Gene: {gene_name}")
            print(f"Description: {desc}")
            print(f"Length: {seq_len} aa")
            state["p53_accession"] = acc
            state["p53_info"] = {"accession": acc, "gene": gene_name, "description": desc, "length": seq_len}
            print()
        return state["p53_info"]
    else:
        print("No results found")
        return {"error": "no results"}
except Exception as e:
    print(f"API call failed: {e}")
    # Use fallback known data for demo
    state["p53_accession"] = "P04637"
    state["p53_info"] = {"accession": "P04637", "gene": "TP53", "description": "Cellular tumor antigen p53", "length": 393}
    return state["p53_info"]
""")
    print(result.to_text())

    # Step 3: Find PDB structures
    print("\n--- Step 3: Search PDB for p53 structures ---")
    result = await sandbox.execute("""
accession = state.get("p53_accession", "P04637")
try:
    structures = await pdb.search_by_uniprot(accession)
    print(f"Found {len(structures)} PDB structures for {accession}")
    state["pdb_structures"] = structures[:5]
    for s in structures[:5]:
        pdb_id = s.get("identifier", "?")
        score = s.get("score", 0)
        print(f"  PDB: {pdb_id} (score: {score:.2f})")

    # Get details for the top structure
    if structures:
        top_pdb = structures[0]["identifier"]
        summary = await pdb.get_structure_summary(top_pdb)
        state["top_structure"] = summary
        print(f"\\nTop structure details:")
        print(f"  PDB ID: {summary['pdb_id']}")
        print(f"  Title: {summary['title']}")
        print(f"  Resolution: {summary.get('resolution')} Å")
        print(f"  Method: {summary.get('experimental_method')}")
        return summary

    return {"structures_found": len(structures)}
except Exception as e:
    print(f"PDB search failed: {e}")
    return {"error": str(e)}
""")
    print(result.to_text())

    # Step 4: Get Ensembl gene info
    print("\n--- Step 4: Cross-reference with Ensembl ---")
    result = await sandbox.execute("""
try:
    gene_summary = await ensembl.get_gene_summary("TP53", species="homo_sapiens")
    state["ensembl_gene"] = gene_summary
    print("Ensembl gene data:")
    for key, value in gene_summary.items():
        print(f"  {key}: {value}")
    return gene_summary
except Exception as e:
    print(f"Ensembl lookup failed: {e}")
    return {"error": str(e)}
""")
    print(result.to_text())

    # Step 5: Compile cross-database summary
    print("\n--- Step 5: Cross-database summary ---")
    result = await sandbox.execute("""
summary = {
    "gene": "TP53",
    "databases_queried": [],
}

if "p53_info" in state:
    summary["uniprot"] = state["p53_info"]
    summary["databases_queried"].append("UniProt")

if "top_structure" in state:
    s = state["top_structure"]
    summary["pdb"] = {
        "top_structure": s.get("pdb_id"),
        "title": s.get("title"),
        "resolution": s.get("resolution"),
    }
    summary["databases_queried"].append("PDB")

if "pdb_structures" in state:
    summary["pdb_structure_count"] = len(state["pdb_structures"])

if "ensembl_gene" in state:
    eg = state["ensembl_gene"]
    summary["ensembl"] = {
        "id": eg.get("ensembl_id"),
        "chromosome": eg.get("chromosome"),
        "biotype": eg.get("biotype"),
    }
    summary["databases_queried"].append("Ensembl")

print("=== Cross-Database Summary for TP53 ===")
for db in summary["databases_queried"]:
    print(f"  ✓ {db}")
print(f"  Total databases: {len(summary['databases_queried'])}")

return summary
""")
    print(result.to_text())
    print("\nWorkflow complete.")


if __name__ == "__main__":
    asyncio.run(main())

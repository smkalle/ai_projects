"""Demo: Using the bioinformatics Code MCP with an AI agent.

This example shows how an AI agent would interact with the Code MCP server
to perform a multi-step bioinformatics research workflow. It simulates the
agent's perspective — generating code, executing it, and chaining results.

This is a standalone script that directly uses the sandbox (no MCP transport
needed), demonstrating the Code Mode pattern in action.

Usage:
    NCBI_EMAIL=you@example.com python examples/agent_demo.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.config import load_config
from bioinfo_code_mcp.registry import Registry
from bioinfo_code_mcp.sandbox import Sandbox


async def main():
    print("=" * 70)
    print("Bioinformatics Code MCP — Agent Demo")
    print("=" * 70)

    config = load_config()
    registry = Registry()
    sandbox = Sandbox(config)

    # ------------------------------------------------------------------
    # Step 1: Agent searches for available operations (like Cloudflare's search())
    # ------------------------------------------------------------------
    print("\n--- Step 1: Discover operations (search tool) ---")
    modules = registry.list_modules()
    print(f"Available modules: {json.dumps(modules, indent=2)}")

    # Agent searches for gene-related operations
    gene_ops = registry.search(query="gene lookup", limit=5)
    print(f"\nOperations matching 'gene lookup':")
    for op in gene_ops:
        print(f"  - {op['name']}: {op['description'][:80]}...")
        print(f"    Example: {op.get('example', 'N/A')}")

    # ------------------------------------------------------------------
    # Step 2: Agent generates and executes code to look up a gene
    # ------------------------------------------------------------------
    print("\n--- Step 2: Look up TP53 gene info (execute tool) ---")

    # This is what an agent would generate:
    code_step2 = """
# Look up the TP53 tumor suppressor gene
genes = await ncbi.fetch_gene_info("TP53", organism="human")
state["tp53_genes"] = genes
print(f"Found {len(genes)} gene record(s) for TP53")
for g in genes[:2]:
    name = g.get("name", g.get("Name", "unknown"))
    desc = g.get("description", g.get("Description", "N/A"))
    print(f"  Gene: {name}")
    print(f"  Description: {desc}")
return {"gene_count": len(genes), "first_gene_id": genes[0].get("uid") if genes else None}
"""
    result = await sandbox.execute(code_step2)
    print(f"Success: {result.success}")
    print(f"Output:\n{result.to_text()}")

    # ------------------------------------------------------------------
    # Step 3: Agent chains to fetch protein info from UniProt
    # ------------------------------------------------------------------
    print("\n--- Step 3: Fetch TP53 protein from UniProt ---")

    code_step3 = """
# Search UniProt for human TP53 protein (Swiss-Prot reviewed)
proteins = await uniprot.search_protein("TP53", organism="Homo sapiens")
if proteins:
    p = proteins[0]
    accession = p.get("primaryAccession", "unknown")
    name = p.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "N/A")
    seq_len = p.get("sequence", {}).get("length", 0)
    state["tp53_accession"] = accession
    print(f"Protein: {name}")
    print(f"Accession: {accession}")
    print(f"Sequence length: {seq_len} aa")
    return {"accession": accession, "name": name, "length": seq_len}
else:
    return {"error": "No results found"}
"""
    result = await sandbox.execute(code_step3)
    print(f"Success: {result.success}")
    print(f"Output:\n{result.to_text()}")

    # ------------------------------------------------------------------
    # Step 4: Agent uses sequence utilities (no API call needed)
    # ------------------------------------------------------------------
    print("\n--- Step 4: Analyze a DNA sequence with utilities ---")

    code_step4 = """
# Analyze a short DNA sequence (TP53 exon 7 region, simplified)
dna = "ATGGAGGAGCCGCAGTCAGATCCTAGCGTGAGTTTGCACTGATGGCCATGGCGCGGACGCGGGTGCCGGGCGGGGGTGTGCAGCCG"

gc = seq_utils.gc_content(dna)
rc = seq_utils.reverse_complement(dna)
protein = seq_utils.translate(dna)
composition = seq_utils.nucleotide_composition(dna)
sites = seq_utils.restriction_sites(dna)
mw = seq_utils.molecular_weight(protein, seq_type="protein")

state["dna_analysis"] = {
    "gc_content": round(gc, 4),
    "protein": protein,
    "mw_daltons": mw,
}

print(f"Sequence length: {len(dna)} bp")
print(f"GC content: {gc:.1%}")
print(f"Composition: {composition}")
print(f"Translated protein: {protein}")
print(f"Molecular weight: {mw:.1f} Da")
print(f"Restriction sites found: {list(sites.keys())}")
print(f"Reverse complement (first 30): {rc[:30]}...")

return state["dna_analysis"]
"""
    result = await sandbox.execute(code_step4)
    print(f"Success: {result.success}")
    print(f"Output:\n{result.to_text()}")

    # ------------------------------------------------------------------
    # Step 5: Agent uses format utilities
    # ------------------------------------------------------------------
    print("\n--- Step 5: Parse FASTA format ---")

    code_step5 = """
# Parse a multi-sequence FASTA
fasta_text = \"\"\">sp|P04637|P53_HUMAN Cellular tumor antigen p53
MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP
DEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYPQGLNGTVNLPGRNSFEV
>sp|P02340|P53_MOUSE Cellular tumor antigen p53
MTAMEESQSDISLELPLSQETFSGLWKLLPPEDILPSPHCMDDLLLPQDVEEFFEGPSEAL
RVSGAPAAQDPVTETPGPVAPAPATPWPLSSFVPSQKTYQGSYGFRLGFLHSGTAKSVTC
\"\"\"

records = fmt.parse_fasta(fasta_text)
state["fasta_records"] = [r.to_dict() for r in records]

for r in records:
    print(f"ID: {r.id}")
    print(f"Description: {r.description}")
    print(f"Length: {r.length} aa")
    gc_approx = len(r.sequence)  # Just length for protein
    print(f"First 30 residues: {r.sequence[:30]}...")
    print()

return [r.to_dict() for r in records]
"""
    result = await sandbox.execute(code_step5)
    print(f"Success: {result.success}")
    print(f"Output:\n{result.to_text()}")

    # ------------------------------------------------------------------
    # Step 6: Demonstrate state persistence
    # ------------------------------------------------------------------
    print("\n--- Step 6: Show state persistence ---")

    code_step6 = """
# Access data saved in previous steps
print("Persistent state keys:", list(state.keys()))

if "dna_analysis" in state:
    print(f"DNA GC content from step 4: {state['dna_analysis']['gc_content']}")
if "tp53_accession" in state:
    print(f"UniProt accession from step 3: {state['tp53_accession']}")
if "fasta_records" in state:
    print(f"FASTA records from step 5: {len(state['fasta_records'])} sequences")

return {"state_keys": list(state.keys()), "state_size": len(state)}
"""
    result = await sandbox.execute(code_step6)
    print(f"Success: {result.success}")
    print(f"Output:\n{result.to_text()}")

    print("\n" + "=" * 70)
    print("Demo complete. The Code MCP pattern enables:")
    print("  - Dynamic discovery via search (no bloated tool definitions)")
    print("  - Flexible code execution via execute (loops, conditionals, chaining)")
    print("  - State persistence across calls (multi-step workflows)")
    print("  - ~1,000 tokens for tool definitions (vs millions for per-endpoint MCP)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

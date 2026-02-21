"""Example: Multi-step sequence analysis workflow.

Demonstrates how an agent would use the Code MCP to perform a complete
sequence analysis pipeline:
1. Fetch a gene sequence from NCBI
2. Analyze sequence properties
3. Find ORFs and restriction sites
4. Cross-reference with UniProt protein data
5. Summarize findings

Usage:
    NCBI_EMAIL=you@example.com python examples/sequence_analysis.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.config import load_config
from bioinfo_code_mcp.sandbox import Sandbox


async def main():
    print("Sequence Analysis Workflow — Code MCP Demo\n")

    config = load_config()
    sandbox = Sandbox(config)

    # Step 1: Analyze a known sequence locally
    print("--- Step 1: Comprehensive sequence analysis ---")
    result = await sandbox.execute("""
# Analyze BRCA1 exon 11 fragment (simplified, first 300bp)
dna = (
    "ATGGATTTATCTGCTCTTCGCGTTGAAGAAGTACAAAATGTCATTAATGCTATGCAGA"
    "AAATCTTAGAGTGTCCCATCTGTCTGGAGTTGATCAAGGAACCTGTCTCCACAAAGTGT"
    "GACCACATATTTTGCAAATTTTGCATGCTGAAACTTCTCAACCAGAAGAAAGGGCCTTC"
    "ACAGTGTCCTTTATGTAAGAATGATATAACCAAAAGGAGCCTACAAGAAAGTACGAGAT"
    "TTAGTCAACTTGTTGAAGAGCTATTGAAAATCATTTGTGCTTTTCAGCTTGACACAGGT"
)

print(f"Sequence length: {len(dna)} bp")
print(f"GC content: {seq_utils.gc_content(dna):.1%}")
print(f"Composition: {seq_utils.nucleotide_composition(dna)}")

# Translate in all 3 frames
for frame in range(3):
    protein = seq_utils.translate(dna, reading_frame=frame)
    stop_count = protein.count("*")
    print(f"Frame +{frame}: {protein[:40]}... (stops: {stop_count})")

# Find ORFs
orfs = seq_utils.find_orfs(dna, min_length=60)
print(f"\\nORFs found (min 60bp): {len(orfs)}")
for orf in orfs[:3]:
    print(f"  Frame {orf['frame']}: pos {orf['start']}-{orf['end']} ({orf['length']}bp)")
    print(f"    Protein: {orf['protein'][:30]}...")

# Restriction sites
sites = seq_utils.restriction_sites(dna)
print(f"\\nRestriction sites:")
for enzyme, positions in sorted(sites.items()):
    print(f"  {enzyme}: positions {positions}")

# Reverse complement
rc = seq_utils.reverse_complement(dna)
print(f"\\nReverse complement GC: {seq_utils.gc_content(rc):.1%} (should match)")

# Molecular weight of longest ORF protein
if orfs:
    mw = seq_utils.molecular_weight(orfs[0]["protein"], seq_type="protein")
    print(f"Longest ORF protein MW: {mw:.1f} Da")

state["sequence_analysis"] = {
    "length": len(dna),
    "gc_content": round(seq_utils.gc_content(dna), 4),
    "orf_count": len(orfs),
    "restriction_sites": {k: len(v) for k, v in sites.items()},
}

return state["sequence_analysis"]
""")
    print(result.to_text())

    # Step 2: Parse and compare FASTA sequences
    print("\n--- Step 2: Parse and compare FASTA sequences ---")
    result = await sandbox.execute("""
fasta_text = \"\"\">human_insulin INSA_HUMAN Insulin precursor
MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT
>mouse_insulin INSA_MOUSE Insulin precursor
MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKS
>rat_insulin INS1_RAT Insulin-1 precursor
MALLVHFLPLLALLALWEPKPTQAFVKQHLCGPHLVEALYLVCGERGFFYTPKS
\"\"\"

records = fmt.parse_fasta(fasta_text)
print(f"Parsed {len(records)} sequences:")

for rec in records:
    comp = seq_utils.amino_acid_composition(rec.sequence)
    mw = seq_utils.molecular_weight(rec.sequence, seq_type="protein")
    print(f"  {rec.id}: {rec.length} aa, MW={mw:.0f} Da")
    # Count charged residues
    charged = sum(comp.get(aa, 0) for aa in "DEKRH")
    print(f"    Charged residues: {charged} ({charged/rec.length:.1%})")

# Simple pairwise identity (positional matches / length)
if len(records) >= 2:
    print("\\nPairwise identity:")
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            s1, s2 = records[i].sequence, records[j].sequence
            min_len = min(len(s1), len(s2))
            matches = sum(1 for a, b in zip(s1[:min_len], s2[:min_len]) if a == b)
            identity = matches / min_len
            print(f"  {records[i].id} vs {records[j].id}: {identity:.1%} ({matches}/{min_len})")

state["fasta_comparison"] = {
    "sequences": [r.to_dict() for r in records],
    "count": len(records),
}

return {"parsed": len(records), "ids": [r.id for r in records]}
""")
    print(result.to_text())

    # Step 3: Show state persistence
    print("\n--- Step 3: Cross-reference with persistent state ---")
    result = await sandbox.execute("""
# Use data from previous steps
analysis = state.get("sequence_analysis", {})
comparison = state.get("fasta_comparison", {})

print("=== Workflow Summary ===")
print(f"DNA analysis: {analysis.get('length', 0)} bp, GC={analysis.get('gc_content', 0):.1%}")
print(f"ORFs found: {analysis.get('orf_count', 0)}")
print(f"Restriction sites: {analysis.get('restriction_sites', {})}")
print(f"FASTA sequences compared: {comparison.get('count', 0)}")

return {
    "workflow_complete": True,
    "steps_with_state": list(state.keys()),
}
""")
    print(result.to_text())
    print("\nWorkflow complete.")


if __name__ == "__main__":
    asyncio.run(main())

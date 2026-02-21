"""Interactive Bioinformatics Playground — Web Application.

A browser-based interactive environment for bioinformatics research
and learning. Built on top of the Code Mode MCP sandbox, it provides:

- Live Python code editor with syntax highlighting
- Pre-loaded bioinformatics API clients and utilities
- 12 starter project templates covering common workflows
- Stateful execution with persistent session data
- Rich result visualization for sequences, tables, and analysis

Usage:
    cd bioinfo-code-mcp
    pip install -e ".[dev]"
    python playground/app.py

    Then open http://localhost:8765 in your browser.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from bioinfo_code_mcp.config import ServerConfig
from bioinfo_code_mcp.registry import Registry
from bioinfo_code_mcp.sandbox import Sandbox

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Bioinformatics Playground", version="0.1.0")

PLAYGROUND_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=PLAYGROUND_DIR / "static"), name="static")
templates = Jinja2Templates(directory=PLAYGROUND_DIR / "templates")

# Per-session sandboxes (in production use Redis/DB-backed sessions)
_sessions: dict[str, Sandbox] = {}
_config = ServerConfig()
_registry = Registry()


def _get_sandbox(session_id: str) -> Sandbox:
    if session_id not in _sessions:
        _sessions[session_id] = Sandbox(_config)
    return _sessions[session_id]


# ---------------------------------------------------------------------------
# Starter project templates
# ---------------------------------------------------------------------------

STARTER_PROJECTS: list[dict[str, Any]] = [
    {
        "id": "gene-lookup",
        "title": "Gene Lookup",
        "category": "Getting Started",
        "difficulty": "Beginner",
        "description": "Search for a gene by symbol and retrieve information from NCBI and Ensembl.",
        "tags": ["ncbi", "ensembl", "gene"],
        "code": '''# Gene Lookup — Search for a gene across databases
# Try changing the gene symbol to explore different genes

gene_symbol = "TP53"
organism = "human"

# Step 1: Search NCBI Gene database
print(f"Searching NCBI for {gene_symbol}...")
genes = await ncbi.fetch_gene_info(gene_symbol, organism=organism)

if genes:
    g = genes[0]
    print(f"  Name: {g.get('name', g.get('Name', 'N/A'))}")
    print(f"  Description: {g.get('description', g.get('Description', 'N/A'))}")
    print(f"  Gene ID: {g.get('uid', 'N/A')}")
    state["gene_id"] = g.get("uid")

# Step 2: Get Ensembl details
print(f"\\nSearching Ensembl for {gene_symbol}...")
summary = await ensembl.get_gene_summary(gene_symbol, species="homo_sapiens")
print(f"  Ensembl ID: {summary.get('ensembl_id')}")
print(f"  Chromosome: {summary.get('chromosome')}")
print(f"  Position: {summary.get('start')}-{summary.get('end')}")
print(f"  Biotype: {summary.get('biotype')}")
print(f"  Description: {summary.get('description')}")

state["gene_summary"] = summary
return summary''',
    },
    {
        "id": "sequence-analysis",
        "title": "DNA Sequence Analysis",
        "category": "Getting Started",
        "difficulty": "Beginner",
        "description": "Analyze a DNA sequence: GC content, translation, ORFs, and restriction sites.",
        "tags": ["sequence", "dna", "analysis"],
        "code": '''# DNA Sequence Analysis — Comprehensive sequence characterization
# Paste your own DNA sequence below or use this example

dna = (
    "ATGGAGGAGCCGCAGTCAGATCCTAGCGTGAGTTTGCACTGATGGCCATG"
    "GCGCGGACGCGGGTGCCGGGCGGGGGTGTGCAGCCGCCGCCCCCTCCTGG"
    "CCCCTGTCATCTTCTGTCCCTTCCCAGAAAACCTACCAGGGCAGCTACGGT"
    "TTCCGTCTGGGCTTCTTGCATTCTGGGACAGCCAAGTCTGTGACTTGCACG"
    "TACTCCCCTGCCCTCAACAAGATGTTTTGCCAACTGGCCAAGACCTGCCCT"
    "GTGCAGCTGTGGGTTGATTCCACACCCCCGCCCGGCACCCGCGTCCGCGCC"
)

print(f"=== DNA Sequence Analysis ===")
print(f"Length: {len(dna)} bp")

# Nucleotide composition
comp = seq_utils.nucleotide_composition(dna)
print(f"\\nComposition: {comp}")

# GC content
gc = seq_utils.gc_content(dna)
print(f"GC Content: {gc:.1%}")

# Molecular weight
mw = seq_utils.molecular_weight(dna, seq_type="dna")
print(f"Molecular Weight: {mw:,.0f} Da")

# Transcribe to mRNA
mrna = seq_utils.transcribe(dna)
print(f"\\nmRNA (first 60): {mrna[:60]}...")

# Translate in all 3 reading frames
print(f"\\n=== Translation (3 frames) ===")
for frame in range(3):
    protein = seq_utils.translate(dna, reading_frame=frame)
    stops = protein.count("*")
    print(f"Frame +{frame}: {protein[:50]}... ({stops} stops)")

# Find ORFs
orfs = seq_utils.find_orfs(dna, min_length=60)
print(f"\\n=== Open Reading Frames (min 60bp) ===")
print(f"Found {len(orfs)} ORFs")
for i, orf in enumerate(orfs[:5]):
    print(f"  ORF {i+1}: pos {orf['start']}-{orf['end']} "
          f"({orf['length']}bp, frame {orf['frame']})")
    print(f"    Protein: {orf['protein'][:40]}...")

# Restriction sites
sites = seq_utils.restriction_sites(dna)
print(f"\\n=== Restriction Sites ===")
if sites:
    for enzyme, positions in sorted(sites.items()):
        print(f"  {enzyme}: {positions}")
else:
    print("  No common restriction sites found")

# Reverse complement
rc = seq_utils.reverse_complement(dna)
print(f"\\nReverse complement (first 50): {rc[:50]}...")

return {
    "length": len(dna), "gc_content": round(gc, 4),
    "orf_count": len(orfs), "restriction_enzymes": list(sites.keys()),
}''',
    },
    {
        "id": "protein-search",
        "title": "Protein Search & Features",
        "category": "Protein Analysis",
        "difficulty": "Beginner",
        "description": "Search UniProt for a protein and explore its features, domains, and GO annotations.",
        "tags": ["uniprot", "protein", "features", "go"],
        "code": '''# Protein Search & Features — Explore protein annotations
# Change the gene name or organism to explore different proteins

gene = "BRCA1"
organism = "Homo sapiens"

# Step 1: Search UniProt
print(f"Searching UniProt for {gene} ({organism})...")
proteins = await uniprot.search_protein(gene, organism=organism, max_results=3)

if not proteins:
    print("No results found")
    return {"error": "no results"}

p = proteins[0]
accession = p.get("primaryAccession", "unknown")
genes = p.get("genes", [{}])
gene_name = genes[0].get("geneName", {}).get("value", "N/A") if genes else "N/A"
desc = (p.get("proteinDescription", {})
         .get("recommendedName", {})
         .get("fullName", {}).get("value", "N/A"))
seq_info = p.get("sequence", {})

print(f"\\n=== {gene_name} ===")
print(f"Accession: {accession}")
print(f"Description: {desc}")
print(f"Length: {seq_info.get('length', 0)} aa")
print(f"Mass: {seq_info.get('molWeight', 0):,} Da")

state["accession"] = accession

# Step 2: Get protein features (domains, variants, etc.)
print(f"\\n=== Features & Domains ===")
features = await uniprot.get_protein_features(accession)

# Group by type
feature_types = {}
for f in features:
    ft = f.get("type", "unknown")
    feature_types[ft] = feature_types.get(ft, 0) + 1

for ft, count in sorted(feature_types.items(), key=lambda x: -x[1])[:10]:
    print(f"  {ft}: {count}")

# Step 3: Get GO terms
print(f"\\n=== Gene Ontology Annotations ===")
go_terms = await uniprot.get_go_terms(accession)
for go in go_terms[:8]:
    props = {p.get("key"): p.get("value") for p in go.get("properties", [])}
    term = props.get("GoTerm", go.get("id", ""))
    evidence = props.get("GoEvidenceType", "")
    print(f"  {go.get('id', '')}: {term} [{evidence}]")

return {
    "accession": accession, "gene": gene_name,
    "description": desc,
    "features": len(features), "go_terms": len(go_terms),
}''',
    },
    {
        "id": "fasta-processing",
        "title": "FASTA Processing",
        "category": "Getting Started",
        "difficulty": "Beginner",
        "description": "Parse, analyze, and manipulate FASTA-format sequences.",
        "tags": ["fasta", "format", "sequence"],
        "code": '''# FASTA Processing — Parse and analyze multi-sequence FASTA files

fasta_text = """>sp|P04637|P53_HUMAN Cellular tumor antigen p53
MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP
DEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYPQGLNGTVNLPGRNSFEV
RVCACPGRDRRTEEENLHKTTGIDSFLHPASTTQAGSWAGSSSEFSSTPNCQHLANATCPA
>sp|P02340|P53_MOUSE Cellular tumor antigen p53
MTAMEESQSDISLELPLSQETFSGLWKLLPPEDILPSPHCMDDLLLPQDVEEFFEGPSEAL
RVSGAPAAQDPVTETPGPVAPAPATPWPLSSFVPSQKTYQGSYGFRLGFLHSGTAKSVTC
TYSPALNKMFCQLAKTCPVQLWVDSTPPPGAEIFREVSACPGRTRSIEDELPPGHTHSPDA
>sp|P10361|P53_RAT Cellular tumor antigen p53
MEDSQSDMSIELPLSQETFSCLWKLLPPDDILPTTATGSPNSEETPFLEHPTLLSPDDIDD
LLPENVEEFFEGPSEALRVSGAPAAQDPVTEAPGQPTPAAAPAVAPVPATATAQTVALAAT
CSPLPKKVFCQLAKTCPVQLWVSATPPAGSRVRAMAIYKKSEHVAEVVRRCPHERCTEEGS"""

# Parse FASTA
records = fmt.parse_fasta(fasta_text)
print(f"Parsed {len(records)} sequences:\\n")

# Analyze each sequence
for rec in records:
    print(f"ID: {rec.id}")
    print(f"  Description: {rec.description}")
    print(f"  Length: {rec.length} aa")

    comp = seq_utils.amino_acid_composition(rec.sequence)
    mw = seq_utils.molecular_weight(rec.sequence, seq_type="protein")
    print(f"  Molecular Weight: {mw:,.0f} Da")

    # Charged residues
    charged = sum(comp.get(aa, 0) for aa in "DEKRH")
    print(f"  Charged residues: {charged} ({charged/rec.length:.1%})")

    # Hydrophobic residues
    hydrophobic = sum(comp.get(aa, 0) for aa in "AILMFWVP")
    print(f"  Hydrophobic residues: {hydrophobic} ({hydrophobic/rec.length:.1%})")
    print()

# Pairwise identity comparison
print("=== Pairwise Sequence Identity ===")
for i in range(len(records)):
    for j in range(i + 1, len(records)):
        s1, s2 = records[i].sequence, records[j].sequence
        min_len = min(len(s1), len(s2))
        matches = sum(1 for a, b in zip(s1[:min_len], s2[:min_len]) if a == b)
        identity = matches / min_len
        print(f"  {records[i].id} vs {records[j].id}: "
              f"{identity:.1%} ({matches}/{min_len})")

# Write back to FASTA
output = fmt.write_fasta(records)
print(f"\\nRoundtrip FASTA output: {len(output)} chars")

state["fasta_records"] = [r.to_dict() for r in records]
return {"sequences": len(records), "ids": [r.id for r in records]}''',
    },
    {
        "id": "pubmed-search",
        "title": "PubMed Literature Search",
        "category": "Research",
        "difficulty": "Beginner",
        "description": "Search PubMed for scientific articles and extract key information.",
        "tags": ["ncbi", "pubmed", "literature"],
        "code": '''# PubMed Literature Search — Find and summarize research papers
# Change the query to search for different topics

query = "CRISPR Cas9 gene therapy 2024"

print(f"Searching PubMed for: {query}")
print("=" * 50)

articles = await ncbi.search_pubmed(query, max_results=8)

if not articles:
    print("No articles found")
    return {"count": 0}

print(f"Found {len(articles)} articles:\\n")

for i, article in enumerate(articles, 1):
    title = article.get("title", "No title")
    authors = article.get("authors", [])
    author_str = ", ".join(
        a.get("name", "") for a in authors[:3]
    )
    if len(authors) > 3:
        author_str += " et al."
    journal = article.get("fulljournalname",
                          article.get("source", "Unknown"))
    pubdate = article.get("pubdate", "Unknown date")
    pmid = article.get("uid", "")

    print(f"{i}. {title}")
    print(f"   Authors: {author_str}")
    print(f"   Journal: {journal} ({pubdate})")
    print(f"   PMID: {pmid}")
    print()

state["search_results"] = articles
return {"query": query, "count": len(articles)}''',
    },
    {
        "id": "pdb-structure",
        "title": "Protein Structure Lookup",
        "category": "Protein Analysis",
        "difficulty": "Intermediate",
        "description": "Search the Protein Data Bank for 3D structures and get experimental details.",
        "tags": ["pdb", "structure", "protein"],
        "code": '''# Protein Structure Lookup — Explore 3D structures in PDB
# Try different search terms or PDB IDs

search_term = "CRISPR-Cas9"

# Step 1: Search PDB
print(f"Searching PDB for: {search_term}")
results = await pdb.text_search(search_term, max_results=5)

print(f"Found {len(results)} structures:\\n")
pdb_ids = []
for r in results:
    pdb_id = r.get("identifier", "?")
    pdb_ids.append(pdb_id)
    print(f"  {pdb_id} (score: {r.get('score', 0):.2f})")

# Step 2: Get details for the top structure
if pdb_ids:
    top_id = pdb_ids[0]
    print(f"\\n=== Details for {top_id} ===")

    summary = await pdb.get_structure_summary(top_id)
    print(f"Title: {summary.get('title', 'N/A')}")
    print(f"Resolution: {summary.get('resolution')} Å")
    print(f"Method: {summary.get('experimental_method', 'N/A')}")
    print(f"Deposition: {summary.get('deposition_date', 'N/A')}")
    print(f"Release: {summary.get('release_date', 'N/A')}")
    print(f"Citation: {summary.get('citation_title', 'N/A')}")
    print(f"Journal: {summary.get('citation_journal', 'N/A')}")

    # Step 3: Get entity (polymer) info
    print(f"\\n=== Polymer Entity ===")
    try:
        entity = await pdb.get_entity(top_id)
        details = entity.get("rcsb_polymer_entity", {})
        print(f"Type: {details.get('pdbx_description', 'N/A')}")
        src = entity.get("rcsb_entity_source_organism", [{}])
        if src:
            print(f"Organism: {src[0].get('ncbi_scientific_name', 'N/A')}")
    except Exception as e:
        print(f"Could not fetch entity: {e}")

    state["top_structure"] = summary
    return summary

return {"search": search_term, "count": len(results)}''',
    },
    {
        "id": "variant-analysis",
        "title": "Variant Analysis with VEP",
        "category": "Genomics",
        "difficulty": "Intermediate",
        "description": "Look up genetic variants and predict their functional effects using Ensembl VEP.",
        "tags": ["ensembl", "variant", "vep", "snp"],
        "code": '''# Variant Analysis — Look up SNPs and predict effects
# Change the rsID to explore different variants

variant_id = "rs699"  # AGT gene variant (angiotensinogen)

# Step 1: Get variant info from Ensembl
print(f"Looking up variant: {variant_id}")
print("=" * 50)

try:
    variant = await ensembl.get_variant(variant_id, species="human")

    print(f"Name: {variant.get('name', variant_id)}")
    print(f"Source: {variant.get('source', 'N/A')}")

    # Alleles and MAF
    mappings = variant.get("mappings", [])
    if mappings:
        m = mappings[0]
        print(f"Location: {m.get('seq_region_name')}:"
              f"{m.get('start')}-{m.get('end')}")
        print(f"Alleles: {m.get('allele_string', 'N/A')}")
        print(f"Strand: {m.get('strand')}")

    maf = variant.get("MAF")
    if maf:
        print(f"Minor Allele Frequency: {maf}")
    minor = variant.get("minor_allele")
    if minor:
        print(f"Minor Allele: {minor}")

    # Clinical significance
    clin = variant.get("clinical_significance", [])
    if clin:
        print(f"Clinical Significance: {', '.join(clin)}")

    state["variant"] = variant

except Exception as e:
    print(f"Variant lookup failed: {e}")

# Step 2: Look up associated gene
print(f"\\n=== Associated Gene ===")
try:
    gene_info = await ncbi.fetch_gene_info("AGT", organism="human")
    if gene_info:
        g = gene_info[0]
        print(f"Gene: {g.get('name', g.get('Name', 'N/A'))}")
        print(f"Description: {g.get('description', g.get('Description', 'N/A'))}")
except Exception as e:
    print(f"Gene lookup failed: {e}")

return {"variant": variant_id, "status": "complete"}''',
    },
    {
        "id": "cross-database",
        "title": "Cross-Database Research",
        "category": "Research",
        "difficulty": "Intermediate",
        "description": "Chain queries across NCBI, UniProt, PDB, and Ensembl to build a complete gene profile.",
        "tags": ["ncbi", "uniprot", "pdb", "ensembl", "cross-reference"],
        "code": '''# Cross-Database Research — Build a complete gene profile
# This chains queries across 4 databases using persistent state

gene = "EGFR"  # Epidermal Growth Factor Receptor
print(f"=== Cross-Database Profile: {gene} ===\\n")

# Database 1: NCBI Gene
print("1. NCBI Gene Database...")
try:
    genes = await ncbi.fetch_gene_info(gene, organism="human")
    if genes:
        g = genes[0]
        state["ncbi"] = {
            "name": g.get("name", g.get("Name")),
            "description": g.get("description", g.get("Description")),
        }
        print(f"   {state['ncbi']['description']}")
except Exception as e:
    print(f"   NCBI failed: {e}")

# Database 2: Ensembl
print("2. Ensembl...")
try:
    ens = await ensembl.get_gene_summary(gene, species="homo_sapiens")
    state["ensembl"] = ens
    print(f"   ID: {ens.get('ensembl_id')}")
    print(f"   Location: chr{ens.get('chromosome')}:"
          f"{ens.get('start')}-{ens.get('end')}")
except Exception as e:
    print(f"   Ensembl failed: {e}")

# Database 3: UniProt
print("3. UniProt...")
try:
    proteins = await uniprot.search_protein(gene, organism="Homo sapiens")
    if proteins:
        p = proteins[0]
        acc = p.get("primaryAccession")
        seq_len = p.get("sequence", {}).get("length", 0)
        state["uniprot"] = {"accession": acc, "length": seq_len}
        print(f"   Accession: {acc}")
        print(f"   Length: {seq_len} aa")

        # Get feature count
        features = await uniprot.get_protein_features(acc)
        state["uniprot"]["features"] = len(features)
        print(f"   Features: {len(features)}")
except Exception as e:
    print(f"   UniProt failed: {e}")

# Database 4: PDB structures
print("4. PDB Structures...")
try:
    acc = state.get("uniprot", {}).get("accession")
    if acc:
        structures = await pdb.search_by_uniprot(acc)
        state["pdb_count"] = len(structures)
        print(f"   Found {len(structures)} structures")
        for s in structures[:3]:
            print(f"   - {s.get('identifier')}")
except Exception as e:
    print(f"   PDB failed: {e}")

# Summary
print(f"\\n=== Summary ===")
print(f"Databases queried: 4")
print(f"State keys: {list(state.keys())}")

return {k: v for k, v in state.items() if k != "variant"}''',
    },
    {
        "id": "primer-design",
        "title": "PCR Primer Design Helper",
        "category": "Lab Tools",
        "difficulty": "Intermediate",
        "description": "Design and evaluate PCR primers: melting temperature, GC content, self-complementarity.",
        "tags": ["sequence", "primer", "pcr", "lab"],
        "code": '''# PCR Primer Design Helper — Evaluate and design primers
# Enter your target sequence and candidate primers

target = (
    "ATGGAGGAGCCGCAGTCAGATCCTAGCGTGAGTTTGCACTGATGGCCATG"
    "GCGCGGACGCGGGTGCCGGGCGGGGGTGTGCAGCCGCCGCCCCCTCCTGG"
)

# Candidate primers (modify or add your own)
primers = {
    "Forward_1": "ATGGAGGAGCCGCAGTCAG",
    "Forward_2": "GCAGTCAGATCCTAGCGTG",
    "Reverse_1": seq_utils.reverse_complement("CCAGGAGGGGGCGGCGGCTG"),
    "Reverse_2": seq_utils.reverse_complement("CATGGCCATCAGTGCAAACT"),
}

print("=== PCR Primer Analysis ===\\n")
print(f"Target: {len(target)} bp")
print(f"Target GC: {seq_utils.gc_content(target):.1%}\\n")

def calc_tm(seq):
    """Basic Tm estimation (Wallace rule for short primers)."""
    s = seq.upper()
    if len(s) < 14:
        return 2 * (s.count('A') + s.count('T')) + 4 * (s.count('G') + s.count('C'))
    # Salt-adjusted for longer primers
    gc = seq_utils.gc_content(s)
    return 64.9 + 41 * (gc - 0.395) * (1.0 / len(s)) + 81.5 * gc - 16.6

def check_self_complement(seq, window=4):
    """Check for self-complementary regions."""
    rc = seq_utils.reverse_complement(seq)
    hits = []
    for i in range(len(seq) - window + 1):
        fragment = seq[i:i+window].upper()
        if fragment in rc.upper():
            hits.append(fragment)
    return hits

print(f"{'Primer':<15} {'Seq':<25} {'Len':>3} {'GC%':>5} {'Tm°C':>5} {'Self-comp'}")
print("-" * 80)

results = []
for name, seq in primers.items():
    gc = seq_utils.gc_content(seq)
    tm = calc_tm(seq)
    self_comp = check_self_complement(seq)

    status = "OK"
    warnings = []
    if gc < 0.40:
        warnings.append("Low GC")
    if gc > 0.65:
        warnings.append("High GC")
    if tm < 55:
        warnings.append("Low Tm")
    if tm > 72:
        warnings.append("High Tm")
    if len(seq) < 18:
        warnings.append("Short")
    if len(seq) > 28:
        warnings.append("Long")
    if len(self_comp) > 3:
        warnings.append(f"{len(self_comp)} self-comp")

    sc = len(self_comp)
    print(f"{name:<15} {seq[:22]+'...' if len(seq)>22 else seq:<25} "
          f"{len(seq):>3} {gc:>4.0%} {tm:>5.1f} {sc}")
    if warnings:
        print(f"{'':>15} Warnings: {', '.join(warnings)}")

    results.append({
        "name": name, "sequence": seq,
        "length": len(seq), "gc": round(gc, 3),
        "tm": round(tm, 1), "warnings": warnings,
    })

# Find pairs with matched Tm
print(f"\\n=== Primer Pair Compatibility ===")
fwd = [(n, r) for n, r in zip(primers.keys(), results) if "Forward" in n]
rev = [(n, r) for n, r in zip(primers.keys(), results) if "Reverse" in n]
for fn, fr in fwd:
    for rn, rr in rev:
        tm_diff = abs(fr["tm"] - rr["tm"])
        compat = "GOOD" if tm_diff < 3 else "OK" if tm_diff < 5 else "POOR"
        print(f"  {fn} + {rn}: ΔTm = {tm_diff:.1f}°C [{compat}]")

state["primers"] = results
return results''',
    },
    {
        "id": "sequence-fetch",
        "title": "Fetch & Analyze NCBI Sequences",
        "category": "Getting Started",
        "difficulty": "Beginner",
        "description": "Fetch nucleotide or protein sequences from NCBI and analyze them.",
        "tags": ["ncbi", "sequence", "fasta", "fetch"],
        "code": '''# Fetch & Analyze Sequences from NCBI
# Try different accession numbers:
#   NM_007294 = BRCA1 mRNA, NM_000546 = TP53 mRNA
#   NP_000537 = p53 protein

accession = "NM_000546"  # TP53 mRNA
db = "nucleotide"  # "nucleotide" or "protein"

print(f"Fetching {accession} from NCBI {db}...")
fasta_text = await ncbi.fetch_sequence(db, accession, rettype="fasta")

# Parse the FASTA
records = fmt.parse_fasta(fasta_text)
if not records:
    print("No sequence returned")
    return {"error": "empty"}

rec = records[0]
seq = rec.sequence

print(f"\\n=== {rec.id} ===")
print(f"Description: {rec.description}")
print(f"Length: {rec.length} {'bp' if db == 'nucleotide' else 'aa'}")

if db == "nucleotide":
    # DNA/RNA analysis
    gc = seq_utils.gc_content(seq)
    comp = seq_utils.nucleotide_composition(seq)
    print(f"GC Content: {gc:.1%}")
    print(f"Composition: {comp}")

    # Find ORFs
    orfs = seq_utils.find_orfs(seq, min_length=300)
    print(f"\\nORFs (min 300bp): {len(orfs)}")
    for i, orf in enumerate(orfs[:3], 1):
        print(f"  ORF {i}: {orf['start']}-{orf['end']} "
              f"({orf['length']}bp)")
        mw = seq_utils.molecular_weight(
            orf['protein'].rstrip('*'), seq_type="protein")
        print(f"    Protein: {len(orf['protein'])} aa, {mw:,.0f} Da")

    # Show restriction sites
    sites = seq_utils.restriction_sites(seq)
    print(f"\\nRestriction sites: {len(sites)} enzymes")
    for enzyme, pos in sorted(sites.items()):
        print(f"  {enzyme}: {len(pos)} site(s)")

    state["sequence"] = {
        "accession": accession, "length": rec.length,
        "gc": round(gc, 4), "orf_count": len(orfs),
    }
else:
    # Protein analysis
    comp = seq_utils.amino_acid_composition(seq)
    mw = seq_utils.molecular_weight(seq, seq_type="protein")
    print(f"Molecular Weight: {mw:,.0f} Da")

    # Top amino acids
    top = sorted(comp.items(), key=lambda x: -x[1])[:5]
    print(f"Most frequent: {', '.join(f'{aa}={c}' for aa, c in top)}")

    state["sequence"] = {
        "accession": accession, "length": rec.length, "mw": mw,
    }

# Print sequence preview
print(f"\\nSequence preview:")
print(f"  5': {seq[:60]}...")
print(f"  3': ...{seq[-60:]}")

return state["sequence"]''',
    },
    {
        "id": "blast-search",
        "title": "BLAST Sequence Search",
        "category": "Research",
        "difficulty": "Advanced",
        "description": "Run BLAST to find similar sequences in NCBI databases. Note: BLAST jobs take 1-5 minutes.",
        "tags": ["blast", "alignment", "similarity", "search"],
        "code": '''# BLAST Sequence Search — Find similar sequences
# WARNING: BLAST jobs can take 1-5 minutes to complete!
# For faster results, use smaller sequences and swissprot database

# Example: short protein query (insulin fragment)
protein_seq = "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKT"
program = "blastp"
database = "swissprot"  # swissprot is fastest, nr is most comprehensive

print(f"Submitting BLAST search...")
print(f"  Program: {program}")
print(f"  Database: {database}")
print(f"  Query length: {len(protein_seq)} aa")
print(f"  Query: {protein_seq[:40]}...")

# Submit the job
rid = await blast.submit(
    program=program,
    database=database,
    sequence=protein_seq,
    hitlist_size=5,
    expect=0.001,
)
print(f"\\nJob submitted: RID = {rid}")
print("Waiting for results (this may take 1-5 minutes)...")

# Poll for results
results = await blast.wait_for_results(rid, format_type="JSON2")

# Parse results
if isinstance(results, dict):
    search = results.get("BlastOutput2", [{}])
    if search:
        report = search[0].get("report", {}).get("results", {})
        hits = report.get("search", {}).get("hits", [])
        print(f"\\n=== Found {len(hits)} hits ===\\n")
        for i, hit in enumerate(hits, 1):
            desc = hit.get("description", [{}])[0]
            title = desc.get("title", "Unknown")
            accession = desc.get("accession", "?")
            hsps = hit.get("hsps", [{}])
            if hsps:
                hsp = hsps[0]
                identity = hsp.get("identity", 0)
                align_len = hsp.get("align_len", 1)
                pct = identity / align_len * 100
                evalue = hsp.get("evalue", "N/A")
                print(f"{i}. {title[:70]}")
                print(f"   Accession: {accession}")
                print(f"   Identity: {identity}/{align_len} ({pct:.1f}%)")
                print(f"   E-value: {evalue}")
                print()
        state["blast_hits"] = len(hits)
        return {"hits": len(hits), "rid": rid}
    else:
        print("No results in expected format")
else:
    print("Results returned as text")

return {"rid": rid, "status": "complete"}''',
    },
    {
        "id": "bed-gff-analysis",
        "title": "Genomic Region Analysis",
        "category": "Genomics",
        "difficulty": "Intermediate",
        "description": "Parse and analyze genomic regions in BED and GFF formats.",
        "tags": ["bed", "gff", "genomic", "annotation"],
        "code": '''# Genomic Region Analysis — Work with BED and GFF formats

# Example BED data (gene promoter regions)
bed_text = """chr1\t11869\t14409\tDDX11L1\t0\t+
chr1\t14404\t29570\tWASH7P\t0\t-
chr1\t29554\t31109\tMIR1302-2HG\t0\t+
chr1\t34554\t36081\tFAM138A\t0\t-
chr1\t65419\t71585\tOR4F5\t0\t+
chr7\t55019017\t55211628\tEGFR\t0\t+
chr17\t7661779\t7687550\tTP53\t0\t-
chr17\t43044295\t43170245\tBRCA1\t0\t-
chr13\t32315086\t32400266\tBRCA2\t0\t+"""

print("=== BED File Analysis ===\\n")
bed_records = fmt.parse_bed(bed_text)
print(f"Parsed {len(bed_records)} regions\\n")

# Summary table
print(f"{'Name':<15} {'Chrom':<6} {'Start':>10} {'End':>10} "
      f"{'Length':>8} {'Strand'}")
print("-" * 65)
for r in bed_records:
    print(f"{r.name:<15} {r.chrom:<6} {r.start:>10,} {r.end:>10,} "
          f"{r.length:>7,} {r.strand:>4}")

# Statistics
total_bp = sum(r.length for r in bed_records)
chroms = set(r.chrom for r in bed_records)
print(f"\\nTotal coverage: {total_bp:,} bp")
print(f"Chromosomes: {', '.join(sorted(chroms))}")
print(f"Average region size: {total_bp // len(bed_records):,} bp")
print(f"Largest: {max(bed_records, key=lambda r: r.length).name} "
      f"({max(r.length for r in bed_records):,} bp)")
print(f"Smallest: {min(bed_records, key=lambda r: r.length).name} "
      f"({min(r.length for r in bed_records):,} bp)")

# Example GFF data
print("\\n\\n=== GFF Feature Analysis ===\\n")
gff_text = """chr17\tENSEMBL\tgene\t7661779\t7687550\t.\t-\t.\tID=ENSG00000141510;Name=TP53;biotype=protein_coding
chr17\tENSEMBL\tmRNA\t7661779\t7687550\t.\t-\t.\tID=ENST00000269305;Parent=ENSG00000141510;Name=TP53-201
chr17\tENSEMBL\texon\t7687377\t7687550\t.\t-\t.\tID=exon1;Parent=ENST00000269305
chr17\tENSEMBL\texon\t7676520\t7676622\t.\t-\t.\tID=exon2;Parent=ENST00000269305
chr17\tENSEMBL\texon\t7676381\t7676403\t.\t-\t.\tID=exon3;Parent=ENST00000269305
chr17\tENSEMBL\tCDS\t7687377\t7687550\t.\t-\t0\tID=CDS1;Parent=ENST00000269305"""

gff_records = fmt.parse_gff(gff_text)
print(f"Parsed {len(gff_records)} GFF features\\n")

# Group by feature type
feature_types = {}
for r in gff_records:
    feature_types[r.feature_type] = feature_types.get(r.feature_type, 0) + 1

for ft, count in sorted(feature_types.items()):
    print(f"  {ft}: {count}")

print(f"\\nFeature details:")
for r in gff_records:
    attrs = ", ".join(f"{k}={v}" for k, v in list(r.attributes.items())[:3])
    print(f"  {r.feature_type:<6} {r.start:>10,}-{r.end:>10,} "
          f"({r.end - r.start + 1:>6,} bp) {attrs}")

state["bed_regions"] = len(bed_records)
state["gff_features"] = len(gff_records)
return {"bed_regions": len(bed_records), "gff_features": len(gff_records)}''',
    },
    {
        "id": "state-workflow",
        "title": "Multi-Step Stateful Workflow",
        "category": "Advanced",
        "difficulty": "Advanced",
        "description": "Build a multi-step analysis pipeline using state persistence across executions.",
        "tags": ["state", "workflow", "pipeline"],
        "code": '''# Multi-Step Stateful Workflow — Data persists between Run clicks
#
# This demonstrates the Code MCP's key advantage: STATE PERSISTENCE.
# Run this code, then modify and run again — previous state is kept!
#
# Step tracking
step = state.get("workflow_step", 0) + 1
state["workflow_step"] = step

print(f"=== Workflow Step {step} ===\\n")

if step == 1:
    print("Step 1: Initialize with a DNA sequence")
    state["dna"] = (
        "ATGGAGGAGCCGCAGTCAGATCCTAGCGTGAGTTTGCACTGATG"
        "GCCATGGCGCGGACGCGGGTGCCGGGCGGGGGTGTGCAGCCGCC"
        "GCCCCCTCCTGGCCCCTGTCATCTTCTGTCCCTTCCCAGAAAACCTAC"
    )
    state["gene"] = "TP53"
    print(f"  Stored DNA sequence ({len(state['dna'])} bp)")
    print(f"  Gene: {state['gene']}")
    print(f"\\n>>> Click Run again for Step 2!")

elif step == 2:
    print("Step 2: Analyze the stored sequence")
    dna = state["dna"]
    state["analysis"] = {
        "gc": round(seq_utils.gc_content(dna), 4),
        "length": len(dna),
        "protein": seq_utils.translate(dna),
    }
    print(f"  GC Content: {state['analysis']['gc']:.1%}")
    print(f"  Translated: {state['analysis']['protein'][:30]}...")
    print(f"\\n>>> Click Run again for Step 3!")

elif step == 3:
    print("Step 3: Fetch data from UniProt")
    gene = state["gene"]
    try:
        proteins = await uniprot.search_protein(gene)
        if proteins:
            acc = proteins[0].get("primaryAccession")
            state["uniprot_acc"] = acc
            print(f"  Found UniProt: {acc}")
    except Exception as e:
        state["uniprot_acc"] = "P04637"
        print(f"  Using known accession: P04637")
    print(f"\\n>>> Click Run again for Step 4!")

elif step == 4:
    print("Step 4: Compile final report from all steps")
    print(f"\\n  Gene: {state.get('gene')}")
    print(f"  Sequence: {state.get('analysis', {}).get('length')} bp")
    print(f"  GC Content: {state.get('analysis', {}).get('gc', 0):.1%}")
    print(f"  Protein: {state.get('analysis', {}).get('protein', '')[:20]}...")
    print(f"  UniProt: {state.get('uniprot_acc', 'N/A')}")
    print(f"\\n  Total state keys: {list(state.keys())}")
    print(f"\\n  Workflow complete! Reset state to start over.")
    state["workflow_step"] = 0  # Reset for next run

else:
    state["workflow_step"] = 0
    print("Workflow reset. Run again to start from Step 1.")

return {"step": step, "state_keys": list(state.keys())}''',
    },
]

# Group templates by category
CATEGORIES: dict[str, list[dict]] = {}
for proj in STARTER_PROJECTS:
    cat = proj["category"]
    if cat not in CATEGORIES:
        CATEGORIES[cat] = []
    CATEGORIES[cat].append(proj)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    session_id = str(uuid.uuid4())
    return templates.TemplateResponse("index.html", {
        "request": request,
        "session_id": session_id,
        "categories": CATEGORIES,
        "projects": STARTER_PROJECTS,
    })


@app.post("/api/execute")
async def execute_code(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    code = body.get("code", "")
    reset = body.get("reset_state", False)

    sandbox = _get_sandbox(session_id)
    if reset:
        sandbox.reset_state()

    result = await sandbox.execute(code)
    return JSONResponse({
        "success": result.success,
        "result": result.to_text(),
        "state_keys": result.state_keys,
    })


@app.post("/api/reset")
async def reset_state(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    sandbox = _get_sandbox(session_id)
    sandbox.reset_state()
    return JSONResponse({"success": True, "message": "State cleared"})


@app.get("/api/search")
async def search_operations(query: str = "", module: str = "", tags: str = ""):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    results = _registry.search(
        query=query,
        module=module or None,
        tags=tag_list,
    )
    return JSONResponse({"results": results, "count": len(results)})


@app.get("/api/modules")
async def list_modules():
    modules = _registry.list_modules()
    tags = _registry.list_tags()
    return JSONResponse({"modules": modules, "tags": tags})


@app.get("/api/templates")
async def list_templates():
    return JSONResponse({
        "categories": {k: [{"id": p["id"], "title": p["title"],
                            "difficulty": p["difficulty"],
                            "description": p["description"]}
                           for p in v] for k, v in CATEGORIES.items()},
        "count": len(STARTER_PROJECTS),
    })


@app.get("/api/template/{template_id}")
async def get_template(template_id: str):
    for proj in STARTER_PROJECTS:
        if proj["id"] == template_id:
            return JSONResponse(proj)
    return JSONResponse({"error": "Template not found"}, status_code=404)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    print("Starting Bioinformatics Playground...")
    print("Open http://localhost:8765 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8765)

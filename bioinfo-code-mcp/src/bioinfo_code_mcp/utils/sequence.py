"""Sequence manipulation helpers for the Code MCP sandbox.

Provides common bioinformatics sequence operations that agents can call
directly in generated code without re-implementing from scratch.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

# Standard genetic code (codon → amino acid)
CODON_TABLE: dict[str, str] = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

COMPLEMENT_MAP = str.maketrans("ATCGatcg", "TAGCtagc")


def reverse_complement(seq: str) -> str:
    """Return the reverse complement of a DNA sequence.

    Args:
        seq: DNA sequence string (A/T/C/G, case-insensitive).

    Returns:
        Reverse complement string.
    """
    return seq.translate(COMPLEMENT_MAP)[::-1]


def transcribe(dna: str) -> str:
    """Transcribe DNA to mRNA (T → U).

    Args:
        dna: DNA sequence string.

    Returns:
        mRNA sequence string.
    """
    return dna.upper().replace("T", "U")


def translate(dna: str, reading_frame: int = 0) -> str:
    """Translate a DNA sequence to a protein sequence.

    Args:
        dna: DNA sequence string.
        reading_frame: 0, 1, or 2 offset for reading frame.

    Returns:
        Protein sequence string (single-letter codes, * = stop).
    """
    seq = dna.upper()
    protein = []
    for i in range(reading_frame, len(seq) - 2, 3):
        codon = seq[i : i + 3]
        aa = CODON_TABLE.get(codon, "X")
        protein.append(aa)
    return "".join(protein)


def gc_content(seq: str) -> float:
    """Calculate GC content of a nucleotide sequence.

    Args:
        seq: DNA or RNA sequence string.

    Returns:
        GC content as a fraction (0.0 to 1.0).
    """
    seq = seq.upper()
    gc = sum(1 for b in seq if b in "GC")
    total = sum(1 for b in seq if b in "ATCGU")
    return gc / total if total > 0 else 0.0


def nucleotide_composition(seq: str) -> dict[str, int]:
    """Count nucleotide frequencies.

    Args:
        seq: Nucleotide sequence.

    Returns:
        Dict mapping each base to its count.
    """
    return dict(Counter(seq.upper()))


def amino_acid_composition(seq: str) -> dict[str, int]:
    """Count amino acid frequencies in a protein sequence.

    Args:
        seq: Protein sequence (single-letter codes).

    Returns:
        Dict mapping each amino acid to its count.
    """
    return dict(Counter(seq.upper()))


def molecular_weight(seq: str, seq_type: str = "protein") -> float:
    """Estimate molecular weight of a sequence.

    Args:
        seq: Sequence string.
        seq_type: "protein" or "dna".

    Returns:
        Approximate molecular weight in Daltons.
    """
    seq = seq.upper()
    if seq_type == "protein":
        # Average amino acid MW ≈ 110 Da
        aa_weights: dict[str, float] = {
            "A": 89.1, "R": 174.2, "N": 132.1, "D": 133.1, "C": 121.2,
            "E": 147.1, "Q": 146.2, "G": 75.0, "H": 155.2, "I": 131.2,
            "L": 131.2, "K": 146.2, "M": 149.2, "F": 165.2, "P": 115.1,
            "S": 105.1, "T": 119.1, "W": 204.2, "Y": 181.2, "V": 117.1,
        }
        weight = sum(aa_weights.get(aa, 110.0) for aa in seq)
        # Subtract water for peptide bonds
        weight -= 18.015 * (len(seq) - 1)
        return round(weight, 2)
    else:
        # Average nucleotide MW ≈ 330 Da (DNA)
        nt_weights: dict[str, float] = {
            "A": 331.2, "T": 322.2, "C": 307.2, "G": 347.2, "U": 308.2,
        }
        weight = sum(nt_weights.get(nt, 330.0) for nt in seq)
        return round(weight, 2)


def find_orfs(dna: str, min_length: int = 100) -> list[dict[str, Any]]:
    """Find open reading frames in a DNA sequence.

    Args:
        dna: DNA sequence string.
        min_length: Minimum ORF length in nucleotides.

    Returns:
        List of dicts with 'start', 'end', 'length', 'frame', 'protein'.
    """
    seq = dna.upper()
    orfs = []
    for frame in range(3):
        i = frame
        while i < len(seq) - 2:
            codon = seq[i : i + 3]
            if codon == "ATG":
                start = i
                j = i + 3
                while j < len(seq) - 2:
                    stop_codon = seq[j : j + 3]
                    if stop_codon in ("TAA", "TAG", "TGA"):
                        length = j + 3 - start
                        if length >= min_length:
                            orf_seq = seq[start : j + 3]
                            orfs.append({
                                "start": start,
                                "end": j + 3,
                                "length": length,
                                "frame": frame,
                                "protein": translate(orf_seq),
                            })
                        break
                    j += 3
                i = j + 3
            else:
                i += 3
    return sorted(orfs, key=lambda x: x["length"], reverse=True)


def restriction_sites(seq: str, enzyme_patterns: dict[str, str] | None = None) -> dict[str, list[int]]:
    """Find restriction enzyme cut sites in a DNA sequence.

    Args:
        seq: DNA sequence.
        enzyme_patterns: Dict of enzyme_name → recognition sequence.
            Defaults to a small set of common enzymes.

    Returns:
        Dict mapping enzyme name to list of cut positions.
    """
    if enzyme_patterns is None:
        enzyme_patterns = {
            "EcoRI": "GAATTC",
            "BamHI": "GGATCC",
            "HindIII": "AAGCTT",
            "NotI": "GCGGCCGC",
            "XhoI": "CTCGAG",
            "SalI": "GTCGAC",
            "NdeI": "CATATG",
            "BglII": "AGATCT",
            "PstI": "CTGCAG",
            "SmaI": "CCCGGG",
        }
    seq_upper = seq.upper()
    results: dict[str, list[int]] = {}
    for name, pattern in enzyme_patterns.items():
        positions = [m.start() for m in re.finditer(pattern, seq_upper)]
        if positions:
            results[name] = positions
    return results

"""Tests for sequence utility functions."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.utils.sequence import (
    amino_acid_composition,
    find_orfs,
    gc_content,
    molecular_weight,
    nucleotide_composition,
    restriction_sites,
    reverse_complement,
    transcribe,
    translate,
)


class TestReverseComplement:
    def test_basic(self):
        assert reverse_complement("ATGC") == "GCAT"

    def test_palindrome(self):
        assert reverse_complement("GAATTC") == "GAATTC"

    def test_empty(self):
        assert reverse_complement("") == ""

    def test_single_base(self):
        assert reverse_complement("A") == "T"
        assert reverse_complement("T") == "A"
        assert reverse_complement("G") == "C"
        assert reverse_complement("C") == "G"

    def test_lowercase(self):
        assert reverse_complement("atgc") == "gcat"

    def test_longer_sequence(self):
        seq = "ATGCGATCGATCG"
        rc = reverse_complement(seq)
        # RC of RC should be the original
        assert reverse_complement(rc) == seq


class TestTranscribe:
    def test_basic(self):
        assert transcribe("ATGCGATCG") == "AUGCGAUCG"

    def test_no_t(self):
        assert transcribe("AAAGCCC") == "AAAGCCC"

    def test_lowercase(self):
        assert transcribe("atgc") == "AUGC"


class TestTranslate:
    def test_basic(self):
        assert translate("ATGGCC") == "MA"

    def test_stop_codon(self):
        assert translate("ATGTAA") == "M*"

    def test_reading_frame_1(self):
        assert translate("AATGGCC", reading_frame=1) == "MA"

    def test_reading_frame_2(self):
        assert translate("AAATGGCC", reading_frame=2) == "MA"

    def test_incomplete_codon(self):
        # Last 2 bases don't form a complete codon
        assert translate("ATGGCCA") == "MA"

    def test_known_sequence(self):
        # ATG=M, GAA=E, GAG=E
        assert translate("ATGGAAGAG") == "MEE"


class TestGCContent:
    def test_all_gc(self):
        assert gc_content("GCGC") == 1.0

    def test_all_at(self):
        assert gc_content("ATAT") == 0.0

    def test_mixed(self):
        assert gc_content("ATGC") == 0.5

    def test_empty(self):
        assert gc_content("") == 0.0

    def test_rna(self):
        assert gc_content("GCGU") == 0.75

    def test_case_insensitive(self):
        assert gc_content("atgc") == 0.5


class TestNucleotideComposition:
    def test_basic(self):
        comp = nucleotide_composition("AATGCC")
        assert comp["A"] == 2
        assert comp["T"] == 1
        assert comp["G"] == 1
        assert comp["C"] == 2


class TestAminoAcidComposition:
    def test_basic(self):
        comp = amino_acid_composition("MEEPQ")
        assert comp["M"] == 1
        assert comp["E"] == 2
        assert comp["P"] == 1
        assert comp["Q"] == 1


class TestMolecularWeight:
    def test_protein(self):
        mw = molecular_weight("MEEPQ", seq_type="protein")
        assert mw > 0
        # 5 amino acids, average ~110 Da each, minus water
        assert 400 < mw < 800

    def test_dna(self):
        mw = molecular_weight("ATGCGATCG", seq_type="dna")
        assert mw > 0
        # 9 nucleotides, average ~330 Da each
        assert 2000 < mw < 4000


class TestFindORFs:
    def test_single_orf(self):
        # ATG...TAA with enough length
        orf_seq = "ATG" + "GCC" * 40 + "TAA"
        orfs = find_orfs(orf_seq, min_length=30)
        assert len(orfs) >= 1
        assert orfs[0]["start"] == 0

    def test_min_length_filter(self):
        # Short ORF below threshold
        short_orf = "ATGGCCTAA"
        orfs = find_orfs(short_orf, min_length=100)
        assert len(orfs) == 0

    def test_no_orf(self):
        orfs = find_orfs("AAACCCGGG", min_length=10)
        assert len(orfs) == 0

    def test_sorted_by_length(self):
        # Create sequence with multiple ORFs
        seq = "ATG" + "GCC" * 50 + "TAA" + "ATG" + "GCC" * 20 + "TAG"
        orfs = find_orfs(seq, min_length=30)
        if len(orfs) >= 2:
            assert orfs[0]["length"] >= orfs[1]["length"]


class TestRestrictionSites:
    def test_ecori(self):
        seq = "ATGCGAATTCGATCG"
        sites = restriction_sites(seq)
        assert "EcoRI" in sites
        assert 4 in sites["EcoRI"]

    def test_no_sites(self):
        seq = "AAAAAAAAAA"
        sites = restriction_sites(seq)
        assert len(sites) == 0

    def test_multiple_sites(self):
        seq = "GAATTCAAAGAATTC"
        sites = restriction_sites(seq)
        assert "EcoRI" in sites
        assert len(sites["EcoRI"]) == 2

    def test_custom_patterns(self):
        seq = "ATGCATGCATGC"
        sites = restriction_sites(seq, enzyme_patterns={"Custom": "ATGC"})
        assert "Custom" in sites
        assert len(sites["Custom"]) == 3

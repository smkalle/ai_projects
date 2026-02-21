"""Tests for format parser utilities."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.utils.formats import (
    BEDRecord,
    FastaRecord,
    GFFRecord,
    parse_bed,
    parse_clustal,
    parse_fasta,
    parse_gff,
    write_fasta,
)


class TestFastaRecord:
    def test_id_extraction(self):
        rec = FastaRecord(header="sp|P04637|P53_HUMAN Tumor antigen", sequence="MEEP")
        assert rec.id == "sp|P04637|P53_HUMAN"

    def test_description(self):
        rec = FastaRecord(header="seq1 Some description", sequence="ATGC")
        assert rec.description == "Some description"

    def test_length(self):
        rec = FastaRecord(header="test", sequence="ATGCGATCG")
        assert rec.length == 9

    def test_to_dict(self):
        rec = FastaRecord(header="seq1 desc", sequence="ATGC")
        d = rec.to_dict()
        assert d["id"] == "seq1"
        assert d["description"] == "desc"
        assert d["sequence"] == "ATGC"
        assert d["length"] == 4


class TestParseFasta:
    def test_single_record(self):
        text = ">seq1 Test\nATGCGATCG\n"
        records = parse_fasta(text)
        assert len(records) == 1
        assert records[0].id == "seq1"
        assert records[0].sequence == "ATGCGATCG"

    def test_multiline_sequence(self):
        text = ">seq1 Test\nATGC\nGATCG\n"
        records = parse_fasta(text)
        assert records[0].sequence == "ATGCGATCG"

    def test_multiple_records(self):
        text = ">seq1\nATGC\n>seq2\nGGCC\n"
        records = parse_fasta(text)
        assert len(records) == 2
        assert records[0].id == "seq1"
        assert records[1].id == "seq2"

    def test_empty_lines(self):
        text = ">seq1\nATGC\n\n>seq2\nGGCC\n"
        records = parse_fasta(text)
        assert len(records) == 2

    def test_empty_input(self):
        records = parse_fasta("")
        assert len(records) == 0

    def test_protein_fasta(self):
        text = ">sp|P04637|P53_HUMAN Cellular tumor antigen p53\nMEEPQSDPSVEPPLSQETFSDLWKLL\nPENNVLSPLPSQAMDDLMLSPDDIE\n"
        records = parse_fasta(text)
        assert len(records) == 1
        assert records[0].sequence == "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIE"


class TestWriteFasta:
    def test_roundtrip(self):
        records = [
            FastaRecord(header="seq1 Test", sequence="ATGCGATCG"),
            FastaRecord(header="seq2 Another", sequence="MEEPQ"),
        ]
        text = write_fasta(records)
        parsed = parse_fasta(text)
        assert len(parsed) == 2
        assert parsed[0].sequence == "ATGCGATCG"
        assert parsed[1].sequence == "MEEPQ"

    def test_line_wrapping(self):
        long_seq = "A" * 200
        records = [FastaRecord(header="long", sequence=long_seq)]
        text = write_fasta(records, line_width=80)
        lines = text.strip().splitlines()
        assert lines[0] == ">long"
        assert len(lines[1]) == 80
        assert len(lines[2]) == 80
        assert len(lines[3]) == 40


class TestParseGFF:
    def test_basic_gff(self):
        text = "chr1\tENSEMBL\tgene\t11869\t14409\t.\t+\t.\tID=ENSG00000223972;Name=DDX11L1\n"
        records = parse_gff(text)
        assert len(records) == 1
        assert records[0].seqid == "chr1"
        assert records[0].feature_type == "gene"
        assert records[0].start == 11869
        assert records[0].end == 14409
        assert records[0].strand == "+"
        assert records[0].attributes["ID"] == "ENSG00000223972"
        assert records[0].attributes["Name"] == "DDX11L1"

    def test_skip_comments(self):
        text = "##gff-version 3\n#comment\nchr1\ttest\tgene\t1\t100\t.\t+\t.\tID=g1\n"
        records = parse_gff(text)
        assert len(records) == 1

    def test_to_dict(self):
        rec = GFFRecord(
            seqid="chr1", source="test", feature_type="exon",
            start=100, end=200, score=".", strand="+", phase=".",
            attributes={"ID": "e1"},
        )
        d = rec.to_dict()
        assert d["seqid"] == "chr1"
        assert d["type"] == "exon"
        assert d["attributes"]["ID"] == "e1"


class TestParseBED:
    def test_bed3(self):
        text = "chr1\t100\t200\n"
        records = parse_bed(text)
        assert len(records) == 1
        assert records[0].chrom == "chr1"
        assert records[0].start == 100
        assert records[0].end == 200
        assert records[0].length == 100

    def test_bed6(self):
        text = "chr1\t100\t200\tgene1\t500\t+\n"
        records = parse_bed(text)
        assert records[0].name == "gene1"
        assert records[0].score == 500
        assert records[0].strand == "+"

    def test_skip_track_lines(self):
        text = "track name=test\nchr1\t100\t200\n"
        records = parse_bed(text)
        assert len(records) == 1

    def test_multiple_records(self):
        text = "chr1\t100\t200\ngene1\nchr2\t300\t400\tgene2\n"
        records = parse_bed(text)
        assert len(records) == 2

    def test_to_dict(self):
        rec = BEDRecord(chrom="chr1", start=100, end=200, name="test", score=0, strand="+")
        d = rec.to_dict()
        assert d["chrom"] == "chr1"
        assert d["length"] == 100


class TestParseClustal:
    def test_basic_clustal(self):
        text = """CLUSTAL W (1.83) multiple sequence alignment

seq1    ATGCGATCG---ATCG
seq2    ATGCGAT--GCGATCG
                 *

seq1    AAACCCTTT
seq2    AAACCC---
"""
        result = parse_clustal(text)
        assert "seq1" in result
        assert "seq2" in result
        assert result["seq1"] == "ATGCGATCG---ATCGAAACCCTTT"
        assert result["seq2"] == "ATGCGAT--GCGATCGAAACCC---"

    def test_empty_alignment(self):
        result = parse_clustal("")
        assert len(result) == 0

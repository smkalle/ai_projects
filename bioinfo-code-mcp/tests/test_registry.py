"""Tests for the API registry and discovery system."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.registry import Registry


@pytest.fixture
def registry():
    return Registry()


class TestRegistrySearch:
    """Test the search functionality."""

    def test_search_by_query(self, registry):
        results = registry.search(query="gene lookup")
        assert len(results) > 0
        # Should find gene-related operations
        names = [r["name"] for r in results]
        assert any("gene" in n or "lookup" in n for n in names)

    def test_search_by_tags(self, registry):
        results = registry.search(tags=["ncbi", "pubmed"])
        assert len(results) > 0
        for r in results:
            assert any(
                t.lower() in ["ncbi", "pubmed"] for t in r["tags"]
            )

    def test_search_by_module(self, registry):
        results = registry.search(module="uniprot")
        assert len(results) > 0
        for r in results:
            assert r["module"] == "uniprot"

    def test_search_combined(self, registry):
        results = registry.search(query="protein", module="uniprot")
        assert len(results) > 0
        for r in results:
            assert r["module"] == "uniprot"

    def test_search_limit(self, registry):
        results = registry.search(query="", limit=3)
        assert len(results) <= 3

    def test_search_no_results(self, registry):
        results = registry.search(query="zzz_nonexistent_xyz")
        assert len(results) == 0

    def test_search_blast(self, registry):
        results = registry.search(query="BLAST protein")
        assert len(results) > 0
        names = [r["name"] for r in results]
        assert any("blast" in n for n in names)

    def test_search_sequence_utils(self, registry):
        results = registry.search(query="reverse complement")
        assert len(results) > 0

    def test_search_format_utils(self, registry):
        results = registry.search(query="parse FASTA")
        assert len(results) > 0

    def test_search_variant(self, registry):
        results = registry.search(query="variant", tags=["ensembl"])
        assert len(results) > 0


class TestRegistryModules:
    """Test module listing."""

    def test_list_modules(self, registry):
        modules = registry.list_modules()
        assert len(modules) > 0
        module_names = [m["module"] for m in modules]
        assert "ncbi" in module_names
        assert "uniprot" in module_names
        assert "pdb" in module_names
        assert "ensembl" in module_names
        assert "blast" in module_names
        assert "sequence_utils" in module_names
        assert "format_utils" in module_names

    def test_module_operation_counts(self, registry):
        modules = registry.list_modules()
        for m in modules:
            assert m["operation_count"] > 0


class TestRegistryTags:
    """Test tag listing."""

    def test_list_tags(self, registry):
        tags = registry.list_tags()
        assert len(tags) > 0
        assert "ncbi" in tags
        assert "protein" in tags
        assert "sequence" in tags
        assert "blast" in tags
        assert "fasta" in tags

    def test_tags_sorted(self, registry):
        tags = registry.list_tags()
        assert tags == sorted(tags)


class TestRegistryGetOperation:
    """Test getting specific operations."""

    def test_get_existing_operation(self, registry):
        op = registry.get_operation("ncbi.esearch")
        assert op is not None
        assert op["name"] == "ncbi.esearch"
        assert op["module"] == "ncbi"
        assert len(op["params"]) > 0

    def test_get_nonexistent_operation(self, registry):
        op = registry.get_operation("nonexistent.method")
        assert op is None

    def test_operation_has_example(self, registry):
        op = registry.get_operation("ncbi.esearch")
        assert op is not None
        assert op["example"] != ""

    def test_operation_params_structure(self, registry):
        op = registry.get_operation("ncbi.esearch")
        assert op is not None
        for param in op["params"]:
            assert "name" in param
            assert "type" in param
            assert "description" in param
            assert "required" in param


class TestRegistryCompleteness:
    """Test that all expected operations are registered."""

    def test_ncbi_operations_registered(self, registry):
        ops = registry.search(module="ncbi")
        names = {o["name"] for o in ops}
        expected = {"ncbi.esearch", "ncbi.efetch", "ncbi.esummary", "ncbi.einfo",
                    "ncbi.elink", "ncbi.search_pubmed", "ncbi.fetch_gene_info",
                    "ncbi.fetch_sequence"}
        assert expected.issubset(names)

    def test_uniprot_operations_registered(self, registry):
        ops = registry.search(module="uniprot")
        names = {o["name"] for o in ops}
        expected = {"uniprot.search", "uniprot.fetch_entry", "uniprot.fetch_fasta",
                    "uniprot.search_protein", "uniprot.get_protein_features",
                    "uniprot.get_go_terms"}
        assert expected.issubset(names)

    def test_pdb_operations_registered(self, registry):
        ops = registry.search(module="pdb")
        names = {o["name"] for o in ops}
        expected = {"pdb.get_entry", "pdb.get_entity", "pdb.text_search",
                    "pdb.search_by_uniprot", "pdb.get_structure_summary"}
        assert expected.issubset(names)

    def test_ensembl_operations_registered(self, registry):
        ops = registry.search(module="ensembl")
        names = {o["name"] for o in ops}
        expected = {"ensembl.lookup_id", "ensembl.lookup_symbol",
                    "ensembl.get_sequence", "ensembl.get_variant",
                    "ensembl.get_vep", "ensembl.get_xrefs",
                    "ensembl.get_gene_summary"}
        assert expected.issubset(names)

    def test_blast_operations_registered(self, registry):
        ops = registry.search(module="blast")
        names = {o["name"] for o in ops}
        expected = {"blast.submit", "blast.wait_for_results",
                    "blast.blastn", "blast.blastp"}
        assert expected.issubset(names)

    def test_sequence_utils_registered(self, registry):
        ops = registry.search(module="sequence_utils")
        assert len(ops) >= 7  # At least 7 sequence utilities

    def test_format_utils_registered(self, registry):
        ops = registry.search(module="format_utils")
        assert len(ops) >= 4  # fasta, gff, bed, clustal

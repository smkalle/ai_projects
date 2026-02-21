"""Tests for the bioinformatics API client wrappers.

These tests verify the client construction and parameter handling.
Tests that make real network calls are marked with @pytest.mark.network
and skipped by default (run with: pytest -m network).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bioinfo_code_mcp.apis.blast import BLASTClient
from bioinfo_code_mcp.apis.ensembl import EnsemblClient
from bioinfo_code_mcp.apis.ncbi import NCBIClient
from bioinfo_code_mcp.apis.pdb import PDBClient
from bioinfo_code_mcp.apis.uniprot import UniProtClient


class TestNCBIClient:
    """Test NCBI client construction and methods."""

    def test_init_default(self):
        client = NCBIClient(email="test@example.com")
        assert client.email == "test@example.com"
        assert client.api_key is None

    def test_init_with_api_key(self):
        client = NCBIClient(email="test@example.com", api_key="abc123")
        assert client.api_key == "abc123"

    def test_base_params(self):
        client = NCBIClient(email="test@example.com", api_key="key123")
        params = client._base_params()
        assert params["email"] == "test@example.com"
        assert params["api_key"] == "key123"
        assert params["retmode"] == "json"

    def test_base_params_no_api_key(self):
        client = NCBIClient(email="test@example.com")
        params = client._base_params()
        assert "api_key" not in params

    @pytest.mark.network
    @pytest.mark.asyncio
    async def test_einfo_all_databases(self):
        client = NCBIClient(email="test@example.com")
        result = await client.einfo()
        assert "einforesult" in result or "dblist" in str(result).lower()

    @pytest.mark.network
    @pytest.mark.asyncio
    async def test_esearch_pubmed(self):
        client = NCBIClient(email="test@example.com")
        result = await client.esearch("pubmed", "CRISPR", retmax=5)
        assert "idlist" in result
        assert result["count"] > 0


class TestUniProtClient:
    """Test UniProt client construction."""

    def test_init(self):
        client = UniProtClient(timeout=60)
        assert client._timeout == 60

    def test_default_timeout(self):
        client = UniProtClient()
        assert client._timeout == 30

    @pytest.mark.network
    @pytest.mark.asyncio
    async def test_search_protein(self):
        client = UniProtClient()
        results = await client.search_protein("TP53", max_results=1)
        assert len(results) > 0
        assert "primaryAccession" in results[0]


class TestPDBClient:
    """Test PDB client construction."""

    def test_init(self):
        client = PDBClient(timeout=45)
        assert client._timeout == 45

    def test_urls(self):
        client = PDBClient()
        assert "rcsb.org" in client.DATA_URL
        assert "rcsb.org" in client.SEARCH_URL

    @pytest.mark.network
    @pytest.mark.asyncio
    async def test_text_search(self):
        client = PDBClient()
        results = await client.text_search("hemoglobin", max_results=3)
        assert len(results) > 0


class TestEnsemblClient:
    """Test Ensembl client construction."""

    def test_init(self):
        client = EnsemblClient(timeout=30)
        assert client._timeout == 30

    def test_base_url(self):
        client = EnsemblClient()
        assert "ensembl.org" in client.BASE_URL

    @pytest.mark.network
    @pytest.mark.asyncio
    async def test_lookup_symbol(self):
        client = EnsemblClient()
        result = await client.lookup_symbol("homo_sapiens", "TP53", expand=False)
        assert "id" in result
        assert result["id"].startswith("ENSG")


class TestBLASTClient:
    """Test BLAST client construction."""

    def test_init(self):
        client = BLASTClient(timeout=30, poll_interval=10, max_polls=5)
        assert client._timeout == 30
        assert client._poll_interval == 10
        assert client._max_polls == 5

    def test_base_url(self):
        client = BLASTClient()
        assert "blast.ncbi.nlm.nih.gov" in client.BASE_URL

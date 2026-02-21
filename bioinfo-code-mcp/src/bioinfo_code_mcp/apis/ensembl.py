"""Ensembl REST API wrapper for the Code MCP sandbox.

Provides access to genomic data — genes, transcripts, variants, sequences,
and cross-references — via the Ensembl REST API.

Reference: https://rest.ensembl.org
"""

from __future__ import annotations

from typing import Any

import httpx


class EnsemblClient:
    """Async client for the Ensembl REST API."""

    BASE_URL = "https://rest.ensembl.org"

    def __init__(self, timeout: int = 30):
        self._timeout = timeout

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self._timeout,
            headers={"Content-Type": "application/json"},
        )

    # ------------------------------------------------------------------
    # Lookup endpoints
    # ------------------------------------------------------------------

    async def lookup_id(
        self, ensembl_id: str, expand: bool = True
    ) -> dict[str, Any]:
        """Look up an Ensembl ID and return its details.

        Args:
            ensembl_id: Ensembl stable ID (e.g. "ENSG00000141510" for TP53).
            expand: Include child objects (transcripts, translations, etc.).

        Returns:
            Dict with gene/transcript/protein details.
        """
        params: dict[str, str] = {}
        if expand:
            params["expand"] = "1"
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/lookup/id/{ensembl_id}",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()

    async def lookup_symbol(
        self, species: str, symbol: str, expand: bool = True
    ) -> dict[str, Any]:
        """Look up a gene by symbol and species.

        Args:
            species: Species name (e.g. "homo_sapiens", "mus_musculus").
            symbol: Gene symbol (e.g. "BRCA2").
            expand: Include child objects.

        Returns:
            Dict with gene details.
        """
        params: dict[str, str] = {}
        if expand:
            params["expand"] = "1"
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/lookup/symbol/{species}/{symbol}",
                params=params,
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Sequence endpoints
    # ------------------------------------------------------------------

    async def get_sequence(
        self,
        ensembl_id: str,
        seq_type: str = "genomic",
        format_: str = "json",
    ) -> dict[str, Any] | str:
        """Get the sequence for an Ensembl ID.

        Args:
            ensembl_id: Ensembl stable ID.
            seq_type: "genomic", "cdna", "cds", or "protein".
            format_: "json" or "fasta".

        Returns:
            Sequence data as dict (JSON) or FASTA string.
        """
        params = {"type": seq_type}
        headers = {"Content-Type": "application/json"}
        if format_ == "fasta":
            headers["Content-Type"] = "text/x-fasta"

        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/sequence/id/{ensembl_id}",
                params=params,
                headers=headers,
            )
            resp.raise_for_status()
            if format_ == "fasta":
                return resp.text
            return resp.json()

    async def get_sequence_region(
        self,
        species: str,
        region: str,
    ) -> dict[str, Any]:
        """Get the genomic sequence for a chromosomal region.

        Args:
            species: Species name (e.g. "human").
            region: Region string (e.g. "X:1000000:1000100:1").

        Returns:
            Dict with sequence and metadata.
        """
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/sequence/region/{species}/{region}",
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Variation endpoints
    # ------------------------------------------------------------------

    async def get_variant(self, variant_id: str, species: str = "human") -> dict[str, Any]:
        """Get details for a known variant.

        Args:
            variant_id: Variant identifier (e.g. "rs699").
            species: Species name.

        Returns:
            Dict with variant details (alleles, MAF, consequences, etc.).
        """
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/variation/{species}/{variant_id}",
            )
            resp.raise_for_status()
            return resp.json()

    async def get_vep(
        self,
        species: str,
        hgvs_notation: str,
    ) -> list[dict[str, Any]]:
        """Run Variant Effect Predictor (VEP) for an HGVS notation.

        Args:
            species: Species name.
            hgvs_notation: HGVS notation (e.g. "ENST00000269305.9:c.817C>T").

        Returns:
            List of predicted variant consequences.
        """
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/vep/{species}/hgvs/{hgvs_notation}",
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Cross-reference endpoints
    # ------------------------------------------------------------------

    async def get_xrefs(self, ensembl_id: str) -> list[dict[str, Any]]:
        """Get cross-references for an Ensembl ID.

        Args:
            ensembl_id: Ensembl stable ID.

        Returns:
            List of cross-reference dicts (dbname, primary_id, display_id).
        """
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/xrefs/id/{ensembl_id}",
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def get_gene_summary(
        self, symbol: str, species: str = "homo_sapiens"
    ) -> dict[str, Any]:
        """Get a compact gene summary by symbol.

        Args:
            symbol: Gene symbol.
            species: Species name.

        Returns:
            Dict with id, name, biotype, location, strand, description.
        """
        gene = await self.lookup_symbol(species, symbol, expand=False)
        return {
            "ensembl_id": gene.get("id", ""),
            "display_name": gene.get("display_name", ""),
            "biotype": gene.get("biotype", ""),
            "species": gene.get("species", ""),
            "chromosome": gene.get("seq_region_name", ""),
            "start": gene.get("start"),
            "end": gene.get("end"),
            "strand": gene.get("strand"),
            "description": gene.get("description", ""),
        }

"""UniProt API wrapper for the Code MCP sandbox.

Provides access to protein sequence, function, and annotation data via
the UniProt REST API (2024+ version).

Reference: https://www.uniprot.org/help/api
"""

from __future__ import annotations

from typing import Any

import httpx


class UniProtClient:
    """Async client for the UniProt REST API."""

    BASE_URL = "https://rest.uniprot.org"

    def __init__(self, timeout: int = 30):
        self._timeout = timeout

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self._timeout,
            headers={"Accept": "application/json"},
        )

    async def search(
        self,
        query: str,
        dataset: str = "uniprotkb",
        fields: list[str] | None = None,
        size: int = 25,
        format_: str = "json",
    ) -> dict[str, Any]:
        """Search UniProt with a query string.

        Args:
            query: UniProt query (e.g. "gene:TP53 AND organism_id:9606").
            dataset: Dataset to search ("uniprotkb", "uniref", "uniparc",
                     "proteomes", "taxonomy", "keywords", "citations", etc.).
            fields: Specific fields to return. None = all fields.
            size: Number of results to return.
            format_: Response format ("json", "tsv", "fasta", "xml").

        Returns:
            Parsed JSON response with 'results' list.
        """
        params: dict[str, str] = {
            "query": query,
            "size": str(size),
            "format": format_,
        }
        if fields:
            params["fields"] = ",".join(fields)

        async with self._client() as client:
            resp = await client.get(f"{self.BASE_URL}/{dataset}/search", params=params)
            resp.raise_for_status()
            if format_ == "json":
                return resp.json()
            return {"text": resp.text}

    async def fetch_entry(
        self,
        accession: str,
        dataset: str = "uniprotkb",
        format_: str = "json",
    ) -> dict[str, Any]:
        """Fetch a single UniProt entry by accession.

        Args:
            accession: UniProt accession (e.g. "P04637" for human p53).
            dataset: Dataset name.
            format_: Response format.

        Returns:
            Entry data as dict (JSON) or text.
        """
        headers = {"Accept": "application/json"} if format_ == "json" else {}
        async with self._client() as client:
            resp = await client.get(
                f"{self.BASE_URL}/{dataset}/{accession}",
                headers=headers,
            )
            resp.raise_for_status()
            if format_ == "json":
                return resp.json()
            return {"text": resp.text}

    async def fetch_fasta(self, accession: str) -> str:
        """Fetch protein sequence in FASTA format.

        Args:
            accession: UniProt accession.

        Returns:
            FASTA-formatted sequence string.
        """
        async with self._client() as client:
            resp = await client.get(f"{self.BASE_URL}/uniprotkb/{accession}.fasta")
            resp.raise_for_status()
            return resp.text

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def search_protein(
        self,
        gene: str,
        organism: str = "Homo sapiens",
        reviewed: bool = True,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for a protein by gene name and organism.

        Args:
            gene: Gene symbol (e.g. "BRCA1").
            organism: Scientific name or taxonomy ID.
            reviewed: If True, restrict to Swiss-Prot (reviewed) entries.
            max_results: Maximum results.

        Returns:
            List of result entries.
        """
        parts = [f"gene:{gene}", f'organism_name:"{organism}"']
        if reviewed:
            parts.append("reviewed:true")
        query = " AND ".join(parts)
        data = await self.search(query, size=max_results)
        return data.get("results", [])

    async def get_protein_features(self, accession: str) -> list[dict[str, Any]]:
        """Get annotated features (domains, variants, PTMs) for a protein.

        Args:
            accession: UniProt accession.

        Returns:
            List of feature dicts with type, location, description.
        """
        entry = await self.fetch_entry(accession)
        return entry.get("features", [])

    async def get_go_terms(self, accession: str) -> list[dict[str, Any]]:
        """Get Gene Ontology annotations for a protein.

        Args:
            accession: UniProt accession.

        Returns:
            List of GO annotation dicts.
        """
        entry = await self.fetch_entry(accession)
        xrefs = entry.get("uniProtKBCrossReferences", [])
        return [x for x in xrefs if x.get("database") == "GO"]

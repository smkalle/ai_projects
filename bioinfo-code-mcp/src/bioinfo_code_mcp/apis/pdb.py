"""RCSB Protein Data Bank (PDB) API wrapper for the Code MCP sandbox.

Provides access to macromolecular structure data via the RCSB PDB
REST and Search APIs.

Reference: https://data.rcsb.org/redoc/index.html
"""

from __future__ import annotations

from typing import Any

import httpx


class PDBClient:
    """Async client for the RCSB PDB REST API."""

    DATA_URL = "https://data.rcsb.org/rest/v1"
    SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"

    def __init__(self, timeout: int = 30):
        self._timeout = timeout

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._timeout)

    async def get_entry(self, pdb_id: str) -> dict[str, Any]:
        """Get basic entry information for a PDB structure.

        Args:
            pdb_id: 4-character PDB ID (e.g. "1TUP").

        Returns:
            Dict with entry metadata (title, authors, resolution, etc.).
        """
        async with self._client() as client:
            resp = await client.get(f"{self.DATA_URL}/core/entry/{pdb_id}")
            resp.raise_for_status()
            return resp.json()

    async def get_entity(self, pdb_id: str, entity_id: int = 1) -> dict[str, Any]:
        """Get polymer entity info (sequence, source organism, etc.).

        Args:
            pdb_id: PDB ID.
            entity_id: Entity number within the entry (usually 1).

        Returns:
            Dict with entity-level data.
        """
        async with self._client() as client:
            resp = await client.get(
                f"{self.DATA_URL}/core/polymer_entity/{pdb_id}/{entity_id}"
            )
            resp.raise_for_status()
            return resp.json()

    async def get_assembly(self, pdb_id: str, assembly_id: int = 1) -> dict[str, Any]:
        """Get biological assembly information.

        Args:
            pdb_id: PDB ID.
            assembly_id: Assembly number (usually 1).

        Returns:
            Dict with assembly data.
        """
        async with self._client() as client:
            resp = await client.get(
                f"{self.DATA_URL}/core/assembly/{pdb_id}/{assembly_id}"
            )
            resp.raise_for_status()
            return resp.json()

    async def search(
        self,
        query: dict[str, Any],
        return_type: str = "entry",
        rows: int = 25,
    ) -> dict[str, Any]:
        """Run an RCSB search query.

        Args:
            query: RCSB Search API query dict. Example::

                {
                    "type": "terminal",
                    "service": "full_text",
                    "parameters": {"value": "CRISPR"}
                }

            return_type: "entry", "polymer_entity", "assembly", etc.
            rows: Number of results.

        Returns:
            Dict with 'result_set' list of IDs and scores.
        """
        payload = {
            "query": query,
            "return_type": return_type,
            "request_options": {"rows": rows},
        }
        async with self._client() as client:
            resp = await client.post(
                self.SEARCH_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def text_search(self, text: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Full-text search for PDB structures.

        Args:
            text: Search text (e.g. "CRISPR-Cas9", "hemoglobin").
            max_results: Maximum number of results.

        Returns:
            List of result dicts with 'identifier' and 'score'.
        """
        query = {
            "type": "terminal",
            "service": "full_text",
            "parameters": {"value": text},
        }
        result = await self.search(query, rows=max_results)
        return result.get("result_set", [])

    async def search_by_uniprot(self, uniprot_id: str) -> list[dict[str, Any]]:
        """Find PDB structures associated with a UniProt accession.

        Args:
            uniprot_id: UniProt accession (e.g. "P04637").

        Returns:
            List of matching PDB entries.
        """
        query = {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_polymer_entity_container_identifiers"
                ".reference_sequence_identifiers.database_accession",
                "operator": "exact_match",
                "value": uniprot_id,
            },
        }
        result = await self.search(query, return_type="entry")
        return result.get("result_set", [])

    async def get_structure_summary(self, pdb_id: str) -> dict[str, Any]:
        """Get a concise summary of a PDB structure.

        Args:
            pdb_id: PDB ID.

        Returns:
            Dict with title, resolution, method, organism, release date.
        """
        entry = await self.get_entry(pdb_id)
        struct = entry.get("rcsb_entry_info", {})
        citation = entry.get("rcsb_primary_citation", {})
        return {
            "pdb_id": pdb_id,
            "title": entry.get("struct", {}).get("title", ""),
            "resolution": struct.get("resolution_combined", [None])[0]
            if struct.get("resolution_combined")
            else None,
            "experimental_method": struct.get("experimental_method", ""),
            "deposition_date": entry.get("rcsb_accession_info", {}).get(
                "deposit_date", ""
            ),
            "release_date": entry.get("rcsb_accession_info", {}).get(
                "initial_release_date", ""
            ),
            "citation_title": citation.get("title", ""),
            "citation_journal": citation.get("rcsb_journal_abbrev", ""),
        }

"""NCBI Entrez API wrapper for the Code MCP sandbox.

Provides programmatic access to NCBI databases (PubMed, GenBank, Gene,
Protein, Nucleotide, etc.) via the Entrez E-utilities REST API.

Reference: https://www.ncbi.nlm.nih.gov/books/NBK25501/
"""

from __future__ import annotations

from typing import Any

import httpx


class NCBIClient:
    """Thin async client for NCBI Entrez E-utilities.

    All methods return parsed Python dicts/lists so agents can process
    results directly in generated code.
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, email: str, api_key: str | None = None, timeout: int = 30):
        self.email = email
        self.api_key = api_key
        self._timeout = timeout

    def _base_params(self) -> dict[str, str]:
        params: dict[str, str] = {"email": self.email, "retmode": "json"}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._timeout)

    # ------------------------------------------------------------------
    # E-utilities endpoints
    # ------------------------------------------------------------------

    async def esearch(
        self,
        db: str,
        term: str,
        retmax: int = 20,
        sort: str = "relevance",
    ) -> dict[str, Any]:
        """Search an NCBI database and return matching IDs.

        Args:
            db: Database name (e.g. "pubmed", "gene", "nucleotide", "protein").
            term: Search query using Entrez query syntax.
            retmax: Maximum number of IDs to return.
            sort: Sort order ("relevance", "pub_date", etc.).

        Returns:
            Dict with 'idlist', 'count', 'retmax', 'querytranslation'.
        """
        params = {
            **self._base_params(),
            "db": db,
            "term": term,
            "retmax": str(retmax),
            "sort": sort,
        }
        async with self._client() as client:
            resp = await client.get(f"{self.BASE_URL}/esearch.fcgi", params=params)
            resp.raise_for_status()
            data = resp.json()
        result = data.get("esearchresult", {})
        return {
            "idlist": result.get("idlist", []),
            "count": int(result.get("count", 0)),
            "retmax": int(result.get("retmax", 0)),
            "querytranslation": result.get("querytranslation", ""),
        }

    async def efetch(
        self,
        db: str,
        ids: list[str],
        rettype: str = "abstract",
        retmode: str = "xml",
    ) -> str:
        """Fetch full records from an NCBI database.

        Args:
            db: Database name.
            ids: List of database IDs.
            rettype: Return type ("abstract", "fasta", "gb", "gp", etc.).
            retmode: Return format ("xml", "text", "json").

        Returns:
            Raw response text (XML, FASTA, GenBank, etc.).
        """
        params = {
            **self._base_params(),
            "db": db,
            "id": ",".join(ids),
            "rettype": rettype,
            "retmode": retmode,
        }
        async with self._client() as client:
            resp = await client.get(f"{self.BASE_URL}/efetch.fcgi", params=params)
            resp.raise_for_status()
            return resp.text

    async def esummary(self, db: str, ids: list[str]) -> list[dict[str, Any]]:
        """Get document summaries for a list of IDs.

        Args:
            db: Database name.
            ids: List of database IDs.

        Returns:
            List of summary dicts with fields like 'title', 'uid', etc.
        """
        params = {
            **self._base_params(),
            "db": db,
            "id": ",".join(ids),
        }
        async with self._client() as client:
            resp = await client.get(f"{self.BASE_URL}/esummary.fcgi", params=params)
            resp.raise_for_status()
            data = resp.json()
        result = data.get("result", {})
        uids = result.get("uids", [])
        return [result[uid] for uid in uids if uid in result]

    async def einfo(self, db: str | None = None) -> dict[str, Any]:
        """Get information about NCBI databases or a specific database.

        Args:
            db: Optional database name. If None, lists all databases.

        Returns:
            Dict with database info (field list, link list, etc.).
        """
        params = self._base_params()
        if db:
            params["db"] = db
        async with self._client() as client:
            resp = await client.get(f"{self.BASE_URL}/einfo.fcgi", params=params)
            resp.raise_for_status()
            return resp.json()

    async def elink(
        self,
        dbfrom: str,
        db: str,
        ids: list[str],
        linkname: str | None = None,
    ) -> dict[str, Any]:
        """Find related records across NCBI databases.

        Args:
            dbfrom: Source database.
            db: Target database.
            ids: List of source IDs.
            linkname: Optional specific link name.

        Returns:
            Dict with linked ID sets.
        """
        params = {
            **self._base_params(),
            "dbfrom": dbfrom,
            "db": db,
            "id": ",".join(ids),
        }
        if linkname:
            params["linkname"] = linkname
        async with self._client() as client:
            resp = await client.get(f"{self.BASE_URL}/elink.fcgi", params=params)
            resp.raise_for_status()
            return resp.json()

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def search_pubmed(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search PubMed and return article summaries.

        Args:
            query: PubMed search query.
            max_results: Maximum articles to return.

        Returns:
            List of article summary dicts.
        """
        search = await self.esearch("pubmed", query, retmax=max_results)
        if not search["idlist"]:
            return []
        return await self.esummary("pubmed", search["idlist"])

    async def fetch_gene_info(self, gene_symbol: str, organism: str = "human") -> list[dict]:
        """Look up a gene by symbol and return summaries.

        Args:
            gene_symbol: Gene symbol (e.g. "BRCA1", "TP53").
            organism: Organism name for filtering.

        Returns:
            List of gene summary dicts.
        """
        term = f"{gene_symbol}[Gene Name] AND {organism}[Organism]"
        search = await self.esearch("gene", term, retmax=5)
        if not search["idlist"]:
            return []
        return await self.esummary("gene", search["idlist"])

    async def fetch_sequence(
        self, db: str, seq_id: str, rettype: str = "fasta"
    ) -> str:
        """Fetch a sequence in FASTA or GenBank format.

        Args:
            db: Database ("nucleotide" or "protein").
            seq_id: Accession or GI number.
            rettype: "fasta" or "gb" / "gp".

        Returns:
            Sequence data as text.
        """
        return await self.efetch(db, [seq_id], rettype=rettype, retmode="text")

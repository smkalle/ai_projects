"""NCBI BLAST API wrapper for the Code MCP sandbox.

Provides programmatic access to NCBI BLAST sequence similarity search
via the BLAST URL API (for short queries) and the QBlast endpoint.

Reference: https://blast.ncbi.nlm.nih.gov/doc/blast-help/developerinfo.html
"""

from __future__ import annotations

import asyncio
import re
from typing import Any

import httpx


class BLASTClient:
    """Async client for the NCBI BLAST API.

    BLAST jobs are submitted and polled asynchronously. Results are returned
    as parsed dicts when possible, or raw text for formats like plain-text
    alignment output.
    """

    BASE_URL = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi"

    def __init__(self, timeout: int = 30, poll_interval: int = 15, max_polls: int = 40):
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._max_polls = max_polls

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._timeout)

    async def submit(
        self,
        program: str,
        database: str,
        sequence: str,
        *,
        megablast: bool = False,
        expect: float = 10.0,
        hitlist_size: int = 50,
        extra_params: dict[str, str] | None = None,
    ) -> str:
        """Submit a BLAST search and return the Request ID (RID).

        Args:
            program: BLAST program ("blastn", "blastp", "blastx", "tblastn", "tblastx").
            database: Target database ("nt", "nr", "swissprot", "pdb", "refseq_rna", etc.).
            sequence: Query sequence (FASTA or raw).
            megablast: Use Megablast (for blastn, faster for highly similar seqs).
            expect: E-value threshold.
            hitlist_size: Maximum number of hits.
            extra_params: Additional BLAST parameters.

        Returns:
            Request ID (RID) string for polling.
        """
        params: dict[str, str] = {
            "CMD": "Put",
            "PROGRAM": program,
            "DATABASE": database,
            "QUERY": sequence,
            "EXPECT": str(expect),
            "HITLIST_SIZE": str(hitlist_size),
        }
        if megablast:
            params["MEGABLAST"] = "on"
        if extra_params:
            params.update(extra_params)

        async with self._client() as client:
            resp = await client.post(self.BASE_URL, data=params)
            resp.raise_for_status()

        # Parse RID from response
        rid_match = re.search(r"RID = (\S+)", resp.text)
        if not rid_match:
            raise RuntimeError(f"Could not parse RID from BLAST response: {resp.text[:500]}")
        return rid_match.group(1)

    async def poll_status(self, rid: str) -> str:
        """Check the status of a BLAST job.

        Args:
            rid: Request ID from submit().

        Returns:
            Status string: "WAITING", "READY", "FAILED", or "UNKNOWN".
        """
        params = {"CMD": "Get", "RID": rid, "FORMAT_TYPE": "XML"}
        async with self._client() as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()

        if "Status=WAITING" in resp.text:
            return "WAITING"
        if "Status=FAILED" in resp.text:
            return "FAILED"
        if "Status=UNKNOWN" in resp.text:
            return "UNKNOWN"
        return "READY"

    async def get_results(
        self,
        rid: str,
        format_type: str = "JSON2",
    ) -> dict[str, Any] | str:
        """Retrieve results for a completed BLAST job.

        Args:
            rid: Request ID.
            format_type: "JSON2" for structured results, "Text" for alignment text,
                        "XML2" for XML.

        Returns:
            Parsed JSON dict or raw text depending on format.
        """
        params = {
            "CMD": "Get",
            "RID": rid,
            "FORMAT_TYPE": format_type,
        }
        async with self._client() as client:
            resp = await client.get(self.BASE_URL, params=params)
            resp.raise_for_status()

        if format_type in ("JSON2", "JSON2_S"):
            return resp.json()
        return resp.text

    async def wait_for_results(
        self,
        rid: str,
        format_type: str = "JSON2",
    ) -> dict[str, Any] | str:
        """Poll a BLAST job until complete and return results.

        Args:
            rid: Request ID from submit().
            format_type: Desired output format.

        Returns:
            BLAST results.

        Raises:
            TimeoutError: If job doesn't complete within max_polls.
            RuntimeError: If job fails.
        """
        for _ in range(self._max_polls):
            status = await self.poll_status(rid)
            if status == "READY":
                return await self.get_results(rid, format_type)
            if status == "FAILED":
                raise RuntimeError(f"BLAST job {rid} failed")
            if status == "UNKNOWN":
                raise RuntimeError(f"BLAST job {rid} not found")
            await asyncio.sleep(self._poll_interval)

        raise TimeoutError(
            f"BLAST job {rid} did not complete within "
            f"{self._max_polls * self._poll_interval}s"
        )

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def blastn(
        self,
        sequence: str,
        database: str = "nt",
        max_hits: int = 10,
        wait: bool = True,
    ) -> dict[str, Any] | str:
        """Run a nucleotide BLAST search.

        Args:
            sequence: Nucleotide sequence (FASTA or raw).
            database: Target database.
            max_hits: Maximum hit count.
            wait: If True, block until results are ready.

        Returns:
            BLAST results (if wait=True) or RID string (if wait=False).
        """
        rid = await self.submit("blastn", database, sequence, hitlist_size=max_hits)
        if wait:
            return await self.wait_for_results(rid)
        return rid

    async def blastp(
        self,
        sequence: str,
        database: str = "nr",
        max_hits: int = 10,
        wait: bool = True,
    ) -> dict[str, Any] | str:
        """Run a protein BLAST search.

        Args:
            sequence: Protein sequence (FASTA or raw).
            database: Target database ("nr", "swissprot", "pdb").
            max_hits: Maximum hit count.
            wait: If True, block until results are ready.

        Returns:
            BLAST results (if wait=True) or RID string (if wait=False).
        """
        rid = await self.submit("blastp", database, sequence, hitlist_size=max_hits)
        if wait:
            return await self.wait_for_results(rid)
        return rid

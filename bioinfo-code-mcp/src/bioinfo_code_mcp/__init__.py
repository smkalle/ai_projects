"""Bioinformatics Code Mode MCP Server.

A Code Mode MCP server for bioinformatics research. Instead of exposing
hundreds of individual tools for each bioinformatics database and operation,
this server exposes just two tools — `search` and `execute` — enabling AI
agents to dynamically discover and run Python code against bioinformatics
APIs (NCBI Entrez, UniProt, PDB, Ensembl, BLAST).

Inspired by Cloudflare's Code Mode MCP and Armin Ronacher's Code MCPs concept.
"""

__version__ = "0.1.0"

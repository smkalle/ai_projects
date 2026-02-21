"""Bioinformatics Code Mode MCP Server.

This server implements the Code Mode MCP pattern (inspired by Cloudflare's
Code Mode and Armin Ronacher's Code MCPs) for bioinformatics. Instead of
hundreds of individual tools for each database endpoint, it exposes just
TWO tools:

    1. `search` — Discover available bioinformatics operations, databases,
       and helpers. Agents query with keywords to find what they need.

    2. `execute` — Run Python code in a sandboxed, stateful environment
       with pre-loaded API clients (NCBI, UniProt, PDB, Ensembl, BLAST)
       and utility functions (sequence manipulation, format parsing).

This keeps the context window at ~1,000 tokens (vs. millions for
traditional per-endpoint MCP), while supporting dynamic discovery,
multi-step workflows, and session state persistence.

Usage:
    # Start via CLI
    bioinfo-mcp

    # Or via Python
    python -m bioinfo_code_mcp.server

    # Configure with environment variables
    NCBI_EMAIL=you@example.com NCBI_API_KEY=xyz bioinfo-mcp
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from .config import load_config
from .registry import Registry
from .sandbox import Sandbox

logger = logging.getLogger("bioinfo-code-mcp")


def create_server():
    """Create and configure the MCP server with search and execute tools."""
    # Import MCP SDK — handle both installed and missing cases
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
    except ImportError:
        logger.error(
            "MCP SDK not installed. Install with: pip install 'bioinfo-code-mcp[dev]' or pip install mcp"
        )
        sys.exit(1)

    config = load_config()
    registry = Registry()
    sandbox = Sandbox(config)

    server = Server("bioinfo-code-mcp")

    # ------------------------------------------------------------------
    # Tool: search
    # ------------------------------------------------------------------

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        context_desc = sandbox.get_context_description()
        return [
            Tool(
                name="search",
                description=(
                    "Search the bioinformatics operations catalog to discover "
                    "available API methods, databases, and utility functions. "
                    "Use this before writing code to find the right operations.\n\n"
                    "Supports free-text queries (e.g., 'protein structure'), "
                    "tag filters (e.g., ['ncbi', 'sequence']), and module filters "
                    "(e.g., 'uniprot'). Returns operation signatures, descriptions, "
                    "parameters, and usage examples."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Free-text search query. Examples: "
                                "'BLAST protein search', 'gene lookup', "
                                "'parse FASTA', 'restriction enzyme'"
                            ),
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Filter by tags. Available: ncbi, uniprot, pdb, "
                                "ensembl, blast, sequence, protein, gene, variant, "
                                "structure, format, utility, search, fasta, etc."
                            ),
                        },
                        "module": {
                            "type": "string",
                            "description": (
                                "Filter by module: ncbi, uniprot, pdb, ensembl, "
                                "blast, sequence_utils, format_utils"
                            ),
                        },
                        "list_modules": {
                            "type": "boolean",
                            "description": "Set true to list all available modules and operation counts",
                        },
                    },
                },
            ),
            Tool(
                name="execute",
                description=(
                    "Execute Python code in a sandboxed bioinformatics environment. "
                    "The code runs async — use `await` for all API calls. "
                    "Return a value to send it back as the result. "
                    "Use `state` dict to persist data between calls.\n\n"
                    + context_desc
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": (
                                "Python code to execute. Async — use `await` for API calls. "
                                "Example:\n"
                                "  genes = await ncbi.fetch_gene_info('TP53')\n"
                                "  state['genes'] = genes\n"
                                "  return genes"
                            ),
                        },
                        "reset_state": {
                            "type": "boolean",
                            "description": "Set true to clear persistent state before execution",
                        },
                    },
                    "required": ["code"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name == "search":
            return await _handle_search(arguments, registry)
        elif name == "execute":
            return await _handle_execute(arguments, sandbox)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def _handle_search(
        args: dict[str, Any], reg: Registry
    ) -> list["TextContent"]:
        if args.get("list_modules"):
            modules = reg.list_modules()
            tags = reg.list_tags()
            result = {
                "modules": modules,
                "available_tags": tags,
                "total_operations": sum(m["operation_count"] for m in modules),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        results = reg.search(
            query=args.get("query", ""),
            tags=args.get("tags"),
            module=args.get("module"),
        )

        if not results:
            return [TextContent(
                type="text",
                text="No operations found. Try broader search terms, or use list_modules=true to see available modules.",
            )]

        # Format results compactly for the agent
        formatted_lines: list[str] = [f"Found {len(results)} operation(s):\n"]
        for op in results:
            formatted_lines.append(f"### {op['name']}")
            formatted_lines.append(f"  {op['description']}")
            formatted_lines.append(f"  Method: `{op['method']}`")
            if op.get("params"):
                param_strs = []
                for p in op["params"]:
                    req = "" if p["required"] else f" (optional, default={p['default']})"
                    param_strs.append(f"    - {p['name']}: {p['type']} — {p['description']}{req}")
                formatted_lines.append("  Params:\n" + "\n".join(param_strs))
            if op.get("example"):
                formatted_lines.append(f"  Example: `{op['example']}`")
            formatted_lines.append("")

        return [TextContent(type="text", text="\n".join(formatted_lines))]

    async def _handle_execute(
        args: dict[str, Any], sb: Sandbox
    ) -> list["TextContent"]:
        code = args.get("code", "")
        if not code.strip():
            return [TextContent(type="text", text="Error: No code provided")]

        if args.get("reset_state"):
            sb.reset_state()

        result = await sb.execute(code)
        return [TextContent(type="text", text=result.to_text())]

    return server, config


async def run_server():
    """Run the MCP server with stdio transport."""
    from mcp.server.stdio import stdio_server

    server, config = create_server()

    logger.info("Starting bioinfo-code-mcp server (transport=%s)", config.transport)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """CLI entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,  # MCP uses stdout for protocol
    )
    asyncio.run(run_server())


if __name__ == "__main__":
    main()

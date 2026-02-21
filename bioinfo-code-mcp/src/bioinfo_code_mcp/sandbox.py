"""Sandboxed Python execution environment for the Code MCP server.

This is the heart of the Code Mode MCP pattern — a single `execute` tool
that runs agent-generated Python code in a controlled environment with
pre-loaded bioinformatics API clients and utilities.

Design principles (from Cloudflare Code Mode & Ronacher's Code MCPs):
- Stateful: `state` dict persists across executions within a session
- Pre-loaded: API clients and helpers are available without imports
- Sandboxed: Restricted builtins prevent file/network/OS access outside APIs
- Async-native: All API calls use async/await
"""

from __future__ import annotations

import asyncio
import io
import json
import traceback
from contextlib import redirect_stdout
from typing import Any

from .apis.blast import BLASTClient
from .apis.ensembl import EnsemblClient
from .apis.ncbi import NCBIClient
from .apis.pdb import PDBClient
from .apis.uniprot import UniProtClient
from .config import ServerConfig
from .utils import formats as fmt_module
from .utils import sequence as seq_module


# Restricted builtins — allow standard computation, block dangerous ops
_SAFE_BUILTINS: dict[str, Any] = {
    # Types and constructors
    "True": True,
    "False": False,
    "None": None,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "frozenset": frozenset,
    "bytes": bytes,
    "bytearray": bytearray,
    "complex": complex,
    "type": type,
    # Numeric and math
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "divmod": divmod,
    # Iterators and sequences
    "range": range,
    "len": len,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "sorted": sorted,
    "reversed": reversed,
    "any": any,
    "all": all,
    "next": next,
    "iter": iter,
    "slice": slice,
    # String and formatting
    "repr": repr,
    "format": format,
    "chr": chr,
    "ord": ord,
    "hex": hex,
    "oct": oct,
    "bin": bin,
    # Object introspection
    "isinstance": isinstance,
    "issubclass": issubclass,
    "hasattr": hasattr,
    "getattr": getattr,
    "setattr": setattr,
    "callable": callable,
    "id": id,
    "hash": hash,
    "dir": dir,
    "vars": vars,
    # I/O (print only — captured)
    "print": print,
    # Exceptions
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "RuntimeError": RuntimeError,
    "StopIteration": StopIteration,
    "AttributeError": AttributeError,
    # JSON
    "json": json,
}


class ExecutionResult:
    """Container for sandbox execution results."""

    def __init__(
        self,
        success: bool,
        result: Any = None,
        stdout: str = "",
        error: str = "",
        state_keys: list[str] | None = None,
    ):
        self.success = success
        self.result = result
        self.stdout = stdout
        self.error = error
        self.state_keys = state_keys or []

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {"success": self.success}

        if self.result is not None:
            try:
                # Try JSON serialization
                json.dumps(self.result)
                output["result"] = self.result
            except (TypeError, ValueError):
                output["result"] = repr(self.result)

        if self.stdout:
            output["stdout"] = self.stdout
        if self.error:
            output["error"] = self.error
        if self.state_keys:
            output["state_keys"] = self.state_keys

        return output

    def to_text(self) -> str:
        """Format result as human-readable text for MCP response."""
        parts: list[str] = []

        if self.success:
            if self.result is not None:
                try:
                    parts.append(json.dumps(self.result, indent=2, default=str))
                except (TypeError, ValueError):
                    parts.append(repr(self.result))
            if self.stdout:
                parts.append(f"[stdout]\n{self.stdout}")
            if self.state_keys:
                parts.append(f"[state keys: {', '.join(self.state_keys)}]")
        else:
            parts.append(f"[error] {self.error}")
            if self.stdout:
                parts.append(f"[stdout]\n{self.stdout}")

        return "\n".join(parts) if parts else "[no output]"


class Sandbox:
    """Stateful, sandboxed Python execution environment.

    The sandbox maintains persistent state across executions, mirroring
    Ronacher's stateful Code MCP pattern. API clients are pre-instantiated
    and available as globals in the execution scope.

    Usage in agent-generated code::

        # These are all available as globals:
        result = await ncbi.search_pubmed("CRISPR therapy")
        state["last_search"] = result
        protein = await uniprot.fetch_entry("P04637")
        gc = seq_utils.gc_content("ATGCGATCGATCG")
        records = fmt.parse_fasta(fasta_text)
    """

    def __init__(self, config: ServerConfig):
        self.config = config
        self.state: dict[str, Any] = {}

        # Pre-instantiate API clients
        self.ncbi = NCBIClient(
            email=config.ncbi_email,
            api_key=config.ncbi_api_key,
            timeout=config.http_timeout_seconds,
        )
        self.uniprot = UniProtClient(timeout=config.http_timeout_seconds)
        self.pdb = PDBClient(timeout=config.http_timeout_seconds)
        self.ensembl = EnsemblClient(timeout=config.http_timeout_seconds)
        self.blast = BLASTClient(timeout=config.http_timeout_seconds)

    def reset_state(self) -> None:
        """Clear all persistent state."""
        self.state.clear()

    def _build_globals(self) -> dict[str, Any]:
        """Build the execution namespace with API clients, utils, and builtins."""
        return {
            "__builtins__": _SAFE_BUILTINS,
            # API clients — agents call these with await
            "ncbi": self.ncbi,
            "uniprot": self.uniprot,
            "pdb": self.pdb,
            "ensembl": self.ensembl,
            "blast": self.blast,
            # Utilities — synchronous helpers
            "seq_utils": seq_module,
            "fmt": fmt_module,
            # Persistent state dict
            "state": self.state,
            # Async support
            "asyncio": asyncio,
        }

    async def execute(self, code: str) -> ExecutionResult:
        """Execute Python code in the sandboxed environment.

        The code is wrapped in an async function so agents can use `await`
        for API calls. The last expression or explicit `return` value becomes
        the result.

        Args:
            code: Python source code (async-compatible).

        Returns:
            ExecutionResult with success status, result, stdout, and errors.
        """
        # Wrap code in an async function for await support
        indented = "\n".join(f"    {line}" for line in code.splitlines())
        wrapped = f"async def __sandbox_main__():\n{indented}"

        exec_globals = self._build_globals()
        stdout_capture = io.StringIO()

        try:
            # Compile the wrapped code
            compiled = compile(wrapped, "<sandbox>", "exec")

            # Execute to define the function
            exec(compiled, exec_globals)  # noqa: S102

            # Run the async function with stdout capture and timeout
            async_fn = exec_globals["__sandbox_main__"]
            with redirect_stdout(stdout_capture):
                result = await asyncio.wait_for(
                    async_fn(),
                    timeout=self.config.execution_timeout_seconds,
                )

            stdout_text = stdout_capture.getvalue()
            if self.config.max_output_chars and len(stdout_text) > self.config.max_output_chars:
                stdout_text = stdout_text[: self.config.max_output_chars] + "\n[truncated]"

            return ExecutionResult(
                success=True,
                result=result,
                stdout=stdout_text,
                state_keys=list(self.state.keys()),
            )

        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                error=f"Execution timed out after {self.config.execution_timeout_seconds}s",
                state_keys=list(self.state.keys()),
            )
        except SyntaxError as e:
            return ExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                error=f"SyntaxError: {e.msg} (line {e.lineno})",
            )
        except Exception as e:
            tb = traceback.format_exc()
            # Clean up sandbox wrapper from traceback
            tb_lines = tb.splitlines()
            clean_lines = [
                line for line in tb_lines
                if "<sandbox>" not in line or "in __sandbox_main__" in line
            ]
            return ExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                error=f"{type(e).__name__}: {e}\n{''.join(clean_lines[-3:])}",
                state_keys=list(self.state.keys()),
            )

    def get_context_description(self) -> str:
        """Return a description of what's available in the sandbox.

        This is included in the MCP tool description so agents know
        what they can use in their generated code.
        """
        return """Available in the execution environment:

## API Clients (async — use `await`)
- `ncbi` — NCBI Entrez (PubMed, Gene, Nucleotide, Protein)
- `uniprot` — UniProt (protein sequences, features, GO terms)
- `pdb` — RCSB PDB (protein structures, search)
- `ensembl` — Ensembl (genes, sequences, variants, VEP)
- `blast` — NCBI BLAST (sequence similarity search)

## Utilities (synchronous)
- `seq_utils` — reverse_complement, translate, gc_content, find_orfs, restriction_sites, molecular_weight
- `fmt` — parse_fasta, write_fasta, parse_gff, parse_bed, parse_clustal

## State
- `state` — persistent dict across executions (e.g., state["last_result"] = ...)

## Standard
- `json` — JSON serialization
- `print()` — output captured in stdout
- Standard Python builtins (math, string ops, list comprehensions, etc.)

## Notes
- All API calls are async: use `await ncbi.search_pubmed("query")`
- Return a value to send it back as the result
- Use `state` to persist data between executions
- Use `print()` for intermediate output"""

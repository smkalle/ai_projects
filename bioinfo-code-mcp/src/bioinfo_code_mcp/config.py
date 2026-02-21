"""Configuration management for the bioinformatics Code MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    """Configuration for the MCP server and its API clients."""

    # NCBI Entrez — required for most bioinformatics queries
    ncbi_email: str = field(
        default_factory=lambda: os.environ.get("NCBI_EMAIL", "user@example.com")
    )
    ncbi_api_key: str | None = field(
        default_factory=lambda: os.environ.get("NCBI_API_KEY")
    )

    # Execution sandbox settings
    execution_timeout_seconds: int = int(os.environ.get("EXEC_TIMEOUT", "30"))
    max_output_chars: int = int(os.environ.get("MAX_OUTPUT_CHARS", "50000"))

    # HTTP client defaults
    http_timeout_seconds: int = int(os.environ.get("HTTP_TIMEOUT", "30"))
    http_max_retries: int = int(os.environ.get("HTTP_MAX_RETRIES", "3"))

    # Server transport
    transport: str = os.environ.get("MCP_TRANSPORT", "stdio")
    host: str = os.environ.get("MCP_HOST", "127.0.0.1")
    port: int = int(os.environ.get("MCP_PORT", "8765"))


def load_config() -> ServerConfig:
    """Load configuration from environment variables."""
    return ServerConfig()

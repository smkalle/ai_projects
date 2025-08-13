"""Configuration management for MCP agents."""

import os
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

@dataclass
class AgentConfig:
    model: str
    provider: LLMProvider
    api_key: Optional[str] = None
    mcp_servers: Optional[List[str]] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: Optional[str] = None

def load_config_from_env() -> AgentConfig:
    """Load configuration from environment variables."""
    return AgentConfig(
        model=os.getenv("DEFAULT_MODEL", "gpt-4o"),
        provider=LLMProvider(os.getenv("DEFAULT_PROVIDER", "openai")),
        api_key=os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
        mcp_servers=os.getenv("MCP_SERVERS", "web-browser").split(","),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MAX_TOKENS", "2000"))
    )

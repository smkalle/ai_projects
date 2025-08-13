"""API routes for MCP agent management."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..mcp_agent.models import AgentConfig, ChatRequest, ChatResponse

router = APIRouter()

# Agent storage (in production, use a database)
agents = {}

@router.get("/agents/", response_model=List[str])
async def list_agents():
    """List all active agents."""
    return list(agents.keys())

@router.post("/agents/create")
async def create_agent(config: AgentConfig):
    """Create a new agent."""
    # Implementation would go here
    pass

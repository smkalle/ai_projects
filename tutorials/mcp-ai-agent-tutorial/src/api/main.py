"""
FastAPI Application for MCP AI Agent Tutorial
Provides REST API endpoints for interacting with MCP-enabled AI agents.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from mcp_agent.core import MCPAgent, AgentConfig, LLMProvider
from mcp_agent.models import (
    ChatRequest, 
    ChatResponse, 
    AgentStatus,
    ToolRequest,
    ToolResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent store
agents: Dict[str, MCPAgent] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting MCP AI Agent API...")
    # Initialization code here
    yield
    # Cleanup code here
    logger.info("Shutting down MCP AI Agent API...")


app = FastAPI(
    title="MCP AI Agent API",
    description="REST API for MCP-enabled AI agents with tool access",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "MCP AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "agents_count": len(agents)
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": len(agents)}


@app.post("/agents/create", response_model=Dict[str, Any])
async def create_agent(config: AgentConfig):
    """Create a new MCP agent."""
    try:
        agent_id = f"agent_{len(agents) + 1}"
        agent = MCPAgent(config)
        agents[agent_id] = agent

        logger.info(f"Created agent {agent_id} with {config.provider}")

        return {
            "agent_id": agent_id,
            "status": "created",
            "config": {
                "model": config.model,
                "provider": config.provider,
                "mcp_servers": config.mcp_servers
            }
        }
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/agents", response_model=List[str])
async def list_agents():
    """List all active agents."""
    return list(agents.keys())


@app.get("/agents/{agent_id}/status", response_model=AgentStatus)
async def get_agent_status(agent_id: str):
    """Get agent status and information."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents[agent_id]
    return AgentStatus(
        agent_id=agent_id,
        model=agent.config.model,
        provider=agent.config.provider.value,
        mcp_servers=agent.config.mcp_servers or [],
        conversation_length=len(agent.get_history())
    )


@app.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """Send a message to an agent and get a response."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents[agent_id]

    try:
        response = await agent.run(request.message, stream=False)
        return ChatResponse(
            agent_id=agent_id,
            message=request.message,
            response=response,
            timestamp=None  # Will be set by Pydantic
        )
    except Exception as e:
        logger.error(f"Error in chat with agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/{agent_id}/chat/stream")
async def stream_chat_with_agent(agent_id: str, request: ChatRequest):
    """Stream a conversation with an agent."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents[agent_id]

    async def generate_stream():
        try:
            stream = await agent.run(request.message, stream=True)
            async for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield f"data: {delta.content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield f"data: ERROR: {str(e)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.post("/agents/{agent_id}/tools", response_model=ToolResponse)
async def execute_tool(agent_id: str, request: ToolRequest):
    """Execute a specific tool through an agent."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents[agent_id]

    try:
        result = await agent.execute_tool(request.tool_name, request.parameters)
        return ToolResponse(
            agent_id=agent_id,
            tool_name=request.tool_name,
            parameters=request.parameters,
            result=result
        )
    except Exception as e:
        logger.error(f"Error executing tool {request.tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_id}/tools")
async def list_agent_tools(agent_id: str):
    """List available tools for an agent."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents[agent_id]

    try:
        tools = await agent._get_available_tools()
        return {"agent_id": agent_id, "tools": tools}
    except Exception as e:
        logger.error(f"Error listing tools for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    del agents[agent_id]
    logger.info(f"Deleted agent {agent_id}")

    return {"message": f"Agent {agent_id} deleted successfully"}


@app.post("/agents/{agent_id}/clear")
async def clear_agent_history(agent_id: str):
    """Clear an agent's conversation history."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents[agent_id]
    agent.clear_history()

    return {"message": f"History cleared for agent {agent_id}"}


@app.get("/agents/{agent_id}/history")
async def get_agent_history(agent_id: str):
    """Get an agent's conversation history."""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = agents[agent_id]
    history = agent.get_history()

    return {"agent_id": agent_id, "history": history}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

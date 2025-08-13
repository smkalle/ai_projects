"""
Pydantic models for the MCP AI Agent API
Defines request/response schemas and data validation.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class AgentConfig(BaseModel):
    """Configuration for creating a new agent."""
    model: str = Field(..., description="LLM model name (e.g., gpt-4, claude-3-sonnet)")
    provider: LLMProvider = Field(..., description="LLM provider")
    api_key: Optional[str] = Field(None, description="API key for the LLM provider")
    mcp_servers: Optional[List[str]] = Field(default_factory=list, description="List of MCP server names")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: int = Field(2000, gt=0, description="Maximum tokens in response")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")


class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    message: str = Field(..., description="User message/query")
    stream: bool = Field(False, description="Whether to stream the response")


class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    agent_id: str = Field(..., description="ID of the agent that generated the response")
    message: str = Field(..., description="Original user message")
    response: str = Field(..., description="Agent response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ToolRequest(BaseModel):
    """Request model for tool execution."""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for tool execution")


class ToolResponse(BaseModel):
    """Response model for tool execution."""
    agent_id: str = Field(..., description="ID of the agent that executed the tool")
    tool_name: str = Field(..., description="Name of the executed tool")
    parameters: Dict[str, Any] = Field(..., description="Parameters used for tool execution")
    result: Any = Field(..., description="Result of tool execution")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")


class AgentStatus(BaseModel):
    """Agent status information."""
    agent_id: str = Field(..., description="Agent identifier")
    model: str = Field(..., description="LLM model being used")
    provider: str = Field(..., description="LLM provider")
    mcp_servers: List[str] = Field(default_factory=list, description="Connected MCP servers")
    conversation_length: int = Field(0, description="Number of messages in conversation history")
    created_at: datetime = Field(default_factory=datetime.now, description="Agent creation timestamp")


class ToolInfo(BaseModel):
    """Information about an available tool."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameter schema")


class AgentSummary(BaseModel):
    """Summary information about an agent."""
    agent_id: str
    model: str
    provider: str
    active: bool = True
    last_activity: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthStatus(BaseModel):
    """API health status."""
    status: str = Field("healthy", description="Health status")
    agents_count: int = Field(0, description="Number of active agents")
    uptime: Optional[str] = Field(None, description="Service uptime")
    version: str = Field("1.0.0", description="API version")


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    content: str = Field(..., description="Chunk content")
    finished: bool = Field(False, description="Whether this is the final chunk")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional chunk metadata")


# Example usage and validation schemas
class CreateAgentRequest(BaseModel):
    """Complete request for creating an agent with validation."""
    config: AgentConfig
    name: Optional[str] = Field(None, description="Optional agent name")
    description: Optional[str] = Field(None, description="Optional agent description")


class UpdateAgentRequest(BaseModel):
    """Request for updating agent configuration."""
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    system_prompt: Optional[str] = None


class BatchChatRequest(BaseModel):
    """Request for batch processing multiple messages."""
    messages: List[str] = Field(..., description="List of messages to process")
    agent_id: str = Field(..., description="Agent ID to use for processing")


class BatchChatResponse(BaseModel):
    """Response for batch chat processing."""
    agent_id: str
    responses: List[ChatResponse]
    total_processed: int
    processing_time: float

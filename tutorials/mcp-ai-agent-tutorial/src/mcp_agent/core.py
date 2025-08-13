"""
MCP AI Agent Core Module
Provides the main functionality for creating and managing MCP-enabled AI agents.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from mcp_use import MCPClient
import openai
import anthropic
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class AgentConfig:
    """Configuration for MCP Agent."""
    model: str
    provider: LLMProvider
    api_key: Optional[str] = None
    mcp_servers: List[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: Optional[str] = None


class MCPAgent:
    """
    Main MCP Agent class that connects LLMs with MCP servers.

    This class provides the core functionality to:
    - Connect to multiple MCP servers
    - Execute tool calls through MCP protocol
    - Manage conversation context
    - Handle streaming responses
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.mcp_client = None
        self.llm_client = None
        self.conversation_history = []
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize MCP and LLM clients."""
        try:
            # Initialize MCP client
            if self.config.mcp_servers:
                self.mcp_client = MCPClient(servers=self.config.mcp_servers)

            # Initialize LLM client based on provider
            if self.config.provider == LLMProvider.OPENAI:
                self.llm_client = openai.OpenAI(api_key=self.config.api_key)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                self.llm_client = anthropic.Anthropic(api_key=self.config.api_key)

            logger.info(f"Initialized agent with {self.config.provider} and {len(self.config.mcp_servers or [])} MCP servers")

        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
            raise

    async def run(self, message: str, stream: bool = False) -> Union[str, Any]:
        """
        Execute a message through the agent with MCP tool access.

        Args:
            message: User message/query
            stream: Whether to stream the response

        Returns:
            Agent response or stream object
        """
        try:
            # Add message to conversation history
            self.conversation_history.append({"role": "user", "content": message})

            # Get available tools from MCP servers
            available_tools = await self._get_available_tools()

            # Prepare system prompt
            system_prompt = self._build_system_prompt(available_tools)

            # Generate response with tool access
            if self.config.provider == LLMProvider.OPENAI:
                response = await self._openai_completion(system_prompt, stream)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                response = await self._anthropic_completion(system_prompt, stream)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            if not stream:
                self.conversation_history.append({"role": "assistant", "content": response})

            return response

        except Exception as e:
            logger.error(f"Error in agent run: {e}")
            raise

    async def _get_available_tools(self) -> List[Dict]:
        """Get available tools from MCP servers."""
        if not self.mcp_client:
            return []

        try:
            tools = await self.mcp_client.list_tools()
            return tools
        except Exception as e:
            logger.error(f"Error getting tools: {e}")
            return []

    def _build_system_prompt(self, tools: List[Dict]) -> str:
        """Build system prompt with available tools."""
        base_prompt = self.config.system_prompt or """
        You are an AI assistant with access to various tools through MCP (Model Context Protocol).
        You can perform web searches, file operations, and other tasks using these tools.
        Always use tools when they would be helpful to answer the user's query.
        """

        if tools:
            tools_info = "\n\nAvailable tools:\n"
            for tool in tools:
                tools_info += f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}\n"
            base_prompt += tools_info

        return base_prompt

    async def _openai_completion(self, system_prompt: str, stream: bool) -> Union[str, Any]:
        """Generate completion using OpenAI."""
        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

        if stream:
            return await self.llm_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )
        else:
            response = await self.llm_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content

    async def _anthropic_completion(self, system_prompt: str, stream: bool) -> Union[str, Any]:
        """Generate completion using Anthropic."""
        messages = self.conversation_history.copy()

        if stream:
            return await self.llm_client.messages.create(
                model=self.config.model,
                system=system_prompt,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )
        else:
            response = await self.llm_client.messages.create(
                model=self.config.model,
                system=system_prompt,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.content[0].text

    async def execute_tool(self, tool_name: str, parameters: Dict) -> Any:
        """Execute a specific tool directly."""
        if not self.mcp_client:
            raise ValueError("No MCP client initialized")

        try:
            result = await self.mcp_client.call_tool(tool_name, parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history.copy()


# Example usage functions
async def create_web_search_agent(api_key: str) -> MCPAgent:
    """Create an agent specialized for web searching."""
    config = AgentConfig(
        model="gpt-4o",
        provider=LLMProvider.OPENAI,
        api_key=api_key,
        mcp_servers=["web-browser", "search"],
        system_prompt="You are a web search assistant. Use web browsing tools to find accurate, up-to-date information."
    )
    return MCPAgent(config)


async def create_file_manager_agent(api_key: str) -> MCPAgent:
    """Create an agent specialized for file operations."""
    config = AgentConfig(
        model="claude-3-sonnet-20240229",
        provider=LLMProvider.ANTHROPIC,
        api_key=api_key,
        mcp_servers=["file-manager", "code-editor"],
        system_prompt="You are a file management assistant. Help users organize, edit, and manage their files."
    )
    return MCPAgent(config)

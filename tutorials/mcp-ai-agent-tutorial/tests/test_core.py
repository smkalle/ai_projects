"""
Tests for core MCP agent functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.mcp_agent.core import MCPAgent, AgentConfig, LLMProvider

@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return AgentConfig(
        model="gpt-4",
        provider=LLMProvider.OPENAI,
        api_key="test-key",
        mcp_servers=["test-server"]
    )

@pytest.fixture
def mock_agent(mock_config):
    """Create a mock agent."""
    with patch('src.mcp_agent.core.MCPClient'), \
         patch('src.mcp_agent.core.openai.OpenAI'):
        agent = MCPAgent(mock_config)
        return agent

class TestMCPAgent:
    """Test suite for MCPAgent class."""

    def test_agent_initialization(self, mock_config):
        """Test agent initialization."""
        with patch('src.mcp_agent.core.MCPClient'), \
             patch('src.mcp_agent.core.openai.OpenAI'):
            agent = MCPAgent(mock_config)
            assert agent.config.model == "gpt-4"
            assert agent.config.provider == LLMProvider.OPENAI

    @pytest.mark.asyncio
    async def test_run_method(self, mock_agent):
        """Test the run method."""
        # Mock the necessary methods
        mock_agent._get_available_tools = AsyncMock(return_value=[])
        mock_agent._openai_completion = AsyncMock(return_value="Test response")

        result = await mock_agent.run("Test message")
        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_get_available_tools(self, mock_agent):
        """Test getting available tools."""
        mock_tools = [{"name": "test_tool", "description": "Test tool"}]
        mock_agent.mcp_client = Mock()
        mock_agent.mcp_client.list_tools = AsyncMock(return_value=mock_tools)

        tools = await mock_agent._get_available_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"

    def test_clear_history(self, mock_agent):
        """Test clearing conversation history."""
        mock_agent.conversation_history = [{"role": "user", "content": "test"}]
        mock_agent.clear_history()
        assert len(mock_agent.conversation_history) == 0

    def test_get_history(self, mock_agent):
        """Test getting conversation history."""
        test_history = [{"role": "user", "content": "test"}]
        mock_agent.conversation_history = test_history

        history = mock_agent.get_history()
        assert history == test_history
        assert history is not mock_agent.conversation_history  # Should be a copy

@pytest.mark.asyncio
async def test_create_web_search_agent():
    """Test creating a web search agent."""
    with patch('src.mcp_agent.core.MCPAgent') as mock_agent_class:
        from src.mcp_agent.core import create_web_search_agent

        agent = await create_web_search_agent("test-key")
        mock_agent_class.assert_called_once()

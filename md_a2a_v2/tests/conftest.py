import pytest
import os
from unittest.mock import patch, MagicMock

# Mock the LangGraph app for tests that don't need real AI responses
@pytest.fixture
def mock_lg_app():
    with patch('server.main.lg_app') as mock_app:
        mock_response = {
            "messages": [
                {"role": "assistant", "content": "Mock response from agent"}
            ]
        }
        mock_app.invoke.return_value = mock_response
        yield mock_app

# Set a test OpenAI API key if not present (for unit tests only)
@pytest.fixture(autouse=True)
def setup_test_env():
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "test-key-for-unit-tests"
    yield
    # Cleanup if needed

# Mock the agent responses for faster unit tests
@pytest.fixture
def mock_agents():
    with patch('agents.publishing.publishing_agent') as mock_pub, \
         patch('agents.broadcasting.broadcasting_agent') as mock_broad, \
         patch('agents.news.news_agent') as mock_news:
        
        # Setup mock responses
        mock_pub.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock book response"}]}
        mock_broad.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock TV response"}]}
        mock_news.invoke.return_value = {"messages": [{"role": "assistant", "content": "Mock news response"}]}
        
        yield {
            "publishing": mock_pub,
            "broadcasting": mock_broad,
            "news": mock_news
        }
"""
Streamlit Frontend Application for MCP AI Agent Tutorial
Provides a user-friendly interface for interacting with MCP-enabled AI agents.
"""

import streamlit as st
import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure page
st.set_page_config(
    page_title="MCP AI Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# Initialize session state
if "agents" not in st.session_state:
    st.session_state.agents = {}
if "current_agent" not in st.session_state:
    st.session_state.current_agent = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


async def make_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """Make async HTTP request to FastAPI backend."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        url = f"{API_BASE_URL}{endpoint}"
        if method.upper() == "GET":
            response = await client.get(url)
        elif method.upper() == "POST":
            response = await client.post(url, json=data)
        elif method.upper() == "DELETE":
            response = await client.delete(url)

        if response.status_code != 200:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}

        return response.json()


def run_async(coro):
    """Run async function in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new event loop for this thread
            import threading
            result = {}

            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result["value"] = new_loop.run_until_complete(coro)
                except Exception as e:
                    result["error"] = str(e)
                finally:
                    new_loop.close()

            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()

            if "error" in result:
                raise Exception(result["error"])
            return result.get("value")
        else:
            return loop.run_until_complete(coro)
    except Exception as e:
        st.error(f"Async execution error: {e}")
        return None


def main():
    """Main Streamlit application."""
    st.title("🤖 MCP AI Agent Dashboard")
    st.markdown("Build and interact with AI agents using the Model Context Protocol")

    # Sidebar for agent management
    with st.sidebar:
        st.header("🔧 Agent Management")

        # Create new agent section
        with st.expander("➕ Create New Agent", expanded=False):
            create_agent_form()

        # List existing agents
        st.subheader("📋 Active Agents")
        list_agents()

        # Agent tools and status
        if st.session_state.current_agent:
            show_agent_info()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Chat interface
        st.header("💬 Chat Interface")
        chat_interface()

    with col2:
        # Agent status and tools
        st.header("📊 Agent Status")
        agent_status_panel()

        st.header("🛠️ Available Tools")
        tools_panel()


def create_agent_form():
    """Form for creating a new agent."""
    with st.form("create_agent_form"):
        st.subheader("Create New Agent")

        # Basic configuration
        col1, col2 = st.columns(2)
        with col1:
            model = st.selectbox(
                "Model",
                ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            )
            provider = st.selectbox("Provider", ["openai", "anthropic"])

        with col2:
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
            max_tokens = st.number_input("Max Tokens", 100, 4000, 2000)

        # API Key
        api_key = st.text_input("API Key", type="password", help="Your OpenAI or Anthropic API key")

        # MCP Servers
        mcp_servers = st.multiselect(
            "MCP Servers",
            ["web-browser", "file-manager", "search", "code-editor", "database"],
            default=["web-browser"]
        )

        # System prompt
        system_prompt = st.text_area(
            "System Prompt (Optional)",
            placeholder="You are a helpful AI assistant..."
        )

        if st.form_submit_button("🚀 Create Agent", type="primary"):
            if api_key:
                create_agent(model, provider, api_key, temperature, max_tokens, mcp_servers, system_prompt)
            else:
                st.error("Please provide an API key")


def create_agent(model: str, provider: str, api_key: str, temperature: float, 
                max_tokens: int, mcp_servers: List[str], system_prompt: str):
    """Create a new agent via API."""
    config = {
        "model": model,
        "provider": provider,
        "api_key": api_key,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mcp_servers": mcp_servers,
        "system_prompt": system_prompt or None
    }

    with st.spinner("Creating agent..."):
        result = run_async(make_request("POST", "/agents/create", {"config": config}))

        if result and "agent_id" in result:
            agent_id = result["agent_id"]
            st.session_state.agents[agent_id] = {
                "id": agent_id,
                "model": model,
                "provider": provider,
                "created_at": datetime.now(),
                "status": "active"
            }
            st.session_state.current_agent = agent_id
            st.success(f"✅ Agent {agent_id} created successfully!")
            st.rerun()
        else:
            st.error("Failed to create agent")


def list_agents():
    """List all active agents."""
    agents = run_async(make_request("GET", "/agents"))

    if agents:
        for agent_id in agents:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"🤖 {agent_id}", key=f"select_{agent_id}", 
                           type="secondary" if st.session_state.current_agent != agent_id else "primary"):
                    st.session_state.current_agent = agent_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{agent_id}", help="Delete agent"):
                    delete_agent(agent_id)
    else:
        st.info("No active agents. Create one to get started!")


def delete_agent(agent_id: str):
    """Delete an agent."""
    with st.spinner(f"Deleting agent {agent_id}..."):
        result = run_async(make_request("DELETE", f"/agents/{agent_id}"))

        if result:
            if agent_id in st.session_state.agents:
                del st.session_state.agents[agent_id]

            if st.session_state.current_agent == agent_id:
                st.session_state.current_agent = None
                st.session_state.chat_history = []

            st.success(f"Agent {agent_id} deleted!")
            st.rerun()


def show_agent_info():
    """Show information about the current agent."""
    agent_id = st.session_state.current_agent

    with st.expander(f"ℹ️ {agent_id} Info", expanded=True):
        status = run_async(make_request("GET", f"/agents/{agent_id}/status"))

        if status:
            st.write(f"**Model:** {status.get('model', 'Unknown')}")
            st.write(f"**Provider:** {status.get('provider', 'Unknown')}")
            st.write(f"**MCP Servers:** {', '.join(status.get('mcp_servers', []))}")
            st.write(f"**Messages:** {status.get('conversation_length', 0)}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear History", key="clear_history"):
                    clear_agent_history()
            with col2:
                if st.button("📊 View History", key="view_history"):
                    show_history()


def clear_agent_history():
    """Clear agent conversation history."""
    if st.session_state.current_agent:
        result = run_async(make_request("POST", f"/agents/{st.session_state.current_agent}/clear"))
        if result:
            st.session_state.chat_history = []
            st.success("History cleared!")
            st.rerun()


def show_history():
    """Show agent conversation history."""
    if st.session_state.current_agent:
        history = run_async(make_request("GET", f"/agents/{st.session_state.current_agent}/history"))

        if history and "history" in history:
            st.write("**Conversation History:**")
            for msg in history["history"]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                st.write(f"**{role.title()}:** {content[:100]}...")


def chat_interface():
    """Main chat interface."""
    if not st.session_state.current_agent:
        st.info("👈 Select or create an agent to start chatting!")
        return

    # Display chat history
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_agent_response(prompt)

                if response:
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to get response from agent")


def get_agent_response(message: str) -> Optional[str]:
    """Get response from the current agent."""
    if not st.session_state.current_agent:
        return None

    agent_id = st.session_state.current_agent
    data = {"message": message}

    result = run_async(make_request("POST", f"/agents/{agent_id}/chat", data))

    if result and "response" in result:
        return result["response"]

    return None


def agent_status_panel():
    """Agent status monitoring panel."""
    if not st.session_state.current_agent:
        st.info("No agent selected")
        return

    agent_id = st.session_state.current_agent

    # Health check
    health = run_async(make_request("GET", "/health"))

    if health:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status", "🟢 Online" if health.get("status") == "healthy" else "🔴 Offline")
        with col2:
            st.metric("Active Agents", health.get("agents", 0))

    # Agent-specific status
    status = run_async(make_request("GET", f"/agents/{agent_id}/status"))

    if status:
        st.metric("Conversation Length", status.get("conversation_length", 0))


def tools_panel():
    """Available tools panel."""
    if not st.session_state.current_agent:
        st.info("No agent selected")
        return

    agent_id = st.session_state.current_agent

    # Get available tools
    tools_data = run_async(make_request("GET", f"/agents/{agent_id}/tools"))

    if tools_data and "tools" in tools_data:
        tools = tools_data["tools"]

        if tools:
            for tool in tools:
                with st.expander(f"🛠️ {tool.get('name', 'Unknown Tool')}"):
                    st.write(f"**Description:** {tool.get('description', 'No description')}")

                    # Tool execution form
                    if st.button(f"Execute {tool.get('name')}", key=f"exec_{tool.get('name')}"):
                        execute_tool_dialog(tool)
        else:
            st.info("No tools available for this agent")
    else:
        st.error("Failed to fetch tools")


def execute_tool_dialog(tool: Dict):
    """Dialog for executing a tool."""
    st.write(f"Executing tool: **{tool.get('name')}**")

    # Simple parameter input (could be enhanced)
    params_json = st.text_area(
        "Parameters (JSON)",
        value="{}",
        help="Enter tool parameters as JSON"
    )

    if st.button("Execute", key=f"exec_confirm_{tool.get('name')}"):
        try:
            params = json.loads(params_json)
            result = execute_tool(tool.get('name'), params)

            if result:
                st.success("Tool executed successfully!")
                st.json(result)
            else:
                st.error("Tool execution failed")

        except json.JSONDecodeError:
            st.error("Invalid JSON parameters")


def execute_tool(tool_name: str, parameters: Dict) -> Optional[Dict]:
    """Execute a tool via API."""
    if not st.session_state.current_agent:
        return None

    agent_id = st.session_state.current_agent
    data = {
        "tool_name": tool_name,
        "parameters": parameters
    }

    return run_async(make_request("POST", f"/agents/{agent_id}/tools", data))


if __name__ == "__main__":
    main()

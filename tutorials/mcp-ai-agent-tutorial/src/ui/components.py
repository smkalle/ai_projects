"""Reusable Streamlit components."""

import streamlit as st
from typing import Dict, List, Any

def agent_selector(agents: List[str]) -> str:
    """Component for selecting an agent."""
    if not agents:
        st.warning("No agents available")
        return None

    return st.selectbox("Select Agent", agents)

def status_badge(status: str) -> None:
    """Display a status badge."""
    color = "green" if status == "healthy" else "red"
    st.markdown(f"**Status:** :{color}[{status.title()}]")

def metric_card(title: str, value: Any, delta: Any = None) -> None:
    """Display a metric card."""
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric(title, value, delta)

def tool_card(tool: Dict[str, Any]) -> None:
    """Display information about a tool."""
    with st.expander(f"🛠️ {tool.get('name', 'Unknown')}"):
        st.write(f"**Description:** {tool.get('description', 'No description')}")
        if 'parameters' in tool:
            st.write("**Parameters:**")
            st.json(tool['parameters'])

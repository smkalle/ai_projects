"""
PagerDuty AI Agent - Main Streamlit Application

A comprehensive AI agent for incident management inspired by PagerDuty,
built with LangChain, LangGraph, and OpenAI GPT-4 omini.
"""

import streamlit as st
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import load_config, get_settings
from src.agents.workflow import create_incident_agent_workflow
from src.data.database import DatabaseManager
from src.utils.logging_config import setup_logging
import logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="PagerDuty AI Agent",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
config = load_config()
settings = get_settings()

@st.cache_resource
def initialize_database():
    """Initialize database connection."""
    try:
        db_manager = DatabaseManager(config.database_url)
        db_manager.init_db()
        logger.info("Database initialized successfully")
        return db_manager
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        st.error(f"Database initialization failed: {e}")
        return None

@st.cache_resource
def initialize_agent():
    """Initialize the AI agent workflow."""
    try:
        workflow = create_incident_agent_workflow(config)
        logger.info("Agent workflow initialized successfully")
        return workflow
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        st.error(f"Agent initialization failed: {e}")
        return None

def init_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if 'agent_workflow' not in st.session_state:
        st.session_state.agent_workflow = initialize_agent()
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = initialize_database()

def display_sidebar():
    """Display sidebar with application info and controls."""
    with st.sidebar:
        st.title("🚨 PagerDuty AI Agent")
        st.markdown("---")

        # Application info
        st.subheader("ℹ️ Application Info")
        st.info(f"""
        **Session ID:** {st.session_state.session_id}
        **Model:** {config.openai_model}
        **Database:** SQLite
        """)

        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        if st.button("🔄 Reset Session"):
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.messages = []
            st.rerun()

        # Database statistics
        if st.session_state.db_manager:
            st.subheader("📊 Database Stats")
            try:
                stats = st.session_state.db_manager.get_incident_stats()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Incidents", stats.get('total', 0))
                    st.metric("Open", stats.get('open', 0))
                with col2:
                    st.metric("High Priority", stats.get('high_priority', 0))
                    st.metric("Resolved", stats.get('resolved', 0))
            except Exception as e:
                st.error(f"Failed to load stats: {e}")

        # Sample queries
        st.subheader("💡 Sample Queries")
        sample_queries = [
            "How many high priority incidents are open?",
            "Show me incidents from the last 24 hours",
            "What's the average resolution time?",
            "Which service has the most incidents?",
            "List all critical incidents",
        ]

        for query in sample_queries:
            if st.button(f"💬 {query}", key=f"sample_{hash(query)}"):
                st.session_state.user_input = query

def display_chat_interface():
    """Display the main chat interface."""
    st.title("🤖 Incident Management AI Assistant")
    st.markdown("""
    Ask me anything about your incidents! I can help you:
    - 📈 Analyze incident trends and patterns
    - 🔍 Search and filter incidents
    - ⏱️ Calculate resolution times and metrics  
    - 📊 Generate reports and insights
    - 🚨 Identify critical issues
    """)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display any data tables or charts
            if "data" in message:
                if isinstance(message["data"], pd.DataFrame) and not message["data"].empty:
                    st.dataframe(message["data"], use_container_width=True)

def process_user_input(user_input: str):
    """Process user input through the AI agent."""
    if not st.session_state.agent_workflow:
        st.error("Agent not initialized. Please check your configuration.")
        return

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Process with agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Create agent state
                state = {
                    "messages": [{"role": "user", "content": user_input}],
                    "session_id": st.session_state.session_id,
                    "error": None
                }

                # Invoke the workflow
                result = st.session_state.agent_workflow.invoke(
                    state,
                    config={"configurable": {"thread_id": st.session_state.session_id}}
                )

                # Extract response
                if result and "messages" in result:
                    last_message = result["messages"][-1]
                    if hasattr(last_message, 'content'):
                        response_content = last_message.content
                    else:
                        response_content = str(last_message)
                else:
                    response_content = "I encountered an issue processing your request."

                # Display response
                st.markdown(response_content)

                # Add to session state
                assistant_message = {"role": "assistant", "content": response_content}

                # Add any data if present
                if "data" in result:
                    assistant_message["data"] = result["data"]
                    if isinstance(result["data"], pd.DataFrame) and not result["data"].empty:
                        st.dataframe(result["data"], use_container_width=True)

                st.session_state.messages.append(assistant_message)

            except Exception as e:
                error_msg = f"Error processing request: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                logger.error(f"Error processing user input: {e}")

def main():
    """Main application function."""
    try:
        # Initialize session state
        init_session_state()

        # Display sidebar
        display_sidebar()

        # Display main chat interface
        display_chat_interface()

        # Handle chat input
        if prompt := st.chat_input("Ask me about incidents..."):
            process_user_input(prompt)

        # Handle sidebar input if any
        if hasattr(st.session_state, 'user_input') and st.session_state.user_input:
            user_input = st.session_state.user_input
            del st.session_state.user_input
            process_user_input(user_input)
            st.rerun()

    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
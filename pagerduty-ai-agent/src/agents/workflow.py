"""
LangGraph workflow for PagerDuty AI Agent.

Defines the agent workflow using LangGraph for stateful conversation management.
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
import operator

from ..data.database import DatabaseManager
from ..tools.database_tools import create_database_tools
from ..tools.analytics_tools import create_analytics_tools
from ..utils.config import Settings

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the incident management agent."""
    messages: Annotated[List[BaseMessage], operator.add]
    session_id: str
    error: Optional[str]
    tool_calls: Optional[List[Dict]]
    iteration_count: int

def create_incident_agent_workflow(config: Settings, db_manager: Optional[DatabaseManager] = None):
    """
    Create the incident management agent workflow.

    Args:
        config: Application configuration
        db_manager: Database manager instance

    Returns:
        Compiled LangGraph workflow
    """

    # Initialize database manager if not provided
    if db_manager is None:
        db_manager = DatabaseManager(config.database_url)
        db_manager.init_db()

    # Create tools
    database_tools = create_database_tools(db_manager)
    analytics_tools = create_analytics_tools(db_manager)
    all_tools = database_tools + analytics_tools

    # Initialize LLM with tools
    llm = ChatOpenAI(
        api_key=config.openai_api_key,
        model=config.openai_model,
        temperature=config.openai_temperature,
    ).bind_tools(all_tools)

    # System prompt for the agent
    system_prompt = """You are an expert AI assistant for incident management, inspired by PagerDuty's system. 
    You help teams analyze, understand, and manage incidents through natural language conversations.

    Your capabilities include:
    - Searching and filtering incidents by various criteria
    - Calculating metrics and resolution times
    - Analyzing trends and patterns
    - Generating comprehensive reports
    - Identifying problematic patterns and providing recommendations
    - Updating incident statuses

    Key principles:
    1. Always use tools to get accurate, real-time data - never make up information
    2. Provide clear, actionable insights with specific numbers and dates
    3. Use emojis and formatting to make responses readable and engaging
    4. When errors occur, explain what went wrong and suggest alternatives
    5. Be proactive in suggesting related analyses that might be helpful
    6. Focus on helping teams save time and make better decisions

    Response guidelines:
    - Start responses with relevant emojis (🚨 for alerts, 📊 for stats, 🔍 for searches, etc.)
    - Use bullet points and clear formatting
    - Include specific numbers, percentages, and time periods
    - Highlight critical information with **bold text**
    - Suggest follow-up questions or analyses when appropriate

    If a user asks something you cannot help with, clearly explain what you can do instead."""

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # Agent node - decides whether to use tools or respond directly
    def agent_node(state: AgentState) -> Dict[str, Any]:
        """Agent reasoning node."""
        try:
            # Increment iteration count
            iteration_count = state.get("iteration_count", 0) + 1

            # Safety check to prevent infinite loops
            if iteration_count > 10:
                return {
                    "messages": [AIMessage(content="I've reached the maximum number of tool calls. Please try rephrasing your question or ask something simpler.")],
                    "iteration_count": iteration_count,
                    "error": "max_iterations_reached"
                }

            # Get the formatted prompt
            formatted_prompt = prompt.invoke({"messages": state["messages"]})

            # Call the LLM
            response = llm.invoke(formatted_prompt.messages)

            logger.info(f"Agent response: {response}")

            return {
                "messages": [response],
                "iteration_count": iteration_count,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error in agent node: {e}")
            error_message = AIMessage(
                content=f"I encountered an error while processing your request: {str(e)}. Please try again or rephrase your question."
            )
            return {
                "messages": [error_message],
                "error": str(e),
                "iteration_count": state.get("iteration_count", 0) + 1
            }

    # Tool node for executing tools
    tool_node = ToolNode(all_tools)

    # Error handling node
    def error_node(state: AgentState) -> Dict[str, Any]:
        """Handle errors and provide fallback responses."""
        try:
            error = state.get("error", "Unknown error")
            logger.warning(f"Error node activated: {error}")

            # Provide different responses based on error type
            if "max_iterations_reached" in error:
                message = "I've tried multiple approaches but couldn't complete your request. Please try asking a simpler question or break your request into smaller parts."
            elif "database" in error.lower():
                message = "I'm having trouble accessing the incident database. Please check if the database is available and try again."
            elif "tool" in error.lower():
                message = "There was an issue with one of my analysis tools. Please try rephrasing your question or ask about something else."
            else:
                message = f"I encountered an unexpected error: {error}. Please try again or contact support if the issue persists."

            return {
                "messages": [AIMessage(content=f"❌ {message}")],
                "error": None  # Clear the error after handling
            }

        except Exception as e:
            logger.error(f"Error in error node: {e}")
            return {
                "messages": [AIMessage(content="I'm experiencing technical difficulties. Please try again later.")],
                "error": None
            }

    # Conditional routing function
    def route_decision(state: AgentState) -> str:
        """Decide the next node based on the current state."""
        try:
            # Check for errors first
            if state.get("error"):
                return "error"

            # Get the last message
            last_message = state["messages"][-1]

            # If the last message has tool calls, go to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"

            # Otherwise, end the conversation
            return END

        except Exception as e:
            logger.error(f"Error in routing: {e}")
            return "error"

    # Create the workflow graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("error", error_node)

    # Add edges
    workflow.set_entry_point("agent")

    # Conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        route_decision,
        {
            "tools": "tools",
            "error": "error",
            END: END
        }
    )

    # After tools, always go back to agent
    workflow.add_edge("tools", "agent")

    # After error handling, end the conversation
    workflow.add_edge("error", END)

    # Compile with memory for multi-session support
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    logger.info("Incident management agent workflow created successfully")

    return app
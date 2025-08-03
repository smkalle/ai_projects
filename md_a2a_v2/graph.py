from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
import warnings

# Filter out the deprecation warning for now
warnings.filterwarnings("ignore", message=".*config_type.*deprecated.*", category=DeprecationWarning)

from agents.publishing import publishing_agent
from agents.broadcasting import broadcasting_agent
from agents.news import news_agent

class AppState(MessagesState):
    pass

def as_node(agent_graph):
    def _node(state: AppState):
        result = agent_graph.invoke(state)
        # Check if there was a handoff in the conversation
        if hasattr(result, 'messages') and result.messages:
            for message in reversed(result.messages):
                # Look for tool messages from handoff
                if hasattr(message, 'name') and message.name == 'handoff':
                    # Extract the next agent from the tool call that created this message
                    for prev_msg in reversed(result.messages):
                        if hasattr(prev_msg, 'tool_calls') and prev_msg.tool_calls:
                            for tool_call in prev_msg.tool_calls:
                                if tool_call.get('name') == 'handoff' and tool_call.get('id') == getattr(message, 'tool_call_id', None):
                                    next_agent = tool_call.get('args', {}).get('next_agent')
                                    if next_agent:
                                        return Command(goto=next_agent)
                        break
                    break
        return result
    return _node

def route_after_agent(state: AppState) -> Literal["publishing", "broadcasting", "news", "__end__"]:
    """Route to the next agent based on tool messages or end the conversation."""
    if hasattr(state, 'messages') and state.messages:
        # Look for handoff tool messages
        for message in reversed(state.messages):
            if hasattr(message, 'name') and message.name == 'handoff':
                # Find the corresponding tool call to get the next agent
                for prev_msg in reversed(state.messages):
                    if hasattr(prev_msg, 'tool_calls') and prev_msg.tool_calls:
                        for tool_call in prev_msg.tool_calls:
                            if tool_call.get('name') == 'handoff' and tool_call.get('id') == getattr(message, 'tool_call_id', None):
                                next_agent = tool_call.get('args', {}).get('next_agent')
                                if next_agent in ['publishing', 'broadcasting', 'news']:
                                    return next_agent
                    break
                break
    return "__end__"

builder = StateGraph(AppState)
builder.add_node("publishing", as_node(publishing_agent))
builder.add_node("broadcasting", as_node(broadcasting_agent))
builder.add_node("news", as_node(news_agent))

# Add conditional edges for handoffs
builder.add_conditional_edges("publishing", route_after_agent)
builder.add_conditional_edges("broadcasting", route_after_agent)
builder.add_conditional_edges("news", route_after_agent)

builder.add_edge(START, "publishing")
app = builder.compile()

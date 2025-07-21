from typing import TypedDict, Annotated, Sequence, Dict, Any, List
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    """State passed between agents in the LangGraph workflow"""
    messages: Annotated[List[Dict[str, str]], operator.add]
    current_agent: str
    context: Dict[str, Any]
    task_queue: List[str]
    memory: Dict[str, Any]
    metadata: Dict[str, Any]
    user_id: str
    should_end: bool

def create_base_graph():
    """Create the base graph structure for the multi-agent system"""
    workflow = StateGraph(AgentState)
    return workflow
from typing import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command

from agents.publishing import publishing_agent
from agents.broadcasting import broadcasting_agent
from agents.news import news_agent

class AppState(MessagesState):
    pass

def as_node(agent_graph):
    def _node(state: AppState):
        return agent_graph.invoke(state)
    return _node

builder = StateGraph(AppState)
builder.add_node("publishing", as_node(publishing_agent))
builder.add_node("broadcasting", as_node(broadcasting_agent))
builder.add_node("news", as_node(news_agent))
builder.add_edge(START, "publishing")
app = builder.compile()

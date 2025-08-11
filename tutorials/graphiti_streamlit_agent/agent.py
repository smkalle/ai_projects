"""Reusable LangGraph agent utilities for Graphiti demos.

This module is importable from notebooks and apps.
"""
from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, TypedDict

# Optional OpenAI via LangChain; gracefully fallback when unavailable
try:  # pragma: no cover
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover
    ChatOpenAI = None


class AgentState(TypedDict):
    input: str
    history: List[Dict[str, str]]
    memory_results: List[Dict[str, Any]]
    answer: str


def search_nodes_sync(graph: Any, query: str, max_results: int = 5):
    from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF
    import asyncio

    async def _run():
        return await graph.search_nodes(
            query=query, config=NODE_HYBRID_SEARCH_RRF(max_results=max_results)
        )

    return asyncio.run(_run())


def search_edges_sync(
    graph: Any, query: str, since: datetime | None = None, max_results: int = 10
):
    from graphiti_core.search.search_config import EdgeSearchConfig
    import asyncio

    async def _run():
        return await graph.search_edges(
            query=query,
            config=EdgeSearchConfig(
                max_results=max_results, search_type="hybrid", since=since
            ),
        )

    return asyncio.run(_run())


def build_agent(graph: Any, model_name: str = "gpt-4o-mini"):
    from langgraph.graph import StateGraph, END

    def retrieve(state: AgentState) -> Dict[str, Any]:
        q = state["input"]
        results = search_nodes_sync(graph, q, max_results=6) or []
        return {"memory_results": results}

    def _format_memory(memory: List[Dict[str, Any]]) -> str:
        if not memory:
            return "No memory found."
        lines = []
        for item in memory[:6]:
            try:
                name = item.get("name") or item.get("edge", {}).get("name")
                labels = item.get("labels")
                lines.append(f"- {name} ({labels})")
            except Exception:
                lines.append(f"- {json.dumps(item)[:200]}")
        return "\n".join(lines)

    def generate(state: AgentState) -> Dict[str, Any]:
        user_input = state["input"]
        history = state.get("history", [])
        memory = state.get("memory_results", [])
        memory_text = _format_memory(memory)

        history_text = "\n".join(
            f"{h.get('role','user')}: {h.get('content','')}" for h in history[-6:]
        )

        prompt = (
            "You are a helpful assistant with access to a temporal knowledge graph.\n"
            "Use the following retrieved memory to answer succinctly.\n\n"
            f"Conversation so far:\n{history_text}\n\n"
            f"User query: {user_input}\n\n"
            f"Retrieved memory:\n{memory_text}\n\n"
            "Answer:"
        )

        if ChatOpenAI and os.getenv("OPENAI_API_KEY"):
            try:
                llm = ChatOpenAI(model=model_name, temperature=0)
                resp = llm.invoke(prompt)
                text = getattr(resp, "content", str(resp))
            except Exception as e:  # Fallback on error
                text = "(LLM unavailable) Summary based on memory: " + memory_text[:600]
        else:
            text = "Summary based on memory: " + memory_text[:600]

        return {"answer": text}

    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


def run_agent_once(graph: Any, query: str, model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
    app = build_agent(graph, model_name=model_name)
    return app.invoke({"input": query, "history": [], "memory_results": [], "answer": ""})


def run_agent_conversation(
    graph: Any,
    turns: List[Dict[str, str]],
    model_name: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    """Run a short multi-turn conversation.

    turns: list of {"role": "user"|"assistant", "content": str}
    Returns the final state including answer and memory_results.
    """
    app = build_agent(graph, model_name=model_name)
    state: Dict[str, Any] = {"history": [], "memory_results": [], "answer": ""}
    for t in turns:
        if t.get("role") != "user":
            # Only retrieve/generate on user turns; assistant turns are context
            state["history"].append(t)
            continue
        state = app.invoke({
            "input": t.get("content", ""),
            "history": state.get("history", []),
            "memory_results": [],
            "answer": "",
        })
        # Append assistant reply into history for next turn context
        state.setdefault("history", []).append({"role": "user", "content": t.get("content", "")})
        state["history"].append({"role": "assistant", "content": state.get("answer", "")})
    return state


def search_edges_anchor_rerank(
    graph: Any,
    query: str,
    anchor: str,
    since: datetime | None = None,
    max_results: int = 15,
) -> List[Dict[str, Any]]:
    """Edge-aware retrieval with naive anchor reranking.

    Fetch edges via hybrid search and bubble up edges whose endpoints or names
    contain the anchor string. Structure of results may vary by Graphiti version.
    """
    edges = search_edges_sync(graph, query=query, since=since, max_results=max_results)
    def score(edge: Dict[str, Any]) -> int:
        blob = json.dumps(edge).lower()
        return (anchor.lower() in blob) * 1
    return sorted(edges or [], key=score, reverse=True)


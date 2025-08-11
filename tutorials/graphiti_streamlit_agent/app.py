import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, TypedDict

import streamlit as st
from dotenv import load_dotenv

# Optional LangChain OpenAI import (fallback if missing)
try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover
    ChatOpenAI = None


def _load_env():
    try:
        load_dotenv()
    except Exception:
        pass


@st.cache_resource(show_spinner=True)
def get_graph(neo4j_uri: str, neo4j_user: str, neo4j_password: str):
    from graphiti_core import Graphiti

    async def _build():
        return await Graphiti.build(neo4j_uri, neo4j_user, neo4j_password)

    return asyncio.run(_build())


def add_episode_sync(
    graph: Any,
    episode_type: str,
    name: str,
    body: Any,
    source_description: str,
    reference_time: datetime,
):
    from graphiti_core.nodes import EpisodeType

    async def _run():
        src = getattr(EpisodeType, episode_type)
        return await graph.add_episode(
            name=name,
            episode_body=body,
            source=src,
            source_description=source_description,
            reference_time=reference_time,
        )

    return asyncio.run(_run())


def search_nodes_sync(graph: Any, query: str, max_results: int = 5):
    from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_RRF

    async def _run():
        return await graph.search_nodes(
            query=query, config=NODE_HYBRID_SEARCH_RRF(max_results=max_results)
        )

    return asyncio.run(_run())


def search_edges_sync(
    graph: Any, query: str, since: datetime | None = None, max_results: int = 10
):
    from graphiti_core.search.search_config import EdgeSearchConfig

    async def _run():
        return await graph.search_edges(
            query=query,
            config=EdgeSearchConfig(
                max_results=max_results, search_type="hybrid", since=since
            ),
        )

    return asyncio.run(_run())


class AgentState(TypedDict):
    input: str
    memory_results: List[Dict[str, Any]]
    answer: str


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
        memory = state.get("memory_results", [])
        memory_text = _format_memory(memory)

        prompt = (
            "You are a helpful assistant with access to a temporal knowledge graph.\n"
            "Use the following retrieved memory to answer succinctly.\n\n"
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
                text = (
                    "(LLM unavailable) Summary based on memory: "
                    + memory_text[:600]
                )
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


def render_sidebar() -> dict:
    st.sidebar.header("Connection")
    uri = st.sidebar.text_input("NEO4J_URI", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user = st.sidebar.text_input("NEO4J_USER", os.getenv("NEO4J_USER", "neo4j"))
    password = st.sidebar.text_input("NEO4J_PASSWORD", os.getenv("NEO4J_PASSWORD", ""), type="password")
    model_name = st.sidebar.text_input("LLM Model (optional)", os.getenv("LLM_MODEL", "gpt-4o-mini"))
    connect = st.sidebar.button("Connect")
    return {"uri": uri, "user": user, "password": password, "connect": connect, "model": model_name}


def main():
    st.set_page_config(page_title="Graphiti + LangGraph Demo", layout="wide")
    _load_env()

    st.title("Graphiti + LangGraph Streamlit Demo")
    st.caption("Temporal knowledge graph memory for agents (Zep/Graphiti)")

    cfg = render_sidebar()

    if cfg["connect"] or "graph" not in st.session_state:
        try:
            st.session_state["graph"] = get_graph(cfg["uri"], cfg["user"], cfg["password"])
            st.success("Connected to Graphiti backend.")
        except Exception as e:
            st.error(f"Failed to connect: {e}")

    graph = st.session_state.get("graph")
    tabs = st.tabs(["Ingest", "Search", "Agent Chat"]) if graph else [st.empty()]

    if graph:
        with tabs[0]:
            st.subheader("Add Episode")
            ep_type = st.selectbox("Episode Type", ["text", "message", "json"], index=0)
            name = st.text_input("Name", value="User_Feedback_1")
            source_desc = st.text_input("Source Description", value="User review")
            ts = st.text_input("Reference Time (ISO)", value=datetime.now(tz=timezone.utc).isoformat())

            if ep_type in ("text", "message"):
                body = st.text_area("Body", height=120)
            else:
                body = st.text_area("JSON Body", value='{"key":"value"}', height=120)

            if st.button("Add Episode"):
                try:
                    ref_time = datetime.fromisoformat(ts)
                except Exception:
                    st.warning("Invalid timestamp; using now().")
                    ref_time = datetime.now(tz=timezone.utc)

                try:
                    payload = body if ep_type != "json" else json.loads(body)
                    add_episode_sync(
                        graph,
                        ep_type,
                        name,
                        payload,
                        source_desc,
                        ref_time,
                    )
                    st.success("Episode added.")
                except Exception as e:
                    st.error(f"Failed to add episode: {e}")

            st.divider()
            if st.button("Seed Demo Data"):
                try:
                    from seed_data import seed  # type: ignore

                    async def _seed():
                        await seed(graph)

                    asyncio.run(_seed())
                    st.success("Seeded demo data.")
                except Exception as e:
                    st.error(f"Seeding failed: {e}")

        with tabs[1]:
            st.subheader("Search Graph")
            q = st.text_input("Query", value="Products loved by Alice")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Search Nodes"):
                    try:
                        nodes = search_nodes_sync(graph, q, max_results=8)
                        st.write(nodes)
                    except Exception as e:
                        st.error(f"Node search failed: {e}")
            with col2:
                if st.button("Search Edges"):
                    try:
                        edges = search_edges_sync(
                            graph, q, since=datetime(2024, 1, 1, tzinfo=timezone.utc), max_results=8
                        )
                        st.write(edges)
                    except Exception as e:
                        st.error(f"Edge search failed: {e}")

        with tabs[2]:
            st.subheader("Agent Chat")
            user_msg = st.text_input("Message", value="What does Alice like and dislike?")
            if st.button("Send"):
                try:
                    app = build_agent(graph, model_name=cfg["model"])  # compile graph
                    result = app.invoke({"input": user_msg, "memory_results": [], "answer": ""})
                    st.markdown("### Answer")
                    st.write(result.get("answer"))
                    st.markdown("### Retrieved Memory (preview)")
                    st.write(result.get("memory_results"))
                except Exception as e:
                    st.error(f"Agent error: {e}")

    else:
        st.info("Enter connection details in the sidebar and click Connect.")


if __name__ == "__main__":
    main()


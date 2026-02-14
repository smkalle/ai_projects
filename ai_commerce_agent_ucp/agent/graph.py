"""LangGraph agent workflow for UCP commerce operations.

Orchestrates the multi-step flow: intent detection -> RAG retrieval ->
LLM response generation -> UCP actions (cart/checkout).
"""

from __future__ import annotations

import json
import logging
from typing import Any, Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from config import settings
from agent.rag import ProductRAG, get_product_rag
from agent.ucp_client import UCPClient, get_ucp_client

logger = logging.getLogger(__name__)


class AgentState(TypedDict, total=False):
    """State passed between nodes in the LangGraph workflow."""

    query: str
    intent: str
    context: str
    product_results: list[dict[str, Any]]
    response: str
    cart_id: str
    checkout_id: str
    checkout_details: dict[str, Any]
    error: str
    conversation_history: list[dict[str, str]]


# --- Intent Detection ---

INTENT_SYSTEM_PROMPT = """You are an intent classifier for a commerce AI agent.
Classify the user's query into exactly ONE of these intents:

- "search": User wants to find, browse, or learn about products
- "buy": User wants to purchase or buy a specific product (includes "add to cart", "buy", "order", "purchase")
- "cart": User wants to view or manage their cart
- "checkout": User wants to complete a purchase / checkout
- "general": General conversation, greetings, or questions not related to shopping

Respond with ONLY the intent word, nothing else."""


def detect_intent(state: AgentState) -> AgentState:
    """Classify the user's intent using the LLM."""
    llm = ChatOpenAI(model=settings.openai_model, temperature=0)

    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=state["query"]),
    ]

    response = llm.invoke(messages)
    intent = response.content.strip().lower().strip('"\'')

    valid_intents = {"search", "buy", "cart", "checkout", "general"}
    if intent not in valid_intents:
        intent = "search"  # default fallback

    state["intent"] = intent
    logger.info("Detected intent: %s for query: %s", intent, state["query"])
    return state


# --- RAG Retrieval ---


def retrieve_products(state: AgentState) -> AgentState:
    """Retrieve relevant products from the RAG vector store."""
    rag = get_product_rag()
    docs = rag.search(state["query"], k=5)

    state["context"] = rag.format_results(docs)
    state["product_results"] = [
        {
            "product_id": doc.metadata.get("product_id", ""),
            "name": doc.metadata.get("name", ""),
            "price": doc.metadata.get("price", 0),
            "category": doc.metadata.get("category", ""),
            "content": doc.page_content[:300],
        }
        for doc in docs
    ]

    logger.info("Retrieved %d products for query: %s", len(docs), state["query"])
    return state


# --- Response Generation ---

RESPONSE_SYSTEM_PROMPT = """You are a helpful AI shopping assistant for an online electronics store.
You help customers find products, answer questions, and assist with purchases.

When presenting products, format them clearly with name, price, and key features.
If the user wants to buy something, confirm the product and suggest proceeding to checkout.
Be concise and helpful. Use the product context provided to give accurate information.

If no relevant products are found, let the user know and suggest alternatives."""


def generate_response(state: AgentState) -> AgentState:
    """Generate a response using the LLM with RAG context."""
    llm = ChatOpenAI(model=settings.openai_model, temperature=0.7)

    context_section = ""
    if state.get("context"):
        context_section = f"\n\nAvailable Products:\n{state['context']}"

    cart_section = ""
    if state.get("cart_id"):
        cart_section = f"\n\nCustomer has an active cart (ID: {state['cart_id']})"

    checkout_section = ""
    if state.get("checkout_details"):
        details = state["checkout_details"]
        checkout_section = (
            f"\n\nCheckout Session Created:"
            f"\n  Session ID: {details.get('id', 'N/A')}"
            f"\n  Subtotal: ${details.get('subtotal', 0)}"
            f"\n  Tax: ${details.get('tax', 0)}"
            f"\n  Total: ${details.get('total', 0)}"
            f"\n  Status: {details.get('status', 'N/A')}"
        )

    messages = [
        SystemMessage(
            content=RESPONSE_SYSTEM_PROMPT + context_section + cart_section + checkout_section
        ),
        HumanMessage(content=state["query"]),
    ]

    response = llm.invoke(messages)
    state["response"] = response.content
    return state


# --- UCP Actions ---


def handle_buy(state: AgentState) -> AgentState:
    """Handle purchase intent: create cart, add items, create checkout."""
    client = get_ucp_client()

    if not state.get("product_results"):
        state["error"] = "No products found to purchase. Please search first."
        return state

    try:
        # Use first matching product
        product = state["product_results"][0]
        product_id = product["product_id"]

        # Create cart if needed
        if not state.get("cart_id"):
            cart_resp = client.create_cart()
            state["cart_id"] = cart_resp["cart"]["id"]

        # Add to cart
        client.add_to_cart(state["cart_id"], product_id, quantity=1)

        # Create checkout session
        checkout_resp = client.create_checkout(
            line_items=[{"product_id": product_id, "quantity": 1}],
        )
        state["checkout_id"] = checkout_resp.get("id", "")
        state["checkout_details"] = checkout_resp

        logger.info(
            "Created checkout %s for product %s", state["checkout_id"], product_id
        )

    except Exception as e:
        logger.error("Buy action failed: %s", e)
        state["error"] = f"Failed to process purchase: {str(e)}"

    return state


def handle_checkout(state: AgentState) -> AgentState:
    """Handle checkout confirmation."""
    client = get_ucp_client()

    if not state.get("checkout_id"):
        state["error"] = "No active checkout session. Please add items first."
        return state

    try:
        confirm_resp = client.confirm_checkout(state["checkout_id"])
        state["checkout_details"] = confirm_resp
        logger.info("Confirmed checkout %s", state["checkout_id"])
    except Exception as e:
        logger.error("Checkout confirmation failed: %s", e)
        state["error"] = f"Checkout failed: {str(e)}"

    return state


def handle_cart_view(state: AgentState) -> AgentState:
    """Handle cart viewing."""
    client = get_ucp_client()

    if not state.get("cart_id"):
        state["context"] = "No active cart. Start shopping to create one!"
        return state

    try:
        cart_resp = client.get_cart(state["cart_id"])
        cart = cart_resp["cart"]
        items = cart.get("items", [])
        if items:
            lines = ["Your cart contains:"]
            for item in items:
                lines.append(
                    f"  - {item['name']} x{item['quantity']} = ${item['price'] * item['quantity']:.2f}"
                )
            lines.append(f"  Total: ${cart.get('total', 0):.2f}")
            state["context"] = "\n".join(lines)
        else:
            state["context"] = "Your cart is empty."
    except Exception as e:
        logger.error("Cart view failed: %s", e)
        state["error"] = f"Could not retrieve cart: {str(e)}"

    return state


# --- Routing ---


def route_intent(state: AgentState) -> str:
    """Route to the appropriate node based on detected intent."""
    intent = state.get("intent", "general")

    if intent == "search":
        return "retrieve"
    elif intent == "buy":
        return "retrieve_then_buy"
    elif intent == "cart":
        return "cart"
    elif intent == "checkout":
        return "checkout"
    else:
        return "respond"


# --- Graph Construction ---


def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph workflow."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("detect_intent", detect_intent)
    graph.add_node("retrieve", retrieve_products)
    graph.add_node("retrieve_for_buy", retrieve_products)
    graph.add_node("buy", handle_buy)
    graph.add_node("cart", handle_cart_view)
    graph.add_node("checkout", handle_checkout)
    graph.add_node("respond", generate_response)

    # Entry point
    graph.set_entry_point("detect_intent")

    # Conditional routing from intent detection
    graph.add_conditional_edges(
        "detect_intent",
        route_intent,
        {
            "retrieve": "retrieve",
            "retrieve_then_buy": "retrieve_for_buy",
            "cart": "cart",
            "checkout": "checkout",
            "respond": "respond",
        },
    )

    # Edges after retrieval / actions -> respond -> END
    graph.add_edge("retrieve", "respond")
    graph.add_edge("retrieve_for_buy", "buy")
    graph.add_edge("buy", "respond")
    graph.add_edge("cart", "respond")
    graph.add_edge("checkout", "respond")
    graph.add_edge("respond", END)

    return graph


def create_agent():
    """Create and compile the agent graph."""
    graph = build_agent_graph()
    return graph.compile()


# Module-level compiled agent
_agent = None


def get_agent():
    """Get or create the compiled agent."""
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


def run_query(query: str, cart_id: str = "", checkout_id: str = "") -> dict[str, Any]:
    """Run a user query through the agent pipeline.

    Args:
        query: The user's natural language query.
        cart_id: Existing cart ID for session continuity.
        checkout_id: Existing checkout ID for session continuity.

    Returns:
        The final agent state containing the response and any action results.
    """
    agent = get_agent()

    initial_state: AgentState = {
        "query": query,
        "intent": "",
        "context": "",
        "product_results": [],
        "response": "",
        "cart_id": cart_id,
        "checkout_id": checkout_id,
        "checkout_details": {},
        "error": "",
        "conversation_history": [],
    }

    result = agent.invoke(initial_state)
    return dict(result)

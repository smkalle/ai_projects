"""LangGraph agent workflow for UCP commerce operations.

Orchestrates the multi-step flow: intent detection -> RAG retrieval ->
LLM response generation -> UCP actions (cart/checkout).

Improvements over v1:
- Error recovery node surfaces errors gracefully
- Conversation history fed into LLM calls for multi-turn context
- LLM-based product selection instead of blind results[0]
- All RAG/UCP calls wrapped in try/except
"""

from __future__ import annotations

import json
import logging
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from config import settings
from agent.rag import get_product_rag
from agent.ucp_client import get_ucp_client

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


# ---------------------------------------------------------------------------
# Intent Detection
# ---------------------------------------------------------------------------

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
    try:
        llm = ChatOpenAI(model=settings.openai_model, temperature=0)

        messages = [SystemMessage(content=INTENT_SYSTEM_PROMPT)]

        # Include recent conversation for multi-turn context
        for msg in (state.get("conversation_history") or [])[-6:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(SystemMessage(content=f"[Previous assistant response]: {msg['content'][:200]}"))

        messages.append(HumanMessage(content=state["query"]))

        response = llm.invoke(messages)
        intent = response.content.strip().lower().strip("\"'")

        valid_intents = {"search", "buy", "cart", "checkout", "general"}
        if intent not in valid_intents:
            intent = "search"

        state["intent"] = intent
        logger.info("Detected intent: %s for query: %s", intent, state["query"])

    except Exception as e:
        logger.error("Intent detection failed: %s", e)
        state["intent"] = "search"
        state["error"] = f"Intent detection failed: {e}"

    return state


# ---------------------------------------------------------------------------
# RAG Retrieval
# ---------------------------------------------------------------------------


def retrieve_products(state: AgentState) -> AgentState:
    """Retrieve relevant products from the RAG vector store."""
    try:
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

    except Exception as e:
        logger.error("Product retrieval failed: %s", e)
        state["product_results"] = []
        state["context"] = "Product search is temporarily unavailable."
        state["error"] = f"Retrieval failed: {e}"

    return state


# ---------------------------------------------------------------------------
# LLM-based Product Selection (Phase 2.2)
# ---------------------------------------------------------------------------

SELECT_PRODUCT_PROMPT = """You are a product selection assistant. The user wants to buy a product.
Given the user's query and the available products, select the BEST matching product.

Return ONLY a JSON object with the key "index" set to the 0-based index of the best match.
Example: {"index": 0}

If none of the products match what the user wants, return: {"index": -1}"""


def select_product(state: AgentState) -> AgentState:
    """Use LLM to select the best product match instead of blindly picking results[0]."""
    products = state.get("product_results") or []
    if not products:
        state["error"] = "No products found to purchase. Please search first."
        return state

    # If only one product, no need to call LLM
    if len(products) == 1:
        return state

    try:
        llm = ChatOpenAI(model=settings.openai_model, temperature=0)

        product_list = "\n".join(
            f"{i}. {p['name']} - ${p['price']} ({p.get('category', '')})"
            for i, p in enumerate(products)
        )

        messages = [
            SystemMessage(content=SELECT_PRODUCT_PROMPT),
            HumanMessage(
                content=f"User query: {state['query']}\n\nAvailable products:\n{product_list}"
            ),
        ]

        response = llm.invoke(messages)
        text = response.content.strip()

        # Parse the JSON response
        selection = json.loads(text)
        idx = selection.get("index", 0)

        if 0 <= idx < len(products):
            # Move selected product to front
            selected = products[idx]
            state["product_results"] = [selected] + [p for i, p in enumerate(products) if i != idx]
            logger.info("LLM selected product: %s (index %d)", selected["name"], idx)
        elif idx == -1:
            state["error"] = "None of the found products match your request. Try a more specific search."

    except Exception as e:
        logger.warning("Product selection LLM call failed, using first result: %s", e)
        # Fall through — keep original order, handle_buy will use [0]

    return state


# ---------------------------------------------------------------------------
# Response Generation
# ---------------------------------------------------------------------------

RESPONSE_SYSTEM_PROMPT = """You are a helpful AI shopping assistant for an online electronics store.
You help customers find products, answer questions, and assist with purchases.

When presenting products, format them clearly with name, price, and key features.
If the user wants to buy something, confirm the product and suggest proceeding to checkout.
Be concise and helpful. Use the product context provided to give accurate information.

If no relevant products are found, let the user know and suggest alternatives."""


def generate_response(state: AgentState) -> AgentState:
    """Generate a response using the LLM with RAG context."""
    try:
        llm = ChatOpenAI(model=settings.openai_model, temperature=0.7)

        system_parts = [RESPONSE_SYSTEM_PROMPT]

        if state.get("context"):
            system_parts.append(f"\nAvailable Products:\n{state['context']}")

        if state.get("cart_id"):
            system_parts.append(f"\nCustomer has an active cart (ID: {state['cart_id']})")

        if state.get("checkout_details"):
            details = state["checkout_details"]
            system_parts.append(
                f"\nCheckout Session Created:"
                f"\n  Session ID: {details.get('id', 'N/A')}"
                f"\n  Subtotal: ${details.get('subtotal', 0)}"
                f"\n  Tax: ${details.get('tax', 0)}"
                f"\n  Total: ${details.get('total', 0)}"
                f"\n  Status: {details.get('status', 'N/A')}"
            )

        if state.get("error"):
            system_parts.append(
                f"\n[Error occurred]: {state['error']}"
                "\nPlease acknowledge the issue gracefully and suggest what the user can do."
            )

        messages = [SystemMessage(content="\n".join(system_parts))]

        # Include conversation history for multi-turn context
        for msg in (state.get("conversation_history") or [])[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(SystemMessage(content=f"[Previous response]: {msg['content'][:300]}"))

        messages.append(HumanMessage(content=state["query"]))

        response = llm.invoke(messages)
        state["response"] = response.content

    except Exception as e:
        logger.error("Response generation failed: %s", e)
        # Provide a useful fallback even if LLM is down
        if state.get("context") and state["context"] != "Product search is temporarily unavailable.":
            state["response"] = (
                f"I found some products for you, but I'm having trouble generating a detailed response.\n\n"
                f"{state['context']}"
            )
        elif state.get("error"):
            state["response"] = f"I encountered an issue: {state['error']}. Please try again."
        else:
            state["response"] = "I'm sorry, I'm having trouble processing your request right now. Please try again."

    return state


# ---------------------------------------------------------------------------
# Error Recovery Node
# ---------------------------------------------------------------------------


def handle_error(state: AgentState) -> AgentState:
    """Generate a graceful response when errors occur in action nodes."""
    error = state.get("error", "An unknown error occurred.")
    logger.warning("Error recovery triggered: %s", error)

    try:
        llm = ChatOpenAI(model=settings.openai_model, temperature=0.7)
        messages = [
            SystemMessage(
                content="You are a helpful shopping assistant. An error occurred while processing "
                "the user's request. Apologize briefly and suggest what they can do next. "
                "Be concise."
            ),
            HumanMessage(content=f"User asked: {state['query']}\nError: {error}"),
        ]
        response = llm.invoke(messages)
        state["response"] = response.content
    except Exception:
        state["response"] = (
            f"I'm sorry, something went wrong while processing your request. "
            f"Please try again or rephrase your query."
        )

    return state


# ---------------------------------------------------------------------------
# UCP Actions
# ---------------------------------------------------------------------------


def handle_buy(state: AgentState) -> AgentState:
    """Handle purchase intent: create cart, add items, create checkout."""
    client = get_ucp_client()

    if not state.get("product_results"):
        state["error"] = "No products found to purchase. Please search first."
        return state

    try:
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
        state["error"] = f"Failed to process purchase: {e}"

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
        state["error"] = f"Checkout failed: {e}"

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
        state["error"] = f"Could not retrieve cart: {e}"

    return state


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


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


def route_after_action(state: AgentState) -> str:
    """Route to error recovery if an error occurred, otherwise to respond."""
    if state.get("error"):
        return "error_recovery"
    return "respond"


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------


def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph workflow."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("detect_intent", detect_intent)
    graph.add_node("retrieve", retrieve_products)
    graph.add_node("retrieve_for_buy", retrieve_products)
    graph.add_node("select_product", select_product)
    graph.add_node("buy", handle_buy)
    graph.add_node("cart", handle_cart_view)
    graph.add_node("checkout", handle_checkout)
    graph.add_node("respond", generate_response)
    graph.add_node("error_recovery", handle_error)

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

    # Search flow: retrieve -> respond
    graph.add_edge("retrieve", "respond")

    # Buy flow: retrieve -> select_product -> buy -> (error_recovery | respond)
    graph.add_edge("retrieve_for_buy", "select_product")
    graph.add_edge("select_product", "buy")
    graph.add_conditional_edges("buy", route_after_action, {"error_recovery": "error_recovery", "respond": "respond"})

    # Cart/Checkout -> (error_recovery | respond)
    graph.add_conditional_edges("cart", route_after_action, {"error_recovery": "error_recovery", "respond": "respond"})
    graph.add_conditional_edges("checkout", route_after_action, {"error_recovery": "error_recovery", "respond": "respond"})

    # Terminal edges
    graph.add_edge("respond", END)
    graph.add_edge("error_recovery", END)

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


def run_query(
    query: str,
    cart_id: str = "",
    checkout_id: str = "",
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Run a user query through the agent pipeline.

    Args:
        query: The user's natural language query.
        cart_id: Existing cart ID for session continuity.
        checkout_id: Existing checkout ID for session continuity.
        conversation_history: Previous conversation messages for multi-turn context.

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
        "conversation_history": conversation_history or [],
    }

    result = agent.invoke(initial_state)
    return dict(result)

"""Tests for the LangGraph agent workflow with mocked LLM/RAG."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.graph import (
    AgentState,
    build_agent_graph,
    detect_intent,
    generate_response,
    handle_buy,
    handle_cart_view,
    handle_checkout,
    handle_error,
    retrieve_products,
    route_after_action,
    route_intent,
    run_query,
    select_product,
)


def _make_state(**overrides) -> AgentState:
    """Create a default AgentState with optional overrides."""
    base: AgentState = {
        "query": "test query",
        "intent": "",
        "context": "",
        "product_results": [],
        "response": "",
        "cart_id": "",
        "checkout_id": "",
        "checkout_details": {},
        "error": "",
        "conversation_history": [],
    }
    base.update(overrides)
    return base


# --- Routing ---


class TestRouting:
    def test_route_search(self):
        assert route_intent(_make_state(intent="search")) == "retrieve"

    def test_route_buy(self):
        assert route_intent(_make_state(intent="buy")) == "retrieve_then_buy"

    def test_route_cart(self):
        assert route_intent(_make_state(intent="cart")) == "cart"

    def test_route_checkout(self):
        assert route_intent(_make_state(intent="checkout")) == "checkout"

    def test_route_general(self):
        assert route_intent(_make_state(intent="general")) == "respond"

    def test_route_unknown_defaults_to_respond(self):
        assert route_intent(_make_state(intent="unknown")) == "respond"

    def test_route_after_action_error(self):
        assert route_after_action(_make_state(error="something broke")) == "error_recovery"

    def test_route_after_action_ok(self):
        assert route_after_action(_make_state(error="")) == "respond"


# --- Intent Detection ---


class TestDetectIntent:
    @patch("agent.graph.ChatOpenAI")
    def test_detect_search_intent(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="search")
        mock_llm_class.return_value = mock_llm

        state = _make_state(query="show me headphones")
        result = detect_intent(state)
        assert result["intent"] == "search"

    @patch("agent.graph.ChatOpenAI")
    def test_detect_buy_intent(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="buy")
        mock_llm_class.return_value = mock_llm

        state = _make_state(query="purchase the keyboard")
        result = detect_intent(state)
        assert result["intent"] == "buy"

    @patch("agent.graph.ChatOpenAI")
    def test_invalid_intent_falls_back_to_search(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="nonsense_intent")
        mock_llm_class.return_value = mock_llm

        state = _make_state(query="blah")
        result = detect_intent(state)
        assert result["intent"] == "search"

    @patch("agent.graph.ChatOpenAI")
    def test_intent_detection_failure_falls_back(self, mock_llm_class):
        mock_llm_class.side_effect = Exception("API down")

        state = _make_state(query="hello")
        result = detect_intent(state)
        assert result["intent"] == "search"
        assert "Intent detection failed" in result.get("error", "")

    @patch("agent.graph.ChatOpenAI")
    def test_conversation_history_included(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="buy")
        mock_llm_class.return_value = mock_llm

        history = [
            {"role": "user", "content": "show me keyboards"},
            {"role": "assistant", "content": "Here are some keyboards..."},
        ]
        state = _make_state(query="buy the first one", conversation_history=history)
        detect_intent(state)

        # Verify history was included in LLM call
        call_args = mock_llm.invoke.call_args[0][0]
        assert len(call_args) > 2  # system + history + current query


# --- Retrieval ---


class TestRetrieveProducts:
    @patch("agent.graph.get_product_rag")
    def test_retrieve_success(self, mock_get_rag):
        mock_doc = MagicMock()
        mock_doc.metadata = {
            "product_id": "SKU-001",
            "name": "Test Product",
            "price": 29.99,
            "category": "Electronics",
        }
        mock_doc.page_content = "Product: Test Product\nPrice: $29.99"

        mock_rag = MagicMock()
        mock_rag.search.return_value = [mock_doc]
        mock_rag.format_results.return_value = "1. Test Product (ID: SKU-001) - $29.99"
        mock_get_rag.return_value = mock_rag

        state = _make_state(query="headphones")
        result = retrieve_products(state)
        assert len(result["product_results"]) == 1
        assert result["product_results"][0]["name"] == "Test Product"
        assert result["context"]

    @patch("agent.graph.get_product_rag")
    def test_retrieve_failure_sets_error(self, mock_get_rag):
        mock_get_rag.side_effect = Exception("ChromaDB down")

        state = _make_state(query="headphones")
        result = retrieve_products(state)
        assert result["product_results"] == []
        assert "Retrieval failed" in result.get("error", "")


# --- Product Selection ---


class TestSelectProduct:
    @patch("agent.graph.ChatOpenAI")
    def test_select_reorders_products(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content='{"index": 1}')
        mock_llm_class.return_value = mock_llm

        products = [
            {"product_id": "A", "name": "Wrong", "price": 10, "category": ""},
            {"product_id": "B", "name": "Right", "price": 20, "category": ""},
        ]
        state = _make_state(query="buy the right one", product_results=products)
        result = select_product(state)
        assert result["product_results"][0]["product_id"] == "B"

    def test_single_product_skips_llm(self):
        products = [{"product_id": "A", "name": "Only", "price": 10, "category": ""}]
        state = _make_state(query="buy it", product_results=products)
        result = select_product(state)
        assert result["product_results"][0]["product_id"] == "A"

    def test_no_products_sets_error(self):
        state = _make_state(query="buy it", product_results=[])
        result = select_product(state)
        assert "No products found" in result.get("error", "")

    @patch("agent.graph.ChatOpenAI")
    def test_llm_failure_keeps_original_order(self, mock_llm_class):
        mock_llm_class.side_effect = Exception("API error")

        products = [
            {"product_id": "A", "name": "First", "price": 10, "category": ""},
            {"product_id": "B", "name": "Second", "price": 20, "category": ""},
        ]
        state = _make_state(query="buy", product_results=products)
        result = select_product(state)
        assert result["product_results"][0]["product_id"] == "A"


# --- Response Generation ---


class TestGenerateResponse:
    @patch("agent.graph.ChatOpenAI")
    def test_generate_response_success(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Here are some great headphones!")
        mock_llm_class.return_value = mock_llm

        state = _make_state(
            query="show headphones",
            context="1. Wireless Headphones - $99",
        )
        result = generate_response(state)
        assert result["response"] == "Here are some great headphones!"

    @patch("agent.graph.ChatOpenAI")
    def test_generate_response_with_error_context(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Sorry about the issue!")
        mock_llm_class.return_value = mock_llm

        state = _make_state(query="buy thing", error="Purchase failed")
        result = generate_response(state)
        assert result["response"] == "Sorry about the issue!"

        # Verify error was included in system prompt
        call_args = mock_llm.invoke.call_args[0][0]
        system_msg = call_args[0].content
        assert "Purchase failed" in system_msg

    @patch("agent.graph.ChatOpenAI")
    def test_generate_response_fallback_on_llm_failure(self, mock_llm_class):
        mock_llm_class.side_effect = Exception("LLM down")

        state = _make_state(
            query="search headphones",
            context="1. Headphones - $99",
        )
        result = generate_response(state)
        assert "trouble generating" in result["response"]
        assert "Headphones" in result["response"]

    @patch("agent.graph.ChatOpenAI")
    def test_generate_response_fallback_with_error(self, mock_llm_class):
        mock_llm_class.side_effect = Exception("LLM down")

        state = _make_state(query="buy thing", error="Cart failed")
        result = generate_response(state)
        assert "Cart failed" in result["response"]


# --- Error Recovery ---


class TestErrorRecovery:
    @patch("agent.graph.ChatOpenAI")
    def test_error_recovery_with_llm(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Sorry, something went wrong.")
        mock_llm_class.return_value = mock_llm

        state = _make_state(query="buy keyboard", error="Out of stock")
        result = handle_error(state)
        assert "Sorry" in result["response"]

    @patch("agent.graph.ChatOpenAI")
    def test_error_recovery_fallback(self, mock_llm_class):
        mock_llm_class.side_effect = Exception("LLM also down")

        state = _make_state(query="buy keyboard", error="Out of stock")
        result = handle_error(state)
        assert "something went wrong" in result["response"]


# --- UCP Actions ---


class TestHandleBuy:
    @patch("agent.graph.get_ucp_client")
    def test_buy_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.create_cart.return_value = {"cart": {"id": "cart-123"}}
        mock_client.add_to_cart.return_value = {}
        mock_client.create_checkout.return_value = {
            "id": "checkout-456",
            "subtotal": 99.99,
            "tax": 8.0,
            "total": 107.99,
            "status": "pending",
        }
        mock_get_client.return_value = mock_client

        state = _make_state(
            query="buy headphones",
            product_results=[{"product_id": "SKU-001", "name": "Headphones", "price": 99.99}],
        )
        result = handle_buy(state)
        assert result["cart_id"] == "cart-123"
        assert result["checkout_id"] == "checkout-456"
        assert result["error"] == ""

    @patch("agent.graph.get_ucp_client")
    def test_buy_reuses_existing_cart(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.add_to_cart.return_value = {}
        mock_client.create_checkout.return_value = {"id": "checkout-789"}
        mock_get_client.return_value = mock_client

        state = _make_state(
            query="buy headphones",
            cart_id="existing-cart",
            product_results=[{"product_id": "SKU-001", "name": "Headphones", "price": 99.99}],
        )
        result = handle_buy(state)
        mock_client.create_cart.assert_not_called()
        assert result["cart_id"] == "existing-cart"

    def test_buy_no_products_sets_error(self):
        state = _make_state(query="buy", product_results=[])
        result = handle_buy(state)
        assert "No products found" in result["error"]

    @patch("agent.graph.get_ucp_client")
    def test_buy_failure_sets_error(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.create_cart.side_effect = Exception("Network error")
        mock_get_client.return_value = mock_client

        state = _make_state(
            query="buy headphones",
            product_results=[{"product_id": "SKU-001", "name": "Headphones", "price": 99.99}],
        )
        result = handle_buy(state)
        assert "Failed to process purchase" in result["error"]


class TestHandleCheckout:
    @patch("agent.graph.get_ucp_client")
    def test_checkout_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.confirm_checkout.return_value = {"status": "confirmed", "total": 107.99}
        mock_get_client.return_value = mock_client

        state = _make_state(checkout_id="checkout-123")
        result = handle_checkout(state)
        assert result["checkout_details"]["status"] == "confirmed"

    def test_checkout_no_session_sets_error(self):
        state = _make_state(checkout_id="")
        result = handle_checkout(state)
        assert "No active checkout" in result["error"]


class TestHandleCartView:
    @patch("agent.graph.get_ucp_client")
    def test_cart_view_with_items(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_cart.return_value = {
            "cart": {
                "items": [{"name": "Headphones", "quantity": 1, "price": 99.99}],
                "total": 99.99,
            }
        }
        mock_get_client.return_value = mock_client

        state = _make_state(cart_id="cart-123")
        result = handle_cart_view(state)
        assert "Headphones" in result["context"]
        assert "99.99" in result["context"]

    def test_cart_view_no_cart(self):
        state = _make_state(cart_id="")
        result = handle_cart_view(state)
        assert "No active cart" in result["context"]


# --- Graph Construction ---


class TestGraphConstruction:
    def test_graph_compiles(self):
        graph = build_agent_graph()
        compiled = graph.compile()
        assert compiled is not None

    def test_graph_has_all_nodes(self):
        graph = build_agent_graph()
        node_names = set(graph.nodes.keys())
        expected = {
            "detect_intent",
            "retrieve",
            "retrieve_for_buy",
            "select_product",
            "buy",
            "cart",
            "checkout",
            "respond",
            "error_recovery",
        }
        assert expected.issubset(node_names)


# --- run_query ---


class TestRunQuery:
    @patch("agent.graph.get_agent")
    def test_run_query_passes_history(self, mock_get_agent):
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "query": "hello",
            "response": "Hi there!",
            "intent": "general",
        }
        mock_get_agent.return_value = mock_agent

        history = [{"role": "user", "content": "previous message"}]
        result = run_query("hello", conversation_history=history)

        call_state = mock_agent.invoke.call_args[0][0]
        assert call_state["conversation_history"] == history
        assert result["response"] == "Hi there!"

    @patch("agent.graph.get_agent")
    def test_run_query_default_state(self, mock_get_agent):
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"response": "OK"}
        mock_get_agent.return_value = mock_agent

        run_query("test")
        call_state = mock_agent.invoke.call_args[0][0]
        assert call_state["query"] == "test"
        assert call_state["cart_id"] == ""
        assert call_state["conversation_history"] == []

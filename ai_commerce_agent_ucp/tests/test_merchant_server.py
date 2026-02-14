"""Tests for the UCP merchant server."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from merchant_server.server import app, load_products, _products, _carts, _checkout_sessions


@pytest.fixture(autouse=True)
def setup_products(tmp_path):
    """Load test products before each test and clean up after."""
    products_data = [
        {
            "id": "TEST-001",
            "name": "Test Headphones",
            "price": 99.99,
            "description": "Noise-cancelling test headphones",
            "category": "Electronics",
            "quantity": 10,
            "rating": 4.5,
            "brand": "TestBrand",
        },
        {
            "id": "TEST-002",
            "name": "Test USB Cable",
            "price": 19.99,
            "description": "Fast charging USB-C cable",
            "category": "Accessories",
            "quantity": 50,
            "rating": 4.0,
            "brand": "CableCo",
        },
        {
            "id": "TEST-003",
            "name": "Test Smart Plug",
            "price": 29.99,
            "description": "WiFi smart plug for home automation",
            "category": "Smart Home",
            "quantity": 0,
            "rating": 3.8,
            "brand": "HomeTech",
        },
    ]

    products_file = tmp_path / "products.json"
    products_file.write_text(json.dumps(products_data))
    load_products(products_file)

    yield

    _products.clear()
    _carts.clear()
    _checkout_sessions.clear()


@pytest.fixture
def client():
    """Create a test client for the merchant server."""
    return TestClient(app)


# --- UCP Discovery ---


class TestUCPDiscovery:
    def test_well_known_ucp(self, client):
        resp = client.get("/.well-known/ucp")
        assert resp.status_code == 200
        data = resp.json()
        assert data["merchant_name"] == "AI Commerce Demo Store"
        assert data["protocol"] == "ucp"
        assert len(data["capabilities"]) > 0
        assert "google_pay" in data["payment_handlers"]

    def test_capabilities_structure(self, client):
        resp = client.get("/.well-known/ucp")
        data = resp.json()
        for cap in data["capabilities"]:
            assert "name" in cap
            assert "endpoint" in cap
            assert "methods" in cap
            assert "description" in cap


# --- Products ---


class TestProducts:
    def test_list_all_products(self, client):
        resp = client.get("/products")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["products"]) == 3

    def test_filter_by_category(self, client):
        resp = client.get("/products?category=Electronics")
        data = resp.json()
        assert data["total"] == 1
        assert data["products"][0]["name"] == "Test Headphones"

    def test_filter_by_price_range(self, client):
        resp = client.get("/products?min_price=20&max_price=50")
        data = resp.json()
        assert data["total"] == 1
        assert data["products"][0]["id"] == "TEST-003"

    def test_get_product_by_id(self, client):
        resp = client.get("/products/TEST-001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Headphones"
        assert data["price"] == 99.99

    def test_get_product_not_found(self, client):
        resp = client.get("/products/NONEXISTENT")
        assert resp.status_code == 404

    def test_search_products(self, client):
        resp = client.post("/products/search", json={"query": "headphones"})
        data = resp.json()
        assert data["total"] >= 1
        assert any("Headphones" in p["name"] for p in data["products"])

    def test_search_products_with_category(self, client):
        resp = client.post(
            "/products/search",
            json={"query": "test", "category": "Accessories"},
        )
        data = resp.json()
        assert all(p["category"] == "Accessories" for p in data["products"])


# --- Cart ---


class TestCart:
    def test_create_cart(self, client):
        resp = client.post("/cart")
        assert resp.status_code == 200
        data = resp.json()
        assert "cart" in data
        assert data["cart"]["id"]
        assert data["cart"]["items"] == []
        assert data["cart"]["total"] == 0

    def test_add_to_cart(self, client):
        # Create cart
        cart_resp = client.post("/cart")
        cart_id = cart_resp.json()["cart"]["id"]

        # Add item
        resp = client.post(
            f"/cart/{cart_id}/items",
            json={"product_id": "TEST-001", "quantity": 2},
        )
        assert resp.status_code == 200
        cart = resp.json()["cart"]
        assert len(cart["items"]) == 1
        assert cart["items"][0]["product_id"] == "TEST-001"
        assert cart["items"][0]["quantity"] == 2
        assert cart["total"] == 199.98

    def test_add_duplicate_item_increments(self, client):
        cart_resp = client.post("/cart")
        cart_id = cart_resp.json()["cart"]["id"]

        client.post(f"/cart/{cart_id}/items", json={"product_id": "TEST-001", "quantity": 1})
        resp = client.post(
            f"/cart/{cart_id}/items",
            json={"product_id": "TEST-001", "quantity": 2},
        )
        cart = resp.json()["cart"]
        assert cart["items"][0]["quantity"] == 3

    def test_add_to_cart_insufficient_stock(self, client):
        cart_resp = client.post("/cart")
        cart_id = cart_resp.json()["cart"]["id"]

        resp = client.post(
            f"/cart/{cart_id}/items",
            json={"product_id": "TEST-001", "quantity": 999},
        )
        assert resp.status_code == 400

    def test_remove_from_cart(self, client):
        cart_resp = client.post("/cart")
        cart_id = cart_resp.json()["cart"]["id"]

        client.post(f"/cart/{cart_id}/items", json={"product_id": "TEST-001", "quantity": 1})
        resp = client.delete(f"/cart/{cart_id}/items/TEST-001")
        assert resp.status_code == 200
        assert len(resp.json()["cart"]["items"]) == 0

    def test_get_cart_not_found(self, client):
        resp = client.get("/cart/nonexistent-id")
        assert resp.status_code == 404


# --- Checkout ---


class TestCheckout:
    def test_create_checkout_session(self, client):
        resp = client.post(
            "/checkout-sessions",
            json={
                "line_items": [{"product_id": "TEST-001", "quantity": 1}],
                "payment_handler": "google_pay",
                "currency": "USD",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"]
        assert data["status"] == "pending"
        assert data["subtotal"] == 99.99
        assert data["tax"] == 8.0  # 8% of 99.99 rounded
        assert data["total"] == 107.99
        assert len(data["line_items"]) == 1

    def test_create_checkout_product_not_found(self, client):
        resp = client.post(
            "/checkout-sessions",
            json={"line_items": [{"product_id": "NONEXISTENT", "quantity": 1}]},
        )
        assert resp.status_code == 404

    def test_confirm_checkout(self, client):
        # Create session
        create_resp = client.post(
            "/checkout-sessions",
            json={"line_items": [{"product_id": "TEST-002", "quantity": 2}]},
        )
        session_id = create_resp.json()["id"]

        # Confirm
        resp = client.post(
            f"/checkout-sessions/{session_id}/confirm",
            json={"payment_token": "test_token"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "confirmed"
        assert data["confirmed_at"] is not None

        # Verify inventory decreased
        product = client.get("/products/TEST-002").json()
        assert product["quantity"] == 48  # 50 - 2

    def test_confirm_already_confirmed(self, client):
        create_resp = client.post(
            "/checkout-sessions",
            json={"line_items": [{"product_id": "TEST-001", "quantity": 1}]},
        )
        session_id = create_resp.json()["id"]

        client.post(
            f"/checkout-sessions/{session_id}/confirm",
            json={"payment_token": "token"},
        )
        # Try again
        resp = client.post(
            f"/checkout-sessions/{session_id}/confirm",
            json={"payment_token": "token"},
        )
        assert resp.status_code == 400

    def test_get_checkout_session(self, client):
        create_resp = client.post(
            "/checkout-sessions",
            json={"line_items": [{"product_id": "TEST-001", "quantity": 1}]},
        )
        session_id = create_resp.json()["id"]

        resp = client.get(f"/checkout-sessions/{session_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == session_id


# --- Health ---


class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["products_loaded"] == 3

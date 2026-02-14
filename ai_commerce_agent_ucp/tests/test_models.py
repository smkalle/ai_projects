"""Tests for Pydantic models."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from merchant_server.models import (
    Cart,
    CartItem,
    CheckoutSession,
    CheckoutStatus,
    LineItem,
    Product,
    ProductSearchRequest,
    UCPCapability,
    UCPManifest,
)


class TestProduct:
    def test_create_product(self):
        p = Product(
            id="SKU-001",
            name="Test Product",
            price=29.99,
            description="A test product",
        )
        assert p.id == "SKU-001"
        assert p.price == 29.99
        assert p.category == "General"
        assert p.quantity == 0

    def test_product_with_all_fields(self):
        p = Product(
            id="SKU-002",
            name="Full Product",
            price=49.99,
            description="Full description",
            category="Electronics",
            quantity=100,
            rating=4.5,
            brand="TestBrand",
        )
        assert p.brand == "TestBrand"
        assert p.rating == 4.5


class TestCart:
    def test_empty_cart(self):
        cart = Cart(id="cart-1")
        assert cart.items == []
        assert cart.total == 0

    def test_recalculate_total(self):
        cart = Cart(
            id="cart-1",
            items=[
                CartItem(product_id="A", quantity=2, price=10.0, name="Item A"),
                CartItem(product_id="B", quantity=1, price=25.50, name="Item B"),
            ],
        )
        cart.recalculate_total()
        assert cart.total == 45.50

    def test_cart_currency_default(self):
        cart = Cart(id="cart-1")
        assert cart.currency == "USD"


class TestCheckoutSession:
    def test_create_session(self):
        session = CheckoutSession(
            id="sess-1",
            line_items=[
                LineItem(product_id="SKU-001", quantity=1, price=99.99, name="Widget"),
            ],
            subtotal=99.99,
            tax=8.00,
            total=107.99,
        )
        assert session.status == CheckoutStatus.PENDING
        assert session.total == 107.99
        assert session.payment_handler == "google_pay"

    def test_checkout_status_values(self):
        assert CheckoutStatus.PENDING == "pending"
        assert CheckoutStatus.CONFIRMED == "confirmed"
        assert CheckoutStatus.COMPLETED == "completed"


class TestUCPManifest:
    def test_manifest(self):
        manifest = UCPManifest(
            merchant_name="Test Store",
            capabilities=[
                UCPCapability(
                    name="search",
                    endpoint="/search",
                    methods=["POST"],
                    description="Search products",
                ),
            ],
            payment_handlers=["google_pay"],
            supported_currencies=["USD"],
        )
        assert manifest.protocol == "ucp"
        assert manifest.version == "1.0"
        assert len(manifest.capabilities) == 1


class TestProductSearchRequest:
    def test_defaults(self):
        req = ProductSearchRequest()
        assert req.query == ""
        assert req.limit == 10

    def test_with_filters(self):
        req = ProductSearchRequest(
            query="headphones",
            category="Electronics",
            min_price=50.0,
            max_price=200.0,
        )
        assert req.min_price == 50.0

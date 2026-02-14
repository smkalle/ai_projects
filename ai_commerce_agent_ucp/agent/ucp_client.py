"""UCP client for communicating with the merchant server.

Wraps HTTP calls to UCP endpoints for product search, cart management,
and checkout session creation/confirmation.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import requests

from config import settings

logger = logging.getLogger(__name__)


class UCPClient:
    """Client for interacting with a UCP-compliant merchant server."""

    def __init__(self, base_url: str = ""):
        self.base_url = (base_url or settings.merchant_base_url).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def discover(self) -> dict[str, Any]:
        """Fetch the UCP discovery manifest."""
        resp = self.session.get(f"{self.base_url}/.well-known/ucp")
        resp.raise_for_status()
        return resp.json()

    # --- Products ---

    def list_products(
        self,
        category: str = "",
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """List products with optional filters."""
        params: dict[str, Any] = {"limit": limit}
        if category:
            params["category"] = category
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price

        resp = self.session.get(f"{self.base_url}/products", params=params)
        resp.raise_for_status()
        return resp.json()

    def search_products(
        self,
        query: str,
        category: str = "",
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search products by query."""
        payload: dict[str, Any] = {"query": query, "limit": limit}
        if category:
            payload["category"] = category
        if min_price is not None:
            payload["min_price"] = min_price
        if max_price is not None:
            payload["max_price"] = max_price

        resp = self.session.post(f"{self.base_url}/products/search", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_product(self, product_id: str) -> dict[str, Any]:
        """Get a single product by ID."""
        resp = self.session.get(f"{self.base_url}/products/{product_id}")
        resp.raise_for_status()
        return resp.json()

    # --- Cart ---

    def create_cart(self) -> dict[str, Any]:
        """Create a new shopping cart."""
        resp = self.session.post(f"{self.base_url}/cart")
        resp.raise_for_status()
        return resp.json()

    def get_cart(self, cart_id: str) -> dict[str, Any]:
        """Get cart details."""
        resp = self.session.get(f"{self.base_url}/cart/{cart_id}")
        resp.raise_for_status()
        return resp.json()

    def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1) -> dict[str, Any]:
        """Add an item to the cart."""
        resp = self.session.post(
            f"{self.base_url}/cart/{cart_id}/items",
            json={"product_id": product_id, "quantity": quantity},
        )
        resp.raise_for_status()
        return resp.json()

    def remove_from_cart(self, cart_id: str, product_id: str) -> dict[str, Any]:
        """Remove an item from the cart."""
        resp = self.session.delete(f"{self.base_url}/cart/{cart_id}/items/{product_id}")
        resp.raise_for_status()
        return resp.json()

    # --- Checkout ---

    def create_checkout(
        self,
        line_items: list[dict[str, Any]],
        payment_handler: str = "",
        currency: str = "",
        customer_email: str = "",
    ) -> dict[str, Any]:
        """Create a checkout session."""
        payload: dict[str, Any] = {
            "line_items": line_items,
            "payment_handler": payment_handler or settings.default_payment_handler,
            "currency": currency or settings.default_currency,
        }
        if customer_email:
            payload["customer_email"] = customer_email

        resp = self.session.post(f"{self.base_url}/checkout-sessions", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_checkout(self, session_id: str) -> dict[str, Any]:
        """Get checkout session details."""
        resp = self.session.get(f"{self.base_url}/checkout-sessions/{session_id}")
        resp.raise_for_status()
        return resp.json()

    def confirm_checkout(
        self, session_id: str, payment_token: str = "simulated_token"
    ) -> dict[str, Any]:
        """Confirm a checkout session."""
        resp = self.session.post(
            f"{self.base_url}/checkout-sessions/{session_id}/confirm",
            json={"payment_token": payment_token},
        )
        resp.raise_for_status()
        return resp.json()

    # --- Health ---

    def health_check(self) -> dict[str, Any]:
        """Check if the merchant server is healthy."""
        try:
            resp = self.session.get(f"{self.base_url}/health")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}


# Module-level convenience instance
_default_client: Optional[UCPClient] = None


def get_ucp_client() -> UCPClient:
    """Get or create the default UCPClient instance."""
    global _default_client
    if _default_client is None:
        _default_client = UCPClient()
    return _default_client

"""Pydantic models for the UCP merchant server."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --- Product Models ---


class Product(BaseModel):
    """A product in the merchant catalog."""

    id: str
    name: str
    price: float
    description: str
    category: str = "General"
    quantity: int = 0
    rating: float = 0.0
    brand: str = ""


class ProductSearchRequest(BaseModel):
    """Search request for products."""

    query: str = ""
    category: str = ""
    min_price: float | None = None
    max_price: float | None = None
    limit: int = 10


class ProductSearchResponse(BaseModel):
    """Search response with matching products."""

    products: list[Product]
    total: int


# --- Cart Models ---


class CartItem(BaseModel):
    """An item in a shopping cart."""

    product_id: str
    quantity: int = 1
    price: float = 0.0
    name: str = ""


class Cart(BaseModel):
    """Shopping cart."""

    id: str
    items: list[CartItem] = Field(default_factory=list)
    total: float = 0.0
    currency: str = "USD"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def recalculate_total(self) -> None:
        self.total = round(sum(item.price * item.quantity for item in self.items), 2)


class AddToCartRequest(BaseModel):
    """Request to add an item to cart."""

    product_id: str
    quantity: int = 1


class UpdateCartItemRequest(BaseModel):
    """Request to update a cart item's quantity."""

    quantity: int


class CartResponse(BaseModel):
    """Response containing cart details."""

    cart: Cart


# --- Checkout Models ---


class CheckoutStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class LineItem(BaseModel):
    """Line item for checkout."""

    product_id: str
    quantity: int = 1
    price: float = 0.0
    name: str = ""


class CheckoutSessionRequest(BaseModel):
    """Request to create a checkout session."""

    line_items: list[LineItem]
    payment_handler: str = "google_pay"
    currency: str = "USD"
    customer_email: str = ""


class CheckoutSession(BaseModel):
    """A checkout session."""

    id: str
    status: CheckoutStatus = CheckoutStatus.PENDING
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    currency: str = "USD"
    payment_handler: str = "google_pay"
    customer_email: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    confirmed_at: Optional[str] = None


class ConfirmCheckoutRequest(BaseModel):
    """Request to confirm a checkout session."""

    payment_token: str = "simulated_token"


# --- UCP Discovery Models ---


class UCPCapability(BaseModel):
    """A capability exposed by the merchant."""

    name: str
    endpoint: str
    methods: list[str]
    description: str


class UCPManifest(BaseModel):
    """UCP discovery manifest at /.well-known/ucp."""

    merchant_name: str
    version: str = "1.0"
    protocol: str = "ucp"
    capabilities: list[UCPCapability]
    payment_handlers: list[str]
    supported_currencies: list[str]

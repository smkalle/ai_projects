"""UCP-compliant merchant server built with FastAPI.

Simulates a retail backend exposing UCP endpoints for product discovery,
cart management, and checkout.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .models import (
    AddToCartRequest,
    Cart,
    CartItem,
    CartResponse,
    CheckoutSession,
    CheckoutStatus,
    CheckoutSessionRequest,
    ConfirmCheckoutRequest,
    LineItem,
    Product,
    ProductSearchRequest,
    ProductSearchResponse,
    UCPCapability,
    UCPManifest,
)

app = FastAPI(
    title="UCP Merchant Server",
    description="A UCP-compliant merchant server simulator for AI commerce agents",
    version="1.0.0",
)

# In-memory stores
_products: dict[str, Product] = {}
_carts: dict[str, Cart] = {}
_checkout_sessions: dict[str, CheckoutSession] = {}


def load_products(path: str | Path) -> None:
    """Load products from a JSON file into memory."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Products file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    _products.clear()
    for item in data:
        product = Product(**item)
        _products[product.id] = product


def get_products_store() -> dict[str, Product]:
    """Return the products store (for testing)."""
    return _products


# --- UCP Discovery ---


@app.get("/.well-known/ucp")
def ucp_discovery() -> UCPManifest:
    """UCP discovery endpoint. Returns the merchant manifest."""
    return UCPManifest(
        merchant_name="AI Commerce Demo Store",
        version="1.0",
        protocol="ucp",
        capabilities=[
            UCPCapability(
                name="product_search",
                endpoint="/products/search",
                methods=["POST"],
                description="Search and discover products in the catalog",
            ),
            UCPCapability(
                name="product_detail",
                endpoint="/products/{product_id}",
                methods=["GET"],
                description="Get detailed information about a specific product",
            ),
            UCPCapability(
                name="cart",
                endpoint="/cart",
                methods=["GET", "POST"],
                description="Manage shopping cart (view, add items)",
            ),
            UCPCapability(
                name="checkout",
                endpoint="/checkout-sessions",
                methods=["POST"],
                description="Create and manage checkout sessions",
            ),
        ],
        payment_handlers=["google_pay", "credit_card", "paypal"],
        supported_currencies=["USD", "EUR", "GBP"],
    )


# --- Product Endpoints ---


@app.get("/products")
def list_products(
    category: str = "",
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 50,
) -> ProductSearchResponse:
    """List all products with optional filters."""
    results = list(_products.values())

    if category:
        results = [p for p in results if p.category.lower() == category.lower()]
    if min_price is not None:
        results = [p for p in results if p.price >= min_price]
    if max_price is not None:
        results = [p for p in results if p.price <= max_price]

    results = results[:limit]
    return ProductSearchResponse(products=results, total=len(results))


@app.post("/products/search")
def search_products(request: ProductSearchRequest) -> ProductSearchResponse:
    """Search products by query string (simple keyword matching)."""
    query_lower = request.query.lower()
    results = []

    for product in _products.values():
        searchable = f"{product.name} {product.description} {product.category} {product.brand}"
        if query_lower in searchable.lower():
            results.append(product)

    if request.category:
        results = [p for p in results if p.category.lower() == request.category.lower()]
    if request.min_price is not None:
        results = [p for p in results if p.price >= request.min_price]
    if request.max_price is not None:
        results = [p for p in results if p.price <= request.max_price]

    results = results[: request.limit]
    return ProductSearchResponse(products=results, total=len(results))


@app.get("/products/{product_id}")
def get_product(product_id: str) -> Product:
    """Get a product by ID."""
    product = _products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


# --- Cart Endpoints ---


@app.post("/cart")
def create_cart() -> CartResponse:
    """Create a new shopping cart."""
    cart = Cart(id=str(uuid.uuid4()))
    _carts[cart.id] = cart
    return CartResponse(cart=cart)


@app.get("/cart/{cart_id}")
def get_cart(cart_id: str) -> CartResponse:
    """Get cart by ID."""
    cart = _carts.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart {cart_id} not found")
    return CartResponse(cart=cart)


@app.post("/cart/{cart_id}/items")
def add_to_cart(cart_id: str, request: AddToCartRequest) -> CartResponse:
    """Add an item to an existing cart."""
    cart = _carts.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart {cart_id} not found")

    product = _products.get(request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {request.product_id} not found")

    if product.quantity < request.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock for {product.name}. Available: {product.quantity}",
        )

    # Check if item already in cart
    existing = next((i for i in cart.items if i.product_id == request.product_id), None)
    if existing:
        existing.quantity += request.quantity
    else:
        cart.items.append(
            CartItem(
                product_id=product.id,
                quantity=request.quantity,
                price=product.price,
                name=product.name,
            )
        )

    cart.recalculate_total()
    return CartResponse(cart=cart)


@app.delete("/cart/{cart_id}/items/{product_id}")
def remove_from_cart(cart_id: str, product_id: str) -> CartResponse:
    """Remove an item from the cart."""
    cart = _carts.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart {cart_id} not found")

    cart.items = [i for i in cart.items if i.product_id != product_id]
    cart.recalculate_total()
    return CartResponse(cart=cart)


# --- Checkout Endpoints ---


@app.post("/checkout-sessions")
def create_checkout_session(request: CheckoutSessionRequest) -> CheckoutSession:
    """Create a new checkout session from line items."""
    session_id = str(uuid.uuid4())
    line_items: list[LineItem] = []

    for item in request.line_items:
        product = _products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}",
            )

        line_items.append(
            LineItem(
                product_id=product.id,
                quantity=item.quantity,
                price=product.price,
                name=product.name,
            )
        )

    subtotal = round(sum(li.price * li.quantity for li in line_items), 2)
    tax = round(subtotal * 0.08, 2)  # 8% tax
    total = round(subtotal + tax, 2)

    session = CheckoutSession(
        id=session_id,
        status=CheckoutStatus.PENDING,
        line_items=line_items,
        subtotal=subtotal,
        tax=tax,
        total=total,
        currency=request.currency,
        payment_handler=request.payment_handler,
        customer_email=request.customer_email,
    )

    _checkout_sessions[session_id] = session
    return session


@app.get("/checkout-sessions/{session_id}")
def get_checkout_session(session_id: str) -> CheckoutSession:
    """Get a checkout session by ID."""
    session = _checkout_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Checkout session {session_id} not found")
    return session


@app.post("/checkout-sessions/{session_id}/confirm")
def confirm_checkout(session_id: str, request: ConfirmCheckoutRequest) -> CheckoutSession:
    """Confirm a checkout session (simulates payment processing)."""
    session = _checkout_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Checkout session {session_id} not found")

    if session.status != CheckoutStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Session is {session.status.value}, cannot confirm",
        )

    # Simulate payment and reduce inventory
    for li in session.line_items:
        product = _products.get(li.product_id)
        if product:
            product.quantity -= li.quantity

    from datetime import datetime

    session.status = CheckoutStatus.CONFIRMED
    session.confirmed_at = datetime.utcnow().isoformat()
    return session


# --- Health Check ---


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy", "products_loaded": len(_products)}

"""Merchant server app with lifespan for product loading.

This module provides a configured FastAPI app that loads products on startup.
Use this when running the merchant server as a standalone process.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).parent.parent.resolve()
_DEFAULT_PRODUCTS = _BASE_DIR / "data" / "products.json"


@asynccontextmanager
async def merchant_lifespan(app: FastAPI):
    """Lifespan handler that loads products on startup."""
    from .server import load_products

    products_path = _DEFAULT_PRODUCTS
    try:
        load_products(products_path)
        logger.info("Loaded products from %s", products_path)
    except FileNotFoundError:
        logger.warning(
            "Products file not found at %s, starting with empty catalog", products_path
        )
    except Exception as e:
        logger.error("Failed to load products: %s", e)

    yield


def create_merchant_app() -> FastAPI:
    """Create a merchant server app with product loading lifespan."""
    from .server import app

    app.router.lifespan_context = merchant_lifespan
    return app

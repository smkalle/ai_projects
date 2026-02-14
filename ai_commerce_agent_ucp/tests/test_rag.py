"""Tests for the RAG module (keyword search fallback)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.rag import ProductRAG, _keyword_search


@pytest.fixture
def products_file(tmp_path):
    """Create a temporary products JSON file."""
    products = [
        {
            "id": "SKU-001",
            "name": "Wireless Headphones",
            "price": 99.99,
            "description": "Noise-cancelling wireless headphones with great bass",
            "category": "Electronics",
            "brand": "AudioTech",
            "rating": 4.5,
            "quantity": 10,
        },
        {
            "id": "SKU-002",
            "name": "USB-C Cable",
            "price": 12.99,
            "description": "Fast charging braided USB-C cable",
            "category": "Accessories",
            "brand": "CablePro",
            "rating": 4.0,
            "quantity": 100,
        },
        {
            "id": "SKU-003",
            "name": "Mechanical Keyboard",
            "price": 149.99,
            "description": "RGB mechanical gaming keyboard with cherry switches",
            "category": "Electronics",
            "brand": "KeyMaster",
            "rating": 4.8,
            "quantity": 5,
        },
    ]
    path = tmp_path / "products.json"
    path.write_text(json.dumps(products))
    return str(path)


# --- Keyword Search ---


class TestKeywordSearch:
    def test_search_by_name(self, products_file):
        results = _keyword_search("headphones", products_file)
        assert len(results) >= 1
        assert any("Headphones" in doc.metadata["name"] for doc in results)

    def test_search_by_category(self, products_file):
        results = _keyword_search("electronics", products_file)
        assert len(results) >= 2

    def test_search_by_brand(self, products_file):
        results = _keyword_search("audiotech", products_file)
        assert len(results) >= 1
        assert results[0].metadata["brand"] == "AudioTech"

    def test_search_by_description(self, products_file):
        results = _keyword_search("gaming", products_file)
        assert len(results) >= 1
        assert results[0].metadata["name"] == "Mechanical Keyboard"

    def test_search_no_results(self, products_file):
        results = _keyword_search("xyznonexistent", products_file)
        assert len(results) == 0

    def test_search_limit(self, products_file):
        results = _keyword_search("cable headphones keyboard", products_file, k=2)
        assert len(results) <= 2

    def test_search_nonexistent_file(self, tmp_path):
        results = _keyword_search("test", str(tmp_path / "missing.json"))
        assert results == []

    def test_search_result_metadata(self, products_file):
        results = _keyword_search("headphones", products_file)
        assert len(results) >= 1
        meta = results[0].metadata
        assert "product_id" in meta
        assert "name" in meta
        assert "price" in meta
        assert "category" in meta

    def test_search_result_page_content(self, products_file):
        results = _keyword_search("keyboard", products_file)
        assert len(results) >= 1
        content = results[0].page_content
        assert "Mechanical Keyboard" in content
        assert "$149.99" in content

    def test_multi_word_search_scored(self, products_file):
        results = _keyword_search("wireless headphones bass", products_file)
        assert len(results) >= 1
        # The headphones should be first due to highest score
        assert results[0].metadata["name"] == "Wireless Headphones"


# --- ProductRAG ---


class TestProductRAG:
    def test_rag_uninitialized_uses_keyword(self, products_file):
        rag = ProductRAG(products_path=products_file)
        # _initialized is False, should fallback to keyword search
        results = rag.search("headphones")
        assert len(results) >= 1
        assert any("Headphones" in doc.metadata["name"] for doc in results)

    def test_rag_search_with_scores_uninitialized(self, products_file):
        rag = ProductRAG(products_path=products_file)
        results = rag.search_with_scores("keyboard")
        assert len(results) >= 1
        doc, score = results[0]
        assert score == 1.0  # keyword fallback returns 1.0

    def test_format_results_empty(self, products_file):
        rag = ProductRAG(products_path=products_file)
        assert rag.format_results([]) == "No products found matching your query."

    def test_format_results_with_docs(self, products_file):
        rag = ProductRAG(products_path=products_file)
        docs = rag.search("headphones")
        formatted = rag.format_results(docs)
        assert "Wireless Headphones" in formatted
        assert "SKU-001" in formatted

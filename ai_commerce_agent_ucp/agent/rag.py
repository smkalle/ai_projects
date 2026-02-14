"""RAG (Retrieval-Augmented Generation) module for product retrieval.

Uses ChromaDB as the vector store and OpenAI embeddings to enable
semantic search over the product catalog. Falls back to keyword search
if embeddings are unavailable.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from langchain_core.documents import Document

from config import settings

logger = logging.getLogger(__name__)


def _keyword_search(query: str, products_path: str | Path = "", k: int = 5) -> list[Document]:
    """Fallback keyword search when vector store is unavailable.

    Loads products from JSON and matches on name/description/category/brand.
    """
    path = Path(products_path or settings.products_json_path)
    if not path.exists():
        return []

    with open(path) as f:
        products = json.load(f)

    query_terms = query.lower().split()
    scored: list[tuple[dict, int]] = []

    for p in products:
        searchable = (
            f"{p['name']} {p['description']} {p.get('category', '')} {p.get('brand', '')}"
        ).lower()
        score = sum(1 for term in query_terms if term in searchable)
        if score > 0:
            scored.append((p, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    docs = []
    for p, _ in scored[:k]:
        text = (
            f"Product: {p['name']}\n"
            f"ID: {p['id']}\n"
            f"Price: ${p['price']}\n"
            f"Category: {p.get('category', 'General')}\n"
            f"Brand: {p.get('brand', 'N/A')}\n"
            f"Rating: {p.get('rating', 'N/A')}/5\n"
            f"Description: {p['description']}\n"
            f"In Stock: {p.get('quantity', 0)} units"
        )
        doc = Document(
            page_content=text,
            metadata={
                "product_id": p["id"],
                "name": p["name"],
                "price": p["price"],
                "category": p.get("category", "General"),
                "brand": p.get("brand", ""),
                "quantity": p.get("quantity", 0),
            },
        )
        docs.append(doc)

    return docs


class ProductRAG:
    """Manages the product vector store for semantic retrieval."""

    def __init__(
        self,
        collection_name: str = "",
        persist_directory: str = "",
        embedding_model: str = "",
        products_path: str = "",
    ):
        self.collection_name = collection_name or settings.chroma_collection_name
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        self.embedding_model = embedding_model or settings.embedding_model
        self.products_path = products_path or settings.products_json_path

        self._embeddings = None
        self._vectorstore = None
        self._initialized = False

    @property
    def embeddings(self):
        if self._embeddings is None:
            from langchain_openai import OpenAIEmbeddings

            self._embeddings = OpenAIEmbeddings(model=self.embedding_model)
        return self._embeddings

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            from langchain_community.vectorstores import Chroma

            self._vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
        return self._vectorstore

    def load_products(self, products_path: str | Path = "") -> int:
        """Load products from JSON into the vector store."""
        from langchain_community.vectorstores import Chroma
        from langchain_text_splitters import CharacterTextSplitter

        path = Path(products_path or self.products_path)
        self.products_path = str(path)

        if not path.exists():
            raise FileNotFoundError(f"Products file not found: {path}")

        with open(path) as f:
            products = json.load(f)

        documents = []
        for p in products:
            text = (
                f"Product: {p['name']}\n"
                f"ID: {p['id']}\n"
                f"Price: ${p['price']}\n"
                f"Category: {p.get('category', 'General')}\n"
                f"Brand: {p.get('brand', 'N/A')}\n"
                f"Rating: {p.get('rating', 'N/A')}/5\n"
                f"Description: {p['description']}\n"
                f"In Stock: {p.get('quantity', 0)} units"
            )
            doc = Document(
                page_content=text,
                metadata={
                    "product_id": p["id"],
                    "name": p["name"],
                    "price": p["price"],
                    "category": p.get("category", "General"),
                    "brand": p.get("brand", ""),
                    "quantity": p.get("quantity", 0),
                },
            )
            documents.append(doc)

        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        self._vectorstore = Chroma.from_documents(
            chunks,
            self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
        )

        self._initialized = True
        logger.info("Indexed %d product documents (%d chunks)", len(products), len(chunks))
        return len(products)

    def search(self, query: str, k: int = 5) -> list[Document]:
        """Semantic search with automatic keyword fallback."""
        if not self._initialized:
            logger.info("RAG not initialized, using keyword search fallback")
            return _keyword_search(query, self.products_path, k=k)

        try:
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            logger.warning("Semantic search failed, falling back to keyword search: %s", e)
            return _keyword_search(query, self.products_path, k=k)

    def search_with_scores(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        """Semantic search returning documents with relevance scores."""
        if not self._initialized:
            docs = _keyword_search(query, self.products_path, k=k)
            return [(doc, 1.0) for doc in docs]

        try:
            return self.vectorstore.similarity_search_with_score(query, k=k)
        except Exception as e:
            logger.warning("Scored search failed, falling back to keyword search: %s", e)
            docs = _keyword_search(query, self.products_path, k=k)
            return [(doc, 1.0) for doc in docs]

    def format_results(self, docs: list[Document]) -> str:
        """Format search results into a readable string for the LLM."""
        if not docs:
            return "No products found matching your query."

        parts = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            parts.append(
                f"{i}. {meta.get('name', 'Unknown')} "
                f"(ID: {meta.get('product_id', 'N/A')}) - "
                f"${meta.get('price', 'N/A')} - "
                f"{meta.get('category', '')}"
            )
            parts.append(f"   {doc.page_content[:200]}")
            parts.append("")

        return "\n".join(parts)


# Module-level convenience instance
_default_rag: Optional[ProductRAG] = None


def get_product_rag() -> ProductRAG:
    """Get or create the default ProductRAG instance."""
    global _default_rag
    if _default_rag is None:
        _default_rag = ProductRAG()
    return _default_rag


def initialize_rag(products_path: str = "") -> ProductRAG:
    """Initialize the RAG system and load products."""
    global _default_rag
    _default_rag = ProductRAG(products_path=products_path)
    _default_rag.load_products(products_path)
    return _default_rag

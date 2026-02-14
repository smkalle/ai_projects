"""RAG (Retrieval-Augmented Generation) module for product retrieval.

Uses ChromaDB as the vector store and OpenAI embeddings to enable
semantic search over the product catalog.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from config import settings

logger = logging.getLogger(__name__)


class ProductRAG:
    """Manages the product vector store for semantic retrieval."""

    def __init__(
        self,
        collection_name: str = "",
        persist_directory: str = "",
        embedding_model: str = "",
    ):
        self.collection_name = collection_name or settings.chroma_collection_name
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        self.embedding_model = embedding_model or settings.embedding_model

        self._embeddings: Optional[OpenAIEmbeddings] = None
        self._vectorstore: Optional[Chroma] = None

    @property
    def embeddings(self) -> OpenAIEmbeddings:
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model=self.embedding_model)
        return self._embeddings

    @property
    def vectorstore(self) -> Chroma:
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
        return self._vectorstore

    def load_products(self, products_path: str | Path = "") -> int:
        """Load products from JSON into the vector store.

        Returns the number of products indexed.
        """
        path = Path(products_path or settings.products_json_path)
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

        logger.info("Indexed %d product documents (%d chunks)", len(products), len(chunks))
        return len(products)

    def search(self, query: str, k: int = 5) -> list[Document]:
        """Semantic search for products matching the query."""
        return self.vectorstore.similarity_search(query, k=k)

    def search_with_scores(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        """Semantic search returning documents with relevance scores."""
        return self.vectorstore.similarity_search_with_score(query, k=k)

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
    _default_rag = ProductRAG()
    _default_rag.load_products(products_path)
    return _default_rag

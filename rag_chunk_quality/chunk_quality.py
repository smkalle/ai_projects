"""Utilities for chunk quality control."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class ProcessedChunks:
    """Container for chunks and their embeddings."""

    chunks: List[str]
    embeddings: np.ndarray


class ChunkQualityProcessor:
    """Process documents into high-quality chunks."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_tokens: int = 50,
        max_tokens: int = 512,
        duplicate_threshold: float = 0.9,
    ) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "?", "!", " "],
        )
        self.embedder = SentenceTransformer(model_name)
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.duplicate_threshold = duplicate_threshold

    def split_text(self, text: str) -> List[str]:
        """Split text into raw chunks."""
        return self.splitter.split_text(text)

    def embed(self, chunks: List[str]) -> np.ndarray:
        """Compute embeddings for chunks."""
        return self.embedder.encode(chunks)

    def remove_duplicates(
        self, chunks: List[str], embeddings: np.ndarray
    ) -> Tuple[List[str], np.ndarray]:
        """Drop near-duplicate chunks."""
        unique_chunks: List[str] = []
        unique_embeds: List[np.ndarray] = []
        for idx, chunk in enumerate(chunks):
            if not unique_embeds:
                unique_chunks.append(chunk)
                unique_embeds.append(embeddings[idx])
                continue
            sims = cosine_similarity([embeddings[idx]], np.array(unique_embeds))
            if sims.max() < self.duplicate_threshold:
                unique_chunks.append(chunk)
                unique_embeds.append(embeddings[idx])
        return unique_chunks, np.array(unique_embeds)

    def filter_low_info(
        self, chunks: List[str], embeddings: np.ndarray
    ) -> Tuple[List[str], np.ndarray]:
        """Remove low-information or size-extreme chunks."""
        filtered_chunks: List[str] = []
        filtered_embeds: List[np.ndarray] = []
        for chunk, emb in zip(chunks, embeddings):
            tokens = chunk.split()
            if len(tokens) < self.min_tokens or len(tokens) > self.max_tokens:
                continue
            punctuation = sum(1 for c in chunk if c in ",.;:!?")
            if punctuation / max(len(chunk), 1) > 0.5:
                continue
            filtered_chunks.append(chunk)
            filtered_embeds.append(emb)
        return filtered_chunks, np.array(filtered_embeds)

    def process_text(self, text: str) -> ProcessedChunks:
        """Full pipeline for a single text string."""
        raw_chunks = self.split_text(text)
        embeds = self.embed(raw_chunks)
        chunks, embeds = self.remove_duplicates(raw_chunks, embeds)
        chunks, embeds = self.filter_low_info(chunks, embeds)
        return ProcessedChunks(chunks=chunks, embeddings=embeds)

    def process_files(self, paths: List[Path]) -> ProcessedChunks:
        """Process multiple files and concatenate results."""
        all_chunks: List[str] = []
        all_embeds: List[np.ndarray] = []
        for path in paths:
            text = path.read_text(encoding="utf-8")
            result = self.process_text(text)
            all_chunks.extend(result.chunks)
            all_embeds.append(result.embeddings)
        if not all_embeds:
            return ProcessedChunks([], np.empty((0, 384)))
        return ProcessedChunks(chunks=all_chunks, embeddings=np.vstack(all_embeds))

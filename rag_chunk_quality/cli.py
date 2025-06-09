"""Command line interface for chunk quality processing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import faiss
import numpy as np

from .chunk_quality import ChunkQualityProcessor


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk quality control and indexing")
    parser.add_argument("input", nargs="+", help="Text files to process")
    parser.add_argument("--index", default="index.faiss", help="Output FAISS index")
    parser.add_argument(
        "--chunks",
        default="chunks.json",
        help="Path to save processed chunks as JSON",
    )
    args = parser.parse_args()

    paths = [Path(p) for p in args.input]
    processor = ChunkQualityProcessor()
    result = processor.process_files(paths)

    if result.embeddings.size == 0:
        print("No chunks created")
        return

    dimension = result.embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(result.embeddings.astype(np.float32))
    faiss.write_index(index, args.index)

    with open(args.chunks, "w", encoding="utf-8") as f:
        json.dump(result.chunks, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(result.chunks)} chunks")
    print(f"Index written to {args.index}")


if __name__ == "__main__":
    main()

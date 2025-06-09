# RAG Chunk Quality Control

This app provides utilities for preprocessing documents for Retrieval-Augmented Generation (RAG) systems.
It performs chunking with quality checks before indexing so that only meaningful content is stored in the
vector database.

## Features
- Splits text files using `RecursiveCharacterTextSplitter` from LangChain.
- Removes near-duplicate chunks based on embedding similarity.
- Filters low-information chunks (short length or high punctuation).
- Enforces minimum and maximum token lengths.
- Saves embeddings to a FAISS index for later retrieval.

## Quick Start
```bash
pip install -r requirements.txt
python -m rag_chunk_quality.cli mydoc.txt --index index.faiss --chunks chunks.json
```

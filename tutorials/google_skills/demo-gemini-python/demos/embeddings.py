"""
Section 9 — Text Embeddings
Generate vector embeddings for semantic search and similarity matching.
"""

from typing import Sequence

DEFAULT_TEXTS = [
    "How do I get a driver's license?",
    "How long is a driver's license valid for?",
    "What are the requirements for renewing a passport?",
]
EMBED_MODEL = "gemini-embedding-001"


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def run(client, *, model: str = EMBED_MODEL, prompt: str | None = None, **_) -> None:
    from google.genai import types  # pylint: disable=import-outside-toplevel

    # Use the default embed model regardless of --model (which targets generate models)
    embed_model = EMBED_MODEL if model == "gemini-3-flash-preview" else model

    texts = [prompt] + DEFAULT_TEXTS[1:] if prompt else DEFAULT_TEXTS
    print(f"Model : {embed_model}")
    print(f"Texts : {len(texts)} documents\n")

    response = client.models.embed_content(
        model=embed_model,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=256,
        ),
    )

    vectors = [e.values for e in response.embeddings]
    for i, (text, vec) in enumerate(zip(texts, vectors)):
        print(f"[{i}] {text[:60]!r}")
        print(f"     dim={len(vec)}  first_5={[round(v, 4) for v in vec[:5]]}")

    if len(vectors) >= 2:
        sim = cosine_similarity(vectors[0], vectors[1])
        print(f"\nCosine similarity [0] vs [1]: {sim:.4f}")

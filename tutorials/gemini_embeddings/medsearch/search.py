"""
Search medical research content across all modalities with a single query.

Cross-modal examples (what makes this powerful):
    "bilateral infiltrates lower lobe"
        → returns matching chest X-rays + paper sections describing it
          + audio clips from radiology conference discussing it

    Upload a pathology slide image
        → finds papers about that tissue pattern + similar slides + related talks

    "BRCA1 mutation prognosis"
        → returns abstracts + clinical guidelines + related imaging studies

Query types:
    text only     — natural language description
    image only    — reference image (finds similar images AND semantically
                    related text/audio/video — cross-modal magic)
    image + text  — combined (e.g. image of an X-ray + "show me similar cases
                    with ground glass opacity") for highest precision

Usage (CLI):
    # Text query
    python -m medsearch.search --query "ground glass opacity bilateral lungs"

    # Image query (cross-modal: finds papers, audio, video too)
    python -m medsearch.search --image ./media/imaging/xray_001.jpg

    # Combined image + text
    python -m medsearch.search --image ./media/imaging/xray_001.jpg --query "COVID pneumonia pattern"

    # Filter to one modality
    python -m medsearch.search --query "ARDS management" --modality pdf

    # Interactive REPL
    python -m medsearch.search --interactive
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .utils import configure, embed
from .ingest import get_collection

load_dotenv()
console = Console()

_ICONS = {
    "text":  "T",
    "image": "IMG",
    "pdf":   "PDF",
    "audio": "AUDIO",
    "video": "VIDEO",
}


def search(
    query: str = None,
    image_path: str = None,
    collection=None,
    n_results: int = 7,
    db_path: str = None,
    filter_modality: str = None,
) -> list:
    """
    Search by text, image, or both (cross-modal).

    Args:
        query:           Natural language query string
        image_path:      Path to a reference image (JPEG or PNG)
        collection:      ChromaDB collection — auto-loaded from db_path if None
        n_results:       How many results to return
        db_path:         ChromaDB storage path (overrides env var)
        filter_modality: Restrict results to one modality:
                         "text" | "image" | "pdf" | "audio" | "video"

    Returns:
        List of dicts with keys: modality, source, pages, distance, score, document, meta
    """
    configure()

    if collection is None:
        collection = get_collection(db_path)

    if not query and not image_path:
        raise ValueError("Provide at least a query string or image_path.")

    # Build the query embedding
    # Combining image + text gives one aggregate embedding in the unified space
    content = []
    if image_path:
        from PIL import Image
        content.append(Image.open(image_path))
    if query:
        content.append(query)

    embed_input = content[0] if len(content) == 1 else content
    q_emb = embed(embed_input, task_type="RETRIEVAL_QUERY")

    where = {"modality": filter_modality} if filter_modality else None

    raw = collection.query(
        query_embeddings=[q_emb],
        n_results=n_results,
        where=where,
        include=["metadatas", "distances", "documents"],
    )

    results = []
    for i in range(len(raw["ids"][0])):
        meta = raw["metadatas"][0][i]
        dist = raw["distances"][0][i]
        results.append({
            "modality": meta.get("modality", "unknown"),
            "source":   meta.get("source", ""),
            "pages":    meta.get("pages", ""),
            "distance": dist,
            "score":    round(1 - dist, 4),   # cosine similarity
            "document": raw["documents"][0][i],
            "meta":     meta,
        })

    return results


def _render(results: list, query: str = None, image_path: str = None):
    """Pretty-print search results as a rich table."""
    title_parts = []
    if query:
        title_parts.append(f'"{query}"')
    if image_path:
        title_parts.append(f"[image: {Path(image_path).name}]")
    title = "Results for: " + " + ".join(title_parts) if title_parts else "Results"

    table = Table(title=title, show_lines=True, expand=False)
    table.add_column("#",       style="dim",    width=3)
    table.add_column("Type",    width=7)
    table.add_column("Source",  no_wrap=False,  min_width=30)
    table.add_column("Score",   width=7,        style="green")

    for i, r in enumerate(results, 1):
        icon = _ICONS.get(r["modality"], "?")
        source = Path(r["source"]).name if r["source"] else r["document"][:60]
        if r["pages"]:
            source += f"  [{r['pages']}]"
        table.add_row(str(i), icon, source, str(r["score"]))

    console.print(table)

    # Show extra metadata for top result
    if results:
        top = results[0]
        extras = {k: v for k, v in top["meta"].items()
                  if k not in ("modality", "source", "pages", "total_chunks")}
        if extras:
            console.print("[dim]Top result metadata:[/dim]", extras)


def interactive_search(db_path: str = None):
    """
    Run an interactive search REPL.

    Commands:
        <text>               — search by text
        img:<path>           — search by image
        img:<path> <text>    — combined search
        q                    — quit
    """
    configure()
    collection = get_collection(db_path)

    console.print("[bold green]MedSearch[/bold green] — Medical Research Intelligence")
    console.print("Type a query, [bold]img:<path>[/bold] for image search, or [bold]q[/bold] to quit.\n")

    while True:
        try:
            raw = console.input("[bold cyan]Query>[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw or raw.lower() == "q":
            break

        image_path = None
        query = raw

        if raw.lower().startswith("img:"):
            rest = raw[4:].strip()
            parts = rest.split(" ", 1)
            image_path = parts[0]
            query = parts[1].strip() if len(parts) > 1 else None

        try:
            results = search(query=query, image_path=image_path, collection=collection)
            _render(results, query=query, image_path=image_path)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

    console.print("Bye.")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(
        description="Search medical research content in MedSearch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--query",       "-q", default=None, help="Text search query")
    p.add_argument("--image",       "-i", default=None, help="Reference image path")
    p.add_argument("--modality",    "-m", default=None,
                   choices=["text", "image", "pdf", "audio", "video"],
                   help="Restrict results to one modality")
    p.add_argument("--n",           default=7, type=int, help="Number of results")
    p.add_argument("--db",          default=None, help="ChromaDB storage path")
    p.add_argument("--interactive", action="store_true", help="Run interactive REPL")
    args = p.parse_args()

    if args.interactive:
        interactive_search(db_path=args.db)
    elif args.query or args.image:
        configure()
        results = search(
            query=args.query,
            image_path=args.image,
            n_results=args.n,
            db_path=args.db,
            filter_modality=args.modality,
        )
        _render(results, query=args.query, image_path=args.image)
    else:
        p.print_help()

#!/usr/bin/env python3
"""
MedSearch — Medical Research Intelligence Workbench

A cross-modal search UI powered by Gemini Embedding 2.
Search across research papers, medical images, audio recordings, and procedure
videos from a single query — text, image, or both combined.

Usage:
    python app.py                   # launch on http://0.0.0.0:7860
    python app.py --port 8080       # custom port
    python app.py --share           # create public Gradio link
"""

import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from PIL import Image

from medsearch.utils import configure, embed, normalize, DEFAULT_DIM, MODEL
from medsearch.ingest import get_collection

configure()
collection = get_collection()

# ── Theme & Constants ────────────────────────────────────────────────────────

MODALITY_LABELS = {
    "text":  "Text",
    "image": "Image",
    "pdf":   "PDF",
    "audio": "Audio",
    "video": "Video",
}

MODALITY_COLORS = {
    "text":  "#3b82f6",
    "image": "#10b981",
    "pdf":   "#f59e0b",
    "audio": "#8b5cf6",
    "video": "#ef4444",
}


# ── Core Search ──────────────────────────────────────────────────────────────

def search_core(query_text, query_image, modality_filter, num_results):
    """Run cross-modal search and return formatted results."""
    if not query_text and query_image is None:
        return "Enter a text query, upload an image, or both.", "", None

    # Build query embedding
    content = []
    if query_image is not None:
        content.append(Image.fromarray(query_image))
    if query_text:
        content.append(query_text)

    embed_input = content[0] if len(content) == 1 else content
    q_emb = embed(embed_input, task_type="RETRIEVAL_QUERY")

    where = {"modality": modality_filter} if modality_filter and modality_filter != "all" else None

    raw = collection.query(
        query_embeddings=[q_emb],
        n_results=int(num_results),
        where=where,
        include=["metadatas", "distances", "documents"],
    )

    if not raw["ids"][0]:
        return "No results found.", "", None

    # Format results as HTML cards
    html_parts = []
    gallery_images = []

    for i in range(len(raw["ids"][0])):
        meta = raw["metadatas"][0][i]
        dist = raw["distances"][0][i]
        doc = raw["documents"][0][i]
        score = round(1 - dist, 4)
        modality = meta.get("modality", "unknown")
        source = meta.get("source", "")
        pages = meta.get("pages", "")
        fname = Path(source).name if source else ""
        color = MODALITY_COLORS.get(modality, "#6b7280")
        label = MODALITY_LABELS.get(modality, modality)

        # Build card
        source_line = ""
        if fname:
            source_line = f'<div style="font-size:0.85em;color:#64748b;margin-top:4px">{fname}'
            if pages:
                source_line += f" &middot; {pages}"
            source_line += "</div>"

        preview = ""
        if modality == "text":
            snippet = doc[:200] + "..." if len(doc) > 200 else doc
            preview = f'<div style="font-size:0.85em;color:#334155;margin-top:6px;white-space:pre-wrap">{snippet}</div>'
        elif modality == "image" and source and Path(source).exists():
            gallery_images.append((source, f"#{i+1} {fname} (score: {score})"))

        html_parts.append(f"""
        <div style="border:1px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:10px;
                    background:white;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
            <div style="display:flex;align-items:center;gap:10px">
                <span style="background:{color};color:white;padding:3px 10px;border-radius:6px;
                            font-size:0.8em;font-weight:600">{label}</span>
                <span style="font-size:1.1em;font-weight:600">#{i+1}</span>
                <span style="margin-left:auto;font-size:1.1em;font-weight:700;color:{color}">
                    {score}
                </span>
            </div>
            {source_line}
            {preview}
        </div>
        """)

    # Stats summary
    modalities_found = set(raw["metadatas"][0][i].get("modality") for i in range(len(raw["ids"][0])))
    top_score = round(1 - raw["distances"][0][0], 4)
    query_desc = []
    if query_text:
        query_desc.append(f'text: "{query_text[:50]}"')
    if query_image is not None:
        query_desc.append("image upload")
    stats = f"**{len(raw['ids'][0])} results** across {', '.join(modalities_found)} | top score: {top_score} | query: {' + '.join(query_desc)}"

    html = f'<div style="max-height:600px;overflow-y:auto;padding:4px">{"".join(html_parts)}</div>'

    return stats, html, gallery_images if gallery_images else None


# ── Index Stats ──────────────────────────────────────────────────────────────

def get_index_stats():
    """Return index statistics as markdown."""
    count = collection.count()
    if count == 0:
        return "Index is empty. Run `./run.sh ingest` first."

    # Sample metadata to count modalities
    sample = collection.get(limit=count, include=["metadatas"])
    modality_counts = {}
    for meta in sample["metadatas"]:
        m = meta.get("modality", "unknown")
        modality_counts[m] = modality_counts.get(m, 0) + 1

    lines = [f"## Index: {count} items\n"]
    lines.append("| Modality | Count |")
    lines.append("|----------|-------|")
    for m, c in sorted(modality_counts.items()):
        emoji = {"text": "T", "image": "IMG", "pdf": "PDF", "audio": "AUD", "video": "VID"}.get(m, "?")
        lines.append(f"| {emoji} {MODALITY_LABELS.get(m, m)} | {c} |")
    lines.append(f"\n**Model:** `{MODEL}`  ")
    lines.append(f"**Dimensions:** {DEFAULT_DIM}  ")
    lines.append(f"**Similarity:** cosine")
    return "\n".join(lines)


# ── Build UI ─────────────────────────────────────────────────────────────────

def build_app():
    with gr.Blocks(
        title="MedSearch — Medical Research Intelligence",
    ) as app:

        gr.HTML("""
        <h1 class="main-title">MedSearch</h1>
        <p class="subtitle">Medical Research Intelligence &mdash; Cross-Modal Search powered by Gemini Embedding 2</p>
        """)

        with gr.Tabs():

            # ── Search Tab ───────────────────────────────────────
            with gr.Tab("Search", id="search"):
                with gr.Row():
                    with gr.Column(scale=2):
                        query_text = gr.Textbox(
                            label="Text Query",
                            placeholder="e.g. bilateral pneumonia infiltrates, ARDS ventilation strategy, BRCA1 mutation...",
                            lines=2,
                        )
                        with gr.Row():
                            modality_filter = gr.Dropdown(
                                choices=["all", "text", "image", "pdf", "audio", "video"],
                                value="all",
                                label="Filter Modality",
                            )
                            num_results = gr.Slider(
                                minimum=3, maximum=20, value=7, step=1,
                                label="Results",
                            )
                        search_btn = gr.Button("Search", variant="primary", size="lg")

                    with gr.Column(scale=1):
                        query_image = gr.Image(
                            label="Image Query (optional — cross-modal)",
                            type="numpy",
                            height=200,
                        )

                gr.HTML("<hr style='margin:8px 0;border-color:#e2e8f0'>")

                stats_md = gr.Markdown("")
                results_html = gr.HTML("")
                gallery = gr.Gallery(
                    label="Matched Images",
                    columns=4,
                    height=200,
                    visible=True,
                )

                search_btn.click(
                    fn=search_core,
                    inputs=[query_text, query_image, modality_filter, num_results],
                    outputs=[stats_md, results_html, gallery],
                )
                query_text.submit(
                    fn=search_core,
                    inputs=[query_text, query_image, modality_filter, num_results],
                    outputs=[stats_md, results_html, gallery],
                )

            # ── Example Queries Tab ──────────────────────────────
            with gr.Tab("Examples", id="examples"):
                gr.Markdown("""
## Try These Queries

**Cross-modal text queries** (searches across ALL modalities):

| Query | What it finds |
|-------|---------------|
| `bilateral pneumonia infiltrates` | Abstracts + relevant X-rays + paper sections |
| `ARDS mechanical ventilation treatment` | ARDS paper + ventilation abstracts |
| `deep learning pathology cancer` | Pathology AI papers + relevant abstracts |
| `lung cancer CT screening nodule` | Lung cancer PDFs + imaging abstracts |
| `cardiac MRI myocardial infarction` | Cardiac abstracts + related papers |
| `breast mammography screening` | Breast cancer abstracts |

**Image queries** (upload a medical image):
- Upload a chest X-ray to find similar images + related papers + abstracts
- Upload a pathology slide to find papers describing similar patterns

**Combined queries** (image + text):
- Upload an X-ray + type "ground glass opacity" for highest precision

**Modality filtering**:
- Set filter to "pdf" to search only research papers
- Set filter to "image" to find similar medical images only
                """)

            # ── Index Info Tab ───────────────────────────────────
            with gr.Tab("Index", id="index"):
                stats_display = gr.Markdown(get_index_stats())
                refresh_btn = gr.Button("Refresh Stats")
                refresh_btn.click(fn=get_index_stats, outputs=[stats_display])

            # ── About Tab ────────────────────────────────────────
            with gr.Tab("About", id="about"):
                gr.Markdown(f"""
## How MedSearch Works

**Gemini Embedding 2** (`{MODEL}`) maps text, images, video, audio, and PDFs into a
single unified vector space. This means a text query like _"pneumonia chest imaging"_
can retrieve:

- A chest X-ray showing pneumonia patterns
- A research paper section describing imaging findings
- An audio clip from a radiology conference discussing the topic
- A procedure video demonstrating diagnostic technique

All ranked together by semantic similarity — no keyword matching, no modality-specific pipelines.

### Architecture
```
Query (text / image / both)
    |
    v
Gemini Embedding 2  -->  1536-dim normalized vector
    |
    v
ChromaDB (cosine similarity)  -->  ranked results across all modalities
```

### Key Technical Details
- **Dimensions:** {DEFAULT_DIM} (Matryoshka truncation from 3072)
- **Similarity:** Cosine distance, L2-normalized vectors
- **PDF chunking:** Auto-split at 6 pages (Gemini File API limit)
- **Video limit:** 120s per clip
- **Audio:** Natively embedded (no transcription needed)

### Data Sources
- **Abstracts:** PubMed / NCBI (public)
- **Papers:** PMC Open Access (CC BY / CC BY-NC)
- **Images:** Open-i / MedPix / NIH (public domain)
                """)

    return app


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedSearch Web UI")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    args = parser.parse_args()

    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=args.port,
        share=args.share,
    )

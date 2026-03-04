"""CLI app demonstrating Gemini 3.1 Flash-Lite capabilities."""

import json
import time

import click
from google.genai import types
from PIL import Image
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .client import (
    EMBED_MODEL,
    MODEL,
    THINKING_LEVELS,
    extract_response_parts,
    get_client,
    get_usage,
    make_config,
    traced_embed,
    traced_generate,
    traced_generate_stream,
)
from .examples import AUDIO_MIME_TYPES, DEFAULT_PROMPTS, Recipe, calculate, get_weather

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Gemini 3.1 Flash-Lite Explorer — discover model capabilities from the CLI."""
    pass


# ── Chat ─────────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--level", type=click.Choice(list(THINKING_LEVELS)), default="medium", help="Thinking level")
@click.option("--system", default=None, help="System instruction")
def chat(level, system):
    """Interactive multi-turn chat with streaming."""
    client = get_client()
    config = make_config(thinking_level=level, system_instruction=system or "You are a helpful assistant.")
    history = []

    console.print(Panel(f"[bold green]Gemini 3.1 Flash-Lite Chat[/] | thinking: {level}\nType 'quit' to exit."))

    while True:
        try:
            user_input = console.input("[bold cyan]You:[/] ")
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.strip().lower() in ("quit", "exit", "q"):
            break

        history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))
        console.print("[bold yellow]Gemini:[/] ", end="")

        full_text = ""
        for chunk in traced_generate_stream(client, MODEL, history, config):
            if chunk.text:
                console.print(chunk.text, end="")
                full_text += chunk.text

        console.print()
        history.append(types.Content(role="model", parts=[types.Part.from_text(text=full_text)]))


# ── Think ────────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("prompt")
@click.option("--levels", default="minimal,low,medium,high", help="Comma-separated thinking levels to compare")
def think(prompt, levels):
    """Compare thinking levels on the same prompt."""
    client = get_client()
    level_list = [l.strip() for l in levels.split(",")]

    table = Table(title="Thinking Level Comparison")
    table.add_column("Level", style="cyan")
    table.add_column("Thoughts", style="dim")
    table.add_column("Answer", max_width=60)
    table.add_column("Think Tokens", justify="right", style="magenta")
    table.add_column("Time (s)", justify="right", style="green")

    for level in level_list:
        if level not in THINKING_LEVELS:
            console.print(f"[red]Unknown level: {level}[/]")
            continue
        config = make_config(thinking_level=level)
        start = time.time()
        response = traced_generate(client, MODEL, prompt, config)
        elapsed = time.time() - start
        thoughts, answer = extract_response_parts(response)
        usage = get_usage(response)
        table.add_row(
            level,
            (thoughts[:80] + "...") if len(thoughts) > 80 else thoughts,
            (answer[:120] + "...") if len(answer) > 120 else answer,
            str(usage["thoughts_tokens"]),
            f"{elapsed:.2f}",
        )

    console.print(table)


# ── Vision ───────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--prompt", default=DEFAULT_PROMPTS["vision"], help="Prompt for the image")
@click.option("--level", type=click.Choice(list(THINKING_LEVELS)), default="medium")
def vision(image_path, prompt, level):
    """Analyze an image file."""
    client = get_client()
    config = make_config(thinking_level=level)
    img = Image.open(image_path)

    console.print(f"[dim]Analyzing: {image_path}[/]")
    response = traced_generate(client, MODEL, [img, prompt], config)
    thoughts, answer = extract_response_parts(response)
    if thoughts:
        console.print(Panel(thoughts, title="Thoughts", style="dim"))
    console.print(Markdown(answer))
    usage = get_usage(response)
    console.print(f"[dim]Tokens: {usage['total_tokens']} (thoughts: {usage['thoughts_tokens']})[/]")


# ── Audio ────────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("audio_path", type=click.Path(exists=True))
@click.option("--prompt", default=DEFAULT_PROMPTS["audio"], help="Prompt for the audio")
@click.option("--level", type=click.Choice(list(THINKING_LEVELS)), default="medium")
def audio(audio_path, prompt, level):
    """Transcribe/summarize an audio file."""
    client = get_client()
    config = make_config(thinking_level=level)

    ext = audio_path.rsplit(".", 1)[-1].lower()
    mime = AUDIO_MIME_TYPES.get(ext, "audio/mp3")

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    console.print(f"[dim]Processing: {audio_path} ({mime})[/]")
    response = traced_generate(client, MODEL, [types.Part.from_bytes(data=audio_bytes, mime_type=mime), prompt], config)
    thoughts, answer = extract_response_parts(response)
    if thoughts:
        console.print(Panel(thoughts, title="Thoughts", style="dim"))
    console.print(Markdown(answer))


# ── JSON (Structured Output) ────────────────────────────────────────────────


@cli.command("json")
@click.option("--prompt", default=None, help="Custom prompt (default: recipe generation)")
@click.option("--level", type=click.Choice(list(THINKING_LEVELS)), default="medium")
def json_cmd(prompt, level):
    """Demonstrate structured JSON output with a Pydantic schema."""
    client = get_client()
    config = make_config(
        thinking_level=level,
        json_schema=Recipe.model_json_schema(),
    )
    prompt = prompt or DEFAULT_PROMPTS["recipe"]

    console.print(f"[dim]Schema: {Recipe.__name__}[/]")
    response = traced_generate(client, MODEL, prompt, config)

    result = Recipe.model_validate_json(response.text)
    console.print(Panel(json.dumps(result.model_dump(), indent=2), title=result.name, style="green"))


# ── Function Calling ─────────────────────────────────────────────────────────


@cli.command()
@click.argument("query", default=DEFAULT_PROMPTS["tools"])
@click.option("--level", type=click.Choice(list(THINKING_LEVELS)), default="medium")
def tools(query, level):
    """Demonstrate function calling with weather + calculator tools."""
    client = get_client()
    config = make_config(thinking_level=level, tools=[get_weather, calculate])

    console.print(f"[dim]Query: {query}[/]")
    console.print("[dim]Tools: get_weather, calculate[/]")

    response = traced_generate(client, MODEL, query, config)
    console.print(Markdown(response.text))


# ── Embeddings ───────────────────────────────────────────────────────────────


@cli.command()
@click.argument("text1")
@click.argument("text2")
def embed(text1, text2):
    """Compute embedding similarity between two texts."""
    client = get_client()

    result = traced_embed(
        client, EMBED_MODEL, [text1, text2],
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
    )

    vec1 = result.embeddings[0].values
    vec2 = result.embeddings[1].values
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    similarity = dot / (norm1 * norm2) if norm1 and norm2 else 0.0

    table = Table(title="Embedding Similarity")
    table.add_column("Text 1", max_width=40)
    table.add_column("Text 2", max_width=40)
    table.add_column("Cosine Similarity", justify="right", style="green")
    table.add_column("Dimensions", justify="right")
    table.add_row(text1, text2, f"{similarity:.4f}", str(len(vec1)))
    console.print(table)


# ── Benchmark ────────────────────────────────────────────────────────────────


@cli.command()
@click.argument("prompt", default=DEFAULT_PROMPTS["bench"])
@click.option("--rounds", default=1, type=int, help="Number of rounds per level")
def bench(prompt, rounds):
    """Benchmark latency and token usage across thinking levels."""
    client = get_client()

    table = Table(title="Benchmark Results")
    table.add_column("Level", style="cyan")
    table.add_column("Avg Time (s)", justify="right", style="green")
    table.add_column("Input Tokens", justify="right")
    table.add_column("Output Tokens", justify="right")
    table.add_column("Think Tokens", justify="right", style="magenta")
    table.add_column("Total Tokens", justify="right", style="bold")

    for level_name in THINKING_LEVELS:
        config = make_config(thinking_level=level_name)
        times = []
        last_usage = {}

        for _ in range(rounds):
            start = time.time()
            response = traced_generate(client, MODEL, prompt, config)
            times.append(time.time() - start)
            last_usage = get_usage(response)

        avg_time = sum(times) / len(times)
        table.add_row(
            level_name,
            f"{avg_time:.2f}",
            str(last_usage.get("input_tokens", 0)),
            str(last_usage.get("output_tokens", 0)),
            str(last_usage.get("thoughts_tokens", 0)),
            str(last_usage.get("total_tokens", 0)),
        )

    console.print(table)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()

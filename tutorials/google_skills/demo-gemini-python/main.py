"""
Gemini API demo CLI — exercises 10 capabilities from the tutorial.

Usage:
    python main.py <command> [options]

Commands:
    text        Text generation (Section 1)
    chat        Multi-turn conversation (Section 2)
    stream      Streaming output (Section 3)
    json        Structured JSON output with Pydantic (Section 5)
    tools       Function calling (Section 6)
    code        Code execution tool (Section 8)
    embed       Text embeddings (Section 9)
    thinking    Extended thinking / reasoning (Section 17)
    safety      Safety settings and ratings (Section 18)
    grounding   Google Search grounding (Section 7)
    all         Run all demos sequentially

Options:
    --prompt TEXT   Override the default prompt for the selected demo
    --model  MODEL  Override the default model (default: gemini-3-flash-preview)

Auth (.env file in this directory, or export env vars directly):
    GEMINI_API_KEY              — API key (preferred, loaded from .env)
    GOOGLE_GENAI_USE_VERTEXAI   — set "true" to use Vertex AI / Agent Platform
    GOOGLE_CLOUD_PROJECT        — GCP project (Vertex AI mode)
    GOOGLE_CLOUD_LOCATION       — region (Vertex AI mode, default: global)
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from this file's directory so the app works regardless of cwd.
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

DEMOS = {
    "text":       "Text generation",
    "chat":       "Multi-turn chat",
    "stream":     "Streaming output",
    "json":       "Structured JSON output",
    "tools":      "Function calling",
    "code":       "Code execution",
    "embed":      "Text embeddings",
    "thinking":   "Extended thinking / reasoning",
    "safety":     "Safety settings",
    "grounding":  "Google Search grounding",
}

# Maps CLI short names to their actual module filenames under demos/
_MODULE_MAP = {
    "text":      "text_generation",
    "chat":      "chat",
    "stream":    "streaming",
    "json":      "structured_output",
    "tools":     "function_calling",
    "code":      "code_execution",
    "embed":     "embeddings",
    "thinking":  "thinking",
    "safety":    "safety",
    "grounding": "search_grounding",
}


def _separator(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def get_client():
    """Return a google.genai.Client.

    Auth priority:
      1. GEMINI_API_KEY  — set in .env or environment (api_key mode)
      2. Vertex AI env vars (GOOGLE_GENAI_USE_VERTEXAI + GOOGLE_CLOUD_PROJECT)
      3. GOOGLE_API_KEY  — legacy fallback picked up automatically by the SDK
    """
    from google import genai  # pylint: disable=import-outside-toplevel

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()  # falls back to Vertex AI ADC or GOOGLE_API_KEY


def _import_demo(name: str):
    """Import a demo module by short name."""
    import importlib  # pylint: disable=import-outside-toplevel
    module_name = _MODULE_MAP.get(name, name)
    return importlib.import_module(f"demos.{module_name}")


def run_demo(name: str, client, model: str, prompt: str | None) -> None:
    module = _import_demo(name)
    module.run(client, model=model, prompt=prompt)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Gemini API demo CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "command",
        choices=list(DEMOS.keys()) + ["all"],
        help="Demo to run (or 'all' to run every demo)",
    )
    parser.add_argument("--prompt", default=None, help="Override default prompt")
    parser.add_argument(
        "--model",
        default="gemini-3-flash-preview",
        help="Gemini model ID (default: gemini-3-flash-preview)",
    )
    args = parser.parse_args(argv)

    client = get_client()

    if args.command == "all":
        errors = []
        for name, title in DEMOS.items():
            _separator(title)
            try:
                run_demo(name, client, model=args.model, prompt=args.prompt)
            except Exception as exc:  # noqa: BLE001
                print(f"[ERROR] {exc}")
                errors.append(name)
        if errors:
            print(f"\n[WARN] {len(errors)} demo(s) failed: {', '.join(errors)}")
            return 1
        return 0

    _separator(DEMOS[args.command])
    try:
        run_demo(args.command, client, model=args.model, prompt=args.prompt)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

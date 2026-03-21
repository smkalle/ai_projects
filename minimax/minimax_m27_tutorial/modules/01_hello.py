"""
Module 01 — Hello World: Basic Text Generation
───────────────────────────────────────────────
Covers:
  • Creating an Anthropic client pointed at MiniMax
  • Sending a single-turn user message
  • Reading back text content blocks
  • Inspecting response metadata
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log, report_usage, print_blocks


def run() -> None:
    print_header(
        "Module 01 · Hello World — Basic Text Generation",
        "Single-turn message, response metadata, content blocks"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    # ── Build the request ────────────────────────────────────────────────────
    system = (
        "You are a helpful AI assistant built on MiniMax M2.7. "
        "Be concise, clear, and always mention your model name when asked."
    )
    user_msg = (
        "Hello! Please introduce yourself, state which model you are, "
        "and list 3 things you can help developers build."
    )

    print_divider("Request")
    log("REQUEST", f"model      = {model}")
    log("REQUEST", f"max_tokens = 512")
    log("REQUEST", f"user       = {user_msg[:80]}…")

    # ── Call the API ─────────────────────────────────────────────────────────
    print_divider("API Call")
    try:
        response = client.messages.create(
            model=model,
            max_tokens=512,
            system=system,
            messages=[
                {"role": "user", "content": user_msg}
            ]
        )
        log("RESPONSE", "Success")
    except Exception as e:
        log("ERROR", f"{type(e).__name__}: {e}")
        sys.exit(1)

    # ── Inspect metadata ─────────────────────────────────────────────────────
    print_divider("Metadata")
    for attr in ["id", "model", "role", "stop_reason", "type"]:
        if hasattr(response, attr):
            log("RESPONSE", f"{attr:12s} = {getattr(response, attr)}")

    # ── Content blocks ───────────────────────────────────────────────────────
    print_divider("Content")
    print_blocks(response)

    # ── Token usage ──────────────────────────────────────────────────────────
    print_divider("Usage")
    report_usage(getattr(response, "usage", None))

    print_divider("Module 01 Complete")


if __name__ == "__main__":
    run()

"""
utils.py — Shared utilities for the MiniMax M2.7 Tutorial Suite
"""
import os, sys
from datetime import datetime
from typing import Optional, Any
from dotenv import load_dotenv
import anthropic

from config import (
    MODEL_STANDARD, MODEL_HIGHSPEED,
    ENDPOINT_GLOBAL, ENDPOINT_CHINA,
    PRICE_INPUT_PER_1M, PRICE_OUTPUT_PER_1M,
)


# ── Logging ──────────────────────────────────────────────────────────────────

def log(step: str, message: str) -> None:
    """Timestamped console logger with colour-coded step labels."""
    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    COLOURS = {
        "INIT": "\033[90m", "ENV": "\033[90m", "CLIENT": "\033[36m",
        "REQUEST": "\033[34m", "API": "\033[33m", "STREAM": "\033[33m",
        "RESPONSE": "\033[32m", "BLOCK": "\033[32m", "USAGE": "\033[35m",
        "TOOL": "\033[36m", "AGENT": "\033[35m", "THINK": "\033[90m",
        "WARN": "\033[33m", "ERROR": "\033[31m", "DONE": "\033[32m",
    }
    RESET = "\033[0m"
    colour = COLOURS.get(step, "")
    print(f"\033[90m[{now}]\033[0m {colour}[{step:8s}]\033[0m {message}")


def print_divider(title: str = "", char: str = "─", width: int = 72) -> None:
    line = char * width
    if title:
        pad = max(0, (width - len(title) - 2) // 2)
        print(f"\n{char * pad} {title} {char * (width - pad - len(title) - 2)}")
    else:
        print(f"\n{line}")


def print_header(title: str, subtitle: str = "") -> None:
    print_divider(char="═")
    print(f"  {title}")
    if subtitle:
        print(f"  \033[90m{subtitle}\033[0m")
    print_divider(char="═")


# ── Environment ──────────────────────────────────────────────────────────────

def load_env() -> tuple[str, str, str]:
    """
    Load .env, validate required vars, return (api_key, base_url, model).
    Supports MINIMAX_USE_HIGHSPEED env flag to switch model variant.
    """
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        log("ERROR", "Missing ANTHROPIC_API_KEY in .env")
        sys.exit(1)

    base_url = os.getenv("ANTHROPIC_BASE_URL", ENDPOINT_GLOBAL)
    use_hs   = os.getenv("MINIMAX_USE_HIGHSPEED", "false").lower() == "true"
    model    = MODEL_HIGHSPEED if use_hs else MODEL_STANDARD

    masked = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    log("ENV", f"Endpoint  : {base_url}")
    log("ENV", f"API key   : {masked}")
    log("ENV", f"Model     : {model}")
    return api_key, base_url, model


def make_client(api_key: str, base_url: str) -> anthropic.Anthropic:
    """Create and return an Anthropic client pointed at MiniMax."""
    client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
    log("CLIENT", "Anthropic client initialised → MiniMax endpoint")
    return client


# ── Response helpers ──────────────────────────────────────────────────────────

def report_usage(usage: Any, label: str = "") -> dict:
    """
    Print and return a cost breakdown from message.usage.
    Works with Anthropic SDK usage objects (has input_tokens / output_tokens).
    """
    if usage is None:
        log("USAGE", "No usage object returned")
        return {}

    inp   = getattr(usage, "input_tokens", 0) or 0
    out   = getattr(usage, "output_tokens", 0) or 0
    cr    = getattr(usage, "cache_read_input_tokens", 0) or 0
    cw    = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cost  = (inp / 1_000_000) * PRICE_INPUT_PER_1M \
          + (out / 1_000_000) * PRICE_OUTPUT_PER_1M

    prefix = f"[{label}] " if label else ""
    log("USAGE", f"{prefix}Input  tokens : {inp:,}")
    log("USAGE", f"{prefix}Output tokens : {out:,}")
    if cr:  log("USAGE", f"{prefix}Cache  read   : {cr:,}  ← saved")
    if cw:  log("USAGE", f"{prefix}Cache  write  : {cw:,}")
    log("USAGE", f"{prefix}Est. cost USD : ${cost:.6f}  (at list pricing)")

    return {"input": inp, "output": out, "cache_read": cr,
            "cache_write": cw, "cost_usd": cost}


def extract_text(message: Any) -> str:
    """Return the concatenated text from all text blocks in a response."""
    parts = []
    for block in getattr(message, "content", []):
        if getattr(block, "type", "") == "text":
            parts.append(getattr(block, "text", ""))
    return "\n".join(parts)


def print_blocks(message: Any) -> None:
    """Pretty-print every content block in a response."""
    import json
    for i, block in enumerate(getattr(message, "content", []), 1):
        btype = getattr(block, "type", "unknown")
        log("BLOCK", f"#{i} type={btype}")
        if btype == "thinking":
            think = getattr(block, "thinking", "")
            print(f"\n  ╭─ thinking ({len(think)} chars) ─\n  │ "
                  + think[:400].replace("\n", "\n  │ ")
                  + (" …[truncated]" if len(think) > 400 else "")
                  + "\n  ╰─")
        elif btype == "text":
            print(f"\n  ╭─ text ─\n  │ "
                  + getattr(block, "text", "").replace("\n", "\n  │ ")
                  + "\n  ╰─")
        elif btype == "tool_use":
            print(f"\n  ╭─ tool_use : {getattr(block,'name','?')} "
                  f"(id={getattr(block,'id','?')}) ─")
            print("  │ " + json.dumps(getattr(block, "input", {}), indent=2)
                                     .replace("\n", "\n  │ "))
            print("  ╰─")
        else:
            print(f"\n  ─ unknown block: {block}")

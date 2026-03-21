"""
Module 05 — Extended Thinking / Reasoning Tokens
──────────────────────────────────────────────────
Covers:
  • Enabling extended thinking in the request
  • Reading thinking blocks vs text blocks
  • Setting thinking budget_tokens
  • Comparing responses with / without thinking
  • Preserving thinking blocks in conversation history (CRITICAL for M2-series)

Note: MiniMax M2-series uses interleaved <think>…</think> tokens internally.
When the Anthropic-compat layer surfaces them as thinking blocks, preserve them
in history exactly — do NOT strip them.
"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log, report_usage


def call_with_thinking(client, model: str, prompt: str, budget: int = 2000) -> dict:
    """
    Send a request with extended thinking enabled.
    Returns a dict with thinking text, final text, latency, and usage.
    """
    log("THINK", f"Requesting extended thinking (budget={budget} tokens)")
    t0 = time.perf_counter()

    response = client.messages.create(
        model=model,
        max_tokens=budget + 1024,   # budget + room for output
        thinking={
            "type": "enabled",
            "budget_tokens": budget,
        },
        messages=[{"role": "user", "content": prompt}],
    )

    latency = time.perf_counter() - t0

    thinking_text = ""
    answer_text   = ""
    for block in getattr(response, "content", []):
        btype = getattr(block, "type", "")
        if btype == "thinking":
            thinking_text = getattr(block, "thinking", "")
        elif btype == "text":
            answer_text = getattr(block, "text", "")

    return {
        "thinking":  thinking_text,
        "answer":    answer_text,
        "latency":   latency,
        "usage":     getattr(response, "usage", None),
        "response":  response,
    }


def call_without_thinking(client, model: str, prompt: str) -> dict:
    """Send the same prompt without extended thinking."""
    t0 = time.perf_counter()

    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    latency = time.perf_counter() - t0
    answer  = ""
    for block in getattr(response, "content", []):
        if getattr(block, "type", "") == "text":
            answer = getattr(block, "text", "")
            break

    return {"answer": answer, "latency": latency, "usage": getattr(response, "usage", None)}


def run() -> None:
    print_header(
        "Module 05 · Extended Thinking",
        "Reasoning tokens, thinking budget, before/after comparison"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    # ── Hard reasoning challenge ──────────────────────────────────────────────
    hard_prompt = (
        "A farmer has 17 sheep. All but 9 die. "
        "How many sheep does he have? "
        "Then: if he buys twice as many as he has left, "
        "and sells a third of his total, how many remain? "
        "Show your work step by step."
    )

    print_divider("Prompt")
    print(f"  {hard_prompt}\n")

    # ── Without thinking ─────────────────────────────────────────────────────
    print_divider("Response WITHOUT Extended Thinking")
    try:
        no_think = call_without_thinking(client, model, hard_prompt)
        print(f"\n  {no_think['answer']}\n")
        log("THINK", f"Latency: {no_think['latency']:.2f}s")
        report_usage(no_think["usage"], label="no-think")
    except Exception as e:
        log("WARN", f"No-think call failed: {e}")

    # ── With thinking ─────────────────────────────────────────────────────────
    print_divider("Response WITH Extended Thinking (budget=3000)")
    try:
        with_think = call_with_thinking(client, model, hard_prompt, budget=3000)

        print("\n  ╭─ THINKING (first 600 chars) ─")
        snippet = with_think["thinking"][:600]
        for line in snippet.split("\n"):
            print(f"  │ {line}")
        if len(with_think["thinking"]) > 600:
            print(f"  │ … [{len(with_think['thinking'])-600} more chars]")
        print("  ╰─\n")

        print("\n  ╭─ FINAL ANSWER ─")
        for line in with_think["answer"].split("\n"):
            print(f"  │ {line}")
        print("  ╰─\n")

        log("THINK", f"Thinking length : {len(with_think['thinking'])} chars")
        log("THINK", f"Answer length   : {len(with_think['answer'])} chars")
        log("THINK", f"Latency         : {with_think['latency']:.2f}s")
        report_usage(with_think["usage"], label="thinking")

    except Exception as e:
        log("WARN", f"Thinking call failed (may not be enabled on this endpoint): {e}")
        log("WARN", "Extended thinking is model- and endpoint-dependent. Skipping.")

    # ── Critical note ─────────────────────────────────────────────────────────
    print_divider("Critical: Preserving Thinking in History")
    print("""
  When building multi-turn conversations with M2-series models:

  ✓ DO:   history.append({"role": "assistant", "content": response.content})
           ↳ passes the full list of blocks including thinking blocks

  ✗ DON'T: history.append({"role": "assistant", "content": extract_text(response)})
            ↳ strips thinking blocks, degrades subsequent responses

  MiniMax M2-series uses interleaved <think>…</think> tokens. The Anthropic
  compatibility layer surfaces these as thinking content blocks. Removing them
  from history negatively impacts model performance on follow-up turns.
    """)

    print_divider("Module 05 Complete")


if __name__ == "__main__":
    run()

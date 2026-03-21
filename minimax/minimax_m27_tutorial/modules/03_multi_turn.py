"""
Module 03 — Multi-Turn Conversation
─────────────────────────────────────
Covers:
  • Building a conversation history list
  • Appending assistant responses correctly
  • Maintaining context across turns
  • Tracking cumulative token usage across a session
  • The "thinking" tag preservation requirement for M2-series
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log, report_usage, extract_text


def run() -> None:
    print_header(
        "Module 03 · Multi-Turn Conversation",
        "Context management, history building, cumulative usage tracking"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    system = (
        "You are a Python tutor. Keep answers focused and use code examples. "
        "Build on what was already discussed — don't repeat basics already covered."
    )

    # ── Conversation turns ────────────────────────────────────────────────────
    turns = [
        "What is a Python decorator? Give me a minimal example.",
        "Now show me a decorator that measures execution time.",
        "How would I stack multiple decorators on one function?",
    ]

    history = []
    total_usage = {"input": 0, "output": 0, "cost_usd": 0.0}

    for turn_num, user_text in enumerate(turns, 1):
        print_divider(f"Turn {turn_num} / {len(turns)}")
        log("REQUEST", f"User: {user_text}")

        # Append user message to history
        history.append({"role": "user", "content": user_text})

        try:
            response = client.messages.create(
                model=model,
                max_tokens=512,
                system=system,
                messages=history,
            )
        except Exception as e:
            log("ERROR", f"{type(e).__name__}: {e}")
            sys.exit(1)

        assistant_text = extract_text(response)
        log("RESPONSE", f"Assistant ({len(assistant_text)} chars):")
        print(f"\n{assistant_text}\n")

        # ── IMPORTANT: append full content (preserving thinking tags) ────────
        # M2-series uses interleaved <think>…</think> tokens.
        # Always pass response.content back — never strip thinking blocks.
        history.append({
            "role": "assistant",
            "content": response.content,  # ← full blocks, not just text
        })

        # Track usage
        usage = report_usage(getattr(response, "usage", None), label=f"T{turn_num}")
        for k in ("input", "output", "cost_usd"):
            total_usage[k] += usage.get(k, 0)

    # ── Session summary ───────────────────────────────────────────────────────
    print_divider("Session Summary")
    log("USAGE", f"Total turns        : {len(turns)}")
    log("USAGE", f"Total input  tokens: {total_usage['input']:,}")
    log("USAGE", f"Total output tokens: {total_usage['output']:,}")
    log("USAGE", f"Total est. cost    : ${total_usage['cost_usd']:.6f} USD")
    log("USAGE", f"History length     : {len(history)} messages")

    print_divider("Module 03 Complete")


if __name__ == "__main__":
    run()

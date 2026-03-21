"""
Module 02 — Streaming Responses
────────────────────────────────
Covers:
  • client.messages.stream() context manager
  • Iterating over text deltas in real time
  • Getting the final message object post-stream
  • Token usage from the stream's final_message
  • Measuring time-to-first-token (TTFT) and total latency
"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log, report_usage


def run() -> None:
    print_header(
        "Module 02 · Streaming Responses",
        "Real-time token output, TTFT measurement, stream final_message"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    system = "You are a senior software architect. Be detailed but organised."
    prompt = (
        "Explain the architecture of a production-grade REST API in Python. "
        "Cover: routing, middleware, auth, error handling, and observability. "
        "Use short code snippets where helpful."
    )

    print_divider("Streaming Request")
    log("REQUEST", f"model      = {model}")
    log("REQUEST", f"max_tokens = 800")
    log("REQUEST", f"prompt     = {prompt[:70]}…")

    # ── Stream ───────────────────────────────────────────────────────────────
    print_divider("Live Stream Output")
    start        = time.perf_counter()
    ttft         = None
    char_count   = 0

    try:
        with client.messages.stream(
            model=model,
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                if ttft is None:
                    ttft = time.perf_counter() - start
                print(text, end="", flush=True)
                char_count += len(text)

            final = stream.get_final_message()

        total = time.perf_counter() - start
        print()  # newline after stream

    except Exception as e:
        log("ERROR", f"{type(e).__name__}: {e}")
        sys.exit(1)

    # ── Metrics ──────────────────────────────────────────────────────────────
    print_divider("Stream Metrics")
    log("STREAM", f"Time-to-first-token : {ttft*1000:.0f} ms")
    log("STREAM", f"Total latency       : {total:.2f} s")
    log("STREAM", f"Chars received      : {char_count:,}")
    log("STREAM", f"Stop reason         : {getattr(final, 'stop_reason', '?')}")

    print_divider("Usage")
    report_usage(getattr(final, "usage", None))

    print_divider("Module 02 Complete")


if __name__ == "__main__":
    run()

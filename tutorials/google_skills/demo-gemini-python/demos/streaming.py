"""
Section 3 — Streaming
Get responses streamed token-by-token for lower perceived latency.
"""

DEFAULT_PROMPT = "Write a 100-word story about a curious astronaut."
DEFAULT_MODEL = "gemini-3-flash-preview"


def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    prompt = prompt or DEFAULT_PROMPT
    print(f"Model : {model}")
    print(f"Prompt: {prompt}\n")
    print("Response (streamed):")

    for chunk in client.models.generate_content_stream(model=model, contents=prompt):
        print(chunk.text, end="", flush=True)

    print()  # newline after stream ends

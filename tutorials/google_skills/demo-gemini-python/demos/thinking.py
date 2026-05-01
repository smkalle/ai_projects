"""
Section 17 — Thinking / Reasoning
Control how deeply the model reasons before responding.
Uses gemini-3.1-pro-preview which has thinking enabled by default.
"""

DEFAULT_PROMPT = (
    "A bat and a ball together cost $1.10. "
    "The bat costs $1.00 more than the ball. "
    "How much does the ball cost? Show your reasoning."
)
THINKING_MODEL = "gemini-3.1-pro-preview"


def run(client, *, model: str = THINKING_MODEL, prompt: str | None = None, **_) -> None:
    from google.genai import types  # pylint: disable=import-outside-toplevel

    # Default to the thinking-capable model unless caller overrides.
    thinking_model = THINKING_MODEL if model == "gemini-3-flash-preview" else model

    prompt = prompt or DEFAULT_PROMPT
    print(f"Model : {thinking_model}")
    print(f"Prompt: {prompt}\n")

    response = client.models.generate_content(
        model=thinking_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level=types.ThinkingLevel.HIGH,
            )
        ),
    )

    # Separate reasoning steps from the final answer when available.
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        parts = getattr(candidates[0].content, "parts", [])
        for part in parts:
            if getattr(part, "thought", False):
                print("--- Reasoning ---")
                print(part.text)
                print()
            else:
                print("--- Final answer ---")
                print(part.text)
    else:
        print(response.text)

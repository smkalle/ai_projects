"""
Section 1 — Text Generation
Send a text prompt and receive a single text response.
"""

DEFAULT_PROMPT = "Explain quantum computing in two sentences."
DEFAULT_MODEL = "gemini-3-flash-preview"


def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    prompt = prompt or DEFAULT_PROMPT
    print(f"Model : {model}")
    print(f"Prompt: {prompt}\n")

    response = client.models.generate_content(model=model, contents=prompt)
    print(response.text)

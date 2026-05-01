"""
Section 6 — Function Calling
Let the model decide when to invoke a Python function to fetch real data.
"""

DEFAULT_PROMPT = "What's the weather like in Boston and Tokyo right now?"
DEFAULT_MODEL = "gemini-3-flash-preview"


# ---------------------------------------------------------------------------
# Tool definition — passed directly to GenerateContentConfig
# ---------------------------------------------------------------------------

def get_current_weather(location: str) -> str:
    """Return the current weather for a city (mock data)."""
    city = location.lower()
    if "boston" in city:
        return "Snowing, 28°F (-2°C)"
    if "tokyo" in city:
        return "Partly cloudy, 68°F (20°C)"
    return "Sunny, 72°F (22°C)"


# ---------------------------------------------------------------------------
# Demo runner
# ---------------------------------------------------------------------------

def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    from google.genai import types  # pylint: disable=import-outside-toplevel

    prompt = prompt or DEFAULT_PROMPT
    print(f"Model : {model}")
    print(f"Prompt: {prompt}\n")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(tools=[get_current_weather]),
    )

    function_calls = getattr(response, "function_calls", None)
    if function_calls:
        for fc in function_calls:
            result = get_current_weather(**dict(fc.args))
            print(f"  Tool call : {fc.name}({dict(fc.args)})")
            print(f"  Tool result: {result}")
        print()
        print("(In a real agentic loop you would send tool results back to continue.)")
    else:
        print(response.text)

"""
Section 7 — Search Grounding
Ground model responses in live Google Search results to reduce hallucinations.
"""

DEFAULT_PROMPT = "What are the most recent advancements in fusion energy research?"
DEFAULT_MODEL = "gemini-3-flash-preview"


def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    from google.genai import types  # pylint: disable=import-outside-toplevel

    prompt = prompt or DEFAULT_PROMPT
    print(f"Model : {model}")
    print(f"Prompt: {prompt}\n")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )

    print(response.text)

    # Surface grounding metadata when available.
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        meta = getattr(candidates[0], "grounding_metadata", None)
        if meta:
            queries = getattr(meta, "web_search_queries", [])
            chunks = getattr(meta, "grounding_chunks", [])
            if queries:
                print(f"\nSearch queries used: {queries}")
            if chunks:
                titles = []
                for chunk in chunks:
                    web = getattr(chunk, "web", None)
                    if web:
                        title = getattr(web, "title", None)
                        if title:
                            titles.append(title)
                if titles:
                    print(f"Sources: {titles}")

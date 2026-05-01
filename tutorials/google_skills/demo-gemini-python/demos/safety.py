"""
Section 18 — Safety Settings
Adjust harm-category thresholds and inspect per-category safety ratings.
"""

DEFAULT_PROMPT = "Write a short joke about a software developer."
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
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                ),
            ]
        ),
    )

    text = getattr(response, "text", None)
    if text is None:
        candidates = getattr(response, "candidates", None) or []
        finish = candidates[0].finish_reason if candidates else "unknown"
        print(f"[BLOCKED] finish_reason={finish}")
    else:
        print(text)

    # Print per-category safety ratings when present.
    candidates = getattr(response, "candidates", None) or []
    ratings = getattr(candidates[0], "safety_ratings", []) if candidates else []
    if ratings:
        print("\nSafety ratings:")
        for r in ratings:
            blocked = getattr(r, "blocked", False)
            prob = getattr(r, "probability", "?")
            print(f"  {r.category}: probability={prob}, blocked={blocked}")

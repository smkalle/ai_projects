"""
Section 5 — Structured Output (JSON)
Generate responses that conform to a Pydantic schema via response_json_schema.
"""

from pydantic import BaseModel

DEFAULT_PROMPT = "List 3 popular cookie recipes."
DEFAULT_MODEL = "gemini-3-flash-preview"


class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]


def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    from google.genai import types  # pylint: disable=import-outside-toplevel

    prompt = prompt or DEFAULT_PROMPT
    print(f"Model : {model}")
    print(f"Prompt: {prompt}")
    print(f"Schema: {Recipe.model_json_schema()}\n")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=list[Recipe],
        ),
    )

    # response.parsed contains list[Recipe] when available; fall back to raw JSON.
    parsed = getattr(response, "parsed", None)
    if parsed:
        for recipe in parsed:
            print(f"  {recipe.recipe_name}: {', '.join(recipe.ingredients[:3])}...")
    else:
        print(response.text)

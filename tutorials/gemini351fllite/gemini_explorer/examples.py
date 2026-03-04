"""Shared example data: Pydantic schemas, mock tools, prompts, and constants."""

from pydantic import BaseModel


# ── Pydantic schemas for structured output ────────────────────────────────────


class Recipe(BaseModel):
    name: str
    cuisine: str
    prep_time_minutes: int
    ingredients: list[str]
    steps: list[str]
    difficulty: str


class MovieReview(BaseModel):
    title: str
    year: int
    rating: float
    genre: str
    summary: str
    pros: list[str]
    cons: list[str]


class CodeAnalysis(BaseModel):
    language: str
    purpose: str
    complexity: str
    functions: list[str]
    suggestions: list[str]


SCHEMAS = {
    "Recipe": Recipe,
    "Movie Review": MovieReview,
    "Code Analysis": CodeAnalysis,
}


# ── Default prompts per feature ───────────────────────────────────────────────

DEFAULT_PROMPTS = {
    "recipe": "Create a creative fusion recipe combining Thai and Italian cuisine.",
    "movie_review": "Write a review for a fictional sci-fi movie set in 2150.",
    "code_analysis": "Analyze this code:\ndef fib(n): return n if n<2 else fib(n-1)+fib(n-2)",
    "vision": "Describe this image in detail. What do you observe?",
    "audio": "Transcribe this audio. Then provide a summary.",
    "tools": "What's the weather in Tokyo and Paris? Also, what's 18% tip on a $127.50 bill?",
    "thinking": "A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?",
    "embed_a": "The cat sat on the mat.",
    "embed_b": "A kitten was sitting on a rug.",
    "bench": "Explain the concept of entropy in information theory.",
}



# ── Mock tool functions ──────────────────────────────────────────────────────


def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    data = {
        "tokyo": "22°C, partly cloudy, humidity 65%",
        "new york": "18°C, sunny, humidity 45%",
        "london": "14°C, rainy, humidity 80%",
        "paris": "16°C, overcast, humidity 70%",
        "sydney": "26°C, clear skies, humidity 55%",
    }
    return data.get(city.lower(), f"No weather data for {city}. Available: {', '.join(data)}")


def calculate(expression: str) -> str:
    """Evaluate a math expression. Supports basic arithmetic (+, -, *, /, %)."""
    allowed = set("0123456789+-*/.() %")
    if not all(c in allowed for c in expression):
        return "Error: invalid characters in expression"
    try:
        return str(eval(expression))  # noqa: S307
    except Exception as e:
        return f"Error: {e}"


# ── Shared constants ─────────────────────────────────────────────────────────

AUDIO_MIME_TYPES = {
    "mp3": "audio/mp3",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
}

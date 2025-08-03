from langchain_core.tools import tool
from langgraph.types import Command

@tool
def search_books(query: str) -> list[str]:
    """Search for books related to the query."""
    return [f"Book about {query}", f"Another book about {query}"]

@tool
def search_tv(query: str) -> list[str]:
    """Search for TV content related to the query."""
    return [f"TV show about {query}", f"Documentary about {query}"]

@tool
def search_news(query: str) -> list[str]:
    """Search for news articles related to the query."""
    return [f"News article about {query}", f"Another news article about {query}"]

@tool
def handoff(next_agent: str):
    """Hand off control to another agent by name (A2A).
    Valid names: 'publishing', 'broadcasting', 'news'."""
    return f"Handing off to {next_agent} agent."

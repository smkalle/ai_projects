"""
Example 2: Combined Web Search + Web Fetch with Dynamic Filtering
=================================================================

This example demonstrates combining web search and web fetch tools
in a single request. Claude will:
1. Search the web for relevant pages
2. Fetch and deeply analyze the most promising results
3. Use dynamic filtering to extract only relevant content from fetched pages

This pattern is ideal for:
- Technical research and literature review
- Competitive analysis
- Fact-checking and verification
- Deep-dive analysis of search results
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()


def search_and_fetch_research(topic: str):
    """
    Perform a combined search + fetch workflow with dynamic filtering.

    Claude will search for relevant sources, select the best ones,
    fetch their full content, and extract targeted information.
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print(f"RESEARCH: {topic}")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Research the following topic thoroughly: {topic}\n\n"
                    "Instructions:\n"
                    "1. Search for the most authoritative and recent sources\n"
                    "2. Fetch and analyze the top 2-3 most relevant pages\n"
                    "3. Extract key findings, data points, and conclusions\n"
                    "4. Synthesize a comprehensive summary with citations"
                ),
            }
        ],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 5,
            },
            {
                "type": "web_fetch_20260209",
                "name": "web_fetch",
                "max_uses": 5,
                # Cap fetched content to control token usage.
                # Large pages can be 100K+ tokens without this.
                "max_content_tokens": 50000,
            },
        ],
    )

    # Handle pause_turn for long-running research
    messages = [
        {
            "role": "user",
            "content": f"Research the following topic thoroughly: {topic}\n\n"
            "Instructions:\n"
            "1. Search for the most authoritative and recent sources\n"
            "2. Fetch and analyze the top 2-3 most relevant pages\n"
            "3. Extract key findings, data points, and conclusions\n"
            "4. Synthesize a comprehensive summary with citations",
        }
    ]

    while response.stop_reason == "pause_turn":
        print("[Research in progress — Claude is still working...]")
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": "Please continue your research."})

        response = client.beta.messages.create(
            model="claude-opus-4-6",
            max_tokens=8192,
            betas=["code-execution-web-tools-2026-02-09"],
            messages=messages,
            tools=[
                {"type": "web_search_20260209", "name": "web_search", "max_uses": 5},
                {
                    "type": "web_fetch_20260209",
                    "name": "web_fetch",
                    "max_uses": 5,
                    "max_content_tokens": 50000,
                },
            ],
        )

    # Extract and display results
    print_research_results(response)
    return response


def print_research_results(response):
    """Extract and display the research results with citations."""

    sources = []
    full_text = []

    for block in response.content:
        if block.type == "text":
            full_text.append(block.text)

            # Collect citations
            if hasattr(block, "citations") and block.citations:
                for citation in block.citations:
                    url = getattr(citation, "url", None)
                    title = getattr(citation, "title", None) or getattr(
                        citation, "document_title", None
                    )
                    if url and url not in [s["url"] for s in sources]:
                        sources.append({"url": url, "title": title})

    # Print the synthesized research
    print("\n--- RESEARCH FINDINGS ---\n")
    print("".join(full_text))

    # Print sources
    if sources:
        print("\n--- SOURCES ---\n")
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Untitled")
            print(f"  [{i}] {title}")
            print(f"      {source['url']}")

    # Print usage
    usage = response.usage
    print("\n--- USAGE ---")
    print(f"  Input tokens:  {usage.input_tokens:,}")
    print(f"  Output tokens: {usage.output_tokens:,}")
    if hasattr(usage, "server_tool_use") and usage.server_tool_use:
        stu = usage.server_tool_use
        web_searches = getattr(stu, "web_search_requests", 0) if not isinstance(stu, dict) else stu.get("web_search_requests", 0)
        web_fetches = getattr(stu, "web_fetch_requests", 0) if not isinstance(stu, dict) else stu.get("web_fetch_requests", 0)
        print(f"  Web searches:  {web_searches}")
        print(f"  Web fetches:   {web_fetches}")


def fetch_and_analyze_url(url: str, question: str):
    """
    Fetch a specific URL and answer a question about its content.

    With dynamic filtering, Claude will fetch the page and write code
    to extract only the relevant sections, rather than loading the
    entire page into context.
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print(f"FETCH & ANALYZE: {url}")
    print(f"QUESTION: {question}")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-sonnet-4-6",  # Sonnet for cost efficiency on fetch tasks
        max_tokens=4096,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Fetch the content at {url} and answer this question: "
                    f"{question}\n\n"
                    "Extract only the relevant sections — don't summarize the "
                    "entire page."
                ),
            }
        ],
        tools=[
            {
                "type": "web_fetch_20260209",
                "name": "web_fetch",
                "max_uses": 3,
                "max_content_tokens": 100000,
                "citations": {"enabled": True},
            }
        ],
    )

    for block in response.content:
        if block.type == "text":
            print(f"\n{block.text}")

    # Print usage
    usage = response.usage
    print(f"\n--- Usage: {usage.input_tokens:,} in / {usage.output_tokens:,} out ---")

    return response


def search_with_citations_example():
    """
    Demonstrate how to properly extract and display citations from
    combined search + fetch results.
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print("SEARCH WITH CITATION EXTRACTION")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[
            {
                "role": "user",
                "content": (
                    "What is the current scientific consensus on the health "
                    "effects of intermittent fasting? Cite specific studies."
                ),
            }
        ],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 3,
                # Only search trusted medical sources
                "allowed_domains": [
                    "pubmed.ncbi.nlm.nih.gov",
                    "nih.gov",
                    "who.int",
                    "mayoclinic.org",
                    "nature.com",
                    "thelancet.com",
                    "bmj.com",
                ],
            },
            {
                "type": "web_fetch_20260209",
                "name": "web_fetch",
                "max_uses": 3,
                "citations": {"enabled": True},
            },
        ],
    )

    # Build a structured citation list
    all_citations = []
    text_parts = []

    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
            if hasattr(block, "citations") and block.citations:
                for c in block.citations:
                    citation_data = {
                        "type": getattr(c, "type", "unknown"),
                    }
                    # web_search_result_location citations
                    if hasattr(c, "url"):
                        citation_data["url"] = c.url
                        citation_data["title"] = getattr(c, "title", "")
                        citation_data["cited_text"] = getattr(c, "cited_text", "")
                    # char_location citations (from web_fetch)
                    elif hasattr(c, "document_title"):
                        citation_data["title"] = c.document_title
                        citation_data["cited_text"] = getattr(c, "cited_text", "")
                        citation_data["start"] = getattr(c, "start_char_index", 0)
                        citation_data["end"] = getattr(c, "end_char_index", 0)

                    all_citations.append(citation_data)

    print("\n--- RESPONSE ---\n")
    print("".join(text_parts))

    print(f"\n--- CITATIONS ({len(all_citations)}) ---\n")
    for i, c in enumerate(all_citations, 1):
        print(f"  [{i}] {c.get('title', 'N/A')}")
        if "url" in c:
            print(f"      URL: {c['url']}")
        if c.get("cited_text"):
            print(f"      Text: {c['cited_text'][:120]}...")
        print()

    return response


if __name__ == "__main__":
    # Example 1: Full research workflow
    search_and_fetch_research(
        "Current state of nuclear fusion energy — latest milestones and "
        "timeline projections for commercial viability"
    )

    # Example 2: Fetch and analyze a specific URL
    # Uncomment to run:
    # fetch_and_analyze_url(
    #     "https://docs.python.org/3/whatsnew/3.13.html",
    #     "What are the key performance improvements in Python 3.13?"
    # )

    # Example 3: Search with citation extraction
    # Uncomment to run:
    # search_with_citations_example()

"""
Example 1: Basic Web Search with Dynamic Filtering
===================================================

This example demonstrates the simplest use of Claude's dynamic filtering
for web search. Claude autonomously writes and executes Python code to
filter search results before they reach the context window.

Key concepts:
- Using web_search_20260209 tool type
- The code-execution-web-tools-2026-02-09 beta header
- Parsing the response for text, citations, and usage metadata
- Understanding server_tool_use vs tool_use blocks
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()


def basic_search_with_dynamic_filtering():
    """
    Perform a web search with dynamic filtering enabled.

    Behind the scenes, Claude will:
    1. Generate search queries
    2. Write Python code to filter/process results
    3. Execute that code in a sandboxed container
    4. Return only the filtered, relevant information
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print("BASIC WEB SEARCH WITH DYNAMIC FILTERING")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[
            {
                "role": "user",
                "content": (
                    "What are the most significant AI research breakthroughs "
                    "published in the last 2 months? Focus on papers with "
                    "novel architectures or surprising results."
                ),
            }
        ],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                # max_uses limits the number of search queries Claude can make.
                # Without this, Claude might perform many searches for complex queries.
                "max_uses": 5,
            }
        ],
    )

    # --- Parse and display the response ---
    print(f"\nStop reason: {response.stop_reason}")
    print(f"Model: {response.model}")
    print()

    parse_response(response)
    print_usage(response)


def parse_response(response):
    """Parse a web search response, extracting text, citations, and tool events."""

    for i, block in enumerate(response.content):
        if block.type == "text":
            # Text block — may include citations
            print(f"--- Text Block {i} ---")
            print(block.text[:500])
            if len(block.text) > 500:
                print(f"  ... ({len(block.text)} chars total)")

            # Extract citations if present
            if hasattr(block, "citations") and block.citations:
                print(f"\n  Citations ({len(block.citations)}):")
                for citation in block.citations:
                    if hasattr(citation, "url"):
                        print(f"    - {citation.title}")
                        print(f"      URL: {citation.url}")
                        if hasattr(citation, "cited_text") and citation.cited_text:
                            print(f"      Text: {citation.cited_text[:100]}...")
            print()

        elif block.type == "server_tool_use":
            # Claude decided to use a server-side tool (web_search or code_execution)
            print(f"--- Server Tool Use {i}: {block.name} ---")
            if hasattr(block, "input"):
                # For web_search, input contains the query
                print(f"  Input: {json.dumps(block.input, indent=2)[:200]}")
            print()

        elif block.type == "web_search_tool_result":
            # Search results returned by the server
            print(f"--- Search Results {i} ---")
            if hasattr(block, "content"):
                if isinstance(block.content, list):
                    print(f"  {len(block.content)} results returned")
                    for result in block.content[:3]:
                        if hasattr(result, "title"):
                            print(f"    - {result.title}")
                            print(f"      URL: {result.url}")
                            if hasattr(result, "page_age") and result.page_age:
                                print(f"      Age: {result.page_age}")
                elif hasattr(block.content, "type"):
                    # Could be an error
                    if "error" in block.content.type:
                        print(f"  ERROR: {block.content.error_code}")
            print()

        elif block.type == "bash_code_execution_tool_result":
            # Code execution result (dynamic filtering ran code)
            print(f"--- Code Execution Result {i} ---")
            if hasattr(block, "content"):
                content = block.content
                if hasattr(content, "stdout") and content.stdout:
                    print(f"  stdout: {content.stdout[:200]}")
                if hasattr(content, "stderr") and content.stderr:
                    print(f"  stderr: {content.stderr[:200]}")
                if hasattr(content, "return_code"):
                    print(f"  return_code: {content.return_code}")
            print()

        else:
            print(f"--- Block {i}: {block.type} ---")
            print()


def print_usage(response):
    """Print token usage and cost-relevant metadata."""
    usage = response.usage
    print("=" * 70)
    print("USAGE STATISTICS")
    print("=" * 70)
    print(f"  Input tokens:  {usage.input_tokens:,}")
    print(f"  Output tokens: {usage.output_tokens:,}")

    if hasattr(usage, "cache_read_input_tokens"):
        print(f"  Cache read:    {usage.cache_read_input_tokens:,}")
    if hasattr(usage, "cache_creation_input_tokens"):
        print(f"  Cache created: {usage.cache_creation_input_tokens:,}")

    if hasattr(usage, "server_tool_use") and usage.server_tool_use:
        stu = usage.server_tool_use
        if isinstance(stu, dict):
            web_searches = stu.get("web_search_requests", 0)
            web_fetches = stu.get("web_fetch_requests", 0)
            code_exec = stu.get("code_execution_requests", 0)
        else:
            web_searches = getattr(stu, "web_search_requests", 0)
            web_fetches = getattr(stu, "web_fetch_requests", 0)
            code_exec = getattr(stu, "code_execution_requests", 0)

        print(f"  Web searches:  {web_searches}")
        print(f"  Web fetches:   {web_fetches}")
        print(f"  Code execs:    {code_exec}")

        # Estimate search cost ($10 per 1,000 searches)
        if web_searches:
            search_cost = web_searches * 0.01
            print(f"  Search cost:   ${search_cost:.4f}")

    print("=" * 70)


def compare_with_without_dynamic_filtering():
    """
    Compare the same query with and without dynamic filtering to demonstrate
    the token savings.
    """
    client = anthropic.Anthropic()
    query = "What is the current stock price and P/E ratio of NVIDIA?"

    print("\n" + "=" * 70)
    print("COMPARISON: WITH vs WITHOUT DYNAMIC FILTERING")
    print("=" * 70)

    # --- Without dynamic filtering (basic search) ---
    print("\n--- Without Dynamic Filtering (web_search_20250305) ---")
    response_basic = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": query}],
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 3,
            }
        ],
    )
    print(f"  Input tokens:  {response_basic.usage.input_tokens:,}")
    print(f"  Output tokens: {response_basic.usage.output_tokens:,}")

    # --- With dynamic filtering ---
    print("\n--- With Dynamic Filtering (web_search_20260209) ---")
    response_dynamic = client.beta.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[{"role": "user", "content": query}],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 3,
            }
        ],
    )
    print(f"  Input tokens:  {response_dynamic.usage.input_tokens:,}")
    print(f"  Output tokens: {response_dynamic.usage.output_tokens:,}")

    # --- Calculate savings ---
    input_saved = response_basic.usage.input_tokens - response_dynamic.usage.input_tokens
    if response_basic.usage.input_tokens > 0:
        pct_saved = (input_saved / response_basic.usage.input_tokens) * 100
    else:
        pct_saved = 0

    print(f"\n  Input tokens saved: {input_saved:,} ({pct_saved:.1f}%)")


if __name__ == "__main__":
    basic_search_with_dynamic_filtering()

    # Uncomment to run the comparison (uses 2 API calls):
    # compare_with_without_dynamic_filtering()

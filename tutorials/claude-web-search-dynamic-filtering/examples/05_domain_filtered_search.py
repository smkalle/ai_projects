"""
Example 5: Domain Filtering and Cost Optimization
===================================================

This example demonstrates production-grade patterns for:
1. Domain filtering — restrict searches to trusted sources
2. Location-based search — localize results by geography
3. Cost optimization — control token spend with max_uses, max_content_tokens
4. Usage tracking — monitor and report on search costs
5. Token budget management — stay within budget constraints
"""

import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Domain Filtering Patterns
# ---------------------------------------------------------------------------

def search_academic_sources(query: str):
    """Search only academic and peer-reviewed sources."""
    client = anthropic.Anthropic()

    print("=" * 70)
    print(f"ACADEMIC SEARCH: {query}")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[{"role": "user", "content": query}],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 3,
                "allowed_domains": [
                    "arxiv.org",
                    "scholar.google.com",
                    "pubmed.ncbi.nlm.nih.gov",
                    "nature.com",
                    "science.org",
                    "ieee.org",
                    "acm.org",
                    "openreview.net",
                ],
            }
        ],
    )

    print_response_with_usage(response)
    return response


def search_news_sources(query: str, blocked_sources: list = None):
    """Search news with optional blocking of specific outlets."""
    client = anthropic.Anthropic()

    if blocked_sources is None:
        blocked_sources = [
            "pinterest.com",
            "reddit.com",
            "twitter.com",
            "x.com",
            "facebook.com",
        ]

    print("=" * 70)
    print(f"NEWS SEARCH: {query}")
    print(f"Blocked: {', '.join(blocked_sources)}")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[{"role": "user", "content": query}],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 5,
                "blocked_domains": blocked_sources,
            }
        ],
    )

    print_response_with_usage(response)
    return response


def search_documentation(query: str, doc_domains: list):
    """Search within specific documentation sites."""
    client = anthropic.Anthropic()

    print("=" * 70)
    print(f"DOCS SEARCH: {query}")
    print(f"Domains: {', '.join(doc_domains)}")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[{"role": "user", "content": query}],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 3,
                "allowed_domains": doc_domains,
            },
            {
                "type": "web_fetch_20260209",
                "name": "web_fetch",
                "max_uses": 3,
                "max_content_tokens": 30000,
            },
        ],
    )

    print_response_with_usage(response)
    return response


# ---------------------------------------------------------------------------
# Location-Based Search
# ---------------------------------------------------------------------------

def search_localized(query: str, city: str, region: str, country: str, timezone: str):
    """Perform a location-aware search for geo-specific results."""
    client = anthropic.Anthropic()

    print("=" * 70)
    print(f"LOCALIZED SEARCH: {query}")
    print(f"Location: {city}, {region}, {country}")
    print("=" * 70)

    response = client.beta.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        betas=["code-execution-web-tools-2026-02-09"],
        messages=[{"role": "user", "content": query}],
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 3,
                "user_location": {
                    "type": "approximate",
                    "city": city,
                    "region": region,
                    "country": country,
                    "timezone": timezone,
                },
            }
        ],
    )

    print_response_with_usage(response)
    return response


# ---------------------------------------------------------------------------
# Cost Optimization
# ---------------------------------------------------------------------------

class CostTracker:
    """Track and report on web search API costs."""

    # Pricing as of February 2026
    SEARCH_COST_PER_1K = 10.00  # $10 per 1,000 searches
    # Approximate token costs for Sonnet 4.6 (update with actual pricing)
    INPUT_TOKEN_COST_PER_1M = 3.00
    OUTPUT_TOKEN_COST_PER_1M = 15.00

    def __init__(self):
        self.total_searches = 0
        self.total_fetches = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_read_tokens = 0
        self.requests = []

    def track(self, response, label: str = ""):
        """Track usage from a response."""
        usage = response.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        cache_read = getattr(usage, "cache_read_input_tokens", 0)

        searches = 0
        fetches = 0
        if hasattr(usage, "server_tool_use") and usage.server_tool_use:
            stu = usage.server_tool_use
            if isinstance(stu, dict):
                searches = stu.get("web_search_requests", 0)
                fetches = stu.get("web_fetch_requests", 0)
            else:
                searches = getattr(stu, "web_search_requests", 0)
                fetches = getattr(stu, "web_fetch_requests", 0)

        self.total_searches += searches
        self.total_fetches += fetches
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cache_read_tokens += cache_read

        request_data = {
            "label": label,
            "searches": searches,
            "fetches": fetches,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read,
        }
        self.requests.append(request_data)
        return request_data

    def estimate_cost(self) -> dict:
        """Estimate the total cost of all tracked requests."""
        search_cost = (self.total_searches / 1000) * self.SEARCH_COST_PER_1K
        # Cache reads are cheaper — use 90% discount for estimation
        effective_input_tokens = (
            self.total_input_tokens + self.total_cache_read_tokens * 0.1
        )
        input_cost = (effective_input_tokens / 1_000_000) * self.INPUT_TOKEN_COST_PER_1M
        output_cost = (
            self.total_output_tokens / 1_000_000
        ) * self.OUTPUT_TOKEN_COST_PER_1M

        return {
            "search_cost": search_cost,
            "input_token_cost": input_cost,
            "output_token_cost": output_cost,
            "total_estimated_cost": search_cost + input_cost + output_cost,
        }

    def report(self):
        """Print a detailed cost report."""
        costs = self.estimate_cost()

        print(f"\n{'=' * 70}")
        print("COST REPORT")
        print("=" * 70)
        print(f"  Requests:        {len(self.requests)}")
        print(f"  Web searches:    {self.total_searches}")
        print(f"  Web fetches:     {self.total_fetches}")
        print(f"  Input tokens:    {self.total_input_tokens:,}")
        print(f"  Output tokens:   {self.total_output_tokens:,}")
        print(f"  Cache read:      {self.total_cache_read_tokens:,}")
        print()
        print("  Estimated Costs:")
        print(f"    Search:        ${costs['search_cost']:.4f}")
        print(f"    Input tokens:  ${costs['input_token_cost']:.4f}")
        print(f"    Output tokens: ${costs['output_token_cost']:.4f}")
        print(f"    TOTAL:         ${costs['total_estimated_cost']:.4f}")
        print()

        if self.requests:
            print("  Per-Request Breakdown:")
            for i, req in enumerate(self.requests, 1):
                label = req["label"] or f"Request {i}"
                print(
                    f"    [{i}] {label}: "
                    f"{req['searches']} searches, "
                    f"{req['input_tokens']:,} in, "
                    f"{req['output_tokens']:,} out"
                )
        print("=" * 70)


def cost_optimized_research(queries: list):
    """
    Run multiple research queries with full cost tracking.

    Demonstrates:
    - Using Sonnet for cost efficiency
    - Limiting max_uses to control search count
    - Using max_content_tokens to cap fetch costs
    - Tracking and reporting total costs
    """
    client = anthropic.Anthropic()
    tracker = CostTracker()

    tools = [
        {
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": 3,  # Conservative limit
        },
        {
            "type": "web_fetch_20260209",
            "name": "web_fetch",
            "max_uses": 2,  # Limit expensive fetches
            "max_content_tokens": 30000,  # Cap per-page tokens
        },
    ]

    for query in queries:
        print(f"\n--- Researching: {query[:60]}... ---")

        response = client.beta.messages.create(
            model="claude-sonnet-4-6",  # Sonnet for cost efficiency
            max_tokens=2048,  # Cap output tokens
            betas=["code-execution-web-tools-2026-02-09"],
            messages=[{"role": "user", "content": query}],
            tools=tools,
        )

        tracker.track(response, label=query[:40])

        # Print brief result
        for block in response.content:
            if block.type == "text":
                print(f"  {block.text[:200]}...")
                break

    tracker.report()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_response_with_usage(response):
    """Print response text and usage statistics."""
    for block in response.content:
        if block.type == "text":
            print(f"\n{block.text}")

            if hasattr(block, "citations") and block.citations:
                print(f"\n  [{len(block.citations)} citations]")

    usage = response.usage
    searches = 0
    fetches = 0
    if hasattr(usage, "server_tool_use") and usage.server_tool_use:
        stu = usage.server_tool_use
        if isinstance(stu, dict):
            searches = stu.get("web_search_requests", 0)
            fetches = stu.get("web_fetch_requests", 0)
        else:
            searches = getattr(stu, "web_search_requests", 0)
            fetches = getattr(stu, "web_fetch_requests", 0)

    print(f"\n--- Usage: {usage.input_tokens:,} in / {usage.output_tokens:,} out "
          f"/ {searches} searches / {fetches} fetches ---")


if __name__ == "__main__":
    # Example 1: Academic search
    search_academic_sources(
        "What are the latest advances in transformer architecture efficiency?"
    )

    # Example 2: Documentation search
    # Uncomment to run:
    # search_documentation(
    #     "How do I use streaming with the Messages API?",
    #     doc_domains=[
    #         "docs.anthropic.com",
    #         "platform.claude.com",
    #         "github.com/anthropics",
    #     ]
    # )

    # Example 3: Location-based search
    # Uncomment to run:
    # search_localized(
    #     "Best AI engineering meetups this month",
    #     city="San Francisco",
    #     region="California",
    #     country="US",
    #     timezone="America/Los_Angeles",
    # )

    # Example 4: Cost-optimized batch research
    # Uncomment to run:
    # cost_optimized_research([
    #     "Latest developments in LLM inference optimization techniques",
    #     "Current state of multimodal AI models and benchmarks",
    #     "Recent advances in AI safety and alignment research",
    # ])

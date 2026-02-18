# Claude Web Search with Dynamic Filtering: A Comprehensive Tutorial for AI Engineers

> **Build production-grade AI agents that search the web intelligently using Claude's dynamic filtering — achieving 11% better accuracy with 24% fewer tokens.**

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Deep Dive](#2-architecture-deep-dive)
3. [Environment Setup](#3-environment-setup)
4. [Basic Web Search with Dynamic Filtering](#4-basic-web-search-with-dynamic-filtering)
5. [Web Fetch with Dynamic Filtering](#5-web-fetch-with-dynamic-filtering)
6. [Combined Search + Fetch Workflows](#6-combined-search--fetch-workflows)
7. [Programmatic Tool Calling](#7-programmatic-tool-calling)
8. [Multi-Turn Research Agent with Streaming](#8-multi-turn-research-agent-with-streaming)
9. [Domain Filtering and Cost Optimization](#9-domain-filtering-and-cost-optimization)
10. [Batch Processing at Scale](#10-batch-processing-at-scale)
11. [Handling `pause_turn` and Long-Running Searches](#11-handling-pause_turn-and-long-running-searches)
12. [Prompt Caching for Multi-Turn Conversations](#12-prompt-caching-for-multi-turn-conversations)
13. [Error Handling and Resilience Patterns](#13-error-handling-and-resilience-patterns)
14. [Production Best Practices](#14-production-best-practices)
15. [Benchmarks and Performance Analysis](#15-benchmarks-and-performance-analysis)
16. [References](#16-references)

---

## 1. Introduction

### What Changed

On February 9, 2026, Anthropic released a new version of its web search and web fetch tools (`web_search_20260209` and `web_fetch_20260209`) that support **dynamic filtering**. Instead of dumping raw HTML into Claude's context window, Claude now writes and executes Python code to post-process search results — keeping only what's relevant and discarding the rest.

### Why This Matters for AI Engineers

Web search is one of the most token-intensive operations in agent workflows. A typical search-and-reason cycle involves:

1. Querying a search engine
2. Pulling search result snippets into context
3. Fetching full HTML from multiple URLs
4. Reasoning over all of it to produce an answer

Most of that content is irrelevant. Dynamic filtering solves this by letting Claude act as a researcher — writing Python code to parse, filter, and cross-reference results before they consume context tokens.

### Benchmark Results

| Benchmark | Metric | Sonnet 4.6 (Before) | Sonnet 4.6 (After) | Opus 4.6 (Before) | Opus 4.6 (After) |
|-----------|--------|---------------------|--------------------|--------------------|-------------------|
| BrowseComp | Accuracy | 33.3% | 46.6% | 45.3% | **61.6%** |
| DeepsearchQA | F1 Score | 52.6% | 59.4% | 69.8% | **77.3%** |

Average improvement: **+11% accuracy** with **-24% input tokens**.

### Prerequisites

- Python 3.9+
- An Anthropic API key with web search enabled (enable in [Console Privacy Settings](https://console.anthropic.com/settings/privacy))
- `anthropic` Python SDK >= 0.52.0
- Basic familiarity with the Claude Messages API

---

## 2. Architecture Deep Dive

### How Dynamic Filtering Works Under the Hood

```
┌──────────────────────────────────────────────────────────────────────┐
│                        YOUR APPLICATION                              │
│                                                                      │
│  1. Send message with web_search_20260209 tool                       │
│     + code-execution-web-tools-2026-02-09 beta header                │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      CLAUDE API SERVER                                │
│                                                                      │
│  2. Claude evaluates the prompt                                      │
│  3. Claude decides to search → issues web_search server tool call    │
│  4. API executes the search, returns results                         │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │              CODE EXECUTION SANDBOX                             │  │
│  │                                                                │  │
│  │  5. Claude writes Python to filter/process results             │  │
│  │  6. Script runs in sandboxed container                         │  │
│  │  7. Script pauses when it needs more tool results              │  │
│  │  8. Tool results feed back into the script (NOT the model)     │  │
│  │  9. Only the final filtered output reaches Claude's context    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  10. Claude reasons over filtered results                            │
│  11. Claude generates response with citations                        │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     YOUR APPLICATION                                  │
│                                                                      │
│  12. Receive response with citations + usage metadata                │
└──────────────────────────────────────────────────────────────────────┘
```

### Key Insight: Code Execution as a Filter Layer

The critical architectural innovation is that **tool results from programmatic calls don't enter Claude's context window**. Instead:

- Claude writes a Python script that orchestrates the search workflow
- The script runs in a sandboxed container
- When the script calls `web_search()` or `web_fetch()`, execution pauses
- The API returns results to the script, NOT to Claude
- The script filters, transforms, and aggregates results
- Only the final `print()` output reaches Claude's context

This is why token consumption drops by 24% — Claude never sees the raw HTML or irrelevant search results.

### Tool Version Matrix

| Tool | Version (Dynamic Filtering) | Version (Basic) | Beta Header Required |
|------|----------------------------|-----------------|---------------------|
| Web Search | `web_search_20260209` | `web_search_20250305` | `code-execution-web-tools-2026-02-09` |
| Web Fetch | `web_fetch_20260209` | `web_fetch_20250910` | `code-execution-web-tools-2026-02-09` |
| Code Execution | `code_execution_20250825` | `code_execution_20250522` | None (GA) |

### Model Compatibility

Dynamic filtering works with:
- **Claude Opus 4.6** (`claude-opus-4-6`) — Best accuracy
- **Claude Sonnet 4.6** (`claude-sonnet-4-6`) — Best cost/performance ratio

Code execution is free when used with `web_search_20260209` or `web_fetch_20260209`.

---

## 3. Environment Setup

### Install Dependencies

```bash
pip install anthropic>=0.52.0 python-dotenv
```

### Set Up API Key

```bash
# Option 1: Environment variable
export ANTHROPIC_API_KEY="sk-ant-..."

# Option 2: .env file
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env
```

### Enable Web Search in Console

1. Go to [console.anthropic.com/settings/privacy](https://console.anthropic.com/settings/privacy)
2. Your organization admin must enable web search
3. Optionally configure organization-level domain restrictions

### Verify Setup

```python
import anthropic

client = anthropic.Anthropic()

# Quick verification — basic search (no dynamic filtering)
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "What day is it today?"}],
    tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 1}],
)
print(f"Stop reason: {response.stop_reason}")
print(f"Web searches used: {response.usage.server_tool_use.get('web_search_requests', 0)}")
```

---

## 4. Basic Web Search with Dynamic Filtering

This is the simplest way to use dynamic filtering. You provide the `web_search_20260209` tool with the beta header, and Claude handles everything — including writing the filtering code.

### Minimal Example

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-web-tools-2026-02-09"],
    messages=[
        {
            "role": "user",
            "content": "What are the latest developments in quantum error correction? "
                       "Focus on results from the last 3 months.",
        }
    ],
    tools=[{"type": "web_search_20260209", "name": "web_search"}],
)

# Extract the text response
for block in response.content:
    if block.type == "text":
        print(block.text)
```

### What Happens Behind the Scenes

1. Claude receives the prompt and decides to search
2. Claude writes Python code like:
   ```python
   results = await web_search("quantum error correction 2026")
   # Filter for recency and relevance
   recent = [r for r in results if "2026" in r.get("page_age", "")]
   for r in recent:
       content = await web_fetch(r["url"])
       # Extract key findings
       ...
   print(filtered_summary)
   ```
3. The code runs in a sandbox — search results flow through the script
4. Only the final filtered output reaches Claude's context
5. Claude generates a cited response

### Full Example with Response Parsing

See [`examples/01_basic_dynamic_search.py`](examples/01_basic_dynamic_search.py) for a complete, runnable example that:
- Sends a search query with dynamic filtering
- Parses the response to extract text, citations, and search metadata
- Prints token usage statistics

---

## 5. Web Fetch with Dynamic Filtering

Web fetch retrieves full page content from specific URLs. With dynamic filtering, Claude can extract just the relevant portions.

### When to Use Web Fetch vs Web Search

| Use Case | Tool |
|----------|------|
| Find information across the web | `web_search` |
| Analyze a specific URL's content | `web_fetch` |
| Deep-dive into a search result | `web_search` → `web_fetch` |
| Extract data from a known page | `web_fetch` |
| Process a PDF document | `web_fetch` |

### Example: Fetch and Filter a Technical Document

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-web-tools-2026-02-09"],
    messages=[
        {
            "role": "user",
            "content": "Fetch https://docs.python.org/3/whatsnew/3.13.html and extract "
                       "only the performance improvements and deprecations.",
        }
    ],
    tools=[{"type": "web_fetch_20260209", "name": "web_fetch"}],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
```

With dynamic filtering, Claude writes code to parse the fetched HTML, extract only the "Performance" and "Deprecations" sections, and return a concise summary — instead of loading the entire page (potentially 100K+ tokens) into context.

---

## 6. Combined Search + Fetch Workflows

The most powerful pattern combines search and fetch. Claude searches for relevant pages, then fetches and deeply analyzes the most promising results.

### Example: Technical Research Agent

See [`examples/02_search_fetch_combined.py`](examples/02_search_fetch_combined.py) for a complete example that:
- Combines `web_search_20260209` and `web_fetch_20260209` in a single request
- Uses dynamic filtering to search, fetch top results, and synthesize findings
- Demonstrates citation extraction from the combined workflow

### Key Configuration

```python
tools = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": 5,  # Limit search queries
    },
    {
        "type": "web_fetch_20260209",
        "name": "web_fetch",
        "max_uses": 10,  # Allow fetching multiple pages
        "max_content_tokens": 50000,  # Cap per-page token usage
    },
]
```

---

## 7. Programmatic Tool Calling

This is the most advanced pattern. Claude writes code that calls your **custom tools** programmatically within the code execution sandbox. Tool results flow through the script — not into Claude's context — enabling massive token savings.

### Architecture

```
Claude writes code:
    results = []
    for city in ["NYC", "London", "Tokyo"]:
        weather = await get_weather(city)    # ← Your custom tool
        results.append(weather)
    # Filter and summarize
    print(summary)

Execution flow:
    Script calls get_weather("NYC") → API pauses → You return result → Script continues
    Script calls get_weather("London") → API pauses → You return result → Script continues
    Script calls get_weather("Tokyo") → API pauses → You return result → Script continues
    Script prints summary → Claude sees ONLY the summary (not 3x raw weather data)
```

### Configuring Tools for Programmatic Calling

```python
tools = [
    {"type": "code_execution_20250825", "name": "code_execution"},
    {
        "name": "search_internal_docs",
        "description": "Search internal documentation. Returns JSON array of {title, url, snippet}.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results (default 10)"},
            },
            "required": ["query"],
        },
        "allowed_callers": ["code_execution_20250825"],  # KEY: enables programmatic calling
    },
]
```

### Token Savings

For N tool calls:
- **Direct calling**: ~N × (tool_result_tokens + model_reasoning_tokens)
- **Programmatic calling**: 1 × summary_tokens (tool results never enter context)

For 10 tool calls returning 5K tokens each:
- Direct: ~50K input tokens
- Programmatic: ~2K input tokens (just the summary)

### Full Example

See [`examples/03_programmatic_tool_calling.py`](examples/03_programmatic_tool_calling.py) for a complete implementation with:
- Custom tool definitions with `allowed_callers`
- The tool call → result → continue loop
- Container reuse across requests
- Error handling for container expiration

---

## 8. Multi-Turn Research Agent with Streaming

For complex research tasks, you need multi-turn conversations with streaming to provide real-time feedback.

### Handling `pause_turn`

Long-running searches may trigger a `pause_turn` stop reason. This means the API paused mid-turn, and you should send the response back as-is to let Claude continue:

```python
while True:
    response = client.beta.messages.create(...)

    if response.stop_reason == "pause_turn":
        # Claude hasn't finished — send response back to continue
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": "Please continue."})
    elif response.stop_reason == "end_turn":
        break
    elif response.stop_reason == "tool_use":
        # Handle custom tool calls (for programmatic calling)
        ...
```

### Streaming Example

```python
with client.beta.messages.stream(
    model="claude-opus-4-6",
    max_tokens=8192,
    betas=["code-execution-web-tools-2026-02-09"],
    messages=messages,
    tools=tools,
) as stream:
    for event in stream:
        if event.type == "content_block_start":
            if event.content_block.type == "text":
                print(event.content_block.text, end="", flush=True)
            elif event.content_block.type == "server_tool_use":
                print(f"\n[Searching: {event.content_block.name}]")
        elif event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
```

### Full Example

See [`examples/04_research_agent_streaming.py`](examples/04_research_agent_streaming.py) for a complete multi-turn research agent that:
- Streams results in real-time
- Handles `pause_turn` gracefully
- Maintains conversation context across turns
- Extracts and displays citations

---

## 9. Domain Filtering and Cost Optimization

### Domain Filtering

Restrict searches to trusted sources:

```python
tools = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "allowed_domains": [
            "arxiv.org",
            "scholar.google.com",
            "nature.com",
            "science.org",
        ],
    }
]
```

Or block untrusted sources:

```python
tools = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "blocked_domains": [
            "pinterest.com",
            "reddit.com",
            "quora.com",
        ],
    }
]
```

### Domain Rules

- Omit the scheme (`example.com`, not `https://example.com`)
- Subdomains auto-included (`example.com` covers `docs.example.com`)
- Specific subdomains restrict to only that subdomain
- Subpaths supported (`example.com/blog` matches `example.com/blog/*`)
- One wildcard allowed per entry in the path (`example.com/*/articles`)
- Cannot use both `allowed_domains` and `blocked_domains` in the same request

### Location-Based Search

Localize results for geo-specific queries:

```python
tools = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "user_location": {
            "type": "approximate",
            "city": "San Francisco",
            "region": "California",
            "country": "US",
            "timezone": "America/Los_Angeles",
        },
    }
]
```

### Cost Optimization Strategies

| Strategy | How | Token Savings |
|----------|-----|---------------|
| Dynamic filtering | Use `web_search_20260209` | ~24% fewer input tokens |
| `max_uses` | Limit searches per request | Prevents runaway searches |
| `max_content_tokens` | Cap per-fetch content | Controls fetch costs |
| Domain filtering | Target specific sites | Reduces irrelevant results |
| Prompt caching | Reuse results across turns | Up to 90% on cached turns |
| Batch API | Non-real-time workloads | Same price, better throughput |

### Pricing Summary

| Component | Cost |
|-----------|------|
| Web Search | $10 per 1,000 searches |
| Web Fetch | Free (tokens only) |
| Code Execution (with web tools) | Free |
| Code Execution (standalone) | $0.05/hr after 1,550 free hours/month |
| Input Tokens (Opus 4.6) | Standard model pricing |
| Output Tokens (Opus 4.6) | Standard model pricing |

### Full Example

See [`examples/05_domain_filtered_search.py`](examples/05_domain_filtered_search.py) for a cost-optimized search implementation.

---

## 10. Batch Processing at Scale

For non-real-time workloads (research pipelines, content indexing, monitoring), use the Messages Batches API with web search.

### Example: Batch Research Pipeline

See [`examples/06_batch_search.py`](examples/06_batch_search.py) for a complete batch processing example that:
- Submits multiple research queries as a batch
- Polls for completion
- Processes results and extracts citations
- Handles errors gracefully

---

## 11. Handling `pause_turn` and Long-Running Searches

Complex research queries can trigger long-running turns where Claude performs multiple searches, fetches, and filtering operations. The API may pause these with a `pause_turn` stop reason.

### The `pause_turn` Contract

```python
def handle_conversation(client, messages, tools):
    """Robust conversation loop that handles pause_turn."""
    while True:
        response = client.beta.messages.create(
            model="claude-opus-4-6",
            max_tokens=16384,
            betas=["code-execution-web-tools-2026-02-09"],
            messages=messages,
            tools=tools,
        )

        if response.stop_reason == "pause_turn":
            # API paused a long turn — send response back as-is to continue
            messages.append({"role": "assistant", "content": response.content})
            # You can optionally add user guidance here
            messages.append({
                "role": "user",
                "content": "Continue your research."
            })
            continue

        elif response.stop_reason == "tool_use":
            # Custom tool call (programmatic calling) — provide result
            messages.append({"role": "assistant", "content": response.content})
            tool_results = execute_tool_calls(response)
            messages.append({"role": "user", "content": tool_results})
            continue

        elif response.stop_reason == "end_turn":
            return response

        else:
            raise ValueError(f"Unexpected stop_reason: {response.stop_reason}")
```

---

## 12. Prompt Caching for Multi-Turn Conversations

Prompt caching dramatically reduces costs in multi-turn search conversations by reusing previous search results.

### How It Works

1. First turn: Claude searches and generates results (full token cost)
2. You add a `cache_control` breakpoint after the search results
3. Subsequent turns: Cached search results are reused at reduced cost

### Example

```python
# First turn
messages = [
    {"role": "user", "content": "Research the latest in CRISPR gene therapy."}
]

response1 = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-web-tools-2026-02-09"],
    messages=messages,
    tools=tools,
)

# Add response to conversation
messages.append({"role": "assistant", "content": response1.content})

# Second turn with cache breakpoint
messages.append({
    "role": "user",
    "content": "Based on what you found, which approach is closest to clinical trials?",
    "cache_control": {"type": "ephemeral"},
})

response2 = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-web-tools-2026-02-09"],
    messages=messages,
    tools=tools,
)

print(f"Cache read tokens: {response2.usage.cache_read_input_tokens}")
```

---

## 13. Error Handling and Resilience Patterns

### Web Search Errors

Web search errors are returned **inside** a 200 response, not as HTTP errors:

```python
for block in response.content:
    if block.type == "web_search_tool_result":
        if hasattr(block.content, "type") and block.content.type == "web_search_tool_result_error":
            error_code = block.content.error_code
            # Handle: too_many_requests, invalid_input, max_uses_exceeded,
            #         query_too_long, unavailable
```

### Error Code Reference

| Error Code | Cause | Mitigation |
|-----------|-------|------------|
| `too_many_requests` | Rate limit hit | Exponential backoff |
| `invalid_input` | Bad search query | Validate prompts |
| `max_uses_exceeded` | Exceeded `max_uses` | Increase limit or split queries |
| `query_too_long` | Query too long | Shorten query |
| `unavailable` | Internal error | Retry with backoff |

### Retry Pattern

```python
import time
import anthropic

def search_with_retry(client, messages, tools, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.beta.messages.create(
                model="claude-opus-4-6",
                max_tokens=4096,
                betas=["code-execution-web-tools-2026-02-09"],
                messages=messages,
                tools=tools,
            )
            return response
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                raise
```

### Container Expiration (Programmatic Calling)

Containers expire after ~4.5 minutes of inactivity. Monitor the `expires_at` field:

```python
container_info = response.container
print(f"Container expires at: {container_info.expires_at}")
# Ensure you return tool results before this time
```

---

## 14. Production Best Practices

### 1. Choose the Right Model

- **Opus 4.6**: Best accuracy (61.6% BrowseComp). Use for high-stakes research, fact-checking, complex multi-step queries.
- **Sonnet 4.6**: Best cost/performance (46.6% BrowseComp). Use for most production workloads, customer-facing search, content pipelines.

### 2. Optimize Token Budget

```python
# Set appropriate limits
tools = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "max_uses": 3,  # Don't let Claude search indefinitely
    },
    {
        "type": "web_fetch_20260209",
        "name": "web_fetch",
        "max_uses": 5,
        "max_content_tokens": 50000,  # Cap large pages
    },
]
```

### 3. Use Domain Filtering for Reliability

```python
# For medical information — only use trusted sources
tools = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
        "allowed_domains": [
            "pubmed.ncbi.nlm.nih.gov",
            "who.int",
            "cdc.gov",
            "nature.com/nm",
        ],
    }
]
```

### 4. Monitor Usage

```python
usage = response.usage
print(f"Input tokens: {usage.input_tokens}")
print(f"Output tokens: {usage.output_tokens}")
print(f"Cache read: {getattr(usage, 'cache_read_input_tokens', 0)}")
print(f"Web searches: {usage.server_tool_use.get('web_search_requests', 0)}")
print(f"Web fetches: {usage.server_tool_use.get('web_fetch_requests', 0)}")
```

### 5. Handle Citations Properly

When displaying results to end users, you **must** include citations to original sources:

```python
for block in response.content:
    if block.type == "text" and hasattr(block, "citations") and block.citations:
        for citation in block.citations:
            print(f"  Source: {citation.title} — {citation.url}")
```

### 6. Security Considerations

- **Web Fetch + Untrusted Input**: Enabling web fetch with untrusted user input poses data exfiltration risks. Claude cannot dynamically construct URLs (only fetch URLs from user messages or previous search results), but residual risk exists.
- **Domain Restrictions**: Use `allowed_domains` or `blocked_domains` to restrict access.
- **ZDR**: Web search and web fetch are ZDR eligible. Code execution is NOT covered by ZDR arrangements.

---

## 15. Benchmarks and Performance Analysis

### BrowseComp (Hard-to-Find Information Retrieval)

BrowseComp tests an agent's ability to find deliberately obscure information across multiple websites.

| Model | Without Dynamic Filtering | With Dynamic Filtering | Delta |
|-------|--------------------------|----------------------|-------|
| Sonnet 4.6 | 33.3% | 46.6% | **+13.3%** |
| Opus 4.6 | 45.3% | 61.6% | **+16.3%** |

### DeepsearchQA (Multi-Step Research)

DeepsearchQA tests complex research queries requiring synthesis across multiple sources.

| Model | Without Dynamic Filtering | With Dynamic Filtering | Delta |
|-------|--------------------------|----------------------|-------|
| Sonnet 4.6 | 52.6% (F1) | 59.4% (F1) | **+6.8** |
| Opus 4.6 | 69.8% (F1) | 77.3% (F1) | **+7.5** |

### Token Efficiency

| Model | Token Change (Price-Weighted) |
|-------|------------------------------|
| Sonnet 4.6 | **Decreased** (lower cost) |
| Opus 4.6 | Slightly increased (more complex filtering code) |

The Opus 4.6 token increase reflects the model writing more sophisticated filtering code — the accuracy gains more than justify the marginal token increase.

---

## 16. References

- [Improved Web Search with Dynamic Filtering — Claude Blog](https://claude.com/blog/improved-web-search-with-dynamic-filtering)
- [Web Search Tool — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
- [Web Fetch Tool — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)
- [Code Execution Tool — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)
- [Programmatic Tool Calling — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)
- [Advanced Tool Use — Anthropic Engineering](https://www.anthropic.com/engineering/advanced-tool-use)

---

## Example Files

| File | Description |
|------|-------------|
| [`examples/01_basic_dynamic_search.py`](examples/01_basic_dynamic_search.py) | Basic web search with dynamic filtering |
| [`examples/02_search_fetch_combined.py`](examples/02_search_fetch_combined.py) | Combined search + fetch workflow |
| [`examples/03_programmatic_tool_calling.py`](examples/03_programmatic_tool_calling.py) | Programmatic tool calling with custom tools |
| [`examples/04_research_agent_streaming.py`](examples/04_research_agent_streaming.py) | Multi-turn streaming research agent |
| [`examples/05_domain_filtered_search.py`](examples/05_domain_filtered_search.py) | Domain filtering and cost optimization |
| [`examples/06_batch_search.py`](examples/06_batch_search.py) | Batch processing pipeline |
| [`requirements.txt`](requirements.txt) | Python dependencies |

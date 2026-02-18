"""
Example 3: Programmatic Tool Calling with Web Search
=====================================================

This example demonstrates the most advanced pattern: programmatic tool
calling. Claude writes Python code that calls your custom tools within
a sandboxed code execution container. Tool results flow through the
script — NOT into Claude's context — enabling massive token savings.

Key concepts:
- allowed_callers: ["code_execution_20250825"] on custom tools
- The tool_use → tool_result → continue loop
- Container reuse
- caller field in responses (direct vs programmatic)
- Token efficiency: N tool calls, only summary enters context

Architecture:
    Claude writes code → Script calls your tool → API pauses →
    You return result → Script continues → Script prints summary →
    Only summary enters Claude's context
"""

import os
import json
import time
import anthropic
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Simulated custom tools
# In production, these would call your actual backend services.
# ---------------------------------------------------------------------------

MOCK_DATABASE = {
    "West": {"revenue": 1_250_000, "deals": 45, "avg_deal": 27_778},
    "East": {"revenue": 980_000, "deals": 38, "avg_deal": 25_789},
    "Central": {"revenue": 1_100_000, "deals": 42, "avg_deal": 26_190},
    "North": {"revenue": 750_000, "deals": 28, "avg_deal": 26_786},
    "South": {"revenue": 890_000, "deals": 35, "avg_deal": 25_429},
}


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """
    Execute a tool call and return the result as a string.
    In production, this would dispatch to your actual services.
    """
    if tool_name == "query_sales_data":
        region = tool_input.get("region", "")
        if region in MOCK_DATABASE:
            return json.dumps(MOCK_DATABASE[region])
        return json.dumps({"error": f"Unknown region: {region}"})

    elif tool_name == "get_market_data":
        ticker = tool_input.get("ticker", "")
        # Simulated market data
        market_data = {
            "AAPL": {"price": 242.50, "pe_ratio": 31.2, "market_cap": "3.7T"},
            "GOOGL": {"price": 195.80, "pe_ratio": 24.1, "market_cap": "2.4T"},
            "MSFT": {"price": 445.20, "pe_ratio": 35.8, "market_cap": "3.3T"},
            "NVDA": {"price": 138.90, "pe_ratio": 55.3, "market_cap": "3.4T"},
        }
        if ticker in market_data:
            return json.dumps(market_data[ticker])
        return json.dumps({"error": f"Unknown ticker: {ticker}"})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def programmatic_tool_calling_example():
    """
    Demonstrate programmatic tool calling where Claude writes code that
    calls your custom tools, processes results in-script, and returns
    only a summary to the model context.
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print("PROGRAMMATIC TOOL CALLING")
    print("=" * 70)

    # Define tools — note allowed_callers on custom tools
    tools = [
        # Code execution must be included for programmatic calling
        {"type": "code_execution_20250825", "name": "code_execution"},
        # Custom tool: query sales data by region
        {
            "name": "query_sales_data",
            "description": (
                "Query sales data for a specific region. "
                "Returns JSON with fields: revenue (int), deals (int), avg_deal (int). "
                "Available regions: West, East, Central, North, South."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Sales region name",
                    }
                },
                "required": ["region"],
            },
            # This is the key — enables calling from code execution
            "allowed_callers": ["code_execution_20250825"],
        },
    ]

    messages = [
        {
            "role": "user",
            "content": (
                "Query sales data for all 5 regions (West, East, Central, "
                "North, South), then analyze: which region has the highest "
                "revenue, the best average deal size, and calculate the "
                "total company revenue across all regions."
            ),
        }
    ]

    container_id = None
    iteration = 0
    max_iterations = 20  # Safety limit

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- API Call #{iteration} ---")

        # Build request kwargs
        kwargs = {
            "model": "claude-opus-4-6",
            "max_tokens": 4096,
            "messages": messages,
            "tools": tools,
        }
        if container_id:
            kwargs["container"] = container_id

        response = client.messages.create(**kwargs)

        # Track container for reuse
        if hasattr(response, "container") and response.container:
            container_id = response.container.id
            expires_at = getattr(response.container, "expires_at", "unknown")
            print(f"  Container: {container_id[:20]}... (expires: {expires_at})")

        print(f"  Stop reason: {response.stop_reason}")

        if response.stop_reason == "end_turn":
            # Claude is done — print final response
            print("\n--- FINAL RESPONSE ---\n")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        elif response.stop_reason == "tool_use":
            # Claude's code is calling one of our custom tools
            # Find all tool_use blocks that need results
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    # Check if this is a programmatic call
                    caller = getattr(block, "caller", None)
                    caller_type = getattr(caller, "type", "direct") if caller else "direct"

                    print(f"  Tool call: {block.name}({json.dumps(block.input)})")
                    print(f"  Caller: {caller_type}")

                    # Execute the tool
                    result = handle_tool_call(block.name, block.input)
                    print(f"  Result: {result[:100]}")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            # Send tool results back
            # IMPORTANT: For programmatic calls, only send tool_result blocks
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "pause_turn":
            # Long-running turn — send back to continue
            print("  [pause_turn — continuing...]")
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": "Continue."})

        else:
            print(f"  Unexpected stop_reason: {response.stop_reason}")
            break

    # Print usage
    print(f"\n--- USAGE (final call) ---")
    usage = response.usage
    print(f"  Input tokens:  {usage.input_tokens:,}")
    print(f"  Output tokens: {usage.output_tokens:,}")
    print(f"  API calls:     {iteration}")
    print()
    print("NOTE: With programmatic calling, the 5 tool results never entered")
    print("Claude's context. Only the script's print() output did. This is")
    print("why programmatic calling saves tokens compared to direct calling.")


def programmatic_with_web_search_example():
    """
    Combine programmatic tool calling with web search.

    Claude writes code that:
    1. Calls your custom tools to get internal data
    2. Uses web search to get external context
    3. Cross-references and filters everything in code
    4. Returns only the synthesized summary
    """
    client = anthropic.Anthropic()

    print("=" * 70)
    print("PROGRAMMATIC CALLING + WEB SEARCH")
    print("=" * 70)

    tools = [
        {"type": "code_execution_20250825", "name": "code_execution"},
        # Web search with dynamic filtering
        {"type": "web_search_20260209", "name": "web_search"},
        # Custom tool for internal data
        {
            "name": "get_market_data",
            "description": (
                "Get current market data for a stock ticker. "
                "Returns JSON with: price (float), pe_ratio (float), market_cap (string). "
                "Available tickers: AAPL, GOOGL, MSFT, NVDA."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol",
                    }
                },
                "required": ["ticker"],
            },
            "allowed_callers": ["code_execution_20250825"],
        },
    ]

    messages = [
        {
            "role": "user",
            "content": (
                "Compare the current valuations of AAPL, GOOGL, MSFT, and NVDA. "
                "Get their market data from our internal system, then search the "
                "web for recent analyst consensus ratings. Which stock appears "
                "most undervalued relative to analyst expectations?"
            ),
        }
    ]

    container_id = None
    iteration = 0

    while iteration < 25:
        iteration += 1

        kwargs = {
            "model": "claude-opus-4-6",
            "max_tokens": 8192,
            "betas": ["code-execution-web-tools-2026-02-09"],
            "messages": messages,
            "tools": tools,
        }
        if container_id:
            kwargs["container"] = container_id

        response = client.beta.messages.create(**kwargs)

        if hasattr(response, "container") and response.container:
            container_id = response.container.id

        if response.stop_reason == "end_turn":
            print("\n--- FINAL RESPONSE ---\n")
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        elif response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  Tool: {block.name}({json.dumps(block.input)[:80]})")
                    result = handle_tool_call(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": "Continue."})

        else:
            break

    print(f"\n  Total API calls: {iteration}")


if __name__ == "__main__":
    programmatic_tool_calling_example()

    # Uncomment to also run the combined example:
    # programmatic_with_web_search_example()

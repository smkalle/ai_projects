"""
Module 04 — Tool Use / Function Calling
─────────────────────────────────────────
Covers:
  • Defining tools in Anthropic schema format
  • Sending a request with tools attached
  • Detecting tool_use blocks in the response
  • Executing the tool locally and returning results
  • Completing the tool loop back to the model
  • Multi-tool definitions (calculator + weather mock)

M2.7 is a tier-1 agentic model — tool use is a first-class feature.
"""
import sys, json, math
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log, report_usage


# ── Tool implementations (local functions) ────────────────────────────────────

def calculator(operation: str, a: float, b: float) -> dict:
    ops = {
        "add":      a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide":   a / b if b != 0 else None,
        "power":    a ** b,
        "sqrt":     math.sqrt(a),
        "modulo":   a % b,
    }
    result = ops.get(operation)
    if result is None and operation == "divide":
        return {"error": "Division by zero"}
    if result is None:
        return {"error": f"Unknown operation: {operation}"}
    return {"result": result, "operation": operation, "a": a, "b": b}


def get_weather(city: str, unit: str = "celsius") -> dict:
    """Mock weather tool — returns synthetic data."""
    mock_data = {
        "bangalore": {"temp": 28, "condition": "partly cloudy", "humidity": 65},
        "tokyo":     {"temp": 22, "condition": "clear", "humidity": 55},
        "london":    {"temp": 14, "condition": "overcast", "humidity": 80},
    }
    data = mock_data.get(city.lower(), {"temp": 20, "condition": "unknown", "humidity": 60})
    temp = data["temp"]
    if unit == "fahrenheit":
        temp = round(temp * 9/5 + 32, 1)
    return {
        "city": city,
        "temperature": temp,
        "unit": unit,
        "condition": data["condition"],
        "humidity": data["humidity"],
        "timestamp": datetime.utcnow().isoformat(),
    }


# ── Tool schema definitions (Anthropic format) ─────────────────────────────────

TOOLS = [
    {
        "name": "calculator",
        "description": (
            "Performs arithmetic calculations. "
            "Supports: add, subtract, multiply, divide, power, sqrt, modulo."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt", "modulo"],
                    "description": "The arithmetic operation to perform.",
                },
                "a": {"type": "number", "description": "First operand."},
                "b": {"type": "number", "description": "Second operand (not required for sqrt)."},
            },
            "required": ["operation", "a"],
        },
    },
    {
        "name": "get_weather",
        "description": "Returns current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city":  {"type": "string", "description": "City name, e.g. 'Bangalore'"},
                "unit":  {"type": "string", "enum": ["celsius", "fahrenheit"],
                          "description": "Temperature unit. Defaults to celsius."},
            },
            "required": ["city"],
        },
    },
]


# ── Tool dispatcher ────────────────────────────────────────────────────────────

def dispatch_tool(name: str, inputs: dict) -> str:
    """Run a tool by name and return JSON result string."""
    if name == "calculator":
        result = calculator(**inputs)
    elif name == "get_weather":
        result = get_weather(**inputs)
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result)


# ── Agentic tool loop ──────────────────────────────────────────────────────────

def tool_loop(client, model: str, user_prompt: str) -> None:
    """
    Run a full tool use loop:
    1. Send user message + tools
    2. If model wants a tool: execute it, append result, repeat
    3. When stop_reason == "end_turn": print final answer
    """
    messages = [{"role": "user", "content": user_prompt}]
    iteration = 0
    total_usage = {"input": 0, "output": 0, "cost_usd": 0.0}

    while True:
        iteration += 1
        log("AGENT", f"Iteration {iteration} — calling model")

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        usage = report_usage(getattr(response, "usage", None), label=f"iter{iteration}")
        for k in ("input", "output", "cost_usd"):
            total_usage[k] += usage.get(k, 0)

        log("AGENT", f"stop_reason = {response.stop_reason}")

        # Collect tool calls from this response
        tool_calls = [b for b in response.content if getattr(b, "type", "") == "tool_use"]
        text_blocks = [b for b in response.content if getattr(b, "type", "") == "text"]

        # Print any text the model produced alongside tool calls
        for tb in text_blocks:
            print(f"\n  Model says: {getattr(tb, 'text', '')}\n")

        if response.stop_reason == "end_turn" or not tool_calls:
            # Final answer — print remaining text blocks
            for tb in text_blocks:
                pass  # already printed above
            break

        # Append assistant response (with tool_use blocks) to history
        messages.append({"role": "assistant", "content": response.content})

        # Execute each tool and build tool_result blocks
        tool_results = []
        for tc in tool_calls:
            tool_name   = getattr(tc, "name", "")
            tool_input  = getattr(tc, "input", {})
            tool_id     = getattr(tc, "id", "")

            log("TOOL", f"Calling: {tool_name}({json.dumps(tool_input)})")
            result_str = dispatch_tool(tool_name, tool_input)
            log("TOOL", f"Result : {result_str}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": result_str,
            })

        # Append all tool results as one user message
        messages.append({"role": "user", "content": tool_results})

    # Final text
    print_divider("Final Answer")
    from utils import extract_text
    # get last text from messages
    for block in reversed(response.content):
        if getattr(block, "type", "") == "text":
            print(getattr(block, "text", ""))
            break

    print_divider("Session Totals")
    log("USAGE", f"Iterations  : {iteration}")
    log("USAGE", f"Input tokens: {total_usage['input']:,}")
    log("USAGE", f"Out tokens  : {total_usage['output']:,}")
    log("USAGE", f"Est. cost   : ${total_usage['cost_usd']:.6f} USD")


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print_header(
        "Module 04 · Tool Use / Function Calling",
        "Calculator + weather tools, full agentic loop, tool_result handling"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    prompts = [
        "What is 2^10, and what is that divided by 8?",
        "What's the weather in Bangalore and Tokyo? Which city is warmer?",
    ]

    for i, prompt in enumerate(prompts, 1):
        print_divider(f"Query {i}: {prompt}")
        tool_loop(client, model, prompt)

    print_divider("Module 04 Complete")


if __name__ == "__main__":
    run()

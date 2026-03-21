"""
Module 08 — Agent ReAct Loop
──────────────────────────────
Covers:
  • ReAct (Reason + Act) agentic pattern
  • Dynamic tool selection across multiple calls
  • Agent memory (scratchpad) between steps
  • Stopping conditions and max-iteration guards
  • Full execution trace with step-by-step logging
  • A practical task: research + calculation agent

Tools available to the agent:
  • search(query)         — mock web search returning snippets
  • calculator(expr)      — safe arithmetic evaluator
  • remember(key, value)  — write to agent scratchpad
  • recall(key)           — read from agent scratchpad
  • finish(answer)        — signal task completion
"""
import sys, json, ast, operator
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log, report_usage


# ── Mock tool implementations ─────────────────────────────────────────────────

_SCRATCHPAD: dict = {}

_MOCK_SEARCH_DB = {
    "minimax m2.7 pricing":
        "MiniMax M2.7 costs $0.30 per million input tokens and $1.20 per million output tokens.",
    "minimax m2.7 context window":
        "MiniMax M2.7 has a 204,800-token context window with max output of 131,072 tokens.",
    "claude sonnet pricing 2025":
        "Claude Sonnet 4 costs approximately $3.00 per million input and $15.00 per million output tokens.",
    "gpt-4o pricing":
        "GPT-4o is priced at $2.50 per million input tokens and $10.00 per million output tokens.",
    "default":
        "No specific results found. Please refine your search query.",
}


def tool_search(query: str) -> str:
    key = query.lower().strip()
    for k, v in _MOCK_SEARCH_DB.items():
        if any(word in key for word in k.split()):
            return v
    return _MOCK_SEARCH_DB["default"]


def tool_calculator(expression: str) -> str:
    """Safe arithmetic evaluator using AST parsing."""
    _ALLOWED_OPS = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg,
    }
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")
    try:
        tree = ast.parse(expression, mode='eval')
        result = _eval(tree.body)
        return str(round(result, 8))
    except Exception as e:
        return f"Error: {e}"


def tool_remember(key: str, value: str) -> str:
    _SCRATCHPAD[key] = value
    return f"Stored: {key} = {value}"


def tool_recall(key: str) -> str:
    val = _SCRATCHPAD.get(key)
    return val if val else f"Nothing stored under key: {key}"


def tool_finish(answer: str) -> str:
    return f"FINAL_ANSWER: {answer}"


# ── Tool registry ──────────────────────────────────────────────────────────────

AGENT_TOOLS = [
    {
        "name": "search",
        "description": "Search the web for factual information. Returns a brief text snippet.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Specific search query."}
            },
            "required": ["query"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluates arithmetic expressions. Use Python syntax: 2**10, 1000000 * 0.30 / 1000000",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Arithmetic expression to evaluate."}
            },
            "required": ["expression"],
        },
    },
    {
        "name": "remember",
        "description": "Store a named value in the scratchpad for later recall.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key":   {"type": "string", "description": "Name for the stored value."},
                "value": {"type": "string", "description": "Value to store."},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "recall",
        "description": "Retrieve a previously stored value from the scratchpad by key.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "The key to look up."}
            },
            "required": ["key"],
        },
    },
    {
        "name": "finish",
        "description": "Signal that the task is complete and provide the final answer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "answer": {"type": "string", "description": "The complete final answer."}
            },
            "required": ["answer"],
        },
    },
]


# ── Tool dispatcher ────────────────────────────────────────────────────────────

def dispatch(name: str, inputs: dict) -> str:
    dispatch_map = {
        "search":     lambda i: tool_search(i["query"]),
        "calculator": lambda i: tool_calculator(i["expression"]),
        "remember":   lambda i: tool_remember(i["key"], i["value"]),
        "recall":     lambda i: tool_recall(i["key"]),
        "finish":     lambda i: tool_finish(i["answer"]),
    }
    fn = dispatch_map.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool: {name}"})
    return fn(inputs)


# ── ReAct loop ─────────────────────────────────────────────────────────────────

AGENT_SYSTEM = """You are a research and analysis agent with access to search, calculation, memory, and finish tools.

Your goal is to answer the user's question accurately by:
1. REASONING about what information you need
2. ACTING by calling the appropriate tools
3. OBSERVING results and updating your plan
4. Continuing until you can give a complete, accurate answer
5. Calling finish() when done — never stop without a final answer

Be methodical. Use remember() to store intermediate results. Show your work.
"""

def react_loop(client, model: str, task: str, max_iter: int = 10) -> str:
    """Run the agent until it calls finish() or hits max_iter."""
    _SCRATCHPAD.clear()
    messages = [{"role": "user", "content": task}]
    total_usage = {"input": 0, "output": 0, "cost_usd": 0.0}
    final_answer = None

    log("AGENT", f"Task: {task}")
    log("AGENT", f"Max iterations: {max_iter}")

    for step in range(1, max_iter + 1):
        print_divider(f"Step {step}")

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=AGENT_SYSTEM,
            tools=AGENT_TOOLS,
            messages=messages,
        )

        usage = report_usage(getattr(response, "usage", None), label=f"step{step}")
        for k in ("input", "output", "cost_usd"):
            total_usage[k] += usage.get(k, 0)

        # Collect text reasoning and tool calls
        text_blocks = [b for b in response.content if getattr(b, "type","") == "text"]
        tool_blocks = [b for b in response.content if getattr(b, "type","") == "tool_use"]

        for tb in text_blocks:
            txt = getattr(tb, "text", "").strip()
            if txt:
                log("AGENT", f"Reasoning: {txt[:200]}{'…' if len(txt)>200 else ''}")

        if response.stop_reason == "end_turn" and not tool_blocks:
            # Model decided to stop without calling finish — extract text as answer
            for tb in text_blocks:
                final_answer = getattr(tb, "text", "")
            break

        # Append assistant turn
        messages.append({"role": "assistant", "content": response.content})

        # Execute tool calls
        tool_results = []
        for tc in tool_blocks:
            name   = getattr(tc, "name", "")
            inputs = getattr(tc, "input", {})
            tid    = getattr(tc, "id", "")

            log("TOOL", f"→ {name}({json.dumps(inputs)})")
            result = dispatch(name, inputs)
            log("TOOL", f"← {result[:200]}{'…' if len(result)>200 else ''}")

            # Detect finish() call
            if name == "finish" and result.startswith("FINAL_ANSWER:"):
                final_answer = result[len("FINAL_ANSWER:"):].strip()
                log("AGENT", f"Task complete at step {step}")
                # Report totals then return
                print_divider("Agent Session Totals")
                log("USAGE", f"Steps       : {step}")
                log("USAGE", f"Input tok   : {total_usage['input']:,}")
                log("USAGE", f"Output tok  : {total_usage['output']:,}")
                log("USAGE", f"Est. cost   : ${total_usage['cost_usd']:.6f} USD")
                return final_answer

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tid,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    log("WARN", f"Reached max iterations ({max_iter}) without finish() call")
    print_divider("Agent Session Totals")
    log("USAGE", f"Input tok : {total_usage['input']:,}")
    log("USAGE", f"Output tok: {total_usage['output']:,}")
    log("USAGE", f"Est. cost : ${total_usage['cost_usd']:.6f} USD")
    return final_answer or "Task incomplete — max iterations reached"


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> None:
    print_header(
        "Module 08 · Agent ReAct Loop",
        "Reason+Act pattern, scratchpad memory, multi-tool orchestration"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    task = (
        "I need to understand the cost difference between MiniMax M2.7 and Claude Sonnet "
        "for a use case where I process 500,000 API calls per month, each with an average "
        "of 800 input tokens and 400 output tokens. "
        "Calculate the monthly cost for both models and tell me the savings with M2.7."
    )

    print_divider("Task")
    print(f"\n  {task}\n")

    answer = react_loop(client, model, task, max_iter=12)

    print_divider("Final Answer")
    print(f"\n  {answer}\n")

    print_divider("Module 08 Complete")


if __name__ == "__main__":
    run()

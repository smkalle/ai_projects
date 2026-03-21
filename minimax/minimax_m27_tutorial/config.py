"""
config.py — Central configuration for MiniMax M2.7 Tutorial Suite
All model constants, endpoint URLs, and pricing live here.
"""

# ── Model identifiers ────────────────────────────────────────────────────────
MODEL_STANDARD   = "MiniMax-M2.7"
MODEL_HIGHSPEED  = "MiniMax-M2.7-highspeed"

# ── API Endpoints (Anthropic-compatible) ─────────────────────────────────────
ENDPOINT_GLOBAL  = "https://api.minimax.io/anthropic"
ENDPOINT_CHINA   = "https://api.minimaxi.com/anthropic"

# ── Model capabilities (for reference in tutorials) ──────────────────────────
CONTEXT_WINDOW   = 204_800   # tokens
MAX_OUTPUT       = 131_072   # tokens

# ── Pricing per 1M tokens (March 2025) ───────────────────────────────────────
PRICE_INPUT_PER_1M  = 0.30   # USD
PRICE_OUTPUT_PER_1M = 1.20   # USD

# ── Default generation parameters ────────────────────────────────────────────
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 1.0    # recommended by MiniMax for M2-series
DEFAULT_TOP_P       = 0.95

# ── Tutorial module registry ─────────────────────────────────────────────────
MODULES = [
    {
        "id": "01", "name": "Hello World", "file": "modules/01_hello.py", "tag": "basic",
        "description": "Your first MiniMax M2.7 API call. Learn to initialise the Anthropic client, send a single-turn message, read text content blocks, and inspect response metadata.",
        "covers": ["anthropic.Anthropic client", "messages.create()", "content blocks", "response metadata", "print_blocks()", "report_usage()"],
        "learning_summary": (
            "Key takeaways:\n"
            "• Always use load_env() + make_client() — never hardcode the API key.\n"
            "• response.content is a list of blocks — iterate it to find text/thinking/tool_use.\n"
            "• response.usage.input_tokens and output_tokens feed into cost tracking.\n"
            "• stop_reason='end_turn' means the model finished naturally.\n"
            "Common pitfall: Extracting only text with extract_text() strips important metadata like stop_reason and usage — use print_blocks() for full inspection."
        ),
    },
    {
        "id": "02", "name": "Streaming", "file": "modules/02_streaming.py", "tag": "streaming",
        "description": "Real-time token streaming with time-to-first-token (TTFT) measurement. Dramatically improves perceived latency for long-form output.",
        "covers": ["client.messages.stream()", "text_stream iterator", "stream.get_final_message()", "TTFT measurement", "streaming vs non-streaming"],
        "learning_summary": (
            "Key takeaways:\n"
            "• Use client.messages.stream() as a context manager — handles start/end automatically.\n"
            "• Iterate stream.text_stream for live token output.\n"
            "• Always call stream.get_final_message() after the stream finishes to get usage stats.\n"
            "• TTFT = time from request start to first token — good proxy for model responsiveness.\n"
            "Common pitfall: Forgetting get_final_message() means you lose access to usage and stop_reason."
        ),
    },
    {
        "id": "03", "name": "Multi-Turn Chat", "file": "modules/03_multi_turn.py", "tag": "conversation",
        "description": "Build persistent conversation history. Append both user messages and full response.content (including thinking blocks) to maintain context across turns.",
        "covers": ["message history", "response.content preservation", "accumulated usage", "context window management", "multi-turn loop"],
        "learning_summary": (
            "Key takeaways:\n"
            "• Always append the FULL response.content to history, not extract_text() — especially with thinking enabled.\n"
            "• Pass the entire history list on every messages.create() call.\n"
            "• M2.7's 204,800 token context window handles long conversations.\n"
            "• Accumulate usage across turns to report session totals.\n"
            "Common pitfall: Stripping thinking blocks from history degrades M2 performance — preserve response.content verbatim."
        ),
    },
    {
        "id": "04", "name": "Tool Use", "file": "modules/04_tool_use.py", "tag": "agentic",
        "description": "Function calling with MiniMax M2.7. Define tools in Anthropic schema, detect tool_use blocks, execute locally, and feed results back for a full agentic loop.",
        "covers": ["tool definitions (Anthropic schema)", "tool_use block detection", "tool_result blocks", "dispatch pattern", "multi-tool routing", "calculator + weather mock"],
        "learning_summary": (
            "Key takeaways:\n"
            "• Tools are defined as a list of dicts with name, description, and input_schema.\n"
            "• Detect tool calls: [b for b in response.content if b.type == 'tool_use'].\n"
            "• Execute locally, then append tool_result blocks as a single user message.\n"
            "• Loop until stop_reason == 'end_turn' with no tool_use blocks.\n"
            "• M2.7 has 97% skill adherence for tool use — ideal for reliable agentic loops.\n"
            "Common pitfall: Forgetting to pass the tool result back to the model — the loop won't continue without it."
        ),
    },
    {
        "id": "05", "name": "Extended Thinking", "file": "modules/05_thinking.py", "tag": "reasoning",
        "description": "Enable M2.7's interleaved thinking model. The thinking parameter exposes the model's reasoning chain, improves accuracy on hard problems, and must be preserved in history.",
        "covers": ["thinking parameter", "thinking vs text blocks", "budget_tokens", "preserving <think> in history", "max_tokens vs budget_tokens"],
        "learning_summary": (
            "Key takeaways:\n"
            "• Enable: thinking={'type':'enabled','budget_tokens':3000} — must have max_tokens > budget_tokens.\n"
            "• response.content may contain BOTH thinking blocks and text blocks — iterate all.\n"
            "• Thinking blocks are NOT extracted by extract_text() — preserve full response.content in history.\n"
            "• Higher budget = deeper reasoning = higher output token cost.\n"
            "Common pitfall: Setting max_tokens equal to budget_tokens leaves no room for the answer — always set max_tokens > budget_tokens."
        ),
    },
    {
        "id": "06", "name": "System Prompting", "file": "modules/06_system_prompt.py", "tag": "prompting",
        "description": "Structured system prompts using XML constraint tags (persona, scope, output_format, constraints). Compare bare vs structured prompting and use few-shot examples in the system prompt.",
        "covers": ["system parameter", "XML constraint tags", "few-shot examples in system", "dynamic prompt construction", "persona + scope + format + constraints"],
        "learning_summary": (
            "Key takeaways:\n"
            "• Structured XML tags dramatically improve output consistency over bare instructions.\n"
            "• <persona> sets the identity, <output_format> controls structure, <constraints> lists rules.\n"
            "• Few-shot examples in the system prompt are more efficient than in every user message.\n"
            "• Dynamic prompt construction via f-strings adapts the system to context.\n"
            "Common pitfall: Bare system prompts produce inconsistent formats — always use structured tags for production prompts."
        ),
    },
    {
        "id": "07", "name": "Cost Tracking", "file": "modules/07_cost_tracker.py", "tag": "production",
        "description": "Production-grade cost visibility with CostLedger. Track every call, detect cache hits, enforce budget limits, and project monthly costs at $0.30/$1.20 per 1M tokens.",
        "covers": ["CostLedger class", "usage.input_tokens / output_tokens", "cache_read_input_tokens", "budget enforcement", "cost projection", "per-1K/1M cost estimates"],
        "learning_summary": (
            "Key takeaways:\n"
            "• Always record usage.input_tokens and usage.output_tokens per call.\n"
            "• Cache hits appear as cache_read_input_tokens — they reduce effective cost.\n"
            "• budget_usd guard: raise RuntimeError when cumulative cost exceeds your limit.\n"
            "• Project costs: avg_tokens_per_call × calls_per_month × price_per_token.\n"
            "• At 500K calls/month (800 in / 400 out tokens): M2.7 costs ~$360 vs Claude Sonnet's ~$3,600.\n"
            "Common pitfall: Not checking cache_read_input_tokens underestimates savings — always include it in cost calculations."
        ),
    },
    {
        "id": "08", "name": "Agent ReAct Loop", "file": "modules/08_agent_loop.py", "tag": "agentic",
        "description": "Full ReAct (Reason + Act) agent pattern. The agent reasons, calls tools (search, calculator, remember, recall, finish), observes results, and iterates until completion with a scratchpad.",
        "covers": ["ReAct pattern", "AGENT_TOOLS registry", "scratchpad memory (_SCRATCHPAD)", "finish() sentinel", "max_iter guard", "dispatch_map", "multi-tool orchestration"],
        "learning_summary": (
            "Key takeaways:\n"
            "• ReAct: Reason → Act → Observe → Repeat until finish() is called.\n"
            "• Use a dispatch_map to route tool names to local Python implementations.\n"
            "• finish() returns 'FINAL_ANSWER: ...' — loop detects this prefix to exit.\n"
            "• max_iter guard prevents infinite loops if the model never calls finish().\n"
            "• The scratchpad (module-level dict) persists remember/recall across loop steps.\n"
            "• M2.7's 97% skill adherence makes it highly reliable for multi-step agentic tasks.\n"
            "Common pitfall: Forgetting to convert tool_result content to a string — dispatch returns JSON strings, not dicts."
        ),
    },
]

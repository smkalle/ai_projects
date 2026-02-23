"""
Nanbeige4.1-3B Interactive Demo — Gradio UI

A full-featured chat interface with:
- Multi-mode inference (Chat, Code, Reasoning, Tool Use)
- Thinking/reasoning block display
- Adjustable generation parameters
- Tool-calling simulation
- Conversation history management

Usage:
    uv run python app.py
    # Opens at http://localhost:7860
"""

import json
import time

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_ID = "Nanbeige/Nanbeige4.1-3B"

SYSTEM_PROMPTS = {
    "General Chat": "You are a helpful, concise assistant.",
    "Code Assistant": (
        "You are an expert Python programmer. Write clean, well-documented code "
        "with type hints. Explain your approach briefly before the code."
    ),
    "Math & Reasoning": (
        "You are a mathematics and logic expert. Show your step-by-step reasoning "
        "process. Verify your answer before presenting it."
    ),
    "Science Expert": (
        "You are a science expert covering physics, chemistry, and biology. "
        "Provide accurate, detailed explanations with relevant examples."
    ),
    "Tool Use Agent": """You are a helpful assistant with access to the following tools:

[
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get current weather for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City name"},
          "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
        },
        "required": ["location"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "calculate",
      "description": "Evaluate a mathematical expression",
      "parameters": {
        "type": "object",
        "properties": {
          "expression": {"type": "string", "description": "Math expression"}
        },
        "required": ["expression"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "search_web",
      "description": "Search the web for information",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "description": "Search query"},
          "num_results": {"type": "integer", "default": 3}
        },
        "required": ["query"]
      }
    }
  }
]

When you need to use a tool, respond with a JSON block:
{"tool_call": {"name": "tool_name", "arguments": {"arg1": "value1"}}}

After receiving tool results, incorporate them into your final response.""",
}

# Example prompts per mode
EXAMPLES = {
    "General Chat": [
        "What are the key differences between REST and GraphQL?",
        "Explain the CAP theorem in simple terms.",
        "What are the pros and cons of microservices architecture?",
    ],
    "Code Assistant": [
        "Write a Python LRU cache implementation from scratch.",
        "Create a FastAPI endpoint with Pydantic validation for a user registration form.",
        "Write a decorator that retries a function up to 3 times with exponential backoff.",
    ],
    "Math & Reasoning": [
        "Find all positive integers n where n^2 + n + 41 is not prime.",
        "A bat and ball cost $1.10. The bat costs $1.00 more than the ball. How much does the ball cost?",
        "Prove that the square root of 2 is irrational.",
    ],
    "Science Expert": [
        "Explain CRISPR-Cas9 gene editing mechanism and its limitations.",
        "How do quantum computers differ from classical computers at the physics level?",
        "What causes antibiotic resistance and how does it spread?",
    ],
    "Tool Use Agent": [
        "What's the weather in Tokyo? Convert 100 USD to EUR using calculation.",
        "Search for the latest news about AI regulation, then summarize.",
        "Calculate the compound interest on $10,000 at 5% for 10 years.",
    ],
}

# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

model = None
tokenizer = None


def load_model():
    """Load the model and tokenizer."""
    global model, tokenizer

    if model is not None:
        return "Model already loaded."

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        device_map="auto" if device == "cuda" else None,
        trust_remote_code=True,
    )
    if device == "cpu":
        model = model.to(device)

    param_count = sum(p.numel() for p in model.parameters()) / 1e9
    return f"Model loaded on {device} ({dtype}) — {param_count:.2f}B parameters"


def get_model_status():
    """Return model loading status."""
    if model is None:
        return "Model not loaded. Click 'Load Model' to start."
    device = next(model.parameters()).device
    return f"Model ready on {device}"


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------


def parse_thinking(text):
    """Separate <think> blocks from the final response."""
    thinking = ""
    answer = text
    if "<think>" in text and "</think>" in text:
        think_start = text.index("<think>") + len("<think>")
        think_end = text.index("</think>")
        thinking = text[think_start:think_end].strip()
        answer = text[think_end + len("</think>") :].strip()
    return thinking, answer


def simulate_tool(name, arguments):
    """Simulate tool execution for demo purposes."""
    mock = {
        "get_weather": lambda a: {
            "location": a.get("location", "Unknown"),
            "temperature": 22,
            "unit": a.get("unit", "celsius"),
            "condition": "Partly cloudy",
            "humidity": 65,
        },
        "calculate": lambda a: {
            "expression": a.get("expression", ""),
            "result": str(eval(a.get("expression", "0"))),
        },
        "search_web": lambda a: {
            "query": a.get("query", ""),
            "results": [
                {"title": "Result 1", "snippet": "Relevant information about the query..."},
                {"title": "Result 2", "snippet": "Additional context and details..."},
            ],
        },
    }
    handler = mock.get(name)
    if handler:
        return handler(arguments)
    return {"error": f"Unknown tool: {name}"}


def generate(
    message,
    chat_history,
    system_prompt,
    temperature,
    top_p,
    max_tokens,
    show_thinking,
):
    """Generate a response and yield it for streaming display."""
    if model is None:
        yield chat_history + [{"role": "assistant", "content": "Please load the model first."}], ""
        return

    # Build messages from history
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    start = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature if temperature > 0 else None,
            top_p=top_p if temperature > 0 else None,
            do_sample=temperature > 0,
        )
    elapsed = time.time() - start

    new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)

    tokens_generated = len(new_tokens)
    tokens_per_sec = tokens_generated / elapsed if elapsed > 0 else 0

    thinking, answer = parse_thinking(response)

    # Handle tool calls for agent mode
    tool_info = ""
    if '"tool_call"' in answer:
        try:
            json_start = answer.index("{")
            json_end = answer.rindex("}") + 1
            tool_data = json.loads(answer[json_start:json_end])
            tool_call = tool_data.get("tool_call", {})
            name = tool_call.get("name", "")
            args = tool_call.get("arguments", {})
            tool_result = simulate_tool(name, args)
            tool_info = (
                f"\n\n---\n**Tool Call**: `{name}({json.dumps(args)})`\n"
                f"**Tool Result**: `{json.dumps(tool_result)}`\n---"
            )
        except (json.JSONDecodeError, ValueError):
            pass

    # Build the display response
    display = answer + tool_info

    stats = (
        f"Tokens: {tokens_generated} | Time: {elapsed:.1f}s | Speed: {tokens_per_sec:.1f} tok/s"
    )

    thinking_display = ""
    if thinking and show_thinking:
        thinking_display = f"**Thinking:**\n\n{thinking}"

    updated_history = chat_history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": display},
    ]

    yield updated_history, f"{stats}\n\n{thinking_display}"


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------


def build_ui():
    """Build the Gradio interface."""

    with gr.Blocks(
        title="Nanbeige4.1-3B Interactive Demo",
        theme=gr.themes.Soft(),
        css="""
        .thinking-box { background: #1a1a2e; color: #e0e0e0; padding: 12px;
                        border-radius: 8px; font-size: 13px; max-height: 300px;
                        overflow-y: auto; }
        """,
    ) as demo:
        gr.Markdown(
            """
        # Nanbeige4.1-3B Interactive Demo

        A **3B-parameter** model rivaling 30B+ models in reasoning, code, and tool use.

        | Benchmark | Score | vs. Qwen3-30B-A3B |
        |---|---|---|
        | LiveCodeBench | **76.9** | 66.0 |
        | GPQA-Diamond | **82.2** | 73.4 |
        | AIME 2024 | **90.4** | 89.2 |
        | BFCL-V4 (Tools) | **53.8** | 48.6 |
        """
        )

        with gr.Row():
            with gr.Column(scale=1):
                model_status = gr.Textbox(
                    label="Model Status",
                    value=get_model_status(),
                    interactive=False,
                )
                load_btn = gr.Button("Load Model", variant="primary")

                mode = gr.Dropdown(
                    choices=list(SYSTEM_PROMPTS.keys()),
                    value="General Chat",
                    label="Mode",
                )
                system_prompt = gr.Textbox(
                    label="System Prompt",
                    value=SYSTEM_PROMPTS["General Chat"],
                    lines=4,
                )
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=1.5,
                    value=0.6,
                    step=0.1,
                    label="Temperature (0.5-0.6 recommended)",
                )
                top_p = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.95, step=0.05, label="Top-p"
                )
                max_tokens = gr.Slider(
                    minimum=64,
                    maximum=8192,
                    value=2048,
                    step=64,
                    label="Max Tokens",
                )
                show_thinking = gr.Checkbox(label="Show Thinking Process", value=True)

                gr.Markdown("### Example Prompts")
                example_btns = []
                examples_container = gr.Column()

            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Chat",
                    height=500,
                    type="messages",
                )
                with gr.Row():
                    msg = gr.Textbox(
                        label="Message",
                        placeholder="Type your message here...",
                        scale=4,
                        lines=2,
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

                thinking_output = gr.Markdown(label="Stats & Thinking", elem_classes=["thinking-box"])

                with gr.Row():
                    clear_btn = gr.Button("Clear Chat")
                    retry_btn = gr.Button("Retry Last")

        # --- Event handlers ---

        def update_system_prompt(mode_name):
            return SYSTEM_PROMPTS.get(mode_name, "")

        def update_examples(mode_name):
            return gr.update(
                value="\n".join(f"- {e}" for e in EXAMPLES.get(mode_name, []))
            )

        mode.change(
            fn=update_system_prompt,
            inputs=[mode],
            outputs=[system_prompt],
        )

        load_btn.click(fn=load_model, outputs=[model_status])

        def user_send(message, history, sys_prompt, temp, tp, mt, st):
            if not message.strip():
                yield history, ""
                return
            yield from generate(message, history, sys_prompt, temp, tp, mt, st)

        send_btn.click(
            fn=user_send,
            inputs=[msg, chatbot, system_prompt, temperature, top_p, max_tokens, show_thinking],
            outputs=[chatbot, thinking_output],
        ).then(fn=lambda: "", outputs=[msg])

        msg.submit(
            fn=user_send,
            inputs=[msg, chatbot, system_prompt, temperature, top_p, max_tokens, show_thinking],
            outputs=[chatbot, thinking_output],
        ).then(fn=lambda: "", outputs=[msg])

        clear_btn.click(fn=lambda: ([], ""), outputs=[chatbot, thinking_output])

        def retry_last(history, sys_prompt, temp, tp, mt, st):
            if not history or len(history) < 2:
                yield history, "No messages to retry."
                return
            last_user_msg = history[-2]["content"]
            trimmed = history[:-2]
            yield from generate(last_user_msg, trimmed, sys_prompt, temp, tp, mt, st)

        retry_btn.click(
            fn=retry_last,
            inputs=[chatbot, system_prompt, temperature, top_p, max_tokens, show_thinking],
            outputs=[chatbot, thinking_output],
        )

        # Example click handlers
        def set_example(example_text):
            return example_text

        for mode_name, mode_examples in EXAMPLES.items():
            for ex in mode_examples[:1]:  # First example per mode shown as quick-start
                pass

    return demo


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Launch the Gradio app."""
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()

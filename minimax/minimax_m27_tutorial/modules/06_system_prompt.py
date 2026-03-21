"""
Module 06 — System Prompt Engineering
───────────────────────────────────────
Covers:
  • System prompt structure best practices
  • Persona, scope, format, and constraint patterns
  • Comparing bare vs structured system prompts
  • XML tag formatting for reliable structured output
  • Few-shot examples in the system prompt
  • Dynamic system prompt construction
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import load_env, make_client, print_header, print_divider, log, report_usage, extract_text


# ── System prompt templates ────────────────────────────────────────────────────

BARE_SYSTEM = "You are a helpful assistant."

STRUCTURED_SYSTEM = """You are CodeReview-GPT, an expert code reviewer.

<persona>
You are a principal engineer with 15 years of Python experience.
You value correctness, readability, and performance — in that order.
You are direct and do not pad your answers with pleasantries.
</persona>

<scope>
Review only the code provided. Do not speculate about missing context.
If code is incomplete, say so and review what you have.
</scope>

<output_format>
Always structure your review as:
1. VERDICT: one line — APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION
2. ISSUES: bullet list of problems (severity: CRITICAL / HIGH / MEDIUM / LOW)
3. SUGGESTIONS: up to 3 improvement ideas
4. SCORE: /10 with one-line justification
</output_format>

<constraints>
- Be concise. No issue should exceed 2 sentences.
- Do not rewrite the entire code unless asked.
- If there are no issues, say so plainly.
</constraints>"""

FEW_SHOT_SYSTEM = """You are a JSON data extractor. Extract structured data from text.

<examples>
Input: "John Smith, 34, works as a data engineer at Acme Corp in Bangalore."
Output: {"name": "John Smith", "age": 34, "role": "data engineer", "company": "Acme Corp", "city": "Bangalore"}

Input: "Sarah Connor, CTO, TechStart (London). Background in ML since 2018."
Output: {"name": "Sarah Connor", "role": "CTO", "company": "TechStart", "city": "London", "ml_since": 2018}
</examples>

<rules>
- Output ONLY valid JSON. No markdown fences, no commentary.
- Use null for missing fields.
- Infer reasonable field names from context.
</rules>"""


def compare_prompts(client, model: str, code_snippet: str) -> None:
    """Show the difference between a bare and a structured system prompt."""
    print_divider("With BARE system prompt")
    try:
        r1 = client.messages.create(
            model=model, max_tokens=400, system=BARE_SYSTEM,
            messages=[{"role": "user", "content": f"Review this code:\n\n{code_snippet}"}]
        )
        print(extract_text(r1))
        report_usage(getattr(r1, "usage", None), label="bare")
    except Exception as e:
        log("ERROR", str(e))

    print_divider("With STRUCTURED system prompt")
    try:
        r2 = client.messages.create(
            model=model, max_tokens=400, system=STRUCTURED_SYSTEM,
            messages=[{"role": "user", "content": f"Review this code:\n\n{code_snippet}"}]
        )
        print(extract_text(r2))
        report_usage(getattr(r2, "usage", None), label="structured")
    except Exception as e:
        log("ERROR", str(e))


def few_shot_extraction(client, model: str) -> None:
    """Demonstrate few-shot learning via system prompt examples."""
    test_inputs = [
        "Dr. Priya Nair, 41, VP of Engineering at Rakuten India, Bangalore. Python & ML expert.",
        "Marcus Lee — Frontend Lead at PixelCo, Singapore. 8 years React experience.",
    ]

    print_divider("Few-Shot JSON Extraction")
    for inp in test_inputs:
        log("REQUEST", f"Input: {inp}")
        try:
            r = client.messages.create(
                model=model, max_tokens=200, system=FEW_SHOT_SYSTEM,
                messages=[{"role": "user", "content": inp}]
            )
            result = extract_text(r).strip()
            log("RESPONSE", f"Output: {result}")
        except Exception as e:
            log("ERROR", str(e))
        print()


def dynamic_system_prompt(role: str, domain: str, output_format: str, tone: str) -> str:
    """Build a system prompt dynamically from parameters."""
    return f"""You are an expert {role} specialising in {domain}.

<tone>{tone}</tone>

<output_format>
{output_format}
</output_format>

Always validate your answer before responding. If unsure, say so."""


def run() -> None:
    print_header(
        "Module 06 · System Prompt Engineering",
        "Bare vs structured, XML tags, few-shot examples, dynamic construction"
    )

    api_key, base_url, model = load_env()
    client = make_client(api_key, base_url)

    # ── Code review comparison ────────────────────────────────────────────────
    bad_code = '''
def get_user(id):
    import sqlite3
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE id = {id}")
    return cur.fetchone()
'''
    print_divider("Comparison: Bare vs Structured System Prompt")
    print(f"Code under review:{bad_code}")
    compare_prompts(client, model, bad_code)

    # ── Few-shot ──────────────────────────────────────────────────────────────
    few_shot_extraction(client, model)

    # ── Dynamic prompt builder ────────────────────────────────────────────────
    print_divider("Dynamic System Prompt Builder")
    dynamic = dynamic_system_prompt(
        role="data architect",
        domain="real-time analytics pipelines",
        output_format="Use bullet points. Start with a TL;DR line.",
        tone="Precise and direct. No filler phrases.",
    )
    log("REQUEST", "Asking dynamically-prompted model a question…")
    try:
        r = client.messages.create(
            model=model, max_tokens=400, system=dynamic,
            messages=[{"role": "user",
                       "content": "What are the top 3 mistakes teams make when designing Kafka consumers?"}]
        )
        print(extract_text(r))
        report_usage(getattr(r, "usage", None), label="dynamic")
    except Exception as e:
        log("ERROR", str(e))

    print_divider("Module 06 Complete")


if __name__ == "__main__":
    run()

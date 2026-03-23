"""
Claude-powered Code Bug Fix task.

Uses claude-opus-4-6 with adaptive thinking and streaming
for high-quality, reliable bug fixes.
"""
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an expert Python developer and senior code reviewer with 10+ years of experience.
Your job is to identify and fix bugs in Python code with precision and clarity.

When fixing code:
1. Identify the root cause of the bug, not just symptoms
2. Make the minimal change necessary to fix the bug
3. Preserve the original code style and structure
4. Add a brief inline comment on the changed line(s) marking the fix

Always respond in EXACTLY this format — nothing else:
```python
# [your fixed code here with inline fix comment]
```
Explanation: [1-2 sentences describing what was wrong and how you fixed it]"""


def fix_code_bug(input_dict: dict) -> str:
    """
    Call Claude to fix a code bug.

    Args:
        input_dict: dict with 'buggy_code' and 'bug_description' keys

    Returns:
        Claude's full response (fixed code + explanation)
    """
    prompt = f"""Fix this Python bug.

Buggy code:
```python
{input_dict['buggy_code']}
```

Bug description: {input_dict['bug_description']}"""

    full_response = ""

    # Stream the response — adaptive thinking ensures deep reasoning
    # while streaming prevents HTTP timeout on longer responses
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    return full_response


def fix_code_bug_with_examples(input_dict: dict, few_shot_examples: list[dict]) -> str:
    """
    Fix a bug using few-shot examples for improved accuracy.
    Used when initial scores are low and re-evaluation is triggered.
    """
    # Build few-shot prefix from passing examples
    shots = ""
    for ex in few_shot_examples[:3]:
        shots += (
            f"\n\nExample:\n"
            f"Buggy code:\n```python\n{ex['input']['buggy_code']}\n```\n"
            f"Bug: {ex['input']['bug_description']}\n"
            f"Fix:\n```python\n{ex['reference_output']}\n```\n"
            f"Explanation: See fix comment above."
        )

    prompt = f"""Fix this Python bug. Study the examples first.
{shots}

Now fix this:
Buggy code:
```python
{input_dict['buggy_code']}
```

Bug description: {input_dict['bug_description']}"""

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=2048,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            full_response += text

    return full_response

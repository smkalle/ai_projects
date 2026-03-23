"""
Scoring functions for the Code Eval Workbench.

Four scorers, each returning a float in [0.0, 1.0]:

  1. llm_judge_score   — Claude grades correctness, code quality, explanation
  2. programmatic_score — Runs extracted code against embedded pytest tests
  3. levenshtein_score  — Character-level similarity vs reference (difflib)
  4. composite_score    — Weighted average of enabled scorers
"""
import difflib
import json
import os
import subprocess
import tempfile
from typing import Optional

import anthropic
from dotenv import load_dotenv

from utils import extract_code_block

load_dotenv()

client = anthropic.Anthropic()

# ─── Weights for composite scorer ────────────────────────────────────────────
COMPOSITE_WEIGHTS = {
    "llm_judge": 0.50,
    "programmatic": 0.30,
    "levenshtein": 0.20,
}


# ─── 1. LLM-as-Judge ─────────────────────────────────────────────────────────

def llm_judge_score(
    output: str,
    input_dict: dict,
    reference: str,
) -> tuple[float, str]:
    """
    Use Claude as a judge to score the fix on a 0.0–1.0 rubric.

    Returns:
        (score, reasoning) tuple
    """
    judge_prompt = f"""You are an expert code reviewer evaluating a student's bug fix.

Score the fix on a 0.0–1.0 scale using this EXACT rubric:
  - Correctness (0.40): Does the fix actually solve the stated bug?
  - Code Quality (0.30): Is the fixed code clean, idiomatic, and free of new bugs?
  - Explanation Quality (0.30): Is the explanation clear, accurate, and helpful?

Bug description: {input_dict['bug_description']}

Original buggy code:
```python
{input_dict['buggy_code']}
```

Reference correct fix:
```python
{reference}
```

Student's output:
{output}

Respond ONLY with valid JSON (no markdown, no explanation outside JSON):
{{"score": <float 0.0–1.0>, "reasoning": "<2-3 sentence evaluation>"}}"""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=512,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": judge_prompt}],
        )
        text = next(b.text for b in response.content if b.type == "text")
        # Strip any accidental markdown fences
        text = text.strip()
        if text.startswith("```"):
            import re
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text).strip()

        result = json.loads(text)
        score = float(result.get("score", 0.0))
        score = max(0.0, min(1.0, score))  # clamp to [0,1]
        reasoning = result.get("reasoning", "")
        return score, reasoning

    except Exception as e:
        return 0.0, f"Judge error: {e}"


# ─── 2. Programmatic Scorer ───────────────────────────────────────────────────

def programmatic_score(
    output: str,
    test_code: str,
) -> tuple[float, Optional[int], Optional[int]]:
    """
    Extract fixed code from output, run pytest tests, return pass rate.

    Returns:
        (score, passed_tests, total_tests)
    """
    if not test_code or not test_code.strip():
        return 0.5, None, None  # neutral when no tests available

    fixed_code = extract_code_block(output)
    if not fixed_code:
        return 0.0, 0, 0

    # Combine fixed code + test functions into a single temp file
    combined = fixed_code + "\n\n" + test_code

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix="eval_test_"
        ) as f:
            f.write(combined)
            tmp_path = f.name

        result = subprocess.run(
            ["python", "-m", "pytest", tmp_path, "-v", "--tb=short", "--no-header", "-q"],
            capture_output=True,
            text=True,
            timeout=15,
        )

        stdout = result.stdout + result.stderr

        # Parse pytest summary line: "2 passed, 1 failed"
        passed = stdout.count(" PASSED") + stdout.count(" passed")
        failed = stdout.count(" FAILED") + stdout.count(" failed")

        # Fallback: check exit code
        if passed == 0 and failed == 0:
            if result.returncode == 0:
                return 1.0, None, None
            else:
                return 0.0, 0, 0

        total = passed + failed
        score = passed / total if total > 0 else 0.0
        return score, passed, total

    except subprocess.TimeoutExpired:
        return 0.0, 0, 0
    except Exception:
        return 0.0, 0, 0
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ─── 3. Levenshtein / Sequence Similarity ────────────────────────────────────

def levenshtein_score(output: str, reference: str) -> float:
    """
    Compute normalized similarity between extracted output code and reference.

    Uses difflib.SequenceMatcher (character-level, similar to Levenshtein ratio).
    Returns 0.0–1.0.
    """
    output_code = extract_code_block(output)
    ref_code = reference.strip()

    # Normalize: collapse whitespace for a fairer comparison
    def normalize(code: str) -> str:
        import re
        # Remove comments
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
        # Collapse whitespace
        return " ".join(code.split())

    output_norm = normalize(output_code)
    ref_norm = normalize(ref_code)

    if not output_norm and not ref_norm:
        return 1.0
    if not output_norm or not ref_norm:
        return 0.0

    matcher = difflib.SequenceMatcher(None, output_norm, ref_norm, autojunk=False)
    return round(matcher.ratio(), 4)


# ─── 4. Composite Scorer ─────────────────────────────────────────────────────

def composite_score(
    output: str,
    input_dict: dict,
    reference: str,
    test_code: str = "",
    use_llm_judge: bool = True,
    use_programmatic: bool = True,
    use_levenshtein: bool = True,
) -> dict:
    """
    Run all enabled scorers and return a full score breakdown.

    Returns dict with keys: llm_judge, programmatic, levenshtein, composite,
    reasoning, passed_tests, total_tests
    """
    scores = {}
    reasoning = ""
    passed_tests = None
    total_tests = None

    if use_llm_judge:
        s, r = llm_judge_score(output, input_dict, reference)
        scores["llm_judge"] = s
        reasoning = r

    if use_programmatic:
        s, pt, tt = programmatic_score(output, test_code)
        scores["programmatic"] = s
        passed_tests = pt
        total_tests = tt

    if use_levenshtein:
        scores["levenshtein"] = levenshtein_score(output, reference)

    # Weighted composite over enabled scorers only
    total_weight = 0.0
    weighted_sum = 0.0
    for key, weight in COMPOSITE_WEIGHTS.items():
        if key in scores:
            weighted_sum += scores[key] * weight
            total_weight += weight

    composite = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "llm_judge": scores.get("llm_judge"),
        "programmatic": scores.get("programmatic"),
        "levenshtein": scores.get("levenshtein"),
        "composite": round(composite, 4),
        "reasoning": reasoning,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
    }

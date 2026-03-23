"""Shared utilities for the Code Eval Workbench."""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


# ─── Model / Client Configuration ────────────────────────────────────────────
# Supports two backends, selected via environment variables:
#
#   Claude (default):
#     ANTHROPIC_API_KEY=sk-ant-...          ← Anthropic key
#     (no ANTHROPIC_BASE_URL)
#
#   MiniMax M2.7 override:
#     ANTHROPIC_API_KEY=<minimax key>
#     ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
#     MINIMAX_USE_HIGHSPEED=true            ← optional: use MiniMax-M2.7-highspeed
#     MODEL_OVERRIDE=MiniMax-M2.7           ← optional: explicit model name

_CLAUDE_DEFAULT  = "claude-opus-4-6"
_MINIMAX_STD     = "MiniMax-M2.7"
_MINIMAX_HS      = "MiniMax-M2.7-highspeed"
_MINIMAX_HOSTS   = ("minimax.io", "minimaxi.com")

# MiniMax uses budget_tokens thinking (fixed-budget); Claude uses adaptive.
_THINKING_CLAUDE  = {"type": "adaptive"}
_THINKING_MINIMAX = {"type": "enabled", "budget_tokens": 3000}
# MiniMax requires max_tokens > budget_tokens; use a safe default.
_MAX_TOKENS_MINIMAX = 4096


def _is_minimax() -> bool:
    """Return True when ANTHROPIC_BASE_URL points at a MiniMax endpoint."""
    base_url = os.getenv("ANTHROPIC_BASE_URL", "")
    return any(host in base_url for host in _MINIMAX_HOSTS)


def get_model_config() -> dict:
    """
    Return a config dict for the active backend.

    Keys:
      client        — anthropic.Anthropic instance
      model         — model ID string
      thinking      — thinking param dict
      max_tokens    — safe default max_tokens (task / judge calls may override)
      backend       — "claude" | "minimax"
      base_url      — endpoint URL (for display / logging)
    """
    api_key  = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "")
    minimax  = _is_minimax()

    # Build client — if no base_url, SDK uses Anthropic's default endpoint
    client_kwargs: dict = {"api_key": api_key} if api_key else {}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = anthropic.Anthropic(**client_kwargs)

    # Resolve model name
    override = os.getenv("MODEL_OVERRIDE", "").strip()
    if override:
        model = override
    elif minimax:
        use_hs = os.getenv("MINIMAX_USE_HIGHSPEED", "false").lower() == "true"
        model = _MINIMAX_HS if use_hs else _MINIMAX_STD
    else:
        model = _CLAUDE_DEFAULT

    thinking   = _THINKING_MINIMAX if minimax else _THINKING_CLAUDE
    max_tokens = _MAX_TOKENS_MINIMAX if minimax else 2048
    backend    = "minimax" if minimax else "claude"

    return {
        "client":     client,
        "model":      model,
        "thinking":   thinking,
        "max_tokens": max_tokens,
        "backend":    backend,
        "base_url":   base_url or "https://api.anthropic.com (default)",
    }


# ─── Result Models ───────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    llm_judge: Optional[float] = None
    programmatic: Optional[float] = None
    levenshtein: Optional[float] = None
    composite: float = 0.0

class EvalResult(BaseModel):
    id: str
    category: str
    difficulty: str
    output: str
    scores: ScoreBreakdown
    reasoning: str = ""
    passed_tests: Optional[int] = None
    total_tests: Optional[int] = None
    timestamp: str = ""

    def model_post_init(self, __context):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class RunSummary(BaseModel):
    run_id: str
    timestamp: str
    avg_composite: float
    avg_llm_judge: float
    avg_programmatic: float
    avg_levenshtein: float
    n_examples: int
    scorers_used: list[str]
    results: list[EvalResult]


# ─── Code Extraction ─────────────────────────────────────────────────────────

def extract_code_block(text: str) -> str:
    """Extract the first Python code block from LLM output."""
    # Try ```python ... ```
    match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try ``` ... ```
    match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Return stripped text if no code fence found
    return text.strip()


def extract_explanation(text: str) -> str:
    """Extract the explanation part from LLM output."""
    match = re.search(r'Explanation:\s*(.*?)(?:\n\n|$)', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Try to find text after the last code block
    parts = re.split(r'```(?:python)?.*?```', text, flags=re.DOTALL)
    if len(parts) > 1:
        last = parts[-1].strip()
        if last:
            return last
    return ""


# ─── Results Persistence ─────────────────────────────────────────────────────

RESULTS_DIR = Path(__file__).parent / "results"


def save_run(summary: RunSummary) -> Path:
    """Save a run summary to JSON."""
    RESULTS_DIR.mkdir(exist_ok=True)
    path = RESULTS_DIR / f"run_{summary.run_id}.json"
    path.write_text(summary.model_dump_json(indent=2))
    return path


def load_all_runs() -> list[RunSummary]:
    """Load all saved run summaries sorted newest-first."""
    RESULTS_DIR.mkdir(exist_ok=True)
    runs = []
    for p in sorted(RESULTS_DIR.glob("run_*.json"), reverse=True):
        try:
            data = json.loads(p.read_text())
            runs.append(RunSummary(**data))
        except Exception:
            pass
    return runs


def load_run(run_id: str) -> Optional[RunSummary]:
    """Load a specific run by ID."""
    path = RESULTS_DIR / f"run_{run_id}.json"
    if not path.exists():
        return None
    return RunSummary(**json.loads(path.read_text()))


# ─── Formatting Helpers ───────────────────────────────────────────────────────

def score_color(score: float) -> str:
    """Return a color name based on score for Rich terminal."""
    if score >= 0.8:
        return "green"
    elif score >= 0.6:
        return "yellow"
    elif score >= 0.4:
        return "orange3"
    else:
        return "red"


def score_emoji(score: float) -> str:
    if score >= 0.8:
        return "✅"
    elif score >= 0.6:
        return "🟡"
    elif score >= 0.4:
        return "🟠"
    else:
        return "❌"

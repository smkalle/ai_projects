from __future__ import annotations

from dataclasses import dataclass

from .config import EvalConfig
from .models import EvalCase

RUBRIC_OPTIONS = {
    "balanced": "Balanced correctness, tool use, and latency",
    "strict_correctness": "Exact-answer focused regression gate",
    "tooling_regression": "Higher weight on expected tool use",
}


@dataclass(slots=True)
class ScoreResult:
    score: float
    passed: bool
    assertions: dict


def _norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


def apply_rubric_variant(config: EvalConfig) -> EvalConfig:
    if config.rubric_variant == "strict_correctness":
        config.correctness_weight = 0.85
        config.tool_weight = 0.1
        config.latency_weight = 0.05
        config.semantic_grading = False
        config.pass_threshold = 0.9
    elif config.rubric_variant == "tooling_regression":
        config.correctness_weight = 0.45
        config.tool_weight = 0.4
        config.latency_weight = 0.15
        config.pass_threshold = 0.8
    else:
        config.rubric_variant = "balanced"
        config.correctness_weight = 0.6
        config.tool_weight = 0.2
        config.latency_weight = 0.2
        config.pass_threshold = 0.8
    return config


def score_case(
    case: EvalCase,
    answer: str,
    used_tools: list[str],
    latency_ms: int,
    config: EvalConfig,
) -> ScoreResult:
    expected = _norm(case.expected_answer)
    got = _norm(answer)
    exact = got == expected
    semantic = expected in got or got in expected
    correctness = 1.0 if exact else (0.75 if config.semantic_grading and semantic else 0.0)

    required = set(case.expected_tools)
    used = set(used_tools)
    tool_ok = 1.0 if required.issubset(used) else 0.0

    latency_ok = 1.0 if latency_ms <= config.timeout_s * 1000 else 0.0
    total = (
        correctness * config.correctness_weight
        + tool_ok * config.tool_weight
        + latency_ok * config.latency_weight
    )

    assertions = {
        "expected_answer": case.expected_answer,
        "actual_answer": answer,
        "exact_match": exact,
        "semantic_match": semantic,
        "expected_tools": sorted(required),
        "used_tools": sorted(used),
        "tool_compliance": tool_ok == 1.0,
        "latency_ms": latency_ms,
        "latency_within_budget": latency_ok == 1.0,
    }
    assertions["rubric_variant"] = config.rubric_variant
    assertions["pass_threshold"] = config.pass_threshold
    return ScoreResult(score=round(total, 4), passed=total >= config.pass_threshold, assertions=assertions)

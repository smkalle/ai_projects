from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class EvalCase:
    case_id: str
    prompt: str
    expected_answer: str
    expected_tools: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StepEvent:
    run_id: str
    case_id: str
    step_idx: int
    event_type: str
    status: str
    payload: dict[str, Any]
    duration_ms: int = 0
    timestamp: str = field(default_factory=utc_now_iso)


@dataclass(slots=True)
class CaseResult:
    run_id: str
    case_id: str
    status: str
    score: float
    latency_ms: int
    answer: str
    assertions: dict[str, Any]


@dataclass(slots=True)
class EvalRun:
    run_id: str
    status: str
    dataset_id: str
    agent_profile: dict[str, Any]
    eval_config: dict[str, Any]
    created_at: str = field(default_factory=utc_now_iso)
    git_sha: str = "unknown"
    metrics_summary: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def new_id() -> str:
        return f"run_{uuid.uuid4().hex[:12]}"

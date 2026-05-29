from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(slots=True)
class AgentProfile:
    name: str = "tutorial-agent"
    model: str = "rule-based-v1"
    temperature: float = 0.0
    max_steps: int = 4
    enabled_tools: list[str] = field(default_factory=lambda: ["calculator", "lookup", "format_json"])


@dataclass(slots=True)
class EvalConfig:
    dataset_id: str = "tutorial_basics_v1"
    rubric_variant: str = "balanced"
    retries: int = 1
    timeout_s: int = 30
    fail_fast: bool = False
    semantic_grading: bool = True
    correctness_weight: float = 0.6
    tool_weight: float = 0.2
    latency_weight: float = 0.2
    pass_threshold: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

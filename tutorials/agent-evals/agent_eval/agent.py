from __future__ import annotations

from dataclasses import dataclass
import json
import os
from time import perf_counter
from typing import Any, Protocol
from urllib import request

from .config import AgentProfile
from .tools import TOOL_REGISTRY


@dataclass(slots=True)
class AgentStep:
    step_idx: int
    summary: str
    tool_name: str | None
    tool_args: dict[str, Any]
    tool_output: str | None
    duration_ms: int


@dataclass(slots=True)
class AgentResult:
    answer: str
    steps: list[AgentStep]


class ToolStack(Protocol):
    def run_tool(self, step_idx: int, name: str, args: dict[str, Any], summary: str) -> str:
        ...


class AgentBackend(Protocol):
    def solve(self, prompt: str, profile: AgentProfile, tools: ToolStack) -> AgentResult:
        ...


class LocalToolStack:
    def __init__(self, enabled_tools: list[str]):
        self.enabled_tools = set(enabled_tools)
        self.steps: list[AgentStep] = []

    def run_tool(self, step_idx: int, name: str, args: dict[str, Any], summary: str) -> str:
        if name not in self.enabled_tools:
            raise ValueError(f"Tool is disabled: {name}")
        if name not in TOOL_REGISTRY:
            raise ValueError(f"Unknown tool: {name}")
        start = perf_counter()
        output = str(TOOL_REGISTRY[name](**args))
        duration_ms = int((perf_counter() - start) * 1000)
        self.steps.append(
            AgentStep(
                step_idx=step_idx,
                summary=summary,
                tool_name=name,
                tool_args=args,
                tool_output=output,
                duration_ms=duration_ms,
            )
        )
        return output


class HeuristicBackend:
    def solve(self, prompt: str, profile: AgentProfile, tools: ToolStack) -> AgentResult:
        steps: list[AgentStep] = []

        lower = prompt.lower()
        answer = ""
        if "*" in prompt and "number" in lower and "calculator" in profile.enabled_tools:
            expr = prompt.split("?")[0].replace("What is", "").strip()
            answer = tools.run_tool(1, "calculator", {"expression": expr}, "Compute expression")
        elif "tutorial facts" in lower and "lookup" in profile.enabled_tools:
            key = "console framework" if "framework" in lower else "control panel accent"
            answer = tools.run_tool(1, "lookup", {"key": key}, "Lookup tutorial fact")
        elif "json object" in lower and "format_json" in profile.enabled_tools:
            answer = tools.run_tool(
                1,
                "format_json",
                {"obj": {"mode": "eval", "status": "ok"}},
                "Format JSON response",
            )
        elif "yes or no" in lower:
            steps.append(
                AgentStep(
                    step_idx=1,
                    summary="Direct policy answer",
                    tool_name=None,
                    tool_args={},
                    tool_output=None,
                    duration_ms=0,
                )
            )
            answer = "yes"
        else:
            steps.append(
                AgentStep(
                    step_idx=1,
                    summary="Fallback answer",
                    tool_name=None,
                    tool_args={},
                    tool_output=None,
                    duration_ms=0,
                )
            )
            answer = "unknown"

        if isinstance(tools, LocalToolStack):
            steps = tools.steps + steps
        return AgentResult(answer=answer.strip(), steps=steps)


class OpenAICompatibleBackend:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1/chat/completions"):
        self.api_key = api_key
        self.base_url = base_url

    def solve(self, prompt: str, profile: AgentProfile, tools: ToolStack) -> AgentResult:
        tool_names = ", ".join(profile.enabled_tools)
        body = {
            "model": profile.model.replace("openai:", "", 1),
            "temperature": profile.temperature,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an eval agent. Return compact JSON with keys answer and tool_calls. "
                        "tool_calls is an array of objects with name, args, and summary. "
                        f"Available tools: {tool_names}. Use tools when they directly answer the prompt."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        data = json.dumps(body).encode("utf-8")
        req = request.Request(
            self.base_url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))

        content = payload["choices"][0]["message"]["content"]
        plan = json.loads(content)
        answer = str(plan.get("answer", ""))
        for idx, call in enumerate(plan.get("tool_calls", []), start=1):
            name = call["name"]
            args = call.get("args", {})
            output = tools.run_tool(idx, name, args, call.get("summary", f"Run {name}"))
            answer = output if not answer else answer

        steps = tools.steps if isinstance(tools, LocalToolStack) else []
        return AgentResult(answer=answer.strip(), steps=steps)


def build_backend(profile: AgentProfile) -> AgentBackend:
    if profile.model.startswith("openai:") and os.getenv("OPENAI_API_KEY"):
        return OpenAICompatibleBackend(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.getenv("OPENAI_CHAT_COMPLETIONS_URL", "https://api.openai.com/v1/chat/completions"),
        )
    return HeuristicBackend()


class TutorialAgent:
    def __init__(self, profile: AgentProfile, backend: AgentBackend | None = None):
        self.profile = profile
        self.backend = backend or build_backend(profile)

    def solve(self, prompt: str) -> AgentResult:
        tools = LocalToolStack(self.profile.enabled_tools)
        return self.backend.solve(prompt, self.profile, tools)

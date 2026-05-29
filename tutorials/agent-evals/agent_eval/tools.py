from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(slots=True)
class ToolCall:
    name: str
    args: dict


TUTORIAL_FACTS = {
    "control panel accent": "teal",
    "retry default": "1",
    "console framework": "streamlit",
}


def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if any(ch not in allowed for ch in expression):
        raise ValueError("Unsafe characters in expression")
    return str(eval(expression, {"__builtins__": {}}, {}))


def lookup(key: str) -> str:
    return TUTORIAL_FACTS.get(key.lower().strip(), "unknown")


def format_json(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)


TOOL_REGISTRY = {
    "calculator": calculator,
    "lookup": lookup,
    "format_json": format_json,
}

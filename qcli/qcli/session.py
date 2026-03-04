from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GenerationConfig:
    temperature: float = 0.7
    top_p: float = 0.9
    max_new_tokens: int = 512


@dataclass
class ChatSession:
    system_prompt: str = "You are a helpful assistant."
    config: GenerationConfig = field(default_factory=GenerationConfig)
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.messages:
            self.messages = [{"role": "system", "content": self.system_prompt}]

    def reset(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def set_system_prompt(self, text: str) -> None:
        self.system_prompt = text
        self.reset()

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})

    def save(self, path: str | Path) -> None:
        payload = {
            "system_prompt": self.system_prompt,
            "config": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "max_new_tokens": self.config.max_new_tokens,
            },
            "messages": self.messages,
        }
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ChatSession":
        payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        config = payload.get("config", {})
        session = cls(
            system_prompt=payload.get("system_prompt", "You are a helpful assistant."),
            config=GenerationConfig(
                temperature=float(config.get("temperature", 0.7)),
                top_p=float(config.get("top_p", 0.9)),
                max_new_tokens=int(config.get("max_new_tokens", 512)),
            ),
            messages=payload.get("messages", []),
        )
        if not session.messages:
            session.reset()
        return session


def parse_command(line: str) -> tuple[str, list[str]] | None:
    if not line.startswith("/"):
        return None
    parts = line[1:].strip().split()
    if not parts:
        return None
    return parts[0], parts[1:]

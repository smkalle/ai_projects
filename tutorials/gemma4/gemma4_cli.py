#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              GEMMA 4 CLI  —  Production Chat Interface                       ║
║         Built for AI Engineers  ·  April 2026  ·  Apache 2.0                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Based on the Gemma 4 L5 Engineer Tutorial covering:                         ║
║    · All 4 model sizes  (E2B / E4B / 26B MoE / 31B Dense)                   ║
║    · Multimodal input   (image attached to any message)                      ║
║    · Native function calling  (5 built-in tools + agentic loop)              ║
║    · 256K long-context conversation tracking                                 ║
║    · Offline code generation with engineer-grade system prompts              ║
║    · 140+ language support  (zero-shot)                                      ║
║    · Save / Load / Export conversations                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  REQUIREMENTS                                                                ║
║    pip install rich requests                                                 ║
║                                                                              ║
║  OLLAMA SETUP (must be running before chatting)                              ║
║    curl -fsSL https://ollama.com/install.sh | sh                             ║
║    ollama serve                    # separate terminal                       ║
║    ollama pull gemma4:e4b          # recommended starting model              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  USAGE                                                                       ║
║    python gemma4_cli.py                         default: gemma4:e4b          ║
║    python gemma4_cli.py --model 31b             max intelligence             ║
║    python gemma4_cli.py --model 26b --tools     agent mode w/ tools          ║
║    python gemma4_cli.py --ctx 131072            long-context mode            ║
║    python gemma4_cli.py --system "Be concise"   custom system prompt         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import platform
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional

import requests
from rich import box
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# ──────────────────────────────────────────────────────────────────────────────
# Constants & Configuration
# ──────────────────────────────────────────────────────────────────────────────

APP_VERSION    = "1.0.0"
OLLAMA_URL     = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

# Gemma 4 model catalog — matches the L5 tutorial specs exactly
MODEL_CATALOG: dict[str, dict] = {
    "e2b": {
        "tag":      "gemma4:e2b",
        "params":   "2B effective",
        "ctx":      "128K",
        "ctx_int":  131072,
        "vram":     "~3.2 GB",
        "modality": "Text + Image + Audio + Video",
        "best_for": "Mobile / Edge / Browser",
    },
    "e4b": {
        "tag":      "gemma4:e4b",
        "params":   "4B effective",
        "ctx":      "128K",
        "ctx_int":  131072,
        "vram":     "~5 GB",
        "modality": "Text + Image + Audio + Video",
        "best_for": "Phones / Laptops / Raspberry Pi",
    },
    "26b": {
        "tag":      "gemma4:26b",
        "params":   "4B active / 26B total (MoE)",
        "ctx":      "256K",
        "ctx_int":  262144,
        "vram":     "~15.6 GB",
        "modality": "Text + Image + Audio",
        "best_for": "High-throughput Local Agents",
    },
    "31b": {
        "tag":      "gemma4:31b",
        "params":   "31B dense",
        "ctx":      "256K",
        "ctx_int":  262144,
        "vram":     "~17.4 GB",
        "modality": "Text + Image + Audio",
        "best_for": "Best Reasoning Quality",
    },
}

DEFAULT_SYSTEM_PROMPT = (
    "You are Gemma 4, a helpful, precise, and production-focused AI assistant "
    "built for AI engineers. You excel at code generation, agentic reasoning, "
    "multimodal analysis, and multilingual tasks. When asked to use tools, "
    "always respond with tool calls in valid JSON format as specified in the "
    "tool schemas."
)

CODE_SYSTEM_PROMPT = (
    "You are an expert SDE3 at Google. Write clean, production-ready, "
    "well-documented Python code. Use type hints, pydantic, FastAPI where "
    "appropriate. Include tests. Follow PEP8 + Google style guide."
)

# Rich terminal theme
THEME = Theme({
    "user":      "bold cyan",
    "assistant": "bold green",
    "tool_call": "bold yellow",
    "system_msg":"bold magenta",
    "error_msg": "bold red",
    "info_msg":  "bold blue",
    "dim_txt":   "dim white",
    "hdr":       "bold white on dark_blue",
})


# ──────────────────────────────────────────────────────────────────────────────
# Built-in Tool Definitions  (JSON Schema for function calling)
# ──────────────────────────────────────────────────────────────────────────────

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "Get current weather and forecast for any city. "
                "Returns temperature, sky conditions, humidity, rain chance, "
                "and an umbrella recommendation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Bangalore', 'Tokyo', 'San Francisco'",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit (default: celsius)",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Evaluate a mathematical expression safely. Supports arithmetic, "
                "exponents (**), trig (sin/cos/tan), log, sqrt, floor, ceil, etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Python-style math expression, e.g. 'sqrt(144) + 2**10'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a local file for code review or analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative file path",
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum lines to read (default: 200)",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and folders at a path with sizes and modification times.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (default: current directory '.')",
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Include dotfiles (default: false)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Return OS, Python version, CPU architecture, and memory stats.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# Tool Implementations
# ──────────────────────────────────────────────────────────────────────────────

def _tool_get_weather(city: str, unit: str = "celsius") -> dict:
    """
    Demo weather tool.
    Replace with a real provider like OpenWeatherMap:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",
                         params={"q": city, "appid": API_KEY, "units": "metric"})
    """
    _DB: dict[str, dict] = {
        "bangalore":     {"temp_c": 28, "cond": "Partly Cloudy", "hum": 65, "rain": 30},
        "mumbai":        {"temp_c": 32, "cond": "Hot and Humid",  "hum": 80, "rain": 20},
        "delhi":         {"temp_c": 35, "cond": "Sunny",          "hum": 40, "rain":  5},
        "london":        {"temp_c": 12, "cond": "Overcast",       "hum": 85, "rain": 60},
        "san francisco": {"temp_c": 16, "cond": "Foggy",          "hum": 78, "rain": 25},
        "tokyo":         {"temp_c": 18, "cond": "Clear",          "hum": 60, "rain": 10},
        "new york":      {"temp_c": 15, "cond": "Partly Cloudy",  "hum": 70, "rain": 35},
    }
    d = _DB.get(city.lower(), {"temp_c": 22, "cond": "Clear", "hum": 55, "rain": 10})
    temp = d["temp_c"] if unit == "celsius" else round(d["temp_c"] * 9 / 5 + 32, 1)
    sym  = "°C" if unit == "celsius" else "°F"
    return {
        "city":                   city,
        "temperature":            f"{temp}{sym}",
        "conditions":             d["cond"],
        "humidity":               f"{d['hum']}%",
        "rain_probability":       f"{d['rain']}%",
        "umbrella_recommendation": "Yes, bring an umbrella!" if d["rain"] > 40 else "No umbrella needed.",
        "_note":                  "Demo data — connect to OpenWeatherMap for live results",
    }


def _tool_calculate(expression: str) -> dict:
    """Safe math evaluator — no imports, no builtins, only math module symbols."""
    safe = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    safe.update({"abs": abs, "round": round, "int": int, "float": float, "pow": pow})
    for banned in ("__", "import", "open", "exec", "eval", "compile", "os", "sys", "subprocess"):
        if banned in expression:
            return {"error": f"Blocked: expression contains '{banned}'"}
    try:
        result = eval(expression, {"__builtins__": {}}, safe)  # noqa: S307
        return {
            "expression": expression,
            "result":     result,
            "formatted":  f"{result:,}" if isinstance(result, (int, float)) else str(result),
        }
    except Exception as exc:
        return {"error": str(exc), "expression": expression}


def _tool_read_file(path: str, max_lines: int = 200) -> dict:
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return {"error": f"File not found: {path}"}
        if p.stat().st_size > 10 * 1024 * 1024:
            return {"error": "File too large (>10 MB). Specify a smaller range."}
        lines = p.read_text(errors="replace").splitlines()
        truncated = len(lines) > max_lines
        return {
            "path":        str(p),
            "size_bytes":  p.stat().st_size,
            "total_lines": len(lines),
            "content":     "\n".join(lines[:max_lines]),
            "truncated":   truncated,
            "note":        f"Showing first {max_lines} of {len(lines)} lines" if truncated else "Full file",
        }
    except Exception as exc:
        return {"error": str(exc)}


def _tool_list_directory(path: str = ".", show_hidden: bool = False) -> dict:
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return {"error": f"Path not found: {path}"}
        entries = []
        for item in sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
            if not show_hidden and item.name.startswith("."):
                continue
            st = item.stat()
            entries.append({
                "name":     item.name,
                "type":     "dir" if item.is_dir() else "file",
                "size_kb":  round(st.st_size / 1024, 1) if item.is_file() else None,
                "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
        return {"path": str(p), "entries": entries, "count": len(entries)}
    except Exception as exc:
        return {"error": str(exc)}


def _tool_get_system_info() -> dict:
    info: dict[str, Any] = {
        "os":           platform.system(),
        "os_release":   platform.release(),
        "architecture": platform.machine(),
        "python":       sys.version.split()[0],
        "cpu_cores":    os.cpu_count(),
    }
    try:
        import psutil
        mem = psutil.virtual_memory()
        info["memory_total_gb"]     = round(mem.total     / 1e9, 1)
        info["memory_available_gb"] = round(mem.available / 1e9, 1)
        info["memory_used_pct"]     = mem.percent
    except ImportError:
        info["memory_note"] = "Install psutil for memory stats"
    return info


# Dispatch map: tool name → callable
_TOOL_DISPATCH: dict[str, Any] = {
    "get_weather":    lambda a: _tool_get_weather(**a),
    "calculate":      lambda a: _tool_calculate(**a),
    "read_file":      lambda a: _tool_read_file(**a),
    "list_directory": lambda a: _tool_list_directory(**a),
    "get_system_info": lambda _: _tool_get_system_info(),
}


# ──────────────────────────────────────────────────────────────────────────────
# Ollama REST Client
# ──────────────────────────────────────────────────────────────────────────────

class OllamaClient:
    """
    Thin wrapper around Ollama's REST API.
    Endpoints used:
        GET  /             — health check
        GET  /api/tags     — list installed models
        POST /api/pull     — pull a model (streaming)
        POST /api/chat     — chat completions (streaming)
    """

    def __init__(self, base_url: str = OLLAMA_URL) -> None:
        self.base = base_url.rstrip("/")

    # ── Health ─────────────────────────────────────────────────────────────────

    def ping(self) -> bool:
        try:
            return requests.get(f"{self.base}/", timeout=3).status_code == 200
        except Exception:
            return False

    # ── Model management ───────────────────────────────────────────────────────

    def list_models(self) -> list[dict]:
        try:
            r = requests.get(f"{self.base}/api/tags", timeout=10)
            r.raise_for_status()
            return r.json().get("models", [])
        except Exception:
            return []

    def pull_model(self, tag: str) -> Generator[str, None, None]:
        """Stream pull progress lines."""
        try:
            with requests.post(
                f"{self.base}/api/pull",
                json={"name": tag, "stream": True},
                stream=True,
                timeout=600,
            ) as r:
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        yield data.get("status", "")
        except Exception as exc:
            yield f"Pull error: {exc}"

    # ── Chat (streaming) ───────────────────────────────────────────────────────

    def chat(
        self,
        model: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        options: Optional[dict]     = None,
    ) -> Generator[dict, None, None]:
        """
        POST /api/chat with stream=True.
        Yields parsed JSON dicts until done=True.
        On connection error yields {"error": "..."}.
        """
        payload: dict[str, Any] = {
            "model":    model,
            "messages": messages,
            "stream":   True,
        }
        if tools:
            payload["tools"] = tools
        if options:
            payload["options"] = options

        try:
            with requests.post(
                f"{self.base}/api/chat",
                json=payload,
                stream=True,
                timeout=300,
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        yield json.loads(line)
        except requests.exceptions.ConnectionError:
            yield {"error": "Cannot connect to Ollama. Is `ollama serve` running?"}
        except requests.exceptions.HTTPError as exc:
            yield {"error": f"HTTP {exc.response.status_code}: {exc.response.text[:200]}"}
        except Exception as exc:
            yield {"error": str(exc)}


# ──────────────────────────────────────────────────────────────────────────────
# Conversation Manager
# ──────────────────────────────────────────────────────────────────────────────

class ConversationManager:
    """
    Manages the full message history for multi-turn conversation.

    Message roles:
        system    — initial instruction (persisted across /clear)
        user      — human turn (text, optionally with images list)
        assistant — model response (optionally with tool_calls)
        tool      — tool execution result fed back to the model
    """

    def __init__(self, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> None:
        self.messages: list[dict] = []
        self.system_prompt = system_prompt
        self.tokens_prompt   = 0
        self.tokens_generate = 0
        self.turn_count      = 0
        self.created_at      = datetime.now().isoformat()
        # Install system message
        self._set_system(system_prompt)

    # ── Mutators ───────────────────────────────────────────────────────────────

    def _set_system(self, prompt: str) -> None:
        self.system_prompt = prompt
        self.messages = [m for m in self.messages if m.get("role") != "system"]
        self.messages.insert(0, {"role": "system", "content": prompt})

    def update_system(self, prompt: str) -> None:
        self._set_system(prompt)

    def add_user(self, text: str, image_b64: Optional[str] = None) -> None:
        """
        Ollama multimodal: images are passed as a list of raw base64 strings
        in a top-level 'images' key alongside 'content'.
        """
        msg: dict[str, Any] = {"role": "user", "content": text}
        if image_b64:
            msg["images"] = [image_b64]
        self.messages.append(msg)
        self.turn_count += 1

    def add_assistant(self, content: str, tool_calls: Optional[list] = None) -> None:
        msg: dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)

    def add_tool_result(self, tool_name: str, result: Any) -> None:
        """
        Ollama expects tool results with role='tool'.
        Content must be a string (we JSON-encode the result dict).
        """
        self.messages.append({
            "role":    "tool",
            "name":    tool_name,
            "content": json.dumps(result, ensure_ascii=False, indent=2),
        })

    def update_token_stats(self, prompt_tokens: int, gen_tokens: int) -> None:
        self.tokens_prompt   += prompt_tokens
        self.tokens_generate += gen_tokens

    # ── Context stats ──────────────────────────────────────────────────────────

    def approximate_tokens(self) -> int:
        """Rough estimate: split on whitespace × 1.3 for BPE overhead."""
        total = 0
        for m in self.messages:
            content = m.get("content", "")
            if isinstance(content, str):
                total += len(content.split()) * 1.3
        return int(total)

    def stats(self) -> dict:
        return {
            "turns":           self.turn_count,
            "messages":        len(self.messages),
            "approx_tokens":   self.approximate_tokens(),
            "tokens_prompt":   self.tokens_prompt,
            "tokens_generate": self.tokens_generate,
        }

    # ── Persistence ────────────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        payload = {
            "app_version":   APP_VERSION,
            "created_at":    self.created_at,
            "saved_at":      datetime.now().isoformat(),
            "system_prompt": self.system_prompt,
            "stats":         self.stats(),
            "messages":      self.messages,
        }
        Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    def load(self, path: str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.messages      = data.get("messages", [])
        self.system_prompt = data.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        self.created_at    = data.get("created_at", self.created_at)

    def export_markdown(self, path: str) -> None:
        lines = [
            "# Gemma 4 Conversation Export\n\n",
            f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n",
            "---\n\n",
        ]
        for m in self.messages:
            role    = m.get("role", "unknown").upper()
            content = m.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") for c in content if c.get("type") == "text"
                )
            lines.append(f"### [{role}]\n\n{content}\n\n---\n\n")
        Path(path).write_text("".join(lines), encoding="utf-8")

    def clear(self) -> None:
        """Clear history but keep system prompt."""
        self.messages    = []
        self.turn_count  = 0
        self._set_system(self.system_prompt)


# ──────────────────────────────────────────────────────────────────────────────
# Main CLI
# ──────────────────────────────────────────────────────────────────────────────

class Gemma4CLI:
    """
    Interactive CLI for Gemma 4 via Ollama.

    Implements the full agentic loop:
        user prompt  →  model  →  [tool calls]  →  tool results  →  model  →  final response
    Supports up to MAX_TOOL_ROUNDS rounds of tool calling per user turn.
    """

    MAX_TOOL_ROUNDS = 8   # safety limit for agentic loops

    def __init__(
        self,
        model_key:     str  = "e4b",
        system_prompt: str  = DEFAULT_SYSTEM_PROMPT,
        tools_enabled: bool = False,
        ctx_size:      int  = 32768,
        temperature:   float = 0.7,
    ) -> None:
        self.console   = Console(theme=THEME, highlight=False)
        self.client    = OllamaClient()
        self.model_key = model_key
        self.model_tag = MODEL_CATALOG.get(model_key, MODEL_CATALOG["e4b"])["tag"]
        self.tools_en  = tools_enabled
        self.options   = {"temperature": temperature, "num_ctx": ctx_size}
        self.conv      = ConversationManager(system_prompt)

        # State
        self.pending_image: Optional[str] = None  # path of image queued for next message

    # ── Display helpers ────────────────────────────────────────────────────────

    def _banner(self) -> None:
        info = MODEL_CATALOG.get(self.model_key, {})
        tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 1), border_style="dim blue")
        tbl.add_column(style="dim cyan",   width=14)
        tbl.add_column(style="white")
        tbl.add_row("Model",    f"{self.model_tag}  ({info.get('params','')})")
        tbl.add_row("Context",  info.get("ctx", "—"))
        tbl.add_row("Modality", info.get("modality", "—"))
        tbl.add_row("VRAM",     info.get("vram", "—"))
        tbl.add_row("Best for", info.get("best_for", "—"))
        tbl.add_row("Tools",    "[bold yellow]✅ ON[/bold yellow]  (5 built-in)" if self.tools_en else "❌ OFF  (/tools to enable)")
        tbl.add_row("License",  "Apache 2.0 — commercial use OK")

        self.console.print(Panel(
            tbl,
            title=f"[hdr]  🤖  GEMMA 4 CLI  v{APP_VERSION}  ",
            subtitle="[dim_txt]Type [bold]/help[/bold] for all commands",
            border_style="blue",
            padding=(0, 1),
        ))

    def _help(self) -> None:
        tbl = Table(
            title="Commands", box=box.ROUNDED,
            border_style="blue", show_header=True, header_style="bold cyan",
        )
        tbl.add_column("Command",     style="cyan",  width=26, no_wrap=True)
        tbl.add_column("Description", style="white")

        rows = [
            # Navigation
            ("/help",              "Show this help"),
            ("/quit  /exit",       "Exit the application"),
            # Model
            ("/model <key>",       "Switch model: e2b | e4b | 26b | 31b"),
            ("/models",            "List models installed in Ollama"),
            ("/pull <tag>",        "Pull a model from Ollama registry"),
            ("/specs",             "Gemma 4 full model comparison table"),
            # Multimodal
            ("/image <path>",      "Attach image to next message (multimodal)"),
            # Function calling
            ("/tools",             "Toggle function calling on / off"),
            ("/tool-list",         "Show all 5 built-in tools"),
            # Prompt & context
            ("/system [prompt]",   "View or update system prompt"),
            ("/code-mode",         "Switch to offline code-generation system prompt"),
            ("/context",           "Show context window stats & token counts"),
            ("/temp <0.0-2.0>",    "Set generation temperature"),
            ("/ctx <tokens>",      "Set context window (e.g. 32768 / 131072 / 262144)"),
            # History
            ("/clear",             "Clear conversation (keeps system prompt)"),
            ("/save [file]",       "Save conversation to JSON"),
            ("/load <file>",       "Load saved conversation from JSON"),
            ("/export [file]",     "Export conversation as Markdown"),
        ]
        for cmd, desc in rows:
            tbl.add_row(cmd, desc)
        self.console.print(tbl)

    def _specs(self) -> None:
        tbl = Table(title="Gemma 4 Model Catalog", box=box.ROUNDED, border_style="blue")
        tbl.add_column("Key",      style="bold cyan",  width=5)
        tbl.add_column("Tag",      style="white",      width=14)
        tbl.add_column("Params",   style="green")
        tbl.add_column("Context",  style="yellow")
        tbl.add_column("VRAM",     style="magenta")
        tbl.add_column("Modality", style="white", width=28)
        tbl.add_column("Best For", style="dim white")
        for key, info in MODEL_CATALOG.items():
            marker = "  ◀ active" if key == self.model_key else ""
            tbl.add_row(
                key, info["tag"], info["params"], info["ctx"],
                info["vram"], info["modality"], info["best_for"] + marker,
            )
        tbl.add_section()
        tbl.add_row("", "", "MoE = Mixture of Experts (26B)", "256K = 26B/31B", "", "", "Apache 2.0 License")
        self.console.print(tbl)

    def _context_stats(self) -> None:
        s    = self.conv.stats()
        info = MODEL_CATALOG.get(self.model_key, {})
        tbl  = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tbl.add_column(style="bold cyan",  width=22)
        tbl.add_column(style="white")
        tbl.add_row("Turns",             str(s["turns"]))
        tbl.add_row("Messages",          str(s["messages"]))
        tbl.add_row("~Context Tokens",   f"{s['approx_tokens']:,}")
        tbl.add_row("Model Max Context", info.get("ctx", "—"))
        tbl.add_row("Actual ctx_size",   f"{self.options.get('num_ctx', 0):,}")
        tbl.add_row("Tokens (prompt)",   f"{s['tokens_prompt']:,}")
        tbl.add_row("Tokens (generate)", f"{s['tokens_generate']:,}")
        self.console.print(Panel(tbl, title="[bold]📊 Context Stats", border_style="dim blue"))

    def _tool_list(self) -> None:
        tbl = Table(
            title="Built-in Tools  (function calling)",
            box=box.ROUNDED, border_style="yellow",
        )
        tbl.add_column("Tool",         style="bold yellow", width=18)
        tbl.add_column("Description",  style="white")
        tbl.add_column("Required Args", style="dim")

        rows = [
            ("get_weather",     "Weather + umbrella tip for any city",        "city"),
            ("calculate",       "Safe math: trig / log / sqrt / exponents",   "expression"),
            ("read_file",       "Read a local file (code, docs, data)",        "path"),
            ("list_directory",  "List directory with sizes & timestamps",      "—"),
            ("get_system_info", "OS / Python / CPU / memory",                 "—"),
        ]
        for name, desc, args in rows:
            tbl.add_row(name, desc, args)
        self.console.print(tbl)

    # ── Image handling ─────────────────────────────────────────────────────────

    @staticmethod
    def _encode_image(path: str) -> Optional[str]:
        """Return raw base64 string (no data: prefix) for Ollama's images array."""
        try:
            with open(path, "rb") as fh:
                return base64.b64encode(fh.read()).decode("utf-8")
        except Exception as exc:
            return None

    # ── Tool execution ─────────────────────────────────────────────────────────

    def _run_tool(self, name: str, args: dict) -> Any:
        fn = _TOOL_DISPATCH.get(name)
        if fn is None:
            return {"error": f"Unknown tool: '{name}'"}
        try:
            return fn(args)
        except TypeError as exc:
            return {"error": f"Bad arguments for {name}: {exc}"}
        except Exception as exc:
            return {"error": str(exc)}

    # ── Core chat method ───────────────────────────────────────────────────────

    def _chat(self, user_text: str) -> None:
        """
        Send one user turn to the model, handle streaming response,
        execute tool calls if present, loop until final text response.
        """
        # ── Build user message (with optional image) ──────────────────────────
        image_b64: Optional[str] = None
        if self.pending_image:
            b64 = self._encode_image(self.pending_image)
            if b64:
                image_b64 = b64
                self.console.print(f"[info_msg]📎 Image attached: {self.pending_image}[/info_msg]")
            else:
                self.console.print(f"[error_msg]⚠ Could not read image: {self.pending_image}[/error_msg]")
            self.pending_image = None

        self.conv.add_user(user_text, image_b64=image_b64)
        tools = TOOL_SCHEMAS if self.tools_en else None

        # ── Agentic loop ──────────────────────────────────────────────────────
        for _round in range(self.MAX_TOOL_ROUNDS):
            accumulated   = ""
            tool_calls    = []
            err_flag      = False

            self.console.print(
                f"\n[assistant]Gemma 4[/assistant]  [dim_txt]{self.model_tag}[/dim_txt]"
            )

            # Stream response character-by-character
            with Live("", console=self.console, refresh_per_second=20) as live:
                buf = Text()
                for chunk in self.client.chat(
                    model    = self.model_tag,
                    messages = self.conv.messages,
                    tools    = tools,
                    options  = self.options,
                ):
                    if "error" in chunk:
                        live.update(f"[error_msg]{chunk['error']}[/error_msg]")
                        err_flag = True
                        break

                    msg   = chunk.get("message", {})
                    delta = msg.get("content", "")
                    accumulated += delta
                    buf.append(delta)
                    live.update(buf)

                    # Collect tool calls if model returns them
                    if msg.get("tool_calls"):
                        tool_calls.extend(msg["tool_calls"])

                    if chunk.get("done"):
                        self.conv.update_token_stats(
                            chunk.get("prompt_eval_count", 0),
                            chunk.get("eval_count", 0),
                        )
                        break

            if err_flag:
                return

            # ── No tool calls → final response, render as Markdown ────────────
            if not tool_calls:
                self.conv.add_assistant(accumulated)
                if accumulated.strip():
                    # Rerender as Markdown for pretty code blocks, headers, etc.
                    self.console.print()
                    self.console.print(Markdown(accumulated))
                break

            # ── Tool calls present → execute and loop ─────────────────────────
            self.conv.add_assistant(accumulated, tool_calls)
            self.console.print()  # newline after streamed content

            for tc in tool_calls:
                fn_info = tc.get("function", {})
                name    = fn_info.get("name", "")
                raw_args= fn_info.get("arguments", {})

                # arguments may come as JSON string or dict
                if isinstance(raw_args, str):
                    try:
                        raw_args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        raw_args = {}

                self.console.print(
                    f"[tool_call]🔧  {name}({json.dumps(raw_args, separators=(',', ':'))})[/tool_call]"
                )
                result = self._run_tool(name, raw_args)
                self.console.print(Panel(
                    json.dumps(result, indent=2, ensure_ascii=False),
                    title=f"[tool_call]Tool result: {name}[/tool_call]",
                    border_style="yellow",
                    padding=(0, 1),
                ))
                self.conv.add_tool_result(name, result)
            # → next iteration feeds tool results back to model

        self.console.print(Rule(style="dim blue"))

    # ── Command dispatcher ─────────────────────────────────────────────────────

    def _command(self, raw: str) -> bool:
        """Parse and execute a /command. Returns False to quit."""
        parts = raw.strip().split(maxsplit=1)
        cmd   = parts[0].lower()
        arg   = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ("/quit", "/exit"):
            self.console.print("[info_msg]Goodbye! 👋[/info_msg]")
            return False

        elif cmd == "/help":
            self._help()

        elif cmd == "/specs":
            self._specs()

        elif cmd == "/models":
            models = self.client.list_models()
            if not models:
                self.console.print("[error_msg]No models found or Ollama is not running.[/error_msg]")
            else:
                tbl = Table(title="Installed Ollama Models", box=box.ROUNDED, border_style="blue")
                tbl.add_column("Name",        style="cyan")
                tbl.add_column("Size",        style="green")
                tbl.add_column("Modified",    style="dim")
                for m in models:
                    size_gb = round(m.get("size", 0) / 1e9, 2)
                    tbl.add_row(m.get("name", ""), f"{size_gb} GB", m.get("modified_at", "")[:10])
                self.console.print(tbl)

        elif cmd == "/pull":
            if not arg:
                self.console.print("[error_msg]Usage: /pull <model-tag>[/error_msg]")
            else:
                self.console.print(f"[info_msg]Pulling {arg} …[/info_msg]")
                for status in self.client.pull_model(arg):
                    self.console.print(f"  [dim_txt]{status}[/dim_txt]", end="\r")
                self.console.print(f"\n[info_msg]✅  Pulled {arg}[/info_msg]")

        elif cmd == "/model":
            if arg not in MODEL_CATALOG:
                self.console.print(
                    f"[error_msg]Unknown key '{arg}'. Choose: {', '.join(MODEL_CATALOG)}[/error_msg]"
                )
            else:
                self.model_key = arg
                self.model_tag = MODEL_CATALOG[arg]["tag"]
                # Auto-adjust ctx to model max if current setting exceeds it
                max_ctx = MODEL_CATALOG[arg]["ctx_int"]
                if self.options.get("num_ctx", 0) > max_ctx:
                    self.options["num_ctx"] = max_ctx
                self.console.print(
                    f"[info_msg]✅  Switched to [bold]{self.model_tag}[/bold]"
                    f"  (ctx={self.options['num_ctx']:,})[/info_msg]"
                )

        elif cmd == "/image":
            if not arg:
                self.console.print("[error_msg]Usage: /image <path>[/error_msg]")
            elif not Path(arg).expanduser().exists():
                self.console.print(f"[error_msg]File not found: {arg}[/error_msg]")
            else:
                self.pending_image = str(Path(arg).expanduser())
                self.console.print(f"[info_msg]📎  Image queued: {self.pending_image}[/info_msg]")
                self.console.print("[dim_txt]Now type your prompt and it will be sent with the image.[/dim_txt]")

        elif cmd == "/tools":
            self.tools_en = not self.tools_en
            state = "[bold yellow]✅ Enabled[/bold yellow]" if self.tools_en else "❌ Disabled"
            self.console.print(f"[info_msg]Function calling: {state}[/info_msg]")

        elif cmd == "/tool-list":
            self._tool_list()

        elif cmd == "/system":
            if not arg:
                self.console.print(Panel(
                    self.conv.system_prompt,
                    title="Current System Prompt",
                    border_style="magenta",
                ))
            else:
                self.conv.update_system(arg)
                self.console.print("[info_msg]✅  System prompt updated.[/info_msg]")

        elif cmd == "/code-mode":
            self.conv.update_system(CODE_SYSTEM_PROMPT)
            self.console.print(
                "[info_msg]✅  Code mode active. "
                "Gemma 4 will write production-grade Python.[/info_msg]"
            )

        elif cmd == "/context":
            self._context_stats()

        elif cmd == "/clear":
            self.conv.clear()
            self.console.print("[info_msg]✅  Conversation cleared.[/info_msg]")

        elif cmd == "/save":
            path = arg or f"gemma4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                self.conv.save(path)
                self.console.print(f"[info_msg]✅  Saved → {path}[/info_msg]")
            except Exception as exc:
                self.console.print(f"[error_msg]Save failed: {exc}[/error_msg]")

        elif cmd == "/load":
            if not arg:
                self.console.print("[error_msg]Usage: /load <file.json>[/error_msg]")
            elif not Path(arg).exists():
                self.console.print(f"[error_msg]File not found: {arg}[/error_msg]")
            else:
                try:
                    self.conv.load(arg)
                    self.console.print(
                        f"[info_msg]✅  Loaded {arg}  ({len(self.conv.messages)} messages)[/info_msg]"
                    )
                except Exception as exc:
                    self.console.print(f"[error_msg]Load failed: {exc}[/error_msg]")

        elif cmd == "/export":
            path = arg or f"gemma4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            try:
                self.conv.export_markdown(path)
                self.console.print(f"[info_msg]✅  Exported → {path}[/info_msg]")
            except Exception as exc:
                self.console.print(f"[error_msg]Export failed: {exc}[/error_msg]")

        elif cmd == "/temp":
            try:
                v = float(arg)
                if not 0.0 <= v <= 2.0:
                    raise ValueError("out of range")
                self.options["temperature"] = v
                self.console.print(f"[info_msg]✅  Temperature → {v}[/info_msg]")
            except Exception:
                self.console.print("[error_msg]Usage: /temp <0.0 – 2.0>[/error_msg]")

        elif cmd == "/ctx":
            try:
                v = int(arg)
                self.options["num_ctx"] = v
                self.console.print(f"[info_msg]✅  Context window → {v:,} tokens[/info_msg]")
            except Exception:
                self.console.print("[error_msg]Usage: /ctx <integer>  (e.g. 131072 for 128K)[/error_msg]")

        else:
            self.console.print(f"[error_msg]Unknown command: '{cmd}'.  Type /help.[/error_msg]")

        return True  # continue running

    # ── Main loop ──────────────────────────────────────────────────────────────

    def run(self) -> None:
        self.console.clear()
        self._banner()

        # Warn if Ollama is not reachable
        if not self.client.ping():
            self.console.print(Panel(
                "[error_msg]Ollama is not running![/error_msg]\n\n"
                "Start it with:\n"
                "  [bold]ollama serve[/bold]              (in a separate terminal)\n\n"
                "Then pull a model:\n"
                "  [bold]ollama pull gemma4:e4b[/bold]    (recommended starting point)\n"
                "  [bold]ollama pull gemma4:31b[/bold]    (best reasoning quality)\n\n"
                "You can still use /help and /specs while Ollama is offline.",
                title="⚠  Connection Warning",
                border_style="red",
            ))

        while True:
            try:
                tools_indicator = " [bold yellow]🔧[/bold yellow]" if self.tools_en else ""
                raw = Prompt.ask(
                    f"\n[user]You[/user] [dim_txt][{self.model_key}{tools_indicator}][/dim_txt]"
                ).strip()
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[dim_txt]Ctrl+C caught. Type [bold]/quit[/bold] to exit.[/dim_txt]")
                continue

            if not raw:
                continue

            if raw.startswith("/"):
                if not self._command(raw):
                    break
            else:
                self._chat(raw)


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry-point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        prog="gemma4-cli",
        description="Gemma 4 interactive chat CLI — all capabilities from the L5 tutorial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python gemma4_cli.py                           # default: gemma4:e4b
  python gemma4_cli.py --model 31b               # 31B dense (best quality)
  python gemma4_cli.py --model 26b --tools       # MoE + function calling agent
  python gemma4_cli.py --model e4b --ctx 131072  # full 128K context
  python gemma4_cli.py --system "Reply in Hindi" # multilingual
  python gemma4_cli.py --temp 0.2                # deterministic code gen
        """,
    )
    p.add_argument(
        "--model",  default="e4b", choices=list(MODEL_CATALOG),
        help="Model size key (default: e4b)",
    )
    p.add_argument(
        "--system", default=DEFAULT_SYSTEM_PROMPT,
        help="System prompt (default: engineer-focused)",
    )
    p.add_argument(
        "--tools", action="store_true",
        help="Enable native function calling from startup",
    )
    p.add_argument(
        "--ctx",  type=int, default=32768,
        help="Context window tokens (default: 32768 ≈ 32K)",
    )
    p.add_argument(
        "--temp", type=float, default=0.7,
        help="Generation temperature 0.0–2.0 (default: 0.7)",
    )
    p.add_argument(
        "--ollama-url", default=OLLAMA_URL,
        help=f"Ollama base URL (default: {OLLAMA_URL})",
    )

    args = p.parse_args()

    # Allow overriding Ollama URL via flag
    import gemma4_cli as _self_module  # noqa: F401
    OllamaClient.__init__.__defaults__ = (args.ollama_url,)  # type: ignore[assignment]

    cli = Gemma4CLI(
        model_key     = args.model,
        system_prompt = args.system,
        tools_enabled = args.tools,
        ctx_size      = args.ctx,
        temperature   = args.temp,
    )
    cli.run()


if __name__ == "__main__":
    main()

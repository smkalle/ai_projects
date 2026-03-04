"""Shared Gemini client initialization and helpers."""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

MODEL = "gemini-3.1-flash-lite-preview"
EMBED_MODEL = "gemini-embedding-001"

THINKING_LEVELS = {
    "minimal": types.ThinkingLevel.MINIMAL,
    "low": types.ThinkingLevel.LOW,
    "medium": types.ThinkingLevel.MEDIUM,
    "high": types.ThinkingLevel.HIGH,
}


# ── API Trace Logger ─────────────────────────────────────────────────────────

class ApiTraceLog:
    """Captures API call traces for display in the UI."""

    def __init__(self):
        self.entries: list[dict] = []

    def clear(self):
        self.entries.clear()

    def log_request(self, method: str, model: str, config_summary: dict, contents_summary: str) -> int:
        """Log an outgoing API request. Returns entry index."""
        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3],
            "method": method,
            "model": model,
            "config": config_summary,
            "contents": contents_summary,
            "status": "pending",
            "duration_ms": None,
            "response_summary": None,
            "usage": None,
            "error": None,
        }
        self.entries.append(entry)
        return len(self.entries) - 1

    def log_response(self, idx: int, duration_ms: float, usage: dict | None = None,
                     response_preview: str = "", status: str = "ok"):
        """Log a completed API response."""
        if 0 <= idx < len(self.entries):
            self.entries[idx]["status"] = status
            self.entries[idx]["duration_ms"] = round(duration_ms, 1)
            self.entries[idx]["usage"] = usage
            self.entries[idx]["response_summary"] = response_preview[:200]

    def log_error(self, idx: int, duration_ms: float, error: str):
        """Log a failed API call."""
        if 0 <= idx < len(self.entries):
            self.entries[idx]["status"] = "error"
            self.entries[idx]["duration_ms"] = round(duration_ms, 1)
            self.entries[idx]["error"] = error


# Global trace log instance
trace_log = ApiTraceLog()


def _summarize_contents(contents) -> str:
    """Create a short summary of contents for the trace log."""
    if isinstance(contents, str):
        return f'text: "{contents[:80]}{"..." if len(contents) > 80 else ""}"'
    if isinstance(contents, list):
        parts = []
        for item in contents:
            if isinstance(item, str):
                parts.append(f'text({len(item)} chars)')
            elif hasattr(item, 'format'):  # PIL Image
                parts.append(f'image({getattr(item, "size", "?")})')
            elif hasattr(item, 'mime_type'):
                parts.append(f'{item.mime_type}')
            elif hasattr(item, 'role'):  # Content object
                parts.append(f'{item.role}(...)')
            else:
                parts.append(type(item).__name__)
        return f'[{", ".join(parts)}]'
    if hasattr(contents, 'role'):
        return f'{contents.role}(...)'
    return str(type(contents).__name__)


def _summarize_config(config: types.GenerateContentConfig) -> dict:
    """Create a summary dict of config for the trace log."""
    summary = {}
    if config.max_output_tokens:
        summary["max_tokens"] = config.max_output_tokens
    if config.temperature is not None:
        summary["temperature"] = config.temperature
    if config.thinking_config:
        tc = config.thinking_config
        if tc.thinking_level:
            summary["thinking_level"] = tc.thinking_level.name if hasattr(tc.thinking_level, 'name') else str(tc.thinking_level)
        summary["include_thoughts"] = tc.include_thoughts
    if config.system_instruction:
        si = str(config.system_instruction)
        summary["system"] = si[:60] + ("..." if len(si) > 60 else "")
    if config.response_mime_type:
        summary["response_format"] = config.response_mime_type
    if config.tools:
        summary["tools"] = len(config.tools)
    return summary


def _print_trace_request(method, model, config_summary, contents_summary):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    print(f"\n{'='*70}", flush=True)
    print(f"[{ts}] >>> {method}", flush=True)
    print(f"  model:    {model}", flush=True)
    print(f"  config:   {json.dumps(config_summary, default=str)}", flush=True)
    print(f"  contents: {contents_summary}", flush=True)


def _print_trace_response(method, duration, usage=None, preview="", status="ok"):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] <<< {method}  [{status}]  {duration:.0f}ms", flush=True)
    if usage:
        print(f"  tokens:   in={usage.get('input_tokens','?')}  out={usage.get('output_tokens','?')}  think={usage.get('thoughts_tokens','?')}  total={usage.get('total_tokens','?')}", flush=True)
    if preview:
        print(f"  response: {preview[:150]}{'...' if len(preview)>150 else ''}", flush=True)
    print(f"{'='*70}\n", flush=True)


def _print_trace_error(method, duration, error):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] <<< {method}  [ERROR]  {duration:.0f}ms", flush=True)
    print(f"  error:    {error}", flush=True)
    print(f"{'='*70}\n", flush=True)


def traced_generate(client, model, contents, config):
    """Wrapper around generate_content that logs the API trace."""
    config_summary = _summarize_config(config) if config else {}
    contents_summary = _summarize_contents(contents)
    idx = trace_log.log_request("generate_content", model, config_summary, contents_summary)
    _print_trace_request("generate_content", model, config_summary, contents_summary)

    start = time.time()
    try:
        response = client.models.generate_content(model=model, contents=contents, config=config)
        duration = (time.time() - start) * 1000
        usage = get_usage(response)
        preview = response.text[:200] if response.text else "(empty)"
        trace_log.log_response(idx, duration, usage=usage, response_preview=preview)
        _print_trace_response("generate_content", duration, usage, preview)
        return response
    except Exception as e:
        duration = (time.time() - start) * 1000
        trace_log.log_error(idx, duration, str(e))
        _print_trace_error("generate_content", duration, str(e))
        raise


def traced_generate_stream(client, model, contents, config):
    """Wrapper around generate_content_stream that logs the API trace."""
    config_summary = _summarize_config(config) if config else {}
    contents_summary = _summarize_contents(contents)
    idx = trace_log.log_request("generate_content_stream", model, config_summary, contents_summary)
    _print_trace_request("generate_content_stream", model, config_summary, contents_summary)

    start = time.time()
    try:
        full_text = ""
        for chunk in client.models.generate_content_stream(model=model, contents=contents, config=config):
            if chunk.text:
                full_text += chunk.text
            yield chunk
        duration = (time.time() - start) * 1000
        trace_log.log_response(idx, duration, response_preview=full_text[:200], status="ok (streamed)")
        _print_trace_response("generate_content_stream", duration, preview=full_text[:200], status="ok (streamed)")
    except Exception as e:
        duration = (time.time() - start) * 1000
        trace_log.log_error(idx, duration, str(e))
        _print_trace_error("generate_content_stream", duration, str(e))
        raise


def traced_embed(client, model, contents, config=None):
    """Wrapper around embed_content that logs the API trace."""
    contents_summary = _summarize_contents(contents) if not isinstance(contents, list) else f"{len(contents)} texts"
    idx = trace_log.log_request("embed_content", model, {"task_type": getattr(config, 'task_type', None)} if config else {}, contents_summary)
    _print_trace_request("embed_content", model, {"task_type": getattr(config, 'task_type', None)} if config else {}, contents_summary)

    start = time.time()
    try:
        result = client.models.embed_content(model=model, contents=contents, config=config)
        duration = (time.time() - start) * 1000
        n_embeddings = len(result.embeddings)
        dims = len(result.embeddings[0].values) if result.embeddings else 0
        preview = f"{n_embeddings} embeddings, {dims} dims"
        trace_log.log_response(idx, duration, response_preview=preview)
        _print_trace_response("embed_content", duration, preview=preview)
        return result
    except Exception as e:
        duration = (time.time() - start) * 1000
        trace_log.log_error(idx, duration, str(e))
        _print_trace_error("embed_content", duration, str(e))
        raise


def get_client() -> genai.Client:
    """Initialize and return a Gemini API client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set. Add it to .env or export it.", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)


def make_config(
    thinking_level: str = "medium",
    system_instruction: str | None = None,
    max_output_tokens: int = 8192,
    temperature: float = 1.0,
    json_schema: dict | None = None,
    tools: list | None = None,
) -> types.GenerateContentConfig:
    """Build a GenerateContentConfig with common defaults."""
    kwargs: dict = {
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
        "thinking_config": types.ThinkingConfig(
            thinking_level=THINKING_LEVELS.get(thinking_level, types.ThinkingLevel.MEDIUM),
            include_thoughts=True,
        ),
    }
    if system_instruction:
        kwargs["system_instruction"] = system_instruction
    if json_schema:
        kwargs["response_mime_type"] = "application/json"
        kwargs["response_json_schema"] = json_schema
    if tools:
        kwargs["tools"] = tools
        kwargs["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=5,
        )
    return types.GenerateContentConfig(**kwargs)


def extract_response_parts(response) -> tuple[str, str]:
    """Extract thought and answer text from a response.

    Returns (thoughts, answer) tuple.
    """
    thoughts = []
    answer = []
    for part in response.candidates[0].content.parts:
        if part.thought:
            thoughts.append(part.text)
        else:
            answer.append(part.text)
    return "\n".join(thoughts), "\n".join(answer)


def get_usage(response) -> dict:
    """Extract usage metadata from a response."""
    meta = response.usage_metadata
    return {
        "input_tokens": meta.prompt_token_count,
        "output_tokens": meta.candidates_token_count,
        "thoughts_tokens": getattr(meta, "thoughts_token_count", 0) or 0,
        "total_tokens": meta.total_token_count,
    }

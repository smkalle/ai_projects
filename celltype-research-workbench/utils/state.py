"""Session state management for Streamlit app."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from utils.config import SESSIONS_DIR, REPORTS_DIR, ensure_dirs


def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "session_id": str(uuid.uuid4())[:8],
        "session_name": f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "chat_history": [],
        "workflow_results": {},
        "current_workflow": None,
        "total_tokens_used": 0,
        "total_cost": 0.0,
        "query_count": 0,
        "active_datasets": [],
        "system_health": {},
        "notifications": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_chat_message(role: str, content: str, metadata: dict | None = None):
    """Add a message to chat history."""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {},
    })


def save_session():
    """Persist current session to disk."""
    ensure_dirs()
    session_data = {
        "session_id": st.session_state.session_id,
        "session_name": st.session_state.session_name,
        "chat_history": st.session_state.chat_history,
        "workflow_results": st.session_state.workflow_results,
        "total_tokens_used": st.session_state.total_tokens_used,
        "total_cost": st.session_state.total_cost,
        "query_count": st.session_state.query_count,
        "saved_at": datetime.now().isoformat(),
    }
    path = SESSIONS_DIR / f"{st.session_state.session_id}.json"
    with open(path, "w") as f:
        json.dump(session_data, f, indent=2, default=str)
    return path


def load_session(session_id: str) -> dict:
    """Load a saved session."""
    path = SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def list_sessions() -> list[dict]:
    """List all saved sessions."""
    ensure_dirs()
    sessions = []
    for p in sorted(SESSIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(p) as f:
                data = json.load(f)
            sessions.append({
                "id": data.get("session_id", p.stem),
                "name": data.get("session_name", "Unnamed"),
                "saved_at": data.get("saved_at", "Unknown"),
                "queries": data.get("query_count", 0),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return sessions


def save_report(title: str, content: str, format: str = "md") -> Path:
    """Save a report to disk."""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{title.replace(' ', '_')[:50]}.{format}"
    path = REPORTS_DIR / filename
    with open(path, "w") as f:
        f.write(content)
    return path


def list_reports() -> list[dict]:
    """List all saved reports."""
    ensure_dirs()
    reports = []
    for p in sorted(REPORTS_DIR.glob("*.*"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.suffix in (".md", ".html", ".csv"):
            reports.append({
                "name": p.stem,
                "format": p.suffix[1:],
                "path": str(p),
                "size": f"{p.stat().st_size / 1024:.1f} KB",
                "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
    return reports

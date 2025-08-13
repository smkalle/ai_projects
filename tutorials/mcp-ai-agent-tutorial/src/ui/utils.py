"""Utility functions for the Streamlit app."""

import asyncio
import threading
import streamlit as st
from typing import Any, Callable

def run_async(coro) -> Any:
    """Run async function in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new event loop in thread
            result = {}

            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result["value"] = new_loop.run_until_complete(coro)
                except Exception as e:
                    result["error"] = str(e)
                finally:
                    new_loop.close()

            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()

            if "error" in result:
                raise Exception(result["error"])
            return result.get("value")
        else:
            return loop.run_until_complete(coro)
    except Exception as e:
        st.error(f"Async execution error: {e}")
        return None

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

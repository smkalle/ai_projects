"""Reports & Sessions management page."""

import streamlit as st
from pathlib import Path

from utils.state import list_sessions, list_reports, load_session, save_session
from components.design_system import render_empty_state


def render_reports():
    """Render the reports and sessions management page."""
    st.title("📝 Reports & Sessions")
    st.caption("Manage saved research sessions and generated reports.")

    tab_sessions, tab_reports = st.tabs(["Sessions", "Reports"])

    with tab_sessions:
        _render_sessions()

    with tab_reports:
        _render_reports()


def _render_sessions():
    """Manage research sessions."""
    st.subheader("Saved Sessions")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Save current session", type="primary", use_container_width=True):
            path = save_session()
            st.success("Session saved!")

    sessions = list_sessions()

    if not sessions:
        render_empty_state(
            headline="No saved sessions yet",
            description="Sessions are auto-saved as you work. You can also save manually using the button above.",
            icon="🔄",
        )
        return

    for session in sessions:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{session['name']}**")
                st.caption(f"ID: {session['id']} · Saved: {session['saved_at']}")
            with col2:
                st.metric("Queries", session["queries"])
            with col3:
                if st.button("Load", key=f"load_{session['id']}"):
                    data = load_session(session["id"])
                    if data:
                        st.session_state.session_id = data.get("session_id", session["id"])
                        st.session_state.session_name = data.get("session_name", "Loaded Session")
                        st.session_state.chat_history = data.get("chat_history", [])
                        st.session_state.workflow_results = data.get("workflow_results", {})
                        st.session_state.total_tokens_used = data.get("total_tokens_used", 0)
                        st.session_state.total_cost = data.get("total_cost", 0.0)
                        st.session_state.query_count = data.get("query_count", 0)
                        st.success(f"Session '{session['name']}' loaded!")
                        st.rerun()

    st.divider()
    st.markdown("#### Tips")
    st.markdown(
        "- Sessions are auto-saved after each agent query\n"
        "- Use the chat interface (`/agents 3 query`) for parallel agent runs\n"
        "- Each workflow module saves results to the current session\n"
        "- Resume any session by clicking **Load**"
    )


def _render_reports():
    """Manage generated reports."""
    st.subheader("Generated Reports")

    reports = list_reports()

    if not reports:
        render_empty_state(
            headline="No reports generated yet",
            description="Run any workflow to automatically generate a report. Reports are saved as Markdown or HTML.",
            icon="📄",
        )
        return

    for report in reports:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{report['name']}**")
                st.caption(f"Format: {report['format'].upper()} · Size: {report['size']} · Modified: {report['modified']}")
            with col2:
                path = Path(report["path"])
                if path.exists():
                    content = path.read_text()
                    st.download_button(
                        "Download",
                        content,
                        f"{report['name']}.{report['format']}",
                        key=f"dl_{report['name']}",
                    )
            with col3:
                if st.button("View", key=f"view_{report['name']}"):
                    st.session_state["_view_report"] = report["path"]

    # Report viewer
    view_path = st.session_state.get("_view_report")
    if view_path:
        st.divider()
        st.subheader("Report Viewer")
        path = Path(view_path)
        if path.exists():
            content = path.read_text()
            if path.suffix == ".md":
                st.markdown(content)
            elif path.suffix == ".html":
                st.components.v1.html(content, height=600, scrolling=True)
            else:
                st.code(content)
        if st.button("Close viewer"):
            del st.session_state["_view_report"]
            st.rerun()

    st.divider()

    # CLI report commands
    st.markdown("#### CLI Report Commands")
    st.code("""# List all reports
ct report list

# Publish latest as self-contained HTML
ct report publish

# Open latest report in browser
ct report show

# Export session as Jupyter notebook
/export notebook""", language="bash")

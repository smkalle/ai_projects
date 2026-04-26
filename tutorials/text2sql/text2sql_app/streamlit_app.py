"""Streamlit app — Iteration 3: TextSQL engine + Query tab + Admin tab."""
import re
import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime

# ── Patch text2sql to handle Anthropic extended streaming response ──────────
from text2sql.generate import SQLGenerator

_orig_ask = SQLGenerator.ask

def _extract_text_from_content(content):
    """Extract displayable text from AIMessage.content of any type."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                t = block.get("type")
                if t == "text":
                    parts.append(block.get("text", ""))
                elif t == "thinking":
                    parts.append("[THINKING] " + block.get("thinking", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    if isinstance(content, dict):
        return content.get("text", content.get("thinking", str(content)))
    return str(content)

def _extract_text_for_sql_extraction(content):
    """Extract ONLY text blocks (no thinking) for SQL parsing."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return str(content)

def _extract_sql_from_response(text):
    if not text or not text.strip():
        return "", ""
    match = re.search(r'```(?:sql)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        sql = match.group(1).strip()
        commentary = re.sub(r'```(?:sql)?\s*\n?.*?\n?```', '', text, flags=re.DOTALL).strip()
        return sql, commentary
    stripped = re.sub(r'\[THINKING\][^\n]*\n?', '', text, flags=re.DOTALL).strip()
    stripped = re.sub(r'\*\*[^*]+\*\*', '', stripped).strip()
    stripped = re.sub(r'\|.+\|', '', stripped).strip()
    stripped = re.sub(r'\n\s*[-*•]\s+', '\n', stripped).strip()
    stripped = re.sub(r'\n{3,}', '\n\n', stripped).strip()
    match = re.search(r'((?:WITH\b|SELECT\b).*)', stripped, re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
        if ';' in sql:
            sql = sql[:sql.rindex(';') + 1]
        return sql, ""
    return "", text.strip()

def _patched_ask(self, question, max_rows=None):
    """Patched ask that collects thinking + tool-call log into session_state."""
    messages = self.agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )["messages"]

    thinking_log = []
    tool_log = []
    tool_calls_made = 0
    args_by_id = {}
    last_ai_timestamp = 0.0

    for msg in messages:
        resp_meta = getattr(msg, "response_metadata", {}) if hasattr(msg, "response_metadata") else {}
        msg_time = resp_meta.get("timestamp", 0)
        usage = resp_meta.get("usage", {})
        if usage and self.tracer:
            self.tracer.record_token_usage(usage.get("input_tokens", 0), usage.get("output_tokens", 0))

        if hasattr(msg, "tool_calls") and msg.tool_calls:
            if self.tracer and hasattr(msg, "content"):
                content = msg.content
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            t2 = block.get("text", "")
                            if t2.strip():
                                self.tracer.record_reasoning(t2)
                elif isinstance(content, str) and content.strip():
                    self.tracer.record_reasoning(content)
            for tc in msg.tool_calls:
                tool_calls_made += 1
                args_by_id[tc["id"]] = tc["args"]
                tool_log.append({"step": tool_calls_made, "tool": tc.get("name", "?"),
                                "args": tc.get("args", {}), "type": "call"})
            if msg_time:
                last_ai_timestamp = msg_time

        elif hasattr(msg, "content") and hasattr(msg, "type") and getattr(msg, "type", None) == "ai":
            content = msg.content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "thinking":
                        thinking = block.get("thinking", "").strip()
                        if thinking:
                            thinking_log.append(thinking)
                            if self.tracer:
                                self.tracer.record_reasoning("[thinking] " + thinking)
                    elif isinstance(block, dict) and block.get("type") == "text":
                        t2 = block.get("text", "").strip()
                        if t2 and self.tracer:
                            self.tracer.record_reasoning(t2)
            elif isinstance(content, str) and content.strip():
                thinking_log.append(content)
                if self.tracer:
                    self.tracer.record_reasoning(content)
            if msg_time:
                last_ai_timestamp = msg_time

        if hasattr(msg, "name") and hasattr(msg, "tool_call_id"):
            tc_id = getattr(msg, "tool_call_id", None)
            if self.tracer and last_ai_timestamp > 0:
                self.tracer._last_event_time = self.tracer._last_event_time or last_ai_timestamp
                self.tracer._tool_start_time = last_ai_timestamp
            args = args_by_id.get(tc_id, {})
            tool_result = str(getattr(msg, "content", ""))
            tool_log.append({"step": tool_calls_made, "tool": getattr(msg, "name", "?"),
                            "args": args, "result": tool_result[:200], "type": "result"})

    final_sql = ""
    commentary = ""
    error = None
    if messages:
        last_msg = messages[-1]
        final_text = _extract_text_for_sql_extraction(
            last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        )
        final_sql, commentary = _extract_sql_from_response(final_text)
        if not final_sql:
            final_text = _extract_text_from_content(
                last_msg.content if hasattr(last_msg, "content") else str(last_msg)
            )
            final_sql, commentary = _extract_sql_from_response(final_text)

    if not final_sql:
        last_text = _extract_text_from_content(messages[-1].content if messages else "")
        error = f"No SQL produced. Response: {last_text[:500]}"

    data = []
    sql_executed = ""
    if final_sql and not error:
        try:
            rows = self.db.execute(final_sql)
            if max_rows is not None:
                rows = rows[:max_rows]
            data = rows
            sql_executed = final_sql
            tool_log.append({"step": tool_calls_made + 1, "tool": "execute_sql",
                             "args": {"sql": final_sql[:200]}, "result": f"{len(rows)} rows", "type": "result"})
        except Exception as e:
            error = f"Final execution failed: {e}"
            tool_log.append({"step": tool_calls_made + 1, "tool": "execute_sql",
                             "args": {"sql": final_sql[:200]}, "result": str(e), "type": "error"})
    elif error:
        tool_log.append({"step": tool_calls_made + 1, "tool": "final_check",
                         "args": {}, "result": error, "type": "error"})

    if self.tracer:
        self.tracer.end_query(sql=final_sql, success=error is None and final_sql != "",
                              error=error, iterations=tool_calls_made)

    input_tokens = output_tokens = 0
    if self.tracer and self.tracer.traces:
        lt = self.tracer.traces[-1]
        input_tokens = lt.input_tokens
        output_tokens = lt.output_tokens

    from text2sql.generate import SQLResult
    result = SQLResult(
        question=question, sql=final_sql, data=data, error=error,
        commentary=commentary, tool_calls_made=tool_calls_made,
        iterations=tool_calls_made, input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
    result._thinking_log = thinking_log
    result._tool_log = tool_log
    result._sql_executed = sql_executed
    return result

SQLGenerator.ask = _patched_ask

# ── Streamlit app ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="WardOps SQL", page_icon="🏥", layout="wide")

DEMO_DB = "/tmp/wardops_demo.db"

from init_db import init_db
init_db()

# ── Shared state helpers ─────────────────────────────────────────────────────

def get_engine():
    """Lazily init and return the TextSQL engine."""
    if "engine_done" not in st.session_state:
        api_key = __import__("os").getenv("ANTHROPIC_API_KEY", "")
        if api_key:
            try:
                from text2sql import TextSQL
                engine = TextSQL(
                    f"sqlite:///{DEMO_DB}",
                    model="anthropic:claude-sonnet-4-6",
                    api_key=api_key,
                )
                st.session_state["engine"] = engine
                st.session_state["engine_ready"] = True
            except Exception as e:
                st.session_state["engine_ready"] = False
                st.session_state["engine_error"] = str(e)
        else:
            st.session_state["engine_ready"] = False
            st.session_state["engine_error"] = (
                "⚠️ ANTHROPIC_API_KEY not set — agentic engine disabled. "
                "Set ANTHROPIC_API_KEY and refresh to enable."
            )
        st.session_state["engine_done"] = True
        st.session_state["last_result"] = None
        st.session_state["thinking_log"] = []
        st.session_state["tool_log"] = []
    return st.session_state.get("engine"), st.session_state.get("engine_ready", False)


def run_query(question):
    """Run a query and store result + logs in session state."""
    engine, ready = get_engine()
    if not ready:
        return
    with st.spinner("🤖 Agent exploring schema and reasoning…"):
        try:
            result = engine.ask(question)
            st.session_state["last_result"] = result
            st.session_state["thinking_log"] = getattr(result, "_thinking_log", [])
            st.session_state["tool_log"] = getattr(result, "_tool_log", [])
        except Exception as e:
            st.error(f"Query failed: {e}")
            st.session_state["last_result"] = None
            st.session_state["thinking_log"] = []
            st.session_state["tool_log"] = []


# ── Sidebar debug panels ──────────────────────────────────────────────────────

with st.sidebar:
    st.header("🔍 Debug Panel")
    debug_mode = st.toggle("Show debug panels", value=False)

    st.divider()
    st.subheader("🧠 Thinking Log")
    thinking_placeholder = st.container()
    st.divider()
    st.subheader("📡 Server Log")
    server_placeholder = st.container()

st.title("🏥 WardOps")
st.caption("Natural Language Query — Hospital Operations")

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_query, tab_admin = st.tabs(["💬 Query", "🛠️ Admin"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — QUERY
# ══════════════════════════════════════════════════════════════════════════════

with tab_query:
    # --- Input ---
    user_query = st.text_input(
        "Ask a question:",
        placeholder="e.g. Which nurses in ICU are on overtime this week?",
        key="nl_query",
    )
    st.divider()

    # --- Run query ---
    if user_query:
        run_query(user_query)

    # --- Display result ---
    if st.session_state.get("last_result"):
        result = st.session_state["last_result"]

        if result.error and not result.sql:
            st.error(result.error)
        else:
            st.success(f"Query complete — {result.iterations} step{'s' if result.iterations != 1 else ''}")

        meta_col, sql_col = st.columns([1, 4])
        with meta_col:
            st.metric("Iterations", result.iterations)
            confidence = "high" if result.data and result.sql else ("low" if not result.sql else "medium")
            st.metric("Confidence", confidence)
            if result.input_tokens or result.output_tokens:
                st.caption(f"Tokens: {result.input_tokens} in / {result.output_tokens} out")

        with sql_col:
            st.markdown("**Generated SQL**")
            if result.sql:
                st.code(result.sql, language="sql", wrap_lines=True)
            else:
                st.code("—", language="sql")

        if result.data:
            st.dataframe(result.data)
        elif result.sql:
            st.info("Query returned 0 rows.")
        else:
            st.info("No results returned.")
    else:
        st.info("⬆️ Type a question above to query the database.")

    # --- Debug panels ---
    thinking_log = st.session_state.get("thinking_log", [])
    tool_log = st.session_state.get("tool_log", [])

    with thinking_placeholder:
        if debug_mode:
            if thinking_log:
                for i, thought in enumerate(thinking_log):
                    with st.expander(f"🧠 Thinking {i+1}/{len(thinking_log)}", expanded=(i == len(thinking_log)-1)):
                        st.text(thought)
            else:
                st.caption("No thinking log yet — run a query.")
        else:
            st.caption("Debug off")

    with server_placeholder:
        if debug_mode:
            if tool_log:
                for entry in tool_log:
                    step = entry.get("step", "?")
                    tool = entry.get("tool", "?")
                    etype = entry.get("type", "call")
                    if etype == "call":
                        st.markdown(f"**Step {step} → `{tool}`**")
                        args = entry.get("args", {})
                        if args:
                            for k, v in args.items():
                                st.caption(f"  `{k}`: {str(v)[:120]}")
                    elif etype == "result":
                        result_txt = entry.get("result", "")
                        color = "🔵" if "error" in result_txt.lower() else "🟢"
                        st.markdown(f"  {color} Result: {str(result_txt)[:150]}")
                    elif etype == "error":
                        st.markdown(f"  🔴 Error: {str(entry.get('result',''))[:150]}")
            else:
                st.caption("No server log yet — run a query.")
        else:
            st.caption("Debug off")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ADMIN
# ══════════════════════════════════════════════════════════════════════════════

VIEWS = [
    "v_current_shift_roster",
    "v_nurse_patient_ratio",
    "v_float_pool_available",
    "v_overtime_flags",
    "v_bed_census",
    "v_expected_discharges",
    "v_housekeeping_queue",
    "v_ed_boarding",
    "v_low_stock_items",
    "v_expiry_alerts",
    "v_consumption_anomalies",
]


def _read_view(view_name, limit=500):
    conn = sqlite3.connect(DEMO_DB)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {view_name} LIMIT {limit}", conn)
    except Exception as e:
        df = pd.DataFrame({"error": [str(e)]})
    finally:
        conn.close()
    return df


def _count_view(view_name):
    conn = sqlite3.connect(DEMO_DB)
    try:
        cur = conn.execute(f"SELECT COUNT(*) FROM {view_name}")
        count = cur.fetchone()[0]
    except Exception:
        count = -1
    finally:
        conn.close()
    return count


with tab_admin:
    st.subheader("📋 Schema Monitor — Admin Panel")

    # ── 1. Schema overview cards ──────────────────────────────────────────
    st.markdown("**Database Views & Row Counts**")
    counts = []
    for v in VIEWS:
        c = _count_view(v)
        counts.append({"view": v, "rows": c})
    df_counts = pd.DataFrame(counts)
    st.dataframe(df_counts, use_container_width=True, hide_index=True)

    st.divider()

    # ── 2. Explore schema ─────────────────────────────────────────────────
    st.subheader("🔍 Explore Schema — Ask in Natural Language")
    st.caption("Ask questions about the schema: 'What columns does v_overtime_flags have?'")
    admin_nl_query = st.text_input(
        "Admin NL query:",
        placeholder="e.g. What tables track nurse scheduling? or Show me the structure of the overtime view",
        key="admin_nl_query",
    )

    if admin_nl_query:
        with st.spinner("🤖 Agent exploring schema…"):
            engine, ready = get_engine()
            if ready:
                try:
                    result = engine.ask(admin_nl_query)
                    st.session_state["admin_last_result"] = result
                except Exception as e:
                    st.error(f"Schema query failed: {e}")
                    st.session_state["admin_last_result"] = None
            else:
                st.warning("Engine not ready — check API key.")

    # Show admin NL result
    if st.session_state.get("admin_last_result"):
        result = st.session_state["admin_last_result"]
        st.markdown("**Generated SQL**")
        st.code(result.sql or "—", language="sql", wrap_lines=True)
        if result.data:
            st.dataframe(result.data)
        elif result.error and not result.sql:
            st.error(result.error)

    st.divider()

    # ── 3. Direct view browser ────────────────────────────────────────────
    st.subheader("📊 Direct View Browser")
    selected_view = st.selectbox("Select a view to browse:", ["(select a view)"] + VIEWS)

    if selected_view != "(select a view)":
        df = _read_view(selected_view)
        st.markdown(f"**{selected_view}** — {len(df)} rows × {len(df.columns)} columns")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Column summary
        with st.expander("📌 Column Schema"):
            col_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                nulls = df[col].isna().sum()
                distinct = df[col].nunique()
                sample = str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else "—"
                col_info.append({
                    "column": col,
                    "type": dtype,
                    "nullable": nulls > 0,
                    "distinct": distinct,
                    "sample": sample[:60],
                })
            st.dataframe(pd.DataFrame(col_info), use_container_width=True, hide_index=True)

    st.divider()

    # ── 4. SQL Translation & Verification ─────────────────────────────────
    st.subheader("🔄 SQL Translation & Verification")
    st.caption("Paste a natural language question, run the agent, then verify the generated SQL manually.")
    verify_query = st.text_input(
        "NL question for verification:",
        placeholder="e.g. How many nurses in ICU exceed 44 hours this week?",
        key="verify_nl_query",
    )

    if st.button("▶️ Plan & Execute", key="btn_verify"):
        engine, ready = get_engine()
        if ready and verify_query:
            with st.spinner("🤖 Planning…"):
                result = engine.ask(verify_query)
                st.session_state["verify_result"] = result
        elif not ready:
            st.warning("Engine not ready — check ANTHROPIC_API_KEY.")
        elif not verify_query:
            st.info("Enter a question first.")

    if st.session_state.get("verify_result"):
        result = st.session_state["verify_result"]

        # Plan step
        plan_col, verify_col = st.columns([1, 1])

        with plan_col:
            st.markdown("**📝 Plan**")
            if result._tool_log:
                for entry in result._tool_log:
                    if entry.get("type") == "call":
                        st.markdown(f"`Step {entry['step']}` → `{entry['tool']}`")
                        for k, v in entry.get("args", {}).items():
                            st.caption(f"  `{k}`: {str(v)[:100]}")
            else:
                st.caption("No plan steps captured.")

        with verify_col:
            st.markdown("**✅ Verification**")
            if result.sql:
                st.code(result.sql, language="sql", wrap_lines=True)
            else:
                st.code("—", language="sql")

        # Results
        if result.data:
            st.markdown("**📊 Results**")
            st.dataframe(result.data)

            # Quick sanity checks
            st.markdown("**🩺 Quick Sanity Checks**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Row count", len(result.data))
            with col_b:
                st.metric("Iterations", result.iterations)

            if isinstance(result.data, list) and len(result.data) > 0:
                first_row = result.data[0]
                if isinstance(first_row, dict):
                    with st.expander("🔎 Sample Row (first record)"):
                        for k, v in first_row.items():
                            st.markdown(f"  `{k}`: {v}")
        elif result.error:
            st.error(f"Error: {result.error}")
        else:
            st.info("No results returned.")

    st.divider()

    # ── 5. History / audit log ────────────────────────────────────────────
    st.subheader("📜 Query History (Session)")
    history = st.session_state.get("query_history", [])
    if history:
        hist_df = pd.DataFrame(history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
    else:
        st.info("No queries run in this session yet. Run a query in the **Query** tab to see history here.")

    st.divider()

    # ── 6. Scenarios / seed patterns ──────────────────────────────────────
    st.subheader("🧠 Scenarios Seed Patterns (from BRD)")
    scenarios = [
        ("nurse-to-patient ratio safe threshold", "ICU: ≤1:2; Med-Surg: ≤1:4; Step-down: ≤1:3"),
        ("float pool eligibility", "Must have matching skill tag for target ward"),
        ("overtime threshold", "Weekly limit = 48 hrs; escalation at 44 hrs"),
        ("mandatory rest period", "Min 11 hours between shifts per labour code"),
        ("night shift definition", "21:00–07:00; counts as one shift for ratio calc"),
        ("expected discharge window", "Use expected_discharge_dt ± 2 hours as range"),
        ("housekeeping SLA", "Turnaround target = 90 min; escalation at 120 min"),
        ("boarding patient definition", "ED patient awaiting inpatient bed > 4 hours"),
        ("isolation bed handling", "Isolation beds excluded from general availability pool"),
        ("reorder point logic", "Trigger when current_qty < reorder_point AND no open PO"),
        ("expiry urgency tiers", "Critical: ≤7 days; Warning: 8–30 days; Watch: 31–90 days"),
        ("consumption anomaly threshold", "Flag if delta_pct > 30% week-over-week"),
        ("ward scope injection", "All queries filter by session ward unless role = nurse_manager"),
        ("shift today definition", "Current shift = row where shift_start ≤ NOW() ≤ shift_end"),
        ("data freshness caveat", "Advise if v_bed_census last_updated > 30 min ago"),
    ]
    df_scenarios = pd.DataFrame(scenarios, columns=["scenario_title", "key_business_logic"])
    with st.expander("📂 View all 15 seed scenarios"):
        st.dataframe(df_scenarios, use_container_width=True, hide_index=True)

    st.divider()

    # ── 7. Database health ────────────────────────────────────────────────
    st.subheader("💾 Database Health")
    health = []
    for v in VIEWS:
        count = _count_view(v)
        health.append({"view": v, "row_count": count, "status": "✅" if count >= 0 else "❌"})
    df_health = pd.DataFrame(health)
    st.dataframe(df_health, use_container_width=True, hide_index=True)

    conn = sqlite3.connect(DEMO_DB)
    cur = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    total_tables = cur.fetchone()[0]
    cur = conn.execute("PRAGMA page_count")
    page_count = cur.fetchone()[0]
    cur = conn.execute("PRAGMA page_size")
    page_size = cur.fetchone()[0]
    db_size_kb = (page_count * page_size) / 1024
    conn.close()

    health_meta_col1, health_meta_col2, health_meta_col3 = st.columns(3)
    with health_meta_col1:
        st.metric("Total tables", total_tables)
    with health_meta_col2:
        st.metric("Total views", len(VIEWS))
    with health_meta_col3:
        st.metric("DB size", f"{db_size_kb:.1f} KB")

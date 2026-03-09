"""
HR Onboarding Workbench — MVP
Streamlit + SQLite self-serve dashboard for HR teams.
"""

import streamlit as st
import anthropic
from datetime import date, timedelta
from pathlib import Path
import zipfile, io, json

import db

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="HR Onboarding Workbench",
    page_icon="👥",
    layout="wide",
)

SKILL_DIR = Path("/root/.claude/skills/hr-onboarding-manager")

# ── Init DB ───────────────────────────────────────────────────────────────────

db.init_db()

# ── Sidebar Nav ───────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("👥 HR Onboarding")
    st.caption("Workbench MVP")
    st.divider()
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "📋 Pipeline", "📄 Plan Viewer", "➕ New Hire", "🔧 Workbench"],
        label_visibility="collapsed",
    )
    st.divider()
    stats = db.get_stats()
    st.metric("Total Hires",       stats["total_hires"])
    st.metric("Starting This Week", stats["starting_week"])
    st.metric("🔴 Open Critical",   stats["open_critical"],
              delta=None if stats["open_critical"] == 0 else f"needs action",
              delta_color="inverse")
    st.metric("Plans Generated",    stats["plans_generated"])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════

if page == "📊 Dashboard":
    st.title("📊 Dashboard")

    # ── KPI row ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Hires",        stats["total_hires"])
    k2.metric("Starting This Week", stats["starting_week"],
              help="Start date within next 7 days")
    k3.metric("🔴 Open Critical Flags", stats["open_critical"])
    k4.metric("Plans Generated",    stats["plans_generated"])

    st.divider()

    hires = db.get_all_hires()
    if not hires:
        st.info("No hires yet. Go to **🔧 Workbench** to seed mock data or **➕ New Hire** to add one.")
        st.stop()

    # ── Upcoming Starts ──
    st.subheader("📅 Upcoming Start Dates")
    today = date.today()
    upcoming = [
        h for h in hires
        if h["start_date"] >= today.isoformat()
    ][:8]

    if upcoming:
        cols = st.columns(min(len(upcoming), 4))
        for i, h in enumerate(upcoming):
            col = cols[i % 4]
            start = date.fromisoformat(h["start_date"])
            days  = (start - today).days
            label = (
                "🚨 TODAY"    if days == 0 else
                f"🟠 {days}d"  if days <= 5 else
                f"🟡 {days}d"  if days <= 14 else
                f"🟢 {days}d"
            )
            col.metric(
                label=h["name"],
                value=h["title"],
                delta=label,
                delta_color="off",
            )
    else:
        st.info("No upcoming starts.")

    st.divider()

    # ── Compliance Alerts ──
    st.subheader("⚑ Open Compliance Flags")
    any_flags = False
    for h in hires:
        flags = [f for f in db.get_flags(h["id"]) if not f["resolved"]]
        criticals = [f for f in flags if f["severity"] == "critical"]
        if criticals:
            any_flags = True
            with st.expander(f"🔴 **{h['name']}** — {h['title']} · {len(criticals)} critical"):
                for f in criticals:
                    st.error(f"🔴 {f['description']}")
                    if st.button(f"Resolve", key=f"res_{f['id']}"):
                        db.resolve_flag(f["id"])
                        st.rerun()
    if not any_flags:
        st.success("✅ No open critical compliance flags.")

    st.divider()

    # ── Milestone Checkins Due ──
    st.subheader("🗓️ Milestone Checkins Due")
    due_rows = []
    for h in hires:
        start = date.fromisoformat(h["start_date"])
        checkins = db.get_checkins(h["id"])
        for ci in checkins:
            due_date = start + timedelta(days=ci["day_milestone"])
            if ci["status"] == "pending" and due_date <= today + timedelta(days=3):
                overdue = (today - due_date).days
                due_rows.append({
                    "Hire": h["name"], "Role": h["title"],
                    "Milestone": f"Day {ci['day_milestone']}",
                    "Due": due_date.isoformat(),
                    "Status": "🔴 Overdue" if overdue > 0 else "🟡 Due Soon",
                })
    if due_rows:
        st.dataframe(due_rows, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No checkins due in the next 3 days.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Pipeline
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📋 Pipeline":
    st.title("📋 Onboarding Pipeline")

    hires = db.get_all_hires()
    if not hires:
        st.info("No hires yet. Seed mock data in **🔧 Workbench** or add a hire.")
        st.stop()

    today = date.today()

    # Build display table
    rows = []
    for h in hires:
        start = date.fromisoformat(h["start_date"])
        days  = (start - today).days
        if days > 0:
            timeline = f"🟢 In {days}d" if days > 14 else f"🟡 In {days}d" if days > 5 else f"🔴 In {days}d"
        elif days == 0:
            timeline = "🚨 TODAY"
        else:
            timeline = f"Day {abs(days)}"

        rows.append({
            "Name":       h["name"],
            "Title":      h["title"],
            "Dept":       h["department"],
            "Start":      h["start_date"],
            "Timeline":   timeline,
            "Work":       h["work_type"],
            "State":      h["state"],
            "Status":     h["status"].title(),
            "Plan":       f"✅ {h['plan_sections']}s" if h["plan_sections"] > 0 else "⏳ None",
            "Flags":      f"🔴 {h['open_critical']}" if h["open_critical"] else (f"⚑ {h['total_flags']}" if h["total_flags"] else "—"),
            "id":         h["id"],
        })

    # Filter
    col_f1, col_f2, col_f3 = st.columns(3)
    dept_filter   = col_f1.selectbox("Department", ["All"] + sorted({r["Dept"] for r in rows}))
    status_filter = col_f2.selectbox("Status",     ["All", "Pending", "In_progress", "Complete"])
    work_filter   = col_f3.selectbox("Work Type",  ["All", "Hybrid", "On-site", "Remote"])

    filtered = rows
    if dept_filter   != "All": filtered = [r for r in filtered if r["Dept"]   == dept_filter]
    if status_filter != "All": filtered = [r for r in filtered if r["Status"].lower() == status_filter.lower()]
    if work_filter   != "All": filtered = [r for r in filtered if r["Work"]   == work_filter]

    st.caption(f"Showing {len(filtered)} of {len(rows)} hires")

    display_cols = ["Name", "Title", "Dept", "Start", "Timeline", "Work", "State", "Status", "Plan", "Flags"]
    st.dataframe(
        [{k: r[k] for k in display_cols} for r in filtered],
        use_container_width=True,
        hide_index=True,
    )

    # Quick actions
    st.divider()
    st.subheader("Quick Actions")
    sel_name = st.selectbox("Select hire", [r["Name"] for r in rows])
    sel_hire = next((h for h in hires if h["name"] == sel_name), None)

    if sel_hire:
        c1, c2, c3, c4 = st.columns(4)
        new_status = c1.selectbox("Set Status", ["pending", "in_progress", "complete"],
                                   index=["pending", "in_progress", "complete"].index(sel_hire["status"]))
        if c2.button("Update Status"):
            db.update_hire_status(sel_hire["id"], new_status)
            st.success(f"Updated {sel_name} → {new_status}")
            st.rerun()
        if c3.button("View Plan →"):
            st.session_state["view_hire_id"] = sel_hire["id"]
            st.info("Go to 📄 Plan Viewer")
        if c4.button("🗑️ Delete Hire", type="secondary"):
            db.delete_hire(sel_hire["id"])
            st.success(f"Deleted {sel_name}")
            st.rerun()

    # Checkin tracker
    if sel_hire:
        st.divider()
        st.subheader(f"Milestones — {sel_hire['name']}")
        start    = date.fromisoformat(sel_hire["start_date"])
        checkins = db.get_checkins(sel_hire["id"])
        ci_cols  = st.columns(len(checkins))
        for i, ci in enumerate(checkins):
            due = start + timedelta(days=ci["day_milestone"])
            with ci_cols[i]:
                icon = "✅" if ci["status"] == "complete" else ("🔴" if due < today and ci["status"] == "pending" else "⏳")
                st.metric(f"Day {ci['day_milestone']}", icon, delta=due.isoformat(), delta_color="off")
                if ci["status"] != "complete":
                    if st.button("Mark Done", key=f"ci_{ci['id']}"):
                        db.update_checkin(ci["id"], "complete")
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Plan Viewer
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📄 Plan Viewer":
    st.title("📄 Plan Viewer")

    hires = db.get_all_hires()
    if not hires:
        st.info("No hires yet.")
        st.stop()

    # Hire selector — honour session state from Pipeline page
    default_id = st.session_state.get("view_hire_id")
    hire_names = [h["name"] for h in hires]
    default_idx = next((i for i, h in enumerate(hires) if h["id"] == default_id), 0)
    sel_name  = st.selectbox("Select hire", hire_names, index=default_idx)
    sel_hire  = next(h for h in hires if h["name"] == sel_name)
    hire_id   = sel_hire["id"]

    # Metadata strip
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Role",        sel_hire["title"])
    m2.metric("Department",  sel_hire["department"])
    m3.metric("Start Date",  sel_hire["start_date"])
    m4.metric("Work Type",   sel_hire["work_type"])

    st.divider()

    plans = db.get_plans(hire_id)

    if plans:
        # Phase selector tabs
        phase_names = [p["phase"] for p in plans]
        tabs = st.tabs(phase_names)
        for tab, plan in zip(tabs, plans):
            with tab:
                st.markdown(plan["content"])

        # Download buttons
        st.divider()
        full_text  = "\n\n---\n\n".join(
            f"# {p['phase']}\n\n{p['content']}" for p in plans
        )
        name_slug  = sel_hire["name"].lower().replace(" ", "_")

        # Zip package
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{name_slug}_onboarding_plan.md", full_text)
            for p in plans:
                safe = p["phase"].lower().replace(":", "").replace(" ", "_").strip("_")
                zf.writestr(f"phases/{safe}.md", p["content"])
            for dest, src in [
                ("templates/it-provisioning-checklist.md", "assets/it-provisioning-checklist.md"),
                ("templates/buddy-assignment-form.md",     "assets/buddy-assignment-form.md"),
                ("templates/30-day-checkin-template.md",   "assets/30-day-checkin-template.md"),
            ]:
                p_path = SKILL_DIR / src
                if p_path.exists():
                    zf.writestr(dest, p_path.read_text())
            zf.writestr("hire_info.json", json.dumps(dict(sel_hire), indent=2))

        dl1, dl2 = st.columns(2)
        dl1.download_button(
            "📦 Download Package (.zip)",
            data=buf.getvalue(),
            file_name=f"{name_slug}_onboarding_package.zip",
            mime="application/zip",
            type="primary",
        )
        dl2.download_button(
            "📄 Download Plan (.md)",
            data=full_text.encode(),
            file_name=f"{name_slug}_onboarding_plan.md",
            mime="text/markdown",
        )

    else:
        st.warning("No plan generated yet for this hire.")

    # Compliance flags
    flags = db.get_flags(hire_id)
    if flags:
        st.divider()
        st.subheader("⚑ Compliance Flags")
        for f in flags:
            resolved = f["resolved"]
            if f["severity"] == "critical":
                fn = st.error   if not resolved else st.success
            elif f["severity"] == "warning":
                fn = st.warning if not resolved else st.success
            else:
                fn = st.info
            prefix = "~~" if resolved else ""
            suffix = "~~ ✅ Resolved" if resolved else ""
            fn(f"{'🔴' if f['severity']=='critical' else '🟡' if f['severity']=='warning' else '🔵'} "
               f"{prefix}{f['description']}{suffix}")
            if not resolved:
                if st.button("Resolve", key=f"res_pv_{f['id']}"):
                    db.resolve_flag(f["id"])
                    st.rerun()

    # Generate real plan via agent
    st.divider()
    with st.expander("⚙️ Generate / Regenerate Plan with Claude Agent"):
        st.caption("Calls Claude Opus 4.6 — requires ANTHROPIC_API_KEY")
        if st.button("🤖 Generate Real Plan", type="primary"):
            _generate_plan_for_hire(sel_hire, hire_id)
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: New Hire
# ══════════════════════════════════════════════════════════════════════════════

elif page == "➕ New Hire":
    st.title("➕ Add New Hire")

    with st.form("new_hire_form"):
        c1, c2 = st.columns(2)
        name       = c1.text_input("Full Name *",         placeholder="Jane Smith")
        title      = c2.text_input("Job Title *",          placeholder="Software Engineer")
        department = c1.text_input("Department *",         placeholder="Engineering")
        state      = c2.text_input("State of Employment *", placeholder="California")
        start_date = c1.date_input("Start Date *",         min_value=date.today())
        work_type  = c2.selectbox("Work Type *",           ["Hybrid", "On-site", "Remote"])
        buddy      = c1.radio("Buddy/Mentor Program?",     ["Yes", "No"], horizontal=True)
        hris       = c2.text_input("HRIS System",          placeholder="BambooHR, Workday…")

        col_sub1, col_sub2 = st.columns(2)
        save_only   = col_sub1.form_submit_button("💾 Save (no plan)", use_container_width=True)
        save_and_gen = col_sub2.form_submit_button("🤖 Save + Generate Plan", type="primary", use_container_width=True)

    required = {"Full Name": name, "Job Title": title, "Department": department, "State": state}
    missing  = [k for k, v in required.items() if not v.strip()]

    if save_only or save_and_gen:
        if missing:
            st.error(f"Missing required fields: **{', '.join(missing)}**")
            st.stop()

        hire_data = {
            "name": name.strip(), "title": title.strip(),
            "department": department.strip(), "start_date": start_date.isoformat(),
            "work_type": work_type, "state": state.strip(),
            "buddy": buddy, "hris": hris.strip(),
        }

        days_away = (start_date - date.today()).days
        if days_away < 5:
            st.error(f"🚨 Compressed timeline: {days_away} days. Critical items will be prioritized.")
        elif days_away < 14:
            st.warning(f"⚠️ {days_away} days until start — less than recommended 14.")

        hire_id = db.add_hire(hire_data)
        st.success(f"✅ **{name}** added (ID #{hire_id})")

        if save_and_gen:
            _generate_plan_for_hire(hire_data | {"id": hire_id}, hire_id)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Workbench
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🔧 Workbench":
    st.title("🔧 Data Workbench")

    # ── Seed / Reset ──
    st.subheader("Mock Data")
    c1, c2 = st.columns(2)
    if c1.button("🌱 Seed Mock Data (6 hires)", type="primary", use_container_width=True):
        db.seed_mock_data()
        st.success("Mock data seeded: 6 hires across all onboarding stages.")
        st.rerun()
    if c2.button("🗑️ Reset Database", use_container_width=True):
        db.reset_db()
        st.success("Database reset. All data cleared.")
        st.rerun()

    st.divider()

    # ── Table Inspector ──
    st.subheader("Table Inspector")
    table = st.selectbox("Table", ["hires", "plans", "flags", "checkins"])
    cols, rows = db.get_raw_table(table)
    if rows:
        st.caption(f"{len(rows)} rows")
        import pandas as pd
        df = pd.DataFrame(rows, columns=cols)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info(f"Table `{table}` is empty.")

    st.divider()

    # ── DB Stats ──
    st.subheader("Database Stats")
    stats = db.get_stats()
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Hires",     stats["total_hires"])
    s2.metric("Starting Week",   stats["starting_week"])
    s3.metric("Open Critical",   stats["open_critical"])
    s4.metric("Plans Generated", stats["plans_generated"])

    st.divider()
    st.caption(f"DB path: `{db.DB_PATH}`")


# ══════════════════════════════════════════════════════════════════════════════
# Agent helper — defined after pages so it's available everywhere
# ══════════════════════════════════════════════════════════════════════════════

def _generate_plan_for_hire(hire: dict, hire_id: int):
    """Run the Claude Opus 4.6 agent for a hire and persist results to DB."""

    @st.cache_resource
    def get_system_prompt():
        parts = [
            (SKILL_DIR / "SKILL.md").read_text(),
            "## Domain Notes\n\n"          + (SKILL_DIR / "references/domain-notes.md").read_text(),
            "## Compliance Requirements\n\n"+ (SKILL_DIR / "references/compliance-requirements.md").read_text(),
        ]
        return "\n\n---\n\n".join(parts)

    TOOLS = [
        {
            "name": "save_section",
            "description": "Save a completed onboarding phase. Call after fully generating each phase.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "phase":    {"type": "string"},
                    "markdown": {"type": "string"},
                },
                "required": ["phase", "markdown"],
            },
        },
        {
            "name": "flag_risk",
            "description": "Flag a compliance or onboarding risk for HR.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "severity":    {"type": "string", "enum": ["critical", "warning", "info"]},
                    "description": {"type": "string"},
                },
                "required": ["severity", "description"],
            },
        },
    ]

    try:
        days_away = (date.fromisoformat(hire["start_date"]) - date.today()).days
    except Exception:
        days_away = 14

    timeline_note = (
        "\n🚨 URGENT: Start date is today or in the past."     if days_away < 1 else
        f"\n⚠️ COMPRESSED: {days_away} days until start."       if days_away < 5 else
        f"\n⚠️ SHORT PRE-BOARDING: {days_away} days."           if days_away < 14 else ""
    )

    prompt = f"""Generate a complete HR onboarding plan.{timeline_note}

Name: {hire['name']} | Title: {hire['title']} — {hire['department']}
Start: {hire['start_date']} ({days_away}d away) | Work: {hire['work_type']}
State: {hire['state']} | Buddy: {hire['buddy']} | HRIS: {hire.get('hris') or 'Not specified'}

Generate all 6 phases. Call save_section() after each phase. Call flag_risk() for any compliance issues."""

    client   = anthropic.Anthropic()
    system   = get_system_prompt()
    messages = [{"role": "user", "content": prompt}]

    progress = st.progress(0, text="Agent starting…")
    text_box = st.empty()
    full_text = ""
    phase_count = 0

    while True:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=system,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                    full_text += event.delta.text
                    text_box.markdown(full_text + " ▌")
            response = stream.get_final_message()
            text_box.markdown(full_text)

        messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason == "end_turn":
            break

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "save_section":
                db.save_plan_section(hire_id, block.input["phase"], block.input["markdown"])
                phase_count += 1
                progress.progress(min(phase_count / 7, 1.0), text=f"Saved: {block.input['phase']}")
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": "Saved."})
            elif block.name == "flag_risk":
                db.save_flag(hire_id, block.input["severity"], block.input["description"])
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": "Flagged."})

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    db.update_hire_status(hire_id, "in_progress")
    progress.progress(1.0, text="✅ Plan complete")
    st.success(f"Plan generated and saved for **{hire['name']}**")

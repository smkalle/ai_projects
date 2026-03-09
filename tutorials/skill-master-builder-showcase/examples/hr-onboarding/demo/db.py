"""
db.py — SQLite database layer + mock data seeder
"""

import sqlite3
import json
from pathlib import Path
from datetime import date, timedelta
from contextlib import contextmanager

DB_PATH = Path(__file__).parent / "onboarding.db"

# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS hires (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    title       TEXT NOT NULL,
    department  TEXT NOT NULL,
    start_date  TEXT NOT NULL,
    work_type   TEXT NOT NULL,
    state       TEXT NOT NULL,
    buddy       TEXT NOT NULL,
    hris        TEXT,
    status      TEXT DEFAULT 'pending',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    hire_id      INTEGER NOT NULL,
    phase        TEXT NOT NULL,
    content      TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    FOREIGN KEY (hire_id) REFERENCES hires(id)
);

CREATE TABLE IF NOT EXISTS flags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    hire_id     INTEGER NOT NULL,
    severity    TEXT NOT NULL,
    description TEXT NOT NULL,
    resolved    INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL,
    FOREIGN KEY (hire_id) REFERENCES hires(id)
);

CREATE TABLE IF NOT EXISTS checkins (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    hire_id       INTEGER NOT NULL,
    day_milestone INTEGER NOT NULL,
    status        TEXT DEFAULT 'pending',
    notes         TEXT,
    completed_at  TEXT,
    FOREIGN KEY (hire_id) REFERENCES hires(id)
);
"""

# ── Connection ────────────────────────────────────────────────────────────────

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)

def reset_db():
    DB_PATH.unlink(missing_ok=True)
    init_db()

# ── Hires ─────────────────────────────────────────────────────────────────────

def add_hire(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO hires (name, title, department, start_date, work_type,
               state, buddy, hris, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                data["name"], data["title"], data["department"],
                data["start_date"], data["work_type"], data["state"],
                data["buddy"], data.get("hris", ""), "pending",
                date.today().isoformat(),
            ),
        )
        hire_id = cur.lastrowid
        # Seed milestone checkins
        for day in (1, 7, 30, 60, 90):
            conn.execute(
                "INSERT INTO checkins (hire_id, day_milestone, status) VALUES (?,?,?)",
                (hire_id, day, "pending"),
            )
        return hire_id

def get_all_hires() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT h.*,
                      COUNT(DISTINCT p.id)          AS plan_sections,
                      COUNT(DISTINCT f.id)           AS total_flags,
                      SUM(CASE WHEN f.severity='critical' AND f.resolved=0
                               THEN 1 ELSE 0 END)   AS open_critical
               FROM hires h
               LEFT JOIN plans   p ON p.hire_id = h.id
               LEFT JOIN flags   f ON f.hire_id = h.id
               GROUP BY h.id
               ORDER BY h.start_date ASC"""
        ).fetchall()
        return [dict(r) for r in rows]

def get_hire(hire_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM hires WHERE id=?", (hire_id,)).fetchone()
        return dict(row) if row else None

def update_hire_status(hire_id: int, status: str):
    with get_conn() as conn:
        conn.execute("UPDATE hires SET status=? WHERE id=?", (status, hire_id))

def delete_hire(hire_id: int):
    with get_conn() as conn:
        for tbl in ("checkins", "flags", "plans", "hires"):
            col = "hire_id" if tbl != "hires" else "id"
            conn.execute(f"DELETE FROM {tbl} WHERE {col}=?", (hire_id,))

# ── Plans ─────────────────────────────────────────────────────────────────────

def save_plan_section(hire_id: int, phase: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO plans (hire_id, phase, content, generated_at) VALUES (?,?,?,?)",
            (hire_id, phase, content, date.today().isoformat()),
        )

def get_plans(hire_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM plans WHERE hire_id=? ORDER BY id", (hire_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def has_plan(hire_id: int) -> bool:
    with get_conn() as conn:
        n = conn.execute(
            "SELECT COUNT(*) FROM plans WHERE hire_id=?", (hire_id,)
        ).fetchone()[0]
        return n > 0

# ── Flags ─────────────────────────────────────────────────────────────────────

def save_flag(hire_id: int, severity: str, description: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO flags (hire_id, severity, description, created_at) VALUES (?,?,?,?)",
            (hire_id, severity, description, date.today().isoformat()),
        )

def get_flags(hire_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM flags WHERE hire_id=? ORDER BY severity DESC", (hire_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def resolve_flag(flag_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE flags SET resolved=1 WHERE id=?", (flag_id,))

# ── Checkins ─────────────────────────────────────────────────────────────────

def get_checkins(hire_id: int) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM checkins WHERE hire_id=? ORDER BY day_milestone", (hire_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def update_checkin(checkin_id: int, status: str, notes: str = ""):
    with get_conn() as conn:
        conn.execute(
            "UPDATE checkins SET status=?, notes=?, completed_at=? WHERE id=?",
            (status, notes,
             date.today().isoformat() if status == "complete" else None,
             checkin_id),
        )

# ── Stats ─────────────────────────────────────────────────────────────────────

def get_stats() -> dict:
    today = date.today().isoformat()
    week  = (date.today() + timedelta(days=7)).isoformat()
    with get_conn() as conn:
        total   = conn.execute("SELECT COUNT(*) FROM hires").fetchone()[0]
        starting= conn.execute(
            "SELECT COUNT(*) FROM hires WHERE start_date BETWEEN ? AND ?",
            (today, week)
        ).fetchone()[0]
        critical= conn.execute(
            "SELECT COUNT(*) FROM flags WHERE severity='critical' AND resolved=0"
        ).fetchone()[0]
        planned = conn.execute(
            "SELECT COUNT(DISTINCT hire_id) FROM plans"
        ).fetchone()[0]
        return {
            "total_hires":   total,
            "starting_week": starting,
            "open_critical": critical,
            "plans_generated": planned,
        }

def get_raw_table(table: str) -> tuple[list, list]:
    """Returns (columns, rows) for workbench table viewer."""
    allowed = {"hires", "plans", "flags", "checkins"}
    if table not in allowed:
        return [], []
    with get_conn() as conn:
        cur = conn.execute(f"SELECT * FROM {table} LIMIT 200")
        cols = [d[0] for d in cur.description]
        rows = [list(r) for r in cur.fetchall()]
        return cols, rows

# ── Mock Data Seeder ──────────────────────────────────────────────────────────

MOCK_HIRES = [
    # starts in 12 days — plan generated
    {
        "name": "Alex Chen",    "title": "Software Engineer", "department": "Engineering",
        "start_date": (date.today() + timedelta(days=12)).isoformat(),
        "work_type": "Hybrid", "state": "California", "buddy": "Yes", "hris": "BambooHR",
        "status": "in_progress",
    },
    # starts in 3 days — compressed, critical flag
    {
        "name": "Maria Garcia", "title": "Marketing Manager", "department": "Marketing",
        "start_date": (date.today() + timedelta(days=3)).isoformat(),
        "work_type": "Remote", "state": "New York", "buddy": "Yes", "hris": "Workday",
        "status": "in_progress",
    },
    # starts today
    {
        "name": "James Wilson", "title": "Sales Representative", "department": "Sales",
        "start_date": date.today().isoformat(),
        "work_type": "On-site", "state": "Texas", "buddy": "No", "hris": "Rippling",
        "status": "in_progress",
    },
    # 30-day checkpoint due
    {
        "name": "Sarah Kim",    "title": "HR Coordinator", "department": "People Ops",
        "start_date": (date.today() - timedelta(days=28)).isoformat(),
        "work_type": "Hybrid", "state": "Washington", "buddy": "Yes", "hris": "BambooHR",
        "status": "in_progress",
    },
    # 60-day mark
    {
        "name": "David Brown",  "title": "DevOps Engineer", "department": "Infrastructure",
        "start_date": (date.today() - timedelta(days=58)).isoformat(),
        "work_type": "Remote", "state": "Florida", "buddy": "Yes", "hris": "Workday",
        "status": "in_progress",
    },
    # 90-day close
    {
        "name": "Emma Davis",   "title": "Product Manager", "department": "Product",
        "start_date": (date.today() - timedelta(days=89)).isoformat(),
        "work_type": "Hybrid", "state": "Illinois", "buddy": "Yes", "hris": "Rippling",
        "status": "complete",
    },
]

MOCK_PLAN_TEMPLATE = """\
# NEW HIRE CARD
━━━━━━━━━━━━━━━━━━━━━━━━━
Name:        {name}
Role:        {title} — {department}
Start Date:  {start_date}
Work Type:   {work_type}
State:       {state}
Buddy Prog:  {buddy}
HRIS:        {hris}
━━━━━━━━━━━━━━━━━━━━━━━━━
"""

MOCK_PHASES = [
    ("Phase 1: Pre-Boarding",
     "## Pre-Boarding Checklist\n\n"
     "| Item | Owner | Due Date | Status |\n|------|-------|----------|--------|\n"
     "| Send welcome email | HR | T-12 | ✅ |\n"
     "| Distribute paperwork packet (I-9, W-4) | HR | T-10 | ✅ |\n"
     "| Initiate IT provisioning | IT | T-10 | 🔄 |\n"
     "| Assign buddy/mentor | Manager | T-7 | ✅ |\n"
     "| File state new hire report | HR | Day 20 | ⏳ |\n"
     "| Prepare first-week calendar | Manager | T-3 | ⏳ |\n"
     "| Send logistics email (time, location, dress code) | Manager | T-2 | ⏳ |\n"
     "| Verify IT provisioning complete | IT | T-2 | ⏳ |\n\n"
     "> **CRITICAL:** Verify IT ready by T-2 days. I-9 must be completed by Day 3."),

    ("Phase 2: Day 1 Execution",
     "## Day 1 Run-of-Show\n\n"
     "### Morning (9:00 AM – 12:00 PM)\n"
     "| Time | Activity | Owner |\n|------|----------|-------|\n"
     "| 9:00 | Welcome greeting | Manager |\n"
     "| 9:15 | Office/workspace tour | Manager |\n"
     "| 9:45 | Introduce to buddy | Manager |\n"
     "| 10:00 | Verify system access | IT |\n"
     "| 10:30 | Complete I-9 Section 2 (**MUST by Day 3**) | HR |\n"
     "| 11:00 | Team introduction icebreaker | Manager |\n\n"
     "### Afternoon (1:00 PM – 5:00 PM)\n"
     "| Time | Activity | Owner |\n|------|----------|-------|\n"
     "| 1:00 | Manager 1:1: role overview + 30-day expectations | Manager |\n"
     "| 2:00 | Walk through first-week schedule | Manager |\n"
     "| 3:00 | Assign first quick-win task | Manager |\n"
     "| 4:30 | End-of-day check-in | Manager |\n\n"
     "> **CRITICAL:** I-9 Section 2 deadline = end of Day 3. Fine: $272+ per violation."),

    ("Phase 3: Week 1 Plan",
     "## Week 1 Daily Schedule\n\n"
     "| Day | Compliance Track (HR) | Role Track (Manager) | Culture Track (Buddy) |\n"
     "|-----|----------------------|---------------------|---------------------|\n"
     "| Mon | I-9 Section 2 confirm | Daily 15-min check-in | Buddy intro |\n"
     "| Tue | Launch EEOC training | Role tools walkthrough | Team lunch |\n"
     "| Wed | Security awareness training | Key stakeholder intros | Cross-functional intro |\n"
     "| Thu | W-4 + state tax confirm | Role-specific processes | Informal coffee chat |\n"
     "| Fri | Training status check | Deliver 30-60-90 doc | Team standup |\n\n"
     "**Lock in 30-day check-in by end of Week 1.**"),

    ("Phase 4: 30-Day Checkpoint",
     "## 30-Day Check-In Agenda\n\n"
     "**Duration:** 30 min | **Owner:** Manager + HR\n\n"
     "| Topic | Time | Questions |\n|-------|------|----------|\n"
     "| Overall check-in | 5 min | How are you feeling overall? |\n"
     "| Role clarity | 10 min | Do you understand your responsibilities? |\n"
     "| Tools & access | 5 min | Anything missing or broken? |\n"
     "| Culture & team | 5 min | How are relationships developing? |\n"
     "| Onboarding feedback | 5 min | What could we improve? |\n\n"
     "**Manager Assessment (1–5):**\n"
     "- Task Mastery: ___\n- Culture Fit: ___\n- Initiative: ___\n\n"
     "> Flag any rating 1–2 to HR within 48 hours."),

    ("Phase 5: 60-Day Progress Review",
     "## 60-Day Progress Review\n\n"
     "**Focus:** Independent performance\n\n"
     "**Review Topics:**\n"
     "1. Performance vs 30–60 day milestones\n"
     "2. Career development interests\n"
     "3. Role scope adjustments\n"
     "4. Team integration (buddy feedback)\n"
     "5. Training completion status\n\n"
     "**Manager Assessment (1–5):**\n"
     "- Task Mastery: ___\n- Culture Fit: ___\n"
     "- Initiative: ___\n- Independence: ___\n- Quality: ___\n\n"
     "> Any 1–2 rating → generate 30-day improvement plan."),

    ("Phase 6: 90-Day Formal Review",
     "## 90-Day Evaluation & Onboarding Close\n\n"
     "**Steps (in order — do not skip):**\n"
     "1. Manager completes written 90-day evaluation\n"
     "2. HR schedules formal review meeting (30–45 min)\n"
     "3. New hire self-assessment (recommended)\n"
     "4. Both parties review, discuss, and sign\n"
     "5. Goals set for months 4–12\n"
     "6. Onboarding record marked COMPLETE in HRIS\n\n"
     "**Closure Checklist:**\n"
     "- [ ] I-9 on file, verified, stored per retention (3 yrs from hire)\n"
     "- [ ] W-4 and state tax forms filed\n"
     "- [ ] State new hire report submitted\n"
     "- [ ] All mandatory training completed\n"
     "- [ ] 30 and 60-day reviews in HRIS\n"
     "- [ ] 90-day evaluation signed by both parties\n"
     "- [ ] Benefits enrollment confirmed\n\n"
     "> **CRITICAL:** This is a legal document. Must be signed + retained."),
]

MOCK_FLAGS = {
    "Alex Chen": [
        ("info",     "California requires pay rate notice at hire — include in paperwork packet"),
        ("warning",  "California sexual harassment training required within 6 months of hire"),
    ],
    "Maria Garcia": [
        ("critical", "COMPRESSED TIMELINE: Only 3 days until start — IT provisioning at risk"),
        ("critical", "Remote I-9 completion required — arrange authorized representative or remote I-9 service before Day 1"),
        ("warning",  "New York Wage Theft Prevention Act: written pay notice required in English AND employee's primary language"),
    ],
    "James Wilson": [
        ("info",     "Texas has no state income tax — skip state withholding form"),
        ("warning",  "No buddy assigned — culture risk for first 90 days"),
    ],
    "Sarah Kim": [
        ("warning",  "30-day check-in due in 2 days — schedule immediately"),
        ("info",     "Washington WA Cares Fund payroll deduction — ensure new hire notified"),
    ],
    "David Brown": [
        ("info",     "60-day review due this week"),
        ("info",     "Florida: no state income tax, new hire report filed with FL Dept of Revenue"),
    ],
    "Emma Davis": [
        ("info",     "90-day formal review complete — onboarding record closed"),
    ],
}

MOCK_CHECKIN_STATUS = {
    "Alex Chen":    {1: "complete", 7: "complete", 30: "pending",  60: "pending", 90: "pending"},
    "Maria Garcia": {1: "pending",  7: "pending",  30: "pending",  60: "pending", 90: "pending"},
    "James Wilson": {1: "complete", 7: "pending",  30: "pending",  60: "pending", 90: "pending"},
    "Sarah Kim":    {1: "complete", 7: "complete", 30: "pending",  60: "pending", 90: "pending"},
    "David Brown":  {1: "complete", 7: "complete", 30: "complete", 60: "pending", 90: "pending"},
    "Emma Davis":   {1: "complete", 7: "complete", 30: "complete", 60: "complete",90: "complete"},
}


def seed_mock_data():
    """Drop all data and reseed with mock hires."""
    reset_db()
    for hire_data in MOCK_HIRES:
        hire_id = add_hire(hire_data)
        update_hire_status(hire_id, hire_data["status"])

        # Plan sections
        card = MOCK_PLAN_TEMPLATE.format(**hire_data)
        save_plan_section(hire_id, "New Hire Card", card)
        for phase_name, phase_content in MOCK_PHASES:
            save_plan_section(hire_id, phase_name, phase_content)

        # Flags
        for severity, desc in MOCK_FLAGS.get(hire_data["name"], []):
            save_flag(hire_id, severity, desc)

        # Checkin statuses
        checkins = get_checkins(hire_id)
        status_map = MOCK_CHECKIN_STATUS.get(hire_data["name"], {})
        for ci in checkins:
            st = status_map.get(ci["day_milestone"], "pending")
            update_checkin(ci["id"], st)

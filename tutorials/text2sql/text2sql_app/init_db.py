"""WardOps demo database seeder — Iteration 3.

All 11 views from wardops-brd-prd.md seeded with realistic synthetic data.
Run: python init_db.py
"""
import sqlite3
import random
import datetime

DB = "/tmp/wardops_demo.db"

# Deterministic-ish data so runs are reproducible
random.seed(42)

# ── Helpers ──────────────────────────────────────────────────────────────────

def dt(hour, minute=0, days_offset=0):
    base = datetime.date.today() + datetime.timedelta(days=days_offset)
    return datetime.datetime.combine(base, datetime.time(hour, minute)).isoformat()

WARDS = ["ICU_WARD_3", "MED_SURG_WARD_1", "PEDIATRICS_WARD_2", "OBGYN_WARD_4", "OR_SUITE_1"]
ROLES = ["RN", "AN", "GN", "JN"]
SKILLS = ["critical_care", "pediatrics", "obstetrics", "general", "surgery", "emergency"]
ITEMS = [
    ("Surgical Gloves (M)", "boxes"),
    ("IV Cannula 18G", "units"),
    ("Pulse Oximeter Probes", "units"),
    ("N95 Respirators", "boxes"),
    ("Sterile Gowns (L)", "units"),
    ("Foley Catheters", "units"),
    ("Syringes 5ml", "units"),
    ("Normal Saline 1000ml", "bags"),
    ("Morphine 10mg", "amps"),
    ("Paracetamol 1g IV", "vials"),
    ("Ceftriaxone 1g", "vials"),
    ("Latex Tourniquets", "units"),
    ("Gauze Swabs 4x4", "packs"),
    ("Betadine Solution", "bottles"),
    ("Alcohol Swabs", "boxes"),
]

# ── Schema ───────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS v_current_shift_roster (
    staff_id TEXT, name TEXT, role TEXT, ward TEXT,
    shift_start TEXT, shift_end TEXT, hours_this_week REAL
);
CREATE TABLE IF NOT EXISTS v_nurse_patient_ratio (
    ward TEXT, shift_date TEXT, nurse_count INTEGER,
    patient_census INTEGER, ratio REAL
);
CREATE TABLE IF NOT EXISTS v_float_pool_available (
    staff_id TEXT, name TEXT, skills TEXT,
    available_from TEXT, available_to TEXT
);
CREATE TABLE IF NOT EXISTS v_overtime_flags (
    staff_id TEXT, name TEXT, ward TEXT,
    weekly_hours REAL, overtime_threshold REAL, flag INTEGER
);
CREATE TABLE IF NOT EXISTS v_bed_census (
    ward TEXT, bed_id TEXT, status TEXT, patient_id TEXT
);
CREATE TABLE IF NOT EXISTS v_expected_discharges (
    ward TEXT, bed_id TEXT, expected_discharge_dt TEXT, discharge_type TEXT
);
CREATE TABLE IF NOT EXISTS v_housekeeping_queue (
    ward TEXT, bed_id TEXT, housekeeping_start TEXT,
    elapsed_minutes INTEGER, status TEXT
);
CREATE TABLE IF NOT EXISTS v_ed_boarding (
    patient_count INTEGER, avg_boarding_hours REAL, wards_with_capacity TEXT
);
CREATE TABLE IF NOT EXISTS v_low_stock_items (
    location TEXT, item_id TEXT, item_name TEXT,
    current_qty INTEGER, reorder_point INTEGER, unit TEXT
);
CREATE TABLE IF NOT EXISTS v_expiry_alerts (
    location TEXT, item_id TEXT, item_name TEXT,
    expiry_date TEXT, days_to_expiry INTEGER, qty INTEGER
);
CREATE TABLE IF NOT EXISTS v_consumption_anomalies (
    item_id TEXT, item_name TEXT, ward TEXT,
    this_week_qty INTEGER, last_week_qty INTEGER, delta_pct REAL
);
"""

# ── Seed data ────────────────────────────────────────────────────────────────

STAFF = [
    ("S001","Priya Nair","RN","ICU_WARD_3"),
    ("S002","Ramesh K","RN","ICU_WARD_3"),
    ("S003","Sunita Rao","RN","MED_SURG_WARD_1"),
    ("S004","Arjun Das","RN","ICU_WARD_3"),
    ("S005","Lakshmi V","AN","ICU_WARD_3"),
    ("S006","Vijay Menon","RN","MED_SURG_WARD_1"),
    ("S007","Meera Singh","RN","MED_SURG_WARD_1"),
    ("S008","Kiran Patel","AN","MED_SURG_WARD_1"),
    ("S009","Anita Desai","RN","PEDIATRICS_WARD_2"),
    ("S010","Suresh Nair","RN","PEDIATRICS_WARD_2"),
    ("S011","Deepa Raj","AN","PEDIATRICS_WARD_2"),
    ("S012","Harish Iyer","RN","OBGYN_WARD_4"),
    ("S013","Nirmala P","RN","OBGYN_WARD_4"),
    ("S014","Ravi Kumar","AN","OBGYN_WARD_4"),
    ("S015","Priya L","RN","OR_SUITE_1"),
    ("S016","Ajay S","RN","OR_SUITE_1"),
    ("S017","Geetha M","AN","OR_SUITE_1"),
    ("S018","Biju K","RN","ICU_WARD_3"),
    ("S019","Suma V","RN","MED_SURG_WARD_1"),
    ("S020","Thomas George","RN","PEDIATRICS_WARD_2"),
]

SHIFTS = [(7,15),(15,23),(23,7)]

def build_roster():
    rows = []
    for staff_id, name, role, ward in STAFF:
        shift_h, shift_end_h = SHIFTS[random.randint(0,2)]
        hours = round(random.uniform(32, 60), 1)
        rows.append((staff_id, name, role, ward, dt(shift_h), dt(shift_end_h), hours))
    return rows

def build_overtime_flags():
    rows = []
    for staff_id, name, role, ward in STAFF:
        hours = round(random.uniform(30, 62), 1)
        flag = 1 if hours > 44 else 0
        rows.append((staff_id, name, ward, hours, 44.0, flag))
    return rows

def build_nurse_patient_ratio():
    rows = []
    for ward in WARDS:
        for days in range(-7, 1):
            nc = random.randint(2, 8)
            pc = random.randint(nc, nc * 6)
            ratio = round(pc / nc, 1)
            rows.append((ward, dt(0, days_offset=days)[:10], nc, pc, ratio))
    return rows

def build_float_pool():
    rows = []
    for i, (sid, name, role, _) in enumerate(STAFF[::3]):
        skill = random.choice(SKILLS)
        rows.append((sid, name, skill, dt(6), dt(22)))
    return rows

def build_bed_census():
    statuses = ["available", "occupied", "housekeeping", "maintenance"]
    rows = []
    for ward in WARDS:
        n_beds = random.randint(8, 20)
        for b in range(n_beds):
            bed_id = f"{ward[-1]}{b+101:02d}"
            status = random.choices(statuses, weights=[3, 10, 3, 1])[0]
            pid = f"P{ward[-1]}{b+100:03d}" if status == "occupied" else None
            rows.append((ward, bed_id, status, pid))
    return rows

def build_expected_discharges():
    rows = []
    for ward in WARDS:
        n = random.randint(2, 6)
        for i in range(n):
            bed_id = f"{ward[-1]}{i+101:02d}"
            hour = random.choice([9, 11, 13, 15, 17])
            rows.append((ward, bed_id, dt(hour, random.choice([0,30])), random.choice(["home","transfer","ama"])))
    return rows

def build_housekeeping_queue():
    rows = []
    for ward in WARDS:
        n = random.randint(1, 5)
        for i in range(n):
            bed_id = f"{ward[-1]}{i+201:02d}"
            elapsed = random.randint(15, 180)
            status = random.choice(["in_progress","pending","ready"])
            rows.append((ward, bed_id, dt(6, random.choice([0,15,30,45])), elapsed, status))
    return rows

def build_ed_boarding():
    count = random.randint(3, 12)
    avg_hours = round(random.uniform(2.0, 8.5), 1)
    wards_json = '["ICU_WARD_3","MED_SURG_WARD_1","PEDIATRICS_WARD_2"]'
    return [(count, avg_hours, wards_json)]

def build_low_stock_items():
    rows = []
    for ward in WARDS:
        for i, (iname, unit) in enumerate(ITEMS):
            qty = random.randint(0, 8)
            reorder = random.randint(10, 25)
            rows.append((ward, f"I{i+1:03d}", iname, qty, reorder, unit))
    return rows

def build_expiry_alerts():
    rows = []
    for ward in WARDS:
        for i, (iname, unit) in enumerate(ITEMS[:8]):
            days = random.randint(-2, 60)
            exp = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()
            rows.append((ward, f"I{i+1:03d}", iname, exp, days, random.randint(1, 30)))
    return rows

def build_consumption_anomalies():
    rows = []
    for ward in WARDS:
        for i, (iname, _) in enumerate(ITEMS):
            lw = random.randint(20, 100)
            tw = random.randint(5, 200)
            delta = round((tw - lw) / lw * 100, 1)
            rows.append((f"I{i+1:03d}", iname, ward, tw, lw, delta))
    return rows

# ── Main ──────────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executescript(SCHEMA)

    # Clear existing data
    for table in [
        "v_current_shift_roster","v_nurse_patient_ratio",
        "v_float_pool_available","v_overtime_flags","v_bed_census",
        "v_expected_discharges","v_housekeeping_queue","v_ed_boarding",
        "v_low_stock_items","v_expiry_alerts","v_consumption_anomalies",
    ]:
        c.execute(f"DELETE FROM {table}")

    # Insert
    for row in build_roster():
        c.execute("INSERT INTO v_current_shift_roster VALUES (?,?,?,?,?,?,?)", row)

    for row in build_overtime_flags():
        c.execute("INSERT INTO v_overtime_flags VALUES (?,?,?,?,?,?)", row)

    for row in build_nurse_patient_ratio():
        c.execute("INSERT INTO v_nurse_patient_ratio VALUES (?,?,?,?,?)", row)

    for row in build_float_pool():
        c.execute("INSERT INTO v_float_pool_available VALUES (?,?,?,?,?)", row)

    for row in build_bed_census():
        c.execute("INSERT INTO v_bed_census VALUES (?,?,?,?)", row)

    for row in build_expected_discharges():
        c.execute("INSERT INTO v_expected_discharges VALUES (?,?,?,?)", row)

    for row in build_housekeeping_queue():
        c.execute("INSERT INTO v_housekeeping_queue VALUES (?,?,?,?,?)", row)

    for row in build_ed_boarding():
        c.execute("INSERT INTO v_ed_boarding VALUES (?,?,?)", row)

    for row in build_low_stock_items():
        c.execute("INSERT INTO v_low_stock_items VALUES (?,?,?,?,?,?)", row)

    for row in build_expiry_alerts():
        c.execute("INSERT INTO v_expiry_alerts VALUES (?,?,?,?,?,?)", row)

    for row in build_consumption_anomalies():
        c.execute("INSERT INTO v_consumption_anomalies VALUES (?,?,?,?,?,?)", row)

    conn.commit()

    # Report
    print("WardOps DB seeded:")
    for table in [
        "v_current_shift_roster","v_nurse_patient_ratio",
        "v_float_pool_available","v_overtime_flags","v_bed_census",
        "v_expected_discharges","v_housekeeping_queue","v_ed_boarding",
        "v_low_stock_items","v_expiry_alerts","v_consumption_anomalies",
    ]:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {c.fetchone()[0]} rows")
    conn.close()

if __name__ == "__main__":
    init_db()

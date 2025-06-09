"""Database module for Medical AI Assistant MVP."""

import json
import logging
import sqlite3
import uuid
import random
import string
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, date
from pathlib import Path
from typing import Any, Optional

from .config import settings

logger = logging.getLogger(__name__)

# Database file path from settings
DB_PATH = Path(settings.database_url.replace("sqlite:///", ""))


async def init_database() -> None:
    """Initialize the SQLite database with required tables."""
    logger.info("Initializing database")

    with get_db_connection() as conn:
        # Create patients table (V2.0 enhancement)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                mobile_number TEXT UNIQUE NOT NULL,
                gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
                village TEXT,
                district TEXT,
                city TEXT,
                emergency_contact TEXT,
                guardian_name TEXT,
                occupation TEXT,
                blood_group TEXT,
                allergies TEXT,
                chronic_conditions TEXT,
                photo_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """
        )

        # Create indexes for patients table
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mobile_number ON patients(mobile_number)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON patients(first_name, last_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_location ON patients(village, district, city)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON patients(created_at)")

        # Create healthcare workers table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS healthcare_workers (
                worker_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('Doctor', 'Nurse', 'Health_Worker', 'Supervisor')),
                clinic_id TEXT,
                mobile_number TEXT,
                email TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for healthcare workers
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clinic_id ON healthcare_workers(clinic_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_role ON healthcare_workers(role)")

        # Create visit patterns table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS visit_patterns (
                pattern_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                visit_frequency INTEGER DEFAULT 0,
                last_visit_date TIMESTAMP,
                pattern_type TEXT DEFAULT 'Normal' CHECK (pattern_type IN ('Normal', 'Frequent', 'Emergency', 'Follow-up')),
                concern_level TEXT DEFAULT 'None' CHECK (concern_level IN ('None', 'Low', 'Medium', 'High')),
                pattern_notes TEXT,
                alert_acknowledged BOOLEAN DEFAULT FALSE,
                acknowledged_by TEXT,
                acknowledged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            )
        """
        )

        # Create indexes for visit patterns
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_patient_id ON visit_patterns(patient_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_type ON visit_patterns(pattern_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_concern_level ON visit_patterns(concern_level)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_last_visit ON visit_patterns(last_visit_date)")

        # Create users table (existing)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create original cases table (maintain backward compatibility)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                patient_data TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                severity TEXT NOT NULL,
                ai_assessment TEXT,
                doctor_review TEXT,
                photo_paths TEXT,
                status TEXT DEFAULT 'new',
                volunteer_id TEXT,
                doctor_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Check if cases table needs to be updated for V2.0
        cursor = conn.execute("PRAGMA table_info(cases)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'patient_id' not in columns:
            # Add new columns to existing cases table for V2.0 compatibility
            conn.execute("ALTER TABLE cases ADD COLUMN patient_id TEXT")
            conn.execute("ALTER TABLE cases ADD COLUMN healthcare_worker_id TEXT")
            conn.execute("ALTER TABLE cases ADD COLUMN visit_datetime TIMESTAMP")
            conn.execute("ALTER TABLE cases ADD COLUMN case_type TEXT DEFAULT 'Assessment' CHECK (case_type IN ('Assessment', 'Dosage', 'Photo', 'Follow-up', 'Emergency'))")
            conn.execute("ALTER TABLE cases ADD COLUMN chief_complaint TEXT")
            conn.execute("ALTER TABLE cases ADD COLUMN urgency_level TEXT DEFAULT 'Medium' CHECK (urgency_level IN ('Low', 'Medium', 'High', 'Critical'))")
            conn.execute("ALTER TABLE cases ADD COLUMN recommendations TEXT")
            conn.execute("ALTER TABLE cases ADD COLUMN medications_prescribed TEXT")
            conn.execute("ALTER TABLE cases ADD COLUMN follow_up_required BOOLEAN DEFAULT FALSE")
            conn.execute("ALTER TABLE cases ADD COLUMN follow_up_date DATE")
            conn.execute("ALTER TABLE cases ADD COLUMN case_status TEXT DEFAULT 'Open' CHECK (case_status IN ('Open', 'Closed', 'Referred'))")
            conn.execute("ALTER TABLE cases ADD COLUMN photos TEXT")
            conn.execute("ALTER TABLE cases ADD COLUMN notes TEXT")

        # Create enhanced cases table if it doesn't exist (for new installations)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cases_v2 (
                case_id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                healthcare_worker_id TEXT DEFAULT 'HW001',
                visit_datetime TIMESTAMP NOT NULL,
                case_type TEXT NOT NULL CHECK (case_type IN ('Assessment', 'Dosage', 'Photo', 'Follow-up', 'Emergency')),
                chief_complaint TEXT,
                symptoms TEXT NOT NULL,
                ai_assessment TEXT,
                urgency_level TEXT NOT NULL CHECK (urgency_level IN ('Low', 'Medium', 'High', 'Critical')),
                recommendations TEXT,
                medications_prescribed TEXT,
                follow_up_required BOOLEAN DEFAULT FALSE,
                follow_up_date DATE,
                case_status TEXT DEFAULT 'Open' CHECK (case_status IN ('Open', 'Closed', 'Referred')),
                photos TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            )
        """
        )

        # Create indexes for enhanced cases
        conn.execute("CREATE INDEX IF NOT EXISTS idx_case_patient_id ON cases_v2(patient_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_visit_datetime ON cases_v2(visit_datetime)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_case_type ON cases_v2(case_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_urgency_level ON cases_v2(urgency_level)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_healthcare_worker ON cases_v2(healthcare_worker_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_case_patient_date ON cases_v2(patient_id, visit_datetime DESC)")

        # Create sync queue table (existing)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_queue (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert default healthcare worker if none exists
        cursor = conn.execute("SELECT COUNT(*) FROM healthcare_workers")
        if cursor.fetchone()[0] == 0:
            conn.execute(
                """
                INSERT INTO healthcare_workers (
                    worker_id, first_name, last_name, role, clinic_id
                ) VALUES (?, ?, ?, ?, ?)
                """,
                ("HW001", "Default", "Worker", "Health_Worker", "CLINIC001")
            )

        conn.commit()

    logger.info("Database initialization complete")


def generate_patient_id() -> str:
    """Generate a unique patient ID in format PAT + 5 alphanumeric characters."""
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(characters, k=5))
    return f"PAT{random_part}"


def generate_unique_patient_id() -> str:
    """Generate a unique patient ID with collision detection."""
    max_attempts = 10
    for attempt in range(max_attempts):
        patient_id = generate_patient_id()
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM patients WHERE patient_id = ?", (patient_id,))
            if cursor.fetchone()[0] == 0:
                return patient_id
    raise Exception("Unable to generate unique patient ID after maximum attempts")


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with proper cleanup."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
    finally:
        conn.close()


class DatabaseManager:
    """Database manager for CRUD operations."""

    @staticmethod
    def create_case(case_data: dict[str, Any]) -> str:
        """Create a new medical case."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO cases (
                    id, patient_data, symptoms, severity, ai_assessment,
                    photo_paths, volunteer_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    case_data["id"],
                    json.dumps(case_data["patient_data"]),
                    case_data["symptoms"],
                    case_data["severity"],
                    json.dumps(case_data.get("ai_assessment")),
                    json.dumps(case_data.get("photo_paths", [])),
                    case_data.get("volunteer_id"),
                ),
            )
            conn.commit()
            return case_data["id"]

    @staticmethod
    def get_case(case_id: str) -> Optional[dict[str, Any]]:
        """Get a case by ID."""
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
            row = cursor.fetchone()

            if row:
                case = dict(row)
                # Parse JSON fields
                case["patient_data"] = json.loads(case["patient_data"])
                case["ai_assessment"] = (
                    json.loads(case["ai_assessment"]) if case["ai_assessment"] else None
                )
                case["photo_paths"] = (
                    json.loads(case["photo_paths"]) if case["photo_paths"] else []
                )
                return case
            return None

    @staticmethod
    def get_cases(
        status: Optional[str] = None, 
        patient_name: Optional[str] = None,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get cases with optional status and patient name filters from both legacy and V2 tables."""
        with get_db_connection() as conn:
            cases = []
            
            # Build WHERE conditions for V2 cases
            v2_conditions = []
            v2_params = []
            
            # Status filter
            if status:
                # Map status to case_status for V2 table
                case_status_map = {
                    "new": "Open",
                    "reviewed": "Closed", 
                    "closed": "Closed"
                }
                mapped_status = case_status_map.get(status.lower(), "Open")
                v2_conditions.append("c.case_status = ?")
                v2_params.append(mapped_status)
            
            # Patient name filter
            if patient_name:
                v2_conditions.append("(p.first_name LIKE ? OR p.last_name LIKE ? OR (p.first_name || ' ' || p.last_name) LIKE ?)")
                name_pattern = f"%{patient_name}%"
                v2_params.extend([name_pattern, name_pattern, name_pattern])
            
            # Build V2 query
            v2_where_clause = " AND ".join(v2_conditions) if v2_conditions else "1=1"
            v2_query = f"""
                SELECT 
                    c.case_id as id,
                    c.patient_id,
                    c.case_type,
                    c.chief_complaint,
                    c.symptoms,
                    c.ai_assessment,
                    c.urgency_level,
                    c.recommendations,
                    c.case_status as status,
                    c.created_at,
                    c.updated_at,
                    c.visit_datetime,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.mobile_number,
                    CASE 
                        WHEN p.date_of_birth IS NOT NULL 
                        THEN (julianday('now') - julianday(p.date_of_birth)) / 365.25
                        ELSE 0 
                    END as patient_age,
                    'v2' as source_table
                FROM cases_v2 c
                LEFT JOIN patients p ON c.patient_id = p.patient_id
                WHERE {v2_where_clause}
                ORDER BY c.created_at DESC
                LIMIT ?
            """
            v2_params.append(limit)
            
            cursor = conn.execute(v2_query, v2_params)

            # Process V2 cases
            for row in cursor.fetchall():
                case = dict(row)
                # Parse JSON fields
                case["ai_assessment"] = (
                    json.loads(case["ai_assessment"]) if case["ai_assessment"] else None
                )
                # Convert patient info to legacy format for compatibility
                if case["patient_name"]:
                    case["patient_data"] = {
                        "name": case["patient_name"],
                        "mobile_number": case["mobile_number"],
                        "age_years": case["patient_age"] or 0
                    }
                case["photo_paths"] = []  # V2 doesn't have photos yet
                case["severity"] = case["urgency_level"].lower() if case["urgency_level"] else "medium"
                cases.append(case)
            
            # If we have space, also get legacy cases for backwards compatibility
            remaining_limit = limit - len(cases)
            if remaining_limit > 0:
                legacy_conditions = []
                legacy_params = []
                
                if status:
                    legacy_conditions.append("status = ?")
                    legacy_params.append(status)
                
                # For legacy cases, we'll filter by the patient_data JSON field
                if patient_name:
                    legacy_conditions.append("patient_data LIKE ?")
                    legacy_params.append(f'%"name":"%{patient_name}%"%')
                
                legacy_where_clause = " AND ".join(legacy_conditions) if legacy_conditions else "1=1"
                legacy_query = f"""
                    SELECT *, 'legacy' as source_table FROM cases
                    WHERE {legacy_where_clause}
                    ORDER BY created_at DESC
                    LIMIT ?
                """
                legacy_params.append(remaining_limit)
                
                cursor = conn.execute(legacy_query, legacy_params)

                # Process legacy cases
                for row in cursor.fetchall():
                    case = dict(row)
                    # Parse JSON fields for legacy cases
                    case["patient_data"] = json.loads(case["patient_data"]) if case.get("patient_data") else {}
                    case["ai_assessment"] = (
                        json.loads(case["ai_assessment"]) if case["ai_assessment"] else None
                    )
                    case["photo_paths"] = (
                        json.loads(case["photo_paths"]) if case["photo_paths"] else []
                    )
                    cases.append(case)

            # Map database statuses to API statuses for consistency
            for case in cases:
                # Map V2 case_status to standard API status
                if case.get('status') == 'Open':
                    case['status'] = 'new'
                elif case.get('status') == 'Closed':
                    case['status'] = 'closed'
                # For legacy cases, keep existing status mapping
            
            return cases

    @staticmethod
    def update_case(case_id: str, updates: dict[str, Any]) -> bool:
        """Update a case with new data."""
        with get_db_connection() as conn:
            # Build dynamic update query
            set_clauses = []
            values = []

            for key, value in updates.items():
                if key in ["ai_assessment", "photo_paths"] and value is not None:
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value))
                elif key not in ["id", "created_at"]:  # Don't update these fields
                    set_clauses.append(f"{key} = ?")
                    values.append(value)

            if not set_clauses:
                return False

            # Add updated_at
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(case_id)

            query = f"""
                UPDATE cases
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """

            cursor = conn.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def add_photo_to_case(case_id: str, photo_path: str) -> bool:
        """Add a photo path to a case."""
        case = DatabaseManager.get_case(case_id)
        if not case:
            return False

        photo_paths = case.get("photo_paths", [])
        photo_paths.append(photo_path)

        return DatabaseManager.update_case(case_id, {"photo_paths": photo_paths})

    @staticmethod
    def add_doctor_review(case_id: str, review: str, doctor_id: str) -> bool:
        """Add a doctor review to a case."""
        updates = {
            "doctor_review": review,
            "doctor_id": doctor_id,
            "status": "reviewed"
        }
        return DatabaseManager.update_case(case_id, updates)

    @staticmethod
    def update_case_assessment(case_id: str, assessment: dict[str, Any]) -> bool:
        """Update the AI assessment for a case."""
        return DatabaseManager.update_case(case_id, {"ai_assessment": assessment})

    @staticmethod
    def health_check() -> bool:
        """Perform a database health check."""
        try:
            with get_db_connection() as conn:
                cursor = conn.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            raise

    @staticmethod
    def get_stats() -> dict[str, Any]:
        """Get database statistics."""
        with get_db_connection() as conn:
            stats = {}

            # Case statistics
            cursor = conn.execute("SELECT COUNT(*) FROM cases")
            stats["total_cases"] = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'new'")
            stats["pending_cases"] = cursor.fetchone()[0]

            # Patient statistics (V2.0)
            cursor = conn.execute("SELECT COUNT(*) FROM patients WHERE is_active = TRUE")
            stats["total_patients"] = cursor.fetchone()[0]

            cursor = conn.execute(
                "SELECT COUNT(*) FROM patients WHERE created_at >= date('now', '-30 days')"
            )
            stats["new_patients_30_days"] = cursor.fetchone()[0]

            return stats

    # Patient Management Methods (V2.0)
    @staticmethod
    def register_patient(patient_data: dict[str, Any]) -> str:
        """Register a new patient and return patient ID."""
        patient_id = generate_unique_patient_id()
        
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO patients (
                    patient_id, first_name, last_name, date_of_birth, mobile_number,
                    gender, village, district, city, emergency_contact, guardian_name,
                    occupation, blood_group, allergies, chronic_conditions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_id,
                    patient_data["first_name"],
                    patient_data["last_name"],
                    patient_data["date_of_birth"],
                    patient_data["mobile_number"],
                    patient_data["gender"],
                    patient_data.get("village"),
                    patient_data.get("district"),
                    patient_data.get("city"),
                    patient_data.get("emergency_contact"),
                    patient_data.get("guardian_name"),
                    patient_data.get("occupation"),
                    patient_data.get("blood_group"),
                    patient_data.get("allergies"),
                    patient_data.get("chronic_conditions"),
                )
            )
            conn.commit()
            return patient_id

    @staticmethod
    def get_patient(patient_id: str) -> Optional[dict[str, Any]]:
        """Get patient by ID."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM patients WHERE patient_id = ? AND is_active = TRUE",
                (patient_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def search_patients(
        query: str = None,
        patient_id: str = None,
        mobile: str = None,
        name: str = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """Search patients by multiple criteria."""
        with get_db_connection() as conn:
            base_query = """
                SELECT p.*, 
                       COUNT(c.case_id) as total_visits,
                       MAX(c.visit_datetime) as last_visit,
                       vp.pattern_type,
                       vp.concern_level
                FROM patients p
                LEFT JOIN cases_v2 c ON p.patient_id = c.patient_id
                LEFT JOIN visit_patterns vp ON p.patient_id = vp.patient_id
                WHERE p.is_active = TRUE
            """
            
            conditions = []
            params = []
            
            if patient_id:
                conditions.append("p.patient_id = ?")
                params.append(patient_id)
            elif query:
                conditions.append("""
                    (p.first_name LIKE ? OR p.last_name LIKE ? OR 
                     p.mobile_number LIKE ? OR p.patient_id LIKE ?)
                """)
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term, search_term])
            elif mobile:
                conditions.append("p.mobile_number LIKE ?")
                params.append(f"%{mobile}%")
            elif name:
                conditions.append("(p.first_name LIKE ? OR p.last_name LIKE ?)")
                name_term = f"%{name}%"
                params.extend([name_term, name_term])
            
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            base_query += """
                GROUP BY p.patient_id
                ORDER BY p.updated_at DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor = conn.execute(base_query, params)
            patients = []
            for row in cursor.fetchall():
                patient = dict(row)
                # Calculate age
                if patient['date_of_birth']:
                    birth_date = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    patient['age'] = age
                
                # Determine alert status
                alert_status = "normal"
                if patient.get('concern_level') == 'High':
                    alert_status = "emergency"
                elif patient.get('concern_level') == 'Medium':
                    alert_status = "repeat"
                elif patient.get('pattern_type') == 'Frequent':
                    alert_status = "frequent"
                
                patient['alert_status'] = alert_status
                patients.append(patient)
            
            return patients

    @staticmethod
    def get_patient_history(
        patient_id: str,
        case_type: str = None,
        start_date: date = None,
        end_date: date = None,
        limit: int = 50
    ) -> dict[str, Any]:
        """Get complete case history for a patient."""
        with get_db_connection() as conn:
            # Get patient info
            patient = DatabaseManager.get_patient(patient_id)
            if not patient:
                return None
            
            # Build cases query
            cases_query = """
                SELECT c.*, hw.first_name as worker_first_name, hw.last_name as worker_last_name
                FROM cases_v2 c
                LEFT JOIN healthcare_workers hw ON c.healthcare_worker_id = hw.worker_id
                WHERE c.patient_id = ?
            """
            params = [patient_id]
            
            if case_type:
                cases_query += " AND c.case_type = ?"
                params.append(case_type)
            
            if start_date:
                cases_query += " AND DATE(c.visit_datetime) >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                cases_query += " AND DATE(c.visit_datetime) <= ?"
                params.append(end_date.isoformat())
            
            cases_query += " ORDER BY c.visit_datetime DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(cases_query, params)
            cases = []
            for row in cursor.fetchall():
                case = dict(row)
                # Parse JSON fields
                if case.get('ai_assessment'):
                    case['ai_assessment'] = json.loads(case['ai_assessment'])
                if case.get('photos'):
                    case['photos'] = json.loads(case['photos'])
                if case.get('medications_prescribed'):
                    case['medications_prescribed'] = json.loads(case['medications_prescribed'])
                
                # Add healthcare worker name
                if case.get('worker_first_name'):
                    case['healthcare_worker'] = f"{case['worker_first_name']} {case['worker_last_name']}"
                
                cases.append(case)
            
            # Get visit patterns
            cursor = conn.execute(
                "SELECT * FROM visit_patterns WHERE patient_id = ?",
                (patient_id,)
            )
            pattern_row = cursor.fetchone()
            visit_patterns = dict(pattern_row) if pattern_row else {
                'total_visits': len(cases),
                'last_visit': cases[0]['visit_datetime'] if cases else None,
                'frequent_visitor': False,
                'repeat_visit_alert': False
            }
            
            return {
                'patient_info': patient,
                'cases': cases,
                'visit_patterns': visit_patterns
            }

    @staticmethod
    def create_case_v2(case_data: dict[str, Any]) -> str:
        """Create a new medical case with V2.0 schema."""
        case_id = str(uuid.uuid4())
        
        with get_db_connection() as conn:
            # Start transaction
            conn.execute("BEGIN")
            
            try:
                # Serialize AI assessment if present
                ai_assessment_json = None
                if case_data.get("ai_assessment"):
                    ai_assessment_json = json.dumps(case_data["ai_assessment"])
                
                # Insert case
                conn.execute(
                    """
                    INSERT INTO cases_v2 (
                        case_id, patient_id, healthcare_worker_id, visit_datetime,
                        case_type, chief_complaint, symptoms, ai_assessment, urgency_level,
                        recommendations, follow_up_required, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        case_id,
                        case_data["patient_id"],
                        case_data.get("healthcare_worker_id", "HW001"),
                        case_data.get("visit_datetime", datetime.now().isoformat()),
                        case_data.get("case_type", "Assessment"),
                        case_data.get("chief_complaint"),
                        case_data["symptoms"],
                        ai_assessment_json,
                        case_data.get("urgency_level", "Medium"),
                        case_data.get("recommendations"),
                        case_data.get("follow_up_required", False),
                        case_data.get("notes")
                    )
                )
                
                # Update visit patterns within same transaction
                DatabaseManager._update_visit_pattern_with_connection(conn, case_data["patient_id"])
                
                # Commit transaction
                conn.commit()
                return case_id
                
            except Exception as e:
                # Rollback on error
                conn.rollback()
                raise e

    @staticmethod
    def _update_visit_pattern_with_connection(conn: sqlite3.Connection, patient_id: str) -> None:
        """Update visit pattern for a patient using existing connection."""
        # Get recent visits count (last 30 days)
        cursor = conn.execute(
            """
            SELECT COUNT(*) FROM cases_v2 
            WHERE patient_id = ? AND visit_datetime >= datetime('now', '-30 days')
            """,
            (patient_id,)
        )
        recent_visits = cursor.fetchone()[0]
        
        # Get last visit date
        cursor = conn.execute(
            """
            SELECT MAX(visit_datetime) FROM cases_v2 
            WHERE patient_id = ?
            """,
            (patient_id,)
        )
        last_visit = cursor.fetchone()[0]
        
        # Determine pattern type and concern level
        pattern_type = "Normal"
        concern_level = "None"
        
        if recent_visits >= 5:
            pattern_type = "Frequent"
            concern_level = "High"
        elif recent_visits >= 3:
            pattern_type = "Frequent"
            concern_level = "Medium"
        
        # Check for repeat visits (within 7 days)
        if last_visit:
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM cases_v2 
                WHERE patient_id = ? AND visit_datetime >= datetime('now', '-7 days')
                """,
                (patient_id,)
            )
            recent_week_visits = cursor.fetchone()[0]
            
            if recent_week_visits >= 2:
                if recent_week_visits >= 3:
                    pattern_type = "Emergency"
                    concern_level = "High"
                else:
                    pattern_type = "Follow-up"
                    concern_level = "Medium"
        
        # Insert or update visit pattern
        pattern_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT OR REPLACE INTO visit_patterns (
                pattern_id, patient_id, visit_frequency, last_visit_date,
                pattern_type, concern_level, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (pattern_id, patient_id, recent_visits, last_visit, pattern_type, concern_level)
        )

    @staticmethod
    def update_visit_pattern(patient_id: str) -> None:
        """Update visit pattern for a patient (external interface)."""
        with get_db_connection() as conn:
            DatabaseManager._update_visit_pattern_with_connection(conn, patient_id)
            conn.commit()

    @staticmethod
    def check_visit_alerts(patient_id: str) -> dict[str, Any]:
        """Check for repeat visit alerts and patterns."""
        with get_db_connection() as conn:
            # Get visit pattern
            cursor = conn.execute(
                "SELECT * FROM visit_patterns WHERE patient_id = ?",
                (patient_id,)
            )
            pattern_row = cursor.fetchone()
            
            if not pattern_row:
                return {
                    'has_alerts': False,
                    'alert_level': 'green',
                    'alert_type': 'none',
                    'last_visit': None,
                    'pattern_analysis': {
                        'visits_last_30_days': 0,
                        'average_interval': None,
                        'concerning_pattern': False,
                        'pattern_type': None
                    },
                    'recommendations': ['Continue regular monitoring']
                }
            
            pattern = dict(pattern_row)
            
            # Get last visit details
            cursor = conn.execute(
                """
                SELECT * FROM cases_v2 
                WHERE patient_id = ? 
                ORDER BY visit_datetime DESC 
                LIMIT 1
                """,
                (patient_id,)
            )
            last_visit_row = cursor.fetchone()
            last_visit = dict(last_visit_row) if last_visit_row else None
            
            # Determine alert level
            alert_level = "green"
            alert_type = "none"
            has_alerts = False
            
            if pattern['concern_level'] == 'High':
                alert_level = "red"
                has_alerts = True
                if pattern['pattern_type'] == 'Emergency':
                    alert_type = "emergency_return"
                else:
                    alert_type = "frequent_visitor"
            elif pattern['concern_level'] == 'Medium':
                alert_level = "orange"
                has_alerts = True
                alert_type = "repeat_visit"
            elif pattern['pattern_type'] == 'Frequent':
                alert_level = "yellow"
                has_alerts = True
                alert_type = "frequent_visitor"
            
            # Calculate days since last visit
            days_ago = 0
            if last_visit and last_visit['visit_datetime']:
                last_visit_date = datetime.fromisoformat(last_visit['visit_datetime'])
                days_ago = (datetime.now() - last_visit_date).days
            
            return {
                'has_alerts': has_alerts,
                'alert_level': alert_level,
                'alert_type': alert_type,
                'last_visit': {
                    'date': last_visit['visit_datetime'] if last_visit else None,
                    'days_ago': days_ago,
                    'chief_complaint': last_visit.get('chief_complaint') if last_visit else None,
                    'urgency_level': last_visit.get('urgency_level') if last_visit else None
                } if last_visit else None,
                'pattern_analysis': {
                    'visits_last_30_days': pattern['visit_frequency'],
                    'average_interval': None,  # Could be calculated if needed
                    'concerning_pattern': pattern['concern_level'] in ['Medium', 'High'],
                    'pattern_type': pattern['pattern_type']
                },
                'recommendations': DatabaseManager._get_alert_recommendations(pattern, last_visit)
            }

    @staticmethod
    def _get_alert_recommendations(pattern: dict, last_visit: dict) -> list[str]:
        """Get recommendations based on visit pattern."""
        recommendations = []
        
        if pattern['concern_level'] == 'High':
            recommendations.append("Immediate medical attention recommended")
            recommendations.append("Consider specialist referral")
            recommendations.append("Review treatment effectiveness")
        elif pattern['concern_level'] == 'Medium':
            recommendations.append("Monitor patient closely")
            recommendations.append("Review previous treatment effectiveness")
            recommendations.append("Consider follow-up appointment")
        elif pattern['pattern_type'] == 'Frequent':
            recommendations.append("Investigate underlying causes")
            recommendations.append("Consider preventive care measures")
        
        if not recommendations:
            recommendations.append("Continue regular monitoring")
        
        return recommendations

    @staticmethod
    def get_case_v2(case_id: str) -> Optional[dict[str, Any]]:
        """Get a V2 case by ID."""
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT c.*, p.first_name || ' ' || p.last_name as patient_name
                FROM cases_v2 c
                LEFT JOIN patients p ON c.patient_id = p.patient_id
                WHERE c.case_id = ?
                """,
                (case_id,)
            )
            row = cursor.fetchone()
            
            if row:
                case = dict(row)
                # Map case_id to id for API consistency
                case['id'] = case['case_id']
                
                # Parse JSON fields
                if case.get('ai_assessment'):
                    case['ai_assessment'] = json.loads(case['ai_assessment'])
                if case.get('photos'):
                    case['photos'] = json.loads(case['photos'])
                if case.get('medications_prescribed'):
                    case['medications_prescribed'] = json.loads(case['medications_prescribed'])
                
                # Map V2 case_status to standard API status
                if case.get('case_status') == 'Open':
                    case['status'] = 'new'
                elif case.get('case_status') == 'Closed':
                    case['status'] = 'closed'
                else:
                    case['status'] = case.get('case_status', 'new').lower()
                
                return case
            return None

    @staticmethod
    def update_case_v2_status(case_id: str, status: str) -> bool:
        """Update the status of a V2 case."""
        with get_db_connection() as conn:
            # Map status to V2 case_status values
            status_map = {
                "new": "Open",
                "reviewed": "Closed",
                "closed": "Closed"
            }
            mapped_status = status_map.get(status.lower(), "Open")
            
            cursor = conn.execute(
                """
                UPDATE cases_v2
                SET case_status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE case_id = ?
                """,
                (mapped_status, case_id)
            )
            conn.commit()
            return cursor.rowcount > 0

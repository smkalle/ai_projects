"""Database module for Medical AI Assistant MVP."""

import json
import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
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
        # Create users table
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

        # Create cases table
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

        # Create sync queue table
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

        conn.commit()

    logger.info("Database initialization complete")


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
        status: Optional[str] = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get cases with optional status filter."""
        with get_db_connection() as conn:
            if status:
                cursor = conn.execute(
                    """
                    SELECT * FROM cases
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (status, limit),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM cases
                    ORDER BY created_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            cases = []
            for row in cursor.fetchall():
                case = dict(row)
                # Parse JSON fields
                case["patient_data"] = json.loads(case["patient_data"])
                case["ai_assessment"] = (
                    json.loads(case["ai_assessment"]) if case["ai_assessment"] else None
                )
                case["photo_paths"] = (
                    json.loads(case["photo_paths"]) if case["photo_paths"] else []
                )
                cases.append(case)

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
        """Get database statistics for monitoring."""
        try:
            with get_db_connection() as conn:
                # Total cases
                cursor = conn.execute("SELECT COUNT(*) as total FROM cases")
                total_cases = cursor.fetchone()[0]

                # Cases today
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) as today 
                    FROM cases 
                    WHERE DATE(created_at) = DATE('now')
                    """
                )
                cases_today = cursor.fetchone()[0]

                # Pending reviews
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) as pending 
                    FROM cases 
                    WHERE status = 'new' OR status = 'pending'
                    """
                )
                pending_reviews = cursor.fetchone()[0]

                # Cases by urgency
                cursor = conn.execute(
                    """
                    SELECT 
                        JSON_EXTRACT(ai_assessment, '$.urgency') as urgency,
                        COUNT(*) as count
                    FROM cases 
                    WHERE ai_assessment IS NOT NULL
                    GROUP BY urgency
                    """
                )
                urgency_stats = {row[0]: row[1] for row in cursor.fetchall() if row[0]}

                return {
                    "total_cases": total_cases,
                    "cases_today": cases_today,
                    "pending_reviews": pending_reviews,
                    "urgency_distribution": urgency_stats,
                    "last_updated": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                "total_cases": 0,
                "cases_today": 0,
                "pending_reviews": 0,
                "urgency_distribution": {},
                "error": str(e)
            }

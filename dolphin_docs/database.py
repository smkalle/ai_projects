"""
SQLite Database for Dolphin Extraction Results
Stores and manages extraction results with full query capabilities
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DolphinDatabase:
    """
    SQLite database for storing Dolphin extraction results
    """
    
    def __init__(self, db_path: str = "./data/dolphin_extractions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Database initialized at: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    total_files INTEGER,
                    successful_files INTEGER,
                    failed_files INTEGER,
                    total_processing_time REAL,
                    config TEXT,
                    status TEXT
                )
            """)
            
            # Files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    file_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    file_type TEXT,
                    file_size INTEGER,
                    file_hash TEXT,
                    page_count INTEGER,
                    upload_time TIMESTAMP,
                    processing_start TIMESTAMP,
                    processing_end TIMESTAMP,
                    processing_time REAL,
                    status TEXT,
                    error_message TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Extractions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    extraction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    page_number INTEGER,
                    extraction_type TEXT,
                    extraction_stage TEXT,
                    confidence_score REAL,
                    extracted_data TEXT,
                    anchor_bbox TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(file_id)
                )
            """)
            
            # Patient info table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patient_info (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    patient_name TEXT,
                    patient_mrn TEXT,
                    date_of_birth TEXT,
                    gender TEXT,
                    phone TEXT,
                    address TEXT,
                    extracted_time TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(file_id)
                )
            """)
            
            # Medications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medications (
                    medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    patient_id INTEGER,
                    drug_name TEXT,
                    strength TEXT,
                    dosage_form TEXT,
                    sig TEXT,
                    quantity TEXT,
                    refills INTEGER,
                    prescriber TEXT,
                    prescribed_date TEXT,
                    extracted_time TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(file_id),
                    FOREIGN KEY (patient_id) REFERENCES patient_info(patient_id)
                )
            """)
            
            # Lab results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lab_results (
                    lab_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    patient_id INTEGER,
                    test_name TEXT,
                    test_date TEXT,
                    result_value TEXT,
                    unit TEXT,
                    reference_range TEXT,
                    flag TEXT,
                    status TEXT,
                    extracted_time TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(file_id),
                    FOREIGN KEY (patient_id) REFERENCES patient_info(patient_id)
                )
            """)
            
            # Diagnoses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diagnoses (
                    diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    patient_id INTEGER,
                    diagnosis_description TEXT,
                    icd10_code TEXT,
                    diagnosis_type TEXT,
                    status TEXT,
                    diagnosed_date TEXT,
                    extracted_time TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files(file_id),
                    FOREIGN KEY (patient_id) REFERENCES patient_info(patient_id)
                )
            """)
            
            # Extraction metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extraction_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    stage_name TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration REAL,
                    items_processed INTEGER,
                    items_failed INTEGER,
                    avg_confidence REAL,
                    memory_usage_mb REAL,
                    FOREIGN KEY (file_id) REFERENCES files(file_id)
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_session ON files(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_status ON files(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_extractions_file ON extractions(file_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_file ON patient_info(file_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_medications_file ON medications(file_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_lab_file ON lab_results(file_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_diagnoses_file ON diagnoses(file_id)")
            
            conn.commit()
            
            logger.info("Database schema initialized")
    
    def create_session(self, session_id: str, config: Dict[str, Any]) -> bool:
        """Create a new extraction session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (session_id, start_time, config, status)
                    VALUES (?, ?, ?, ?)
                """, (
                    session_id,
                    datetime.now(),
                    json.dumps(config),
                    "active"
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return False
    
    def update_session(self, session_id: str, **kwargs):
        """Update session information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build update query dynamically
                update_fields = []
                values = []
                
                for key, value in kwargs.items():
                    update_fields.append(f"{key} = ?")
                    values.append(value)
                
                values.append(session_id)
                
                query = f"""
                    UPDATE sessions 
                    SET {', '.join(update_fields)}
                    WHERE session_id = ?
                """
                
                cursor.execute(query, values)
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating session: {e}")
    
    def add_file(self, file_info: Dict[str, Any]) -> bool:
        """Add file record to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO files (
                        file_id, session_id, file_name, file_path, file_type,
                        file_size, file_hash, page_count, upload_time, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_info.get("file_id"),
                    file_info.get("session_id"),
                    file_info.get("file_name"),
                    file_info.get("file_path"),
                    file_info.get("file_type"),
                    file_info.get("file_size"),
                    file_info.get("file_hash"),
                    file_info.get("page_count"),
                    datetime.now(),
                    "pending"
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding file: {e}")
            return False
    
    def update_file_status(self, file_id: str, status: str, **kwargs):
        """Update file processing status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Base update
                cursor.execute("""
                    UPDATE files 
                    SET status = ?, processing_end = ?
                    WHERE file_id = ?
                """, (status, datetime.now(), file_id))
                
                # Additional updates
                if "processing_time" in kwargs:
                    cursor.execute("""
                        UPDATE files 
                        SET processing_time = ?
                        WHERE file_id = ?
                    """, (kwargs["processing_time"], file_id))
                
                if "error_message" in kwargs:
                    cursor.execute("""
                        UPDATE files 
                        SET error_message = ?
                        WHERE file_id = ?
                    """, (kwargs["error_message"], file_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating file status: {e}")
    
    def save_extraction(self, file_id: str, extraction_data: Dict[str, Any]):
        """Save extraction results to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Save raw extraction data
                for page_data in extraction_data.get("pages", []):
                    page_num = page_data.get("page_number", 0)
                    
                    for section, data in page_data.get("extracted_data", {}).items():
                        cursor.execute("""
                            INSERT INTO extractions (
                                file_id, page_number, extraction_type, 
                                extraction_stage, confidence_score, 
                                extracted_data, timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            file_id,
                            page_num,
                            section,
                            "completed",
                            page_data.get("analysis", {}).get("confidence", 0),
                            json.dumps(data),
                            datetime.now()
                        ))
                
                # Save aggregated data
                aggregated = extraction_data.get("aggregated_data", {})
                
                # Save patient info
                patient_info = aggregated.get("patient_info", {})
                if patient_info:
                    cursor.execute("""
                        INSERT INTO patient_info (
                            file_id, patient_name, patient_mrn, 
                            date_of_birth, gender, phone, address, extracted_time
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_id,
                        patient_info.get("patient_name", ""),
                        patient_info.get("patient_id", ""),
                        patient_info.get("dob", ""),
                        patient_info.get("gender", ""),
                        patient_info.get("phone", ""),
                        patient_info.get("address", ""),
                        datetime.now()
                    ))
                    patient_id = cursor.lastrowid
                else:
                    patient_id = None
                
                # Save medications
                for med in aggregated.get("medications", []):
                    cursor.execute("""
                        INSERT INTO medications (
                            file_id, patient_id, drug_name, strength,
                            dosage_form, sig, quantity, refills,
                            prescriber, extracted_time
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_id,
                        patient_id,
                        med.get("name", ""),
                        med.get("strength", ""),
                        med.get("form", ""),
                        med.get("sig", ""),
                        med.get("quantity", ""),
                        med.get("refills", 0),
                        med.get("prescriber", ""),
                        datetime.now()
                    ))
                
                # Save lab results
                for lab_group in aggregated.get("lab_results", []):
                    if "rows" in lab_group:
                        headers = lab_group.get("headers", [])
                        for row in lab_group.get("rows", []):
                            if len(row) >= 4:
                                cursor.execute("""
                                    INSERT INTO lab_results (
                                        file_id, patient_id, test_name, 
                                        result_value, unit, reference_range,
                                        status, extracted_time
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    file_id,
                                    patient_id,
                                    row[0] if len(row) > 0 else "",
                                    row[1] if len(row) > 1 else "",
                                    row[2] if len(row) > 2 else "",
                                    row[3] if len(row) > 3 else "",
                                    row[4] if len(row) > 4 else "Normal",
                                    datetime.now()
                                ))
                
                # Save diagnoses
                for diag in aggregated.get("diagnoses", []):
                    cursor.execute("""
                        INSERT INTO diagnoses (
                            file_id, patient_id, diagnosis_description,
                            icd10_code, diagnosis_type, status,
                            extracted_time
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_id,
                        patient_id,
                        diag.get("description", ""),
                        diag.get("icd10", ""),
                        diag.get("type", "primary"),
                        diag.get("status", "active"),
                        datetime.now()
                    ))
                
                conn.commit()
                logger.info(f"Extraction data saved for file: {file_id}")
                
        except Exception as e:
            logger.error(f"Error saving extraction data: {e}")
    
    def save_metrics(self, file_id: str, metrics: Dict[str, Any]):
        """Save extraction metrics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for stage_name, stage_metrics in metrics.items():
                    cursor.execute("""
                        INSERT INTO extraction_metrics (
                            file_id, stage_name, start_time, end_time,
                            duration, items_processed, items_failed,
                            avg_confidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        file_id,
                        stage_name,
                        stage_metrics.get("start_time"),
                        stage_metrics.get("end_time"),
                        stage_metrics.get("duration"),
                        stage_metrics.get("items_processed", 0),
                        stage_metrics.get("items_failed", 0),
                        stage_metrics.get("avg_confidence", 0)
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute("""
                SELECT * FROM sessions WHERE session_id = ?
            """, (session_id,))
            session = cursor.fetchone()
            
            if not session:
                return {}
            
            # Get file statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    AVG(processing_time) as avg_processing_time,
                    SUM(page_count) as total_pages
                FROM files 
                WHERE session_id = ?
            """, (session_id,))
            file_stats = cursor.fetchone()
            
            # Get extraction statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT e.file_id) as files_with_extractions,
                    COUNT(*) as total_extractions,
                    AVG(e.confidence_score) as avg_confidence
                FROM extractions e
                JOIN files f ON e.file_id = f.file_id
                WHERE f.session_id = ?
            """, (session_id,))
            extraction_stats = cursor.fetchone()
            
            return {
                "session_id": session_id,
                "start_time": session["start_time"],
                "status": session["status"],
                "total_files": file_stats["total_files"] or 0,
                "completed_files": file_stats["completed"] or 0,
                "failed_files": file_stats["failed"] or 0,
                "avg_processing_time": file_stats["avg_processing_time"] or 0,
                "total_pages": file_stats["total_pages"] or 0,
                "total_extractions": extraction_stats["total_extractions"] or 0,
                "avg_confidence": extraction_stats["avg_confidence"] or 0
            }
    
    def get_file_extractions(self, file_id: str) -> List[Dict[str, Any]]:
        """Get all extractions for a file"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get patient info
            cursor.execute("""
                SELECT * FROM patient_info WHERE file_id = ?
            """, (file_id,))
            patient = cursor.fetchone()
            
            # Get medications
            cursor.execute("""
                SELECT * FROM medications WHERE file_id = ?
            """, (file_id,))
            medications = cursor.fetchall()
            
            # Get lab results
            cursor.execute("""
                SELECT * FROM lab_results WHERE file_id = ?
            """, (file_id,))
            lab_results = cursor.fetchall()
            
            # Get diagnoses
            cursor.execute("""
                SELECT * FROM diagnoses WHERE file_id = ?
            """, (file_id,))
            diagnoses = cursor.fetchall()
            
            return {
                "patient_info": dict(patient) if patient else {},
                "medications": [dict(m) for m in medications],
                "lab_results": [dict(l) for l in lab_results],
                "diagnoses": [dict(d) for d in diagnoses]
            }
    
    def search_patients(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for patients by name or MRN"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT p.*, f.file_name, f.upload_time
                FROM patient_info p
                JOIN files f ON p.file_id = f.file_id
                WHERE p.patient_name LIKE ? OR p.patient_mrn LIKE ?
                ORDER BY f.upload_time DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_extractions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent extraction activities"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    f.file_id, f.file_name, f.status, f.processing_time,
                    f.upload_time, f.page_count,
                    COUNT(e.extraction_id) as extraction_count
                FROM files f
                LEFT JOIN extractions e ON f.file_id = e.file_id
                GROUP BY f.file_id
                ORDER BY f.upload_time DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def export_session_data(self, session_id: str, output_path: str):
        """Export all session data to JSON"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all files in session
            cursor.execute("""
                SELECT file_id FROM files WHERE session_id = ?
            """, (session_id,))
            files = cursor.fetchall()
            
            export_data = {
                "session_id": session_id,
                "export_time": datetime.now().isoformat(),
                "statistics": self.get_session_stats(session_id),
                "files": []
            }
            
            for file_row in files:
                file_id = file_row["file_id"]
                
                # Get file info
                cursor.execute("""
                    SELECT * FROM files WHERE file_id = ?
                """, (file_id,))
                file_info = dict(cursor.fetchone())
                
                # Get extractions
                file_info["extractions"] = self.get_file_extractions(file_id)
                
                export_data["files"].append(file_info)
            
            # Save to file
            output_file = Path(output_path)
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Session data exported to: {output_file}")
            return str(output_file)
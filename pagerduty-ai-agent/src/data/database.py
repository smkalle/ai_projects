"""
Database management for PagerDuty AI Agent.

Handles database connections, operations, and queries.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from .models import Base, Incident, Service, IncidentNote, IncidentStats, ServiceStats
from .models import IncidentStatus, IncidentUrgency, ServiceType

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for incident data."""

    def __init__(self, database_url: str):
        """Initialize database manager."""
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        """Initialize database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def get_db(self) -> Session:
        """Get database session."""
        db = self.SessionLocal()
        try:
            return db
        except SQLAlchemyError as e:
            db.close()
            logger.error(f"Error creating database session: {e}")
            raise

    def close_db(self, db: Session):
        """Close database session."""
        try:
            db.close()
        except SQLAlchemyError as e:
            logger.error(f"Error closing database session: {e}")

    # Service operations

    def create_service(self, name: str, service_type: str, description: str = None) -> Service:
        """Create a new service."""
        db = self.get_db()
        try:
            service = Service(
                name=name,
                service_type=service_type,
                description=description
            )
            db.add(service)
            db.commit()
            db.refresh(service)
            logger.info(f"Created service: {service.name}")
            return service
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating service: {e}")
            raise
        finally:
            self.close_db(db)

    def get_services(self) -> List[Service]:
        """Get all services."""
        db = self.get_db()
        try:
            services = db.query(Service).all()
            return services
        except SQLAlchemyError as e:
            logger.error(f"Error fetching services: {e}")
            raise
        finally:
            self.close_db(db)

    def get_service_by_name(self, name: str) -> Optional[Service]:
        """Get service by name."""
        db = self.get_db()
        try:
            service = db.query(Service).filter(Service.name == name).first()
            return service
        except SQLAlchemyError as e:
            logger.error(f"Error fetching service by name: {e}")
            raise
        finally:
            self.close_db(db)

    # Incident operations

    def create_incident(self, title: str, service_id: int, description: str = None, 
                       urgency: str = IncidentUrgency.MEDIUM, 
                       assigned_to: str = None) -> Incident:
        """Create a new incident."""
        db = self.get_db()
        try:
            incident = Incident(
                title=title,
                description=description,
                service_id=service_id,
                urgency=urgency,
                assigned_to=assigned_to
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            logger.info(f"Created incident: {incident.title}")
            return incident
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating incident: {e}")
            raise
        finally:
            self.close_db(db)

    def get_incidents(self, status: str = None, urgency: str = None, 
                     service_id: int = None, limit: int = 100) -> List[Incident]:
        """Get incidents with optional filters."""
        db = self.get_db()
        try:
            query = db.query(Incident)

            if status:
                query = query.filter(Incident.status == status)
            if urgency:
                query = query.filter(Incident.urgency == urgency)
            if service_id:
                query = query.filter(Incident.service_id == service_id)

            incidents = query.order_by(Incident.created_at.desc()).limit(limit).all()
            return incidents
        except SQLAlchemyError as e:
            logger.error(f"Error fetching incidents: {e}")
            raise
        finally:
            self.close_db(db)

    def update_incident_status(self, incident_id: int, status: str) -> Optional[Incident]:
        """Update incident status."""
        db = self.get_db()
        try:
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if not incident:
                return None

            incident.status = status
            if status == IncidentStatus.ACKNOWLEDGED:
                incident.acknowledged_at = datetime.utcnow()
            elif status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.utcnow()

            db.commit()
            db.refresh(incident)
            logger.info(f"Updated incident {incident_id} status to {status}")
            return incident
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating incident status: {e}")
            raise
        finally:
            self.close_db(db)

    def get_incidents_by_timeframe(self, hours: int = 24) -> List[Incident]:
        """Get incidents from the last N hours."""
        db = self.get_db()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            incidents = db.query(Incident).filter(
                Incident.created_at >= cutoff_time
            ).order_by(Incident.created_at.desc()).all()
            return incidents
        except SQLAlchemyError as e:
            logger.error(f"Error fetching incidents by timeframe: {e}")
            raise
        finally:
            self.close_db(db)

    # Analytics and statistics

    def get_incident_stats(self) -> Dict[str, Any]:
        """Get incident statistics."""
        db = self.get_db()
        try:
            # Basic counts
            total = db.query(Incident).count()
            open_incidents = db.query(Incident).filter(
                Incident.status.in_([IncidentStatus.TRIGGERED, IncidentStatus.ACKNOWLEDGED])
            ).count()
            resolved = db.query(Incident).filter(Incident.status == IncidentStatus.RESOLVED).count()
            high_priority = db.query(Incident).filter(
                Incident.urgency.in_([IncidentUrgency.HIGH, IncidentUrgency.CRITICAL])
            ).count()

            # Average resolution time
            resolved_incidents = db.query(Incident).filter(
                and_(Incident.status == IncidentStatus.RESOLVED, 
                     Incident.resolved_at.isnot(None))
            ).all()

            avg_resolution_hours = None
            if resolved_incidents:
                total_resolution_time = sum([
                    (inc.resolved_at - inc.created_at).total_seconds() / 3600
                    for inc in resolved_incidents
                ])
                avg_resolution_hours = total_resolution_time / len(resolved_incidents)

            return {
                "total": total,
                "open": open_incidents,
                "resolved": resolved,
                "high_priority": high_priority,
                "avg_resolution_hours": avg_resolution_hours
            }
        except SQLAlchemyError as e:
            logger.error(f"Error fetching incident stats: {e}")
            raise
        finally:
            self.close_db(db)

    def get_service_stats(self) -> List[Dict[str, Any]]:
        """Get statistics by service."""
        db = self.get_db()
        try:
            services = db.query(Service).all()
            service_stats = []

            for service in services:
                total_incidents = db.query(Incident).filter(
                    Incident.service_id == service.id
                ).count()

                open_incidents = db.query(Incident).filter(
                    and_(Incident.service_id == service.id,
                         Incident.status.in_([IncidentStatus.TRIGGERED, IncidentStatus.ACKNOWLEDGED]))
                ).count()

                # Average resolution time for this service
                resolved_incidents = db.query(Incident).filter(
                    and_(Incident.service_id == service.id,
                         Incident.status == IncidentStatus.RESOLVED,
                         Incident.resolved_at.isnot(None))
                ).all()

                avg_resolution_hours = None
                if resolved_incidents:
                    total_resolution_time = sum([
                        (inc.resolved_at - inc.created_at).total_seconds() / 3600
                        for inc in resolved_incidents
                    ])
                    avg_resolution_hours = total_resolution_time / len(resolved_incidents)

                # Last incident date
                last_incident = db.query(Incident).filter(
                    Incident.service_id == service.id
                ).order_by(Incident.created_at.desc()).first()

                service_stats.append({
                    "service_name": service.name,
                    "service_type": service.service_type,
                    "total_incidents": total_incidents,
                    "open_incidents": open_incidents,
                    "avg_resolution_hours": avg_resolution_hours,
                    "last_incident_date": last_incident.created_at if last_incident else None
                })

            return service_stats
        except SQLAlchemyError as e:
            logger.error(f"Error fetching service stats: {e}")
            raise
        finally:
            self.close_db(db)

    # Data export for analysis

    def get_incidents_dataframe(self, limit: int = 1000) -> pd.DataFrame:
        """Get incidents as pandas DataFrame for analysis."""
        db = self.get_db()
        try:
            query = """
            SELECT 
                i.id, i.title, i.description, i.status, i.urgency,
                i.created_at, i.acknowledged_at, i.resolved_at,
                i.assigned_to, i.escalation_level,
                s.name as service_name, s.service_type,
                CASE 
                    WHEN i.resolved_at IS NOT NULL 
                    THEN (julianday(i.resolved_at) - julianday(i.created_at)) * 24 
                    ELSE NULL 
                END as resolution_time_hours
            FROM incidents i
            LEFT JOIN services s ON i.service_id = s.id
            ORDER BY i.created_at DESC
            LIMIT ?
            """

            df = pd.read_sql_query(query, self.engine, params=(limit,))

            # Convert datetime columns
            datetime_cols = ['created_at', 'acknowledged_at', 'resolved_at']
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])

            return df
        except Exception as e:
            logger.error(f"Error creating DataFrame: {e}")
            raise
        finally:
            self.close_db(db)

    def search_incidents(self, search_term: str, limit: int = 50) -> List[Incident]:
        """Search incidents by title or description."""
        db = self.get_db()
        try:
            incidents = db.query(Incident).filter(
                or_(
                    Incident.title.ilike(f"%{search_term}%"),
                    Incident.description.ilike(f"%{search_term}%")
                )
            ).order_by(Incident.created_at.desc()).limit(limit).all()
            return incidents
        except SQLAlchemyError as e:
            logger.error(f"Error searching incidents: {e}")
            raise
        finally:
            self.close_db(db)
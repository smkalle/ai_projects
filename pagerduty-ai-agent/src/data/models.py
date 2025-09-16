"""
Database models for PagerDuty AI Agent.

Defines SQLAlchemy models for incident management data.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()

class IncidentStatus(str, Enum):
    """Incident status enumeration."""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class IncidentUrgency(str, Enum):
    """Incident urgency enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ServiceType(str, Enum):
    """Service type enumeration."""
    WEB_APP = "web_app"
    DATABASE = "database"
    API = "api"
    EMAIL_SERVICE = "email_service"
    PAYMENT_SERVICE = "payment_service"
    AUTH_SERVICE = "auth_service"
    CDN = "cdn"
    MONITORING = "monitoring"

# SQLAlchemy Models

class Service(Base):
    """Service model."""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    service_type = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    incidents = relationship("Incident", back_populates="service")

class Incident(Base):
    """Incident model."""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default=IncidentStatus.TRIGGERED)
    urgency = Column(String(20), nullable=False, default=IncidentUrgency.MEDIUM)

    # Foreign Keys
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional fields
    assigned_to = Column(String(100), nullable=True)
    escalation_level = Column(Integer, default=1)

    # Relationships
    service = relationship("Service", back_populates="incidents")
    notes = relationship("IncidentNote", back_populates="incident")

class IncidentNote(Base):
    """Incident note model."""
    __tablename__ = "incident_notes"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    incident = relationship("Incident", back_populates="notes")

# Pydantic Models for API

class ServiceBase(BaseModel):
    """Base service schema."""
    name: str
    service_type: str
    description: Optional[str] = None

class ServiceCreate(ServiceBase):
    """Service creation schema."""
    pass

class ServiceResponse(ServiceBase):
    """Service response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IncidentBase(BaseModel):
    """Base incident schema."""
    title: str
    description: Optional[str] = None
    status: IncidentStatus = IncidentStatus.TRIGGERED
    urgency: IncidentUrgency = IncidentUrgency.MEDIUM
    service_id: int
    assigned_to: Optional[str] = None
    escalation_level: int = 1

class IncidentCreate(IncidentBase):
    """Incident creation schema."""
    pass

class IncidentUpdate(BaseModel):
    """Incident update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    urgency: Optional[IncidentUrgency] = None
    assigned_to: Optional[str] = None
    escalation_level: Optional[int] = None

class IncidentResponse(IncidentBase):
    """Incident response schema."""
    id: int
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    updated_at: datetime
    service: ServiceResponse

    class Config:
        from_attributes = True

class IncidentNoteBase(BaseModel):
    """Base incident note schema."""
    content: str
    author: str

class IncidentNoteCreate(IncidentNoteBase):
    """Incident note creation schema."""
    incident_id: int

class IncidentNoteResponse(IncidentNoteBase):
    """Incident note response schema."""
    id: int
    incident_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics models

class IncidentStats(BaseModel):
    """Incident statistics schema."""
    total: int
    open: int
    acknowledged: int
    resolved: int
    high_priority: int
    critical: int
    avg_resolution_time_hours: Optional[float] = None

class ServiceStats(BaseModel):
    """Service statistics schema."""
    service_name: str
    service_type: str
    total_incidents: int
    open_incidents: int
    avg_resolution_time_hours: Optional[float] = None
    last_incident_date: Optional[datetime] = None
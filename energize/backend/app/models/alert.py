"""Alert model for anomaly detection and notifications."""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class Alert(Base, BaseModel):
    """Alert model for tracking anomalies and issues."""
    
    __tablename__ = "alerts"
    
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # anomaly, threshold, system, maintenance
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    message = Column(Text)
    threshold_value = Column(Float)
    actual_value = Column(Float)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    # Relationships
    building = relationship("Building", back_populates="alerts")
    acknowledged_by_user = relationship("User", back_populates="acknowledged_alerts")
    
    def __repr__(self) -> str:
        return f"<Alert {self.alert_type} - {self.severity}>"
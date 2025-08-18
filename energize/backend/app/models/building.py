"""Building model for energy management."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class Building(Base, BaseModel):
    """Building model with location and metadata."""
    
    __tablename__ = "buildings"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    area_sqft = Column(Integer)
    building_type = Column(String(50))  # office, retail, industrial, residential
    timezone = Column(String(50), default="UTC")
    metadata = Column(JSON, default=dict)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="buildings")
    sensors = relationship("Sensor", back_populates="building", cascade="all, delete-orphan")
    energy_readings = relationship("EnergyReading", back_populates="building", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="building", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Building {self.name}>"
"""Sensor model for IoT device management."""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class Sensor(Base, BaseModel):
    """Sensor model for tracking IoT devices."""
    
    __tablename__ = "sensors"
    
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    sensor_type = Column(String(50), nullable=False)  # electricity, gas, water, temperature, humidity
    name = Column(String(255))
    location = Column(String(255))  # Floor 3, Room 301, HVAC Unit 2
    unit = Column(String(20))  # kWh, m³, °C, %
    status = Column(String(20), default="active")  # active, inactive, maintenance, error
    last_reading_at = Column(DateTime(timezone=True))
    metadata = Column(JSON, default=dict)
    
    # Relationships
    building = relationship("Building", back_populates="sensors")
    energy_readings = relationship("EnergyReading", back_populates="sensor", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Sensor {self.name or self.sensor_type} at {self.location}>"
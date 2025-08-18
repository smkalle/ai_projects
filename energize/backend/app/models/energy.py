"""Energy reading model for time-series data."""

from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class EnergyReading(Base):
    """Energy reading model for time-series data storage."""
    
    __tablename__ = "energy_readings"
    
    # Primary time column for TimescaleDB
    time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    
    value = Column(Float, nullable=False)
    quality_flag = Column(Integer, default=0)  # 0=good, 1=estimated, 2=manual, 3=error
    metadata = Column(JSON, default=dict)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="energy_readings")
    building = relationship("Building", back_populates="energy_readings")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_energy_readings_building_time", "building_id", "time"),
        Index("idx_energy_readings_sensor_time", "sensor_id", "time"),
    )
    
    def __repr__(self) -> str:
        return f"<EnergyReading {self.sensor_id} at {self.time}: {self.value}>"
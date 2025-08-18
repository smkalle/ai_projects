"""Tenant model for multi-tenancy."""

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class Tenant(Base, BaseModel):
    """Tenant model for multi-tenant architecture."""
    
    __tablename__ = "tenants"
    
    company_name = Column(String(255), nullable=False)
    subscription_plan = Column(String(50), default="trial")
    max_buildings = Column(Integer, default=5)
    max_users = Column(Integer, default=10)
    billing_email = Column(String(255))
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    buildings = relationship("Building", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Tenant {self.company_name}>"
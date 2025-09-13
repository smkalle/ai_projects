"""Database connection and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import streamlit as st

# Create declarative base
Base = declarative_base()

class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./hospital_booking.db")
        
        # Configure SQLite engine
        if database_url.startswith("sqlite"):
            self.engine = create_engine(
                database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=False  # Set to True for SQL debugging
            )
        else:
            self.engine = create_engine(database_url)
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_all_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def drop_all_tables(self):
        """Drop all database tables (for testing)."""
        Base.metadata.drop_all(bind=self.engine)

# Global database manager instance
@st.cache_resource
def get_database_manager():
    """Get cached database manager instance."""
    return DatabaseManager()

def get_db_session():
    """Get database session for use in Streamlit."""
    db_manager = get_database_manager()
    return db_manager.get_session()
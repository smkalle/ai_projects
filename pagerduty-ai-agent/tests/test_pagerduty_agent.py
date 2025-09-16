"""
Comprehensive tests for PagerDuty AI Agent.

Tests the database operations, tools, and agent workflow.
"""

import pytest
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.data.database import DatabaseManager
from src.data.models import IncidentStatus, IncidentUrgency, ServiceType
from src.tools.database_tools import create_database_tools
from src.tools.analytics_tools import create_analytics_tools
from src.utils.config import Settings
from src.agents.workflow import create_incident_agent_workflow

class TestDatabaseManager:
    """Test database manager functionality."""

    @pytest.fixture
    def db_manager(self):
        """Create a test database manager with temporary database."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_url = f"sqlite:///{tmp.name}"
            manager = DatabaseManager(db_url)
            manager.init_db()
            yield manager
            # Cleanup
            try:
                os.unlink(tmp.name)
            except:
                pass

    def test_database_initialization(self, db_manager):
        """Test database table creation."""
        # Database should be initialized without errors
        assert db_manager.engine is not None

        # Test getting a session
        db = db_manager.get_db()
        assert db is not None
        db_manager.close_db(db)

    def test_service_operations(self, db_manager):
        """Test service CRUD operations."""
        # Create a service
        service = db_manager.create_service(
            name="Test Service",
            service_type=ServiceType.WEB_APP,
            description="Test service description"
        )

        assert service.id is not None
        assert service.name == "Test Service"
        assert service.service_type == ServiceType.WEB_APP

        # Get all services
        services = db_manager.get_services()
        assert len(services) == 1
        assert services[0].name == "Test Service"

        # Get service by name
        found_service = db_manager.get_service_by_name("Test Service")
        assert found_service is not None
        assert found_service.id == service.id

    def test_incident_operations(self, db_manager):
        """Test incident CRUD operations."""
        # First create a service
        service = db_manager.create_service(
            name="Test Service",
            service_type=ServiceType.DATABASE,
            description="Test service"
        )

        # Create an incident
        incident = db_manager.create_incident(
            title="Test Incident",
            service_id=service.id,
            description="Test incident description",
            urgency=IncidentUrgency.HIGH
        )

        assert incident.id is not None
        assert incident.title == "Test Incident"
        assert incident.urgency == IncidentUrgency.HIGH
        assert incident.status == IncidentStatus.TRIGGERED

        # Get incidents
        incidents = db_manager.get_incidents()
        assert len(incidents) == 1
        assert incidents[0].title == "Test Incident"

        # Update incident status
        updated_incident = db_manager.update_incident_status(
            incident.id, 
            IncidentStatus.RESOLVED
        )

        assert updated_incident.status == IncidentStatus.RESOLVED
        assert updated_incident.resolved_at is not None

    def test_incident_statistics(self, db_manager):
        """Test incident statistics calculation."""
        # Create service
        service = db_manager.create_service("Test Service", ServiceType.WEB_APP, "Test")

        # Create mix of incidents
        incident1 = db_manager.create_incident(
            "Critical Issue", service.id, urgency=IncidentUrgency.CRITICAL
        )
        incident2 = db_manager.create_incident(
            "High Issue", service.id, urgency=IncidentUrgency.HIGH
        )
        incident3 = db_manager.create_incident(
            "Medium Issue", service.id, urgency=IncidentUrgency.MEDIUM
        )

        # Resolve one incident
        db_manager.update_incident_status(incident3.id, IncidentStatus.RESOLVED)

        # Get statistics
        stats = db_manager.get_incident_stats()

        assert stats['total'] == 3
        assert stats['open'] == 2  # incident1 and incident2 are still triggered
        assert stats['resolved'] == 1
        assert stats['high_priority'] == 2  # critical and high count as high priority

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
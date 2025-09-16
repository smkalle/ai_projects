"""
Database initialization script for PagerDuty AI Agent.

Creates database tables and populates with sample data.
"""

import sys
import os
from datetime import datetime, timedelta
from random import choice, randint
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.config import load_config
from src.data.database import DatabaseManager
from src.data.models import IncidentStatus, IncidentUrgency, ServiceType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_services(db_manager: DatabaseManager):
    """Create sample services."""
    services_data = [
        ("Web Application", ServiceType.WEB_APP, "Main customer-facing web application"),
        ("User Database", ServiceType.DATABASE, "Primary user data storage"),
        ("Payment API", ServiceType.API, "Payment processing service"),
        ("Email Service", ServiceType.EMAIL_SERVICE, "Email notification system"),
        ("Authentication Service", ServiceType.AUTH_SERVICE, "User authentication and authorization"),
        ("Content CDN", ServiceType.CDN, "Content delivery network"),
        ("Monitoring System", ServiceType.MONITORING, "Application and infrastructure monitoring"),
        ("Order Database", ServiceType.DATABASE, "Order and transaction data"),
    ]

    logger.info("Creating sample services...")

    for name, service_type, description in services_data:
        try:
            existing_service = db_manager.get_service_by_name(name)
            if not existing_service:
                service = db_manager.create_service(name, service_type, description)
                logger.info(f"Created service: {service.name}")
            else:
                logger.info(f"Service already exists: {name}")
        except Exception as e:
            logger.error(f"Error creating service {name}: {e}")

def create_sample_incidents(db_manager: DatabaseManager):
    """Create sample incidents."""
    services = db_manager.get_services()
    if not services:
        logger.error("No services found. Cannot create incidents.")
        return

    # Sample incident templates
    incident_templates = [
        {
            "title": "Database connection timeout",
            "description": "Multiple connection timeouts reported to the database server",
            "urgency": IncidentUrgency.HIGH,
            "service_types": [ServiceType.DATABASE]
        },
        {
            "title": "High response times on web application",
            "description": "Users reporting slow page load times across the application",
            "urgency": IncidentUrgency.MEDIUM,
            "service_types": [ServiceType.WEB_APP]
        },
        {
            "title": "Payment processing failures",
            "description": "Payment transactions failing with gateway errors",
            "urgency": IncidentUrgency.CRITICAL,
            "service_types": [ServiceType.API]
        },
        {
            "title": "Email delivery delays",
            "description": "Email notifications are delayed by more than 30 minutes",
            "urgency": IncidentUrgency.MEDIUM,
            "service_types": [ServiceType.EMAIL_SERVICE]
        },
        {
            "title": "Authentication service down",
            "description": "Users unable to log in - authentication service not responding",
            "urgency": IncidentUrgency.CRITICAL,
            "service_types": [ServiceType.AUTH_SERVICE]
        },
    ]

    # Additional incident variations
    additional_titles = [
        "Memory usage spike detected",
        "Network connectivity issues",
        "Backup job failed",
        "Security scan alert",
        "Performance degradation",
        "Service health check failed",
        "Load balancer configuration error",
        "Database replication lag",
        "Queue processing delays",
        "Log aggregation system down"
    ]

    logger.info("Creating sample incidents...")

    # Create incidents from templates
    for template in incident_templates:
        # Find matching services
        matching_services = [s for s in services if s.service_type in template["service_types"]]
        if not matching_services:
            continue

        service = choice(matching_services)

        # Create multiple incidents with time variations
        for i in range(randint(1, 3)):
            # Random time in the past 30 days
            days_ago = randint(0, 30)
            hours_ago = randint(0, 23)
            created_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)

            # Determine status based on age and urgency
            if days_ago > 7 or template["urgency"] == IncidentUrgency.LOW:
                status = IncidentStatus.RESOLVED
            elif days_ago > 3:
                status = choice([IncidentStatus.RESOLVED, IncidentStatus.ACKNOWLEDGED])
            else:
                status = choice([IncidentStatus.TRIGGERED, IncidentStatus.ACKNOWLEDGED, IncidentStatus.RESOLVED])

            title = template["title"]
            if i > 0:
                title += f" (#{i+1})"

            try:
                incident = db_manager.create_incident(
                    title=title,
                    service_id=service.id,
                    description=template["description"],
                    urgency=template["urgency"]
                )

                # Update the created time and status
                db = db_manager.get_db()
                from src.data.models import Incident
                db_incident = db.query(Incident).filter_by(id=incident.id).first()
                if db_incident:
                    db_incident.created_at = created_time
                    db_incident.status = status
                    if status == IncidentStatus.ACKNOWLEDGED:
                        db_incident.acknowledged_at = created_time + timedelta(hours=randint(1, 4))
                    elif status == IncidentStatus.RESOLVED:
                        db_incident.acknowledged_at = created_time + timedelta(hours=randint(1, 2))
                        db_incident.resolved_at = created_time + timedelta(hours=randint(2, 48))
                    db.commit()
                db_manager.close_db(db)

                logger.info(f"Created incident: {incident.title}")

            except Exception as e:
                logger.error(f"Error creating incident {title}: {e}")

    # Create additional random incidents
    for title in additional_titles:
        service = choice(services)
        urgency = choice(list(IncidentUrgency))

        # Random time in the past 60 days
        days_ago = randint(0, 60)
        created_time = datetime.utcnow() - timedelta(days=days_ago, hours=randint(0, 23))

        status = IncidentStatus.RESOLVED if days_ago > 14 else choice(list(IncidentStatus))

        try:
            incident = db_manager.create_incident(
                title=title,
                service_id=service.id,
                description=f"Automated incident detection for {service.name}",
                urgency=urgency
            )

            # Update timestamps
            db = db_manager.get_db()
            from src.data.models import Incident
            db_incident = db.query(Incident).filter_by(id=incident.id).first()
            if db_incident:
                db_incident.created_at = created_time
                db_incident.status = status
                if status != IncidentStatus.TRIGGERED:
                    if status == IncidentStatus.ACKNOWLEDGED:
                        db_incident.acknowledged_at = created_time + timedelta(hours=randint(1, 6))
                    elif status == IncidentStatus.RESOLVED:
                        db_incident.acknowledged_at = created_time + timedelta(hours=randint(1, 3))
                        db_incident.resolved_at = created_time + timedelta(hours=randint(4, 72))
                db.commit()
            db_manager.close_db(db)

            logger.info(f"Created additional incident: {incident.title}")

        except Exception as e:
            logger.error(f"Error creating additional incident {title}: {e}")

def main():
    """Main initialization function."""
    try:
        logger.info("Starting database initialization...")

        # Load configuration
        config = load_config()

        # Initialize database manager
        db_manager = DatabaseManager(config.database_url)
        db_manager.init_db()

        # Create sample data
        create_sample_services(db_manager)
        create_sample_incidents(db_manager)

        # Print statistics
        stats = db_manager.get_incident_stats()
        logger.info("Database initialization completed successfully!")
        logger.info(f"Created {stats['total']} total incidents")
        logger.info(f"Services: {len(db_manager.get_services())}")
        logger.info(f"Open incidents: {stats['open']}")
        logger.info(f"Resolved incidents: {stats['resolved']}")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
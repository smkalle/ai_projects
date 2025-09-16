"""
Database tools for PagerDuty AI Agent.

LangChain tools for database interaction and incident management.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain.tools import BaseTool
import pandas as pd
from datetime import datetime, timedelta

from ..data.database import DatabaseManager
from ..data.models import IncidentStatus, IncidentUrgency, ServiceType

logger = logging.getLogger(__name__)

class DatabaseTools:
    """Database tools for the AI agent."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @tool
    def get_incident_count(self, status: str = None, urgency: str = None, hours: int = None) -> str:
        """
        Get the count of incidents with optional filters.

        Args:
            status: Filter by status (triggered, acknowledged, resolved)
            urgency: Filter by urgency (low, medium, high, critical)  
            hours: Only count incidents from the last N hours

        Returns:
            String describing the incident count
        """
        try:
            if hours:
                incidents = self.db_manager.get_incidents_by_timeframe(hours)
                if status:
                    incidents = [i for i in incidents if i.status == status]
                if urgency:
                    incidents = [i for i in incidents if i.urgency == urgency]
                count = len(incidents)
                time_desc = f"in the last {hours} hours"
            else:
                incidents = self.db_manager.get_incidents(status=status, urgency=urgency)
                count = len(incidents)
                time_desc = "total"

            filters = []
            if status:
                filters.append(f"status: {status}")
            if urgency:
                filters.append(f"urgency: {urgency}")

            filter_desc = f" ({', '.join(filters)})" if filters else ""

            return f"Found {count} incidents {time_desc}{filter_desc}."

        except Exception as e:
            logger.error(f"Error getting incident count: {e}")
            return f"Error retrieving incident count: {str(e)}"

    @tool
    def get_incident_stats(self) -> str:
        """
        Get comprehensive incident statistics.

        Returns:
            String with incident statistics summary
        """
        try:
            stats = self.db_manager.get_incident_stats()

            result = f"""📊 Incident Statistics:

• Total Incidents: {stats['total']}
• Open Incidents: {stats['open']} 
• Resolved Incidents: {stats['resolved']}
• High Priority: {stats['high_priority']}"""

            if stats['avg_resolution_hours']:
                result += f"\n• Average Resolution Time: {stats['avg_resolution_hours']:.1f} hours"

            return result

        except Exception as e:
            logger.error(f"Error getting incident stats: {e}")
            return f"Error retrieving incident statistics: {str(e)}"

    @tool
    def search_incidents(self, query: str, limit: int = 10) -> str:
        """
        Search incidents by title or description.

        Args:
            query: Search term to look for in incident title or description
            limit: Maximum number of results to return (default 10)

        Returns:
            String with search results
        """
        try:
            incidents = self.db_manager.search_incidents(query, limit=limit)

            if not incidents:
                return f"No incidents found matching '{query}'"

            result = f"🔍 Found {len(incidents)} incidents matching '{query}':\n\n"

            for incident in incidents:
                status_emoji = {"triggered": "🔴", "acknowledged": "🟡", "resolved": "🟢"}
                urgency_emoji = {"low": "🔵", "medium": "🟠", "high": "🔴", "critical": "⚫"}

                result += f"• **#{incident.id}** {incident.title}\n"
                result += f"  Status: {status_emoji.get(incident.status, '❓')} {incident.status.title()}\n"
                result += f"  Urgency: {urgency_emoji.get(incident.urgency, '❓')} {incident.urgency.title()}\n"
                result += f"  Created: {incident.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                if incident.description:
                    desc = incident.description[:100] + "..." if len(incident.description) > 100 else incident.description
                    result += f"  Description: {desc}\n"
                result += "\n"

            return result

        except Exception as e:
            logger.error(f"Error searching incidents: {e}")
            return f"Error searching incidents: {str(e)}"

    @tool
    def get_service_statistics(self) -> str:
        """
        Get statistics by service.

        Returns:
            String with service statistics
        """
        try:
            service_stats = self.db_manager.get_service_stats()

            if not service_stats:
                return "No service statistics available."

            result = "📊 Service Statistics:\n\n"

            # Sort by total incidents descending
            service_stats.sort(key=lambda x: x['total_incidents'], reverse=True)

            for stat in service_stats:
                result += f"**{stat['service_name']}** ({stat['service_type']})\n"
                result += f"  • Total Incidents: {stat['total_incidents']}\n"
                result += f"  • Open Incidents: {stat['open_incidents']}\n"

                if stat['avg_resolution_hours']:
                    result += f"  • Avg Resolution: {stat['avg_resolution_hours']:.1f}h\n"

                if stat['last_incident_date']:
                    result += f"  • Last Incident: {stat['last_incident_date'].strftime('%Y-%m-%d %H:%M')}\n"

                result += "\n"

            return result

        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return f"Error retrieving service statistics: {str(e)}"

    @tool  
    def get_recent_incidents(self, hours: int = 24, limit: int = 10) -> str:
        """
        Get recent incidents from the last N hours.

        Args:
            hours: Number of hours to look back (default 24)
            limit: Maximum number of incidents to return (default 10)

        Returns:
            String with recent incidents
        """
        try:
            incidents = self.db_manager.get_incidents_by_timeframe(hours)[:limit]

            if not incidents:
                return f"No incidents found in the last {hours} hours."

            result = f"🕐 Recent incidents (last {hours} hours):\n\n"

            for incident in incidents:
                status_emoji = {"triggered": "🔴", "acknowledged": "🟡", "resolved": "🟢"}
                urgency_emoji = {"low": "🔵", "medium": "🟠", "high": "🔴", "critical": "⚫"}

                time_ago = datetime.utcnow() - incident.created_at
                hours_ago = int(time_ago.total_seconds() / 3600)
                minutes_ago = int((time_ago.total_seconds() % 3600) / 60)

                if hours_ago > 0:
                    time_desc = f"{hours_ago}h {minutes_ago}m ago"
                else:
                    time_desc = f"{minutes_ago}m ago"

                result += f"• **#{incident.id}** {incident.title}\n"
                result += f"  {status_emoji.get(incident.status, '❓')} {incident.status.title()} | "
                result += f"{urgency_emoji.get(incident.urgency, '❓')} {incident.urgency.title()}\n"
                result += f"  Created: {time_desc}\n\n"

            return result

        except Exception as e:
            logger.error(f"Error getting recent incidents: {e}")
            return f"Error retrieving recent incidents: {str(e)}"

    @tool
    def calculate_resolution_metrics(self, service_name: str = None, days: int = 30) -> str:
        """
        Calculate resolution time metrics.

        Args:
            service_name: Optional service name to filter by
            days: Number of days to look back (default 30)

        Returns:
            String with resolution metrics
        """
        try:
            # Get data as DataFrame for easier analysis
            df = self.db_manager.get_incidents_dataframe()

            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            df = df[df['created_at'] >= cutoff_date]

            # Filter by service if specified
            if service_name:
                df = df[df['service_name'].str.lower() == service_name.lower()]
                title_suffix = f" for {service_name}"
            else:
                title_suffix = ""

            # Only resolved incidents with resolution time
            resolved_df = df[(df['status'] == 'resolved') & (df['resolution_time_hours'].notna())]

            if resolved_df.empty:
                return f"No resolved incidents found in the last {days} days{title_suffix}."

            # Calculate metrics
            avg_resolution = resolved_df['resolution_time_hours'].mean()
            median_resolution = resolved_df['resolution_time_hours'].median()
            min_resolution = resolved_df['resolution_time_hours'].min()
            max_resolution = resolved_df['resolution_time_hours'].max()
            total_resolved = len(resolved_df)

            # Resolution by urgency
            urgency_stats = resolved_df.groupby('urgency')['resolution_time_hours'].agg(['count', 'mean']).round(1)

            result = f"⏱️ Resolution Metrics (Last {days} days){title_suffix}:\n\n"
            result += f"**Overall Statistics:**\n"
            result += f"• Total Resolved: {total_resolved}\n"
            result += f"• Average Resolution: {avg_resolution:.1f} hours\n"
            result += f"• Median Resolution: {median_resolution:.1f} hours\n"
            result += f"• Fastest Resolution: {min_resolution:.1f} hours\n"
            result += f"• Slowest Resolution: {max_resolution:.1f} hours\n\n"

            if not urgency_stats.empty:
                result += "**By Urgency:**\n"
                for urgency, stats in urgency_stats.iterrows():
                    result += f"• {urgency.title()}: {stats['mean']:.1f}h avg ({int(stats['count'])} incidents)\n"

            return result

        except Exception as e:
            logger.error(f"Error calculating resolution metrics: {e}")
            return f"Error calculating resolution metrics: {str(e)}"

    @tool
    def update_incident_status(self, incident_id: int, new_status: str) -> str:
        """
        Update the status of an incident.

        Args:
            incident_id: ID of the incident to update
            new_status: New status (triggered, acknowledged, resolved)

        Returns:
            String confirming the update
        """
        try:
            valid_statuses = ['triggered', 'acknowledged', 'resolved']
            if new_status not in valid_statuses:
                return f"Invalid status '{new_status}'. Valid options: {', '.join(valid_statuses)}"

            incident = self.db_manager.update_incident_status(incident_id, new_status)

            if not incident:
                return f"Incident #{incident_id} not found."

            return f"✅ Successfully updated incident #{incident_id} status to '{new_status}'"

        except Exception as e:
            logger.error(f"Error updating incident status: {e}")
            return f"Error updating incident status: {str(e)}"

def create_database_tools(db_manager: DatabaseManager) -> List[BaseTool]:
    """Create database tools for the agent."""
    db_tools = DatabaseTools(db_manager)

    return [
        db_tools.get_incident_count,
        db_tools.get_incident_stats,
        db_tools.search_incidents,
        db_tools.get_service_statistics,
        db_tools.get_recent_incidents,
        db_tools.calculate_resolution_metrics,
        db_tools.update_incident_status,
    ]
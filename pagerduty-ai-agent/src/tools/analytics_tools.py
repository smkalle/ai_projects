"""
Analytics tools for PagerDuty AI Agent.

Advanced analytics and reporting tools.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
import pandas as pd
from datetime import datetime, timedelta

from ..data.database import DatabaseManager

logger = logging.getLogger(__name__)

class AnalyticsTools:
    """Analytics tools for the AI agent."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @tool
    def analyze_incident_trends(self, days: int = 30) -> str:
        """
        Analyze incident trends over time.

        Args:
            days: Number of days to analyze (default 30)

        Returns:
            String with trend analysis
        """
        try:
            df = self.db_manager.get_incidents_dataframe()

            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            df = df[df['created_at'] >= cutoff_date]

            if df.empty:
                return f"No incidents found in the last {days} days."

            # Group by date
            df['date'] = df['created_at'].dt.date
            daily_counts = df.groupby('date').size()

            # Calculate trend metrics
            total_incidents = len(df)
            avg_per_day = total_incidents / days

            # Get recent vs older comparison
            mid_point = cutoff_date + timedelta(days=days//2)
            recent_incidents = len(df[df['created_at'] >= mid_point])
            older_incidents = len(df[df['created_at'] < mid_point])

            trend_direction = "📈 Increasing" if recent_incidents > older_incidents else "📉 Decreasing" if recent_incidents < older_incidents else "➡️ Stable"

            # Status distribution
            status_counts = df['status'].value_counts()

            # Urgency distribution  
            urgency_counts = df['urgency'].value_counts()

            result = f"📊 Incident Trend Analysis (Last {days} days):\n\n"
            result += f"**Overview:**\n"
            result += f"• Total Incidents: {total_incidents}\n"
            result += f"• Average per Day: {avg_per_day:.1f}\n"
            result += f"• Trend: {trend_direction}\n"
            result += f"• Recent Half: {recent_incidents} incidents\n"
            result += f"• Older Half: {older_incidents} incidents\n\n"

            result += f"**Status Distribution:**\n"
            for status, count in status_counts.items():
                percentage = (count / total_incidents) * 100
                result += f"• {status.title()}: {count} ({percentage:.1f}%)\n"

            result += f"\n**Urgency Distribution:**\n"
            for urgency, count in urgency_counts.items():
                percentage = (count / total_incidents) * 100
                result += f"• {urgency.title()}: {count} ({percentage:.1f}%)\n"

            return result

        except Exception as e:
            logger.error(f"Error analyzing incident trends: {e}")
            return f"Error analyzing incident trends: {str(e)}"

    @tool
    def compare_service_performance(self, days: int = 30) -> str:
        """
        Compare performance across services.

        Args:
            days: Number of days to analyze (default 30)

        Returns:
            String with service performance comparison
        """
        try:
            df = self.db_manager.get_incidents_dataframe()

            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            df = df[df['created_at'] >= cutoff_date]

            if df.empty:
                return f"No incidents found in the last {days} days."

            # Group by service
            service_metrics = []

            for service_name in df['service_name'].unique():
                if pd.isna(service_name):
                    continue

                service_df = df[df['service_name'] == service_name]

                total_incidents = len(service_df)
                resolved_incidents = len(service_df[service_df['status'] == 'resolved'])
                resolution_rate = (resolved_incidents / total_incidents) * 100 if total_incidents > 0 else 0

                # Average resolution time for resolved incidents
                resolved_with_time = service_df[
                    (service_df['status'] == 'resolved') & 
                    (service_df['resolution_time_hours'].notna())
                ]
                avg_resolution = resolved_with_time['resolution_time_hours'].mean() if not resolved_with_time.empty else None

                # High priority incidents
                high_priority = len(service_df[service_df['urgency'].isin(['high', 'critical'])])
                high_priority_rate = (high_priority / total_incidents) * 100 if total_incidents > 0 else 0

                service_metrics.append({
                    'service': service_name,
                    'total_incidents': total_incidents,
                    'resolution_rate': resolution_rate,
                    'avg_resolution_hours': avg_resolution,
                    'high_priority_incidents': high_priority,
                    'high_priority_rate': high_priority_rate
                })

            # Sort by total incidents
            service_metrics.sort(key=lambda x: x['total_incidents'], reverse=True)

            result = f"🏆 Service Performance Comparison (Last {days} days):\n\n"

            for metrics in service_metrics:
                result += f"**{metrics['service']}**\n"
                result += f"  • Total Incidents: {metrics['total_incidents']}\n"
                result += f"  • Resolution Rate: {metrics['resolution_rate']:.1f}%\n"
                if metrics['avg_resolution_hours']:
                    result += f"  • Avg Resolution: {metrics['avg_resolution_hours']:.1f} hours\n"
                result += f"  • High Priority: {metrics['high_priority_incidents']} ({metrics['high_priority_rate']:.1f}%)\n\n"

            # Find best and worst performers
            if len(service_metrics) > 1:
                best_resolution = max(service_metrics, key=lambda x: x['resolution_rate'])
                fastest_resolution = min(
                    [s for s in service_metrics if s['avg_resolution_hours']],
                    key=lambda x: x['avg_resolution_hours'],
                    default=None
                )

                result += "**Highlights:**\n"
                result += f"• Best Resolution Rate: {best_resolution['service']} ({best_resolution['resolution_rate']:.1f}%)\n"
                if fastest_resolution:
                    result += f"• Fastest Avg Resolution: {fastest_resolution['service']} ({fastest_resolution['avg_resolution_hours']:.1f}h)\n"

            return result

        except Exception as e:
            logger.error(f"Error comparing service performance: {e}")
            return f"Error comparing service performance: {str(e)}"

    @tool
    def identify_problem_patterns(self, days: int = 30) -> str:
        """
        Identify problematic patterns in incidents.

        Args:
            days: Number of days to analyze (default 30)

        Returns:
            String with identified problems and recommendations
        """
        try:
            df = self.db_manager.get_incidents_dataframe()

            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            df = df[df['created_at'] >= cutoff_date]

            if df.empty:
                return f"No incidents found in the last {days} days."

            problems = []
            recommendations = []

            # Check for services with too many incidents
            service_counts = df['service_name'].value_counts()
            avg_incidents_per_service = service_counts.mean()
            problematic_services = service_counts[service_counts > avg_incidents_per_service * 1.5]

            if not problematic_services.empty:
                problems.append(f"🚨 High incident volume services: {', '.join(problematic_services.index)}")
                recommendations.append("Consider reviewing infrastructure and monitoring for high-volume services")

            # Check for long resolution times
            resolved_df = df[(df['status'] == 'resolved') & (df['resolution_time_hours'].notna())]
            if not resolved_df.empty:
                avg_resolution = resolved_df['resolution_time_hours'].mean()
                long_resolution = resolved_df[resolved_df['resolution_time_hours'] > avg_resolution * 2]

                if len(long_resolution) > len(resolved_df) * 0.1:  # More than 10%
                    problems.append(f"⏰ {len(long_resolution)} incidents took >2x average resolution time")
                    recommendations.append("Review incident response procedures and escalation policies")

            # Check for unresolved high priority incidents
            unresolved_high = df[
                (df['status'].isin(['triggered', 'acknowledged'])) &
                (df['urgency'].isin(['high', 'critical']))
            ]

            if not unresolved_high.empty:
                oldest_high = unresolved_high['created_at'].min()
                hours_old = (datetime.utcnow() - oldest_high).total_seconds() / 3600

                if hours_old > 4:  # More than 4 hours
                    problems.append(f"🔴 {len(unresolved_high)} unresolved high/critical incidents (oldest: {hours_old:.1f}h)")
                    recommendations.append("Escalate and prioritize high-urgency incidents immediately")

            # Check for recurring patterns in titles/descriptions
            title_words = []
            for title in df['title'].dropna():
                title_words.extend(title.lower().split())

            word_counts = pd.Series(title_words).value_counts()
            common_issues = word_counts[word_counts > len(df) * 0.2]  # Appears in >20% of incidents

            if not common_issues.empty:
                top_issues = common_issues.head(3).index.tolist()
                problems.append(f"🔄 Recurring issue keywords: {', '.join(top_issues)}")
                recommendations.append("Investigate root causes of recurring issues")

            # Check for uneven urgency distribution
            urgency_counts = df['urgency'].value_counts()
            if 'high' in urgency_counts and 'low' in urgency_counts:
                high_ratio = urgency_counts.get('high', 0) / len(df)
                if high_ratio > 0.4:  # More than 40% high urgency
                    problems.append(f"⚠️ {high_ratio*100:.1f}% of incidents marked as high urgency")
                    recommendations.append("Review urgency classification criteria to avoid alert fatigue")

            # Generate report
            result = f"🔍 Problem Pattern Analysis (Last {days} days):\n\n"

            if problems:
                result += "**Identified Issues:**\n"
                for i, problem in enumerate(problems, 1):
                    result += f"{i}. {problem}\n"

                result += "\n**Recommendations:**\n"
                for i, rec in enumerate(recommendations, 1):
                    result += f"{i}. {rec}\n"
            else:
                result += "✅ No significant problem patterns detected. Incident management appears healthy."

            return result

        except Exception as e:
            logger.error(f"Error identifying problem patterns: {e}")
            return f"Error identifying problem patterns: {str(e)}"

    @tool
    def generate_incident_report(self, days: int = 7) -> str:
        """
        Generate a comprehensive incident report.

        Args:
            days: Number of days to include in report (default 7)

        Returns:
            String with comprehensive incident report
        """
        try:
            df = self.db_manager.get_incidents_dataframe()

            # Filter by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            df = df[df['created_at'] >= cutoff_date]

            if df.empty:
                return f"No incidents to report for the last {days} days."

            total_incidents = len(df)

            # Status breakdown
            status_counts = df['status'].value_counts()

            # Urgency breakdown
            urgency_counts = df['urgency'].value_counts()

            # Service breakdown
            service_counts = df['service_name'].value_counts().head(5)

            # Resolution metrics
            resolved_df = df[(df['status'] == 'resolved') & (df['resolution_time_hours'].notna())]
            avg_resolution = resolved_df['resolution_time_hours'].mean() if not resolved_df.empty else None

            # Time distribution (business hours vs off-hours)
            df['hour'] = df['created_at'].dt.hour
            business_hours = df[(df['hour'] >= 9) & (df['hour'] <= 17)]
            off_hours = df[(df['hour'] < 9) | (df['hour'] > 17)]

            # Generate report
            result = f"📋 Incident Report ({cutoff_date.strftime('%Y-%m-%d')} to {datetime.utcnow().strftime('%Y-%m-%d')}):\n\n"

            result += f"**Executive Summary:**\n"
            result += f"• Total Incidents: {total_incidents}\n"
            result += f"• Resolved: {status_counts.get('resolved', 0)} ({(status_counts.get('resolved', 0)/total_incidents)*100:.1f}%)\n"
            result += f"• Still Open: {status_counts.get('triggered', 0) + status_counts.get('acknowledged', 0)}\n"
            if avg_resolution:
                result += f"• Average Resolution Time: {avg_resolution:.1f} hours\n"
            result += f"• Business Hours: {len(business_hours)} ({(len(business_hours)/total_incidents)*100:.1f}%)\n"
            result += f"• Off Hours: {len(off_hours)} ({(len(off_hours)/total_incidents)*100:.1f}%)\n\n"

            result += f"**By Urgency:**\n"
            for urgency, count in urgency_counts.items():
                percentage = (count / total_incidents) * 100
                emoji = {"low": "🔵", "medium": "🟠", "high": "🔴", "critical": "⚫"}.get(urgency, "❓")
                result += f"• {emoji} {urgency.title()}: {count} ({percentage:.1f}%)\n"

            result += f"\n**Top Affected Services:**\n"
            for service, count in service_counts.items():
                percentage = (count / total_incidents) * 100
                result += f"• {service}: {count} ({percentage:.1f}%)\n"

            # Add critical incidents if any
            critical_incidents = df[df['urgency'] == 'critical']
            if not critical_incidents.empty:
                result += f"\n**Critical Incidents:**\n"
                for _, incident in critical_incidents.head(3).iterrows():
                    result += f"• #{incident['id']}: {incident['title']} ({incident['status']})\n"

            return result

        except Exception as e:
            logger.error(f"Error generating incident report: {e}")
            return f"Error generating incident report: {str(e)}"

def create_analytics_tools(db_manager: DatabaseManager) -> List:
    """Create analytics tools for the agent."""
    analytics_tools = AnalyticsTools(db_manager)

    return [
        analytics_tools.analyze_incident_trends,
        analytics_tools.compare_service_performance,
        analytics_tools.identify_problem_patterns,
        analytics_tools.generate_incident_report,
    ]
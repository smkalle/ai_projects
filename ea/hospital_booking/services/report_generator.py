"""
Automated Report Generation Service
Generates PDF/HTML reports for hospital analytics
"""

import os
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from jinja2 import Environment, FileSystemLoader, Template

from database.connection import get_db_session
from database.models import ReportTemplate, ScheduledReport
from services.dashboard_service import DashboardService


class ReportGenerator:
    """Service for generating automated reports."""

    def __init__(self):
        self.reports_dir = "reports"
        self.templates_dir = "templates"

        # Create directories if they don't exist
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_hospital_performance_report(
        self,
        days_back: int = 30,
        format: str = 'html'
    ) -> str:
        """Generate comprehensive hospital performance report."""

        with DashboardService() as dashboard:
            # Gather all data
            hospital_kpis = dashboard.get_hospital_kpis(days_back=days_back)
            dept_performance = dashboard.get_department_performance(days_back=days_back)
            doctor_metrics = dashboard.get_doctor_efficiency_metrics(days_back=days_back, limit=20)
            financial_data = dashboard.get_financial_dashboard_data(days_back=days_back)
            satisfaction_data = dashboard.get_patient_satisfaction_overview(days_back=days_back)
            trends_data = dashboard.get_appointment_trends(days_back=days_back)

        # Generate charts
        charts = self._generate_performance_charts(
            hospital_kpis, dept_performance, doctor_metrics,
            financial_data, satisfaction_data, trends_data
        )

        # Compile report data
        report_data = {
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': f"Last {days_back} days",
            'period_start': (date.today() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
            'period_end': date.today().strftime('%Y-%m-%d'),
            'hospital_kpis': hospital_kpis,
            'department_performance': dept_performance,
            'top_doctors': doctor_metrics[:10],
            'financial_summary': financial_data,
            'satisfaction_summary': satisfaction_data,
            'charts': charts,
            'executive_summary': self._generate_executive_summary(
                hospital_kpis, dept_performance, doctor_metrics, financial_data
            )
        }

        # Generate report
        if format.lower() == 'html':
            return self._generate_html_report(report_data, 'hospital_performance')
        else:
            return self._generate_json_report(report_data, 'hospital_performance')

    def generate_doctor_efficiency_report(
        self,
        days_back: int = 30,
        department_id: str = None,
        format: str = 'html'
    ) -> str:
        """Generate doctor efficiency report."""

        with DashboardService() as dashboard:
            doctor_metrics = dashboard.get_doctor_efficiency_metrics(days_back=days_back, limit=50)

            # Filter by department if specified
            if department_id:
                doctor_metrics = [
                    doc for doc in doctor_metrics
                    if doc.get('department_id') == department_id
                ]

        # Generate doctor performance charts
        charts = self._generate_doctor_efficiency_charts(doctor_metrics)

        report_data = {
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': f"Last {days_back} days",
            'department_filter': department_id or 'All Departments',
            'doctor_metrics': doctor_metrics,
            'charts': charts,
            'top_performers': doctor_metrics[:5],
            'improvement_opportunities': self._identify_improvement_opportunities(doctor_metrics)
        }

        if format.lower() == 'html':
            return self._generate_html_report(report_data, 'doctor_efficiency')
        else:
            return self._generate_json_report(report_data, 'doctor_efficiency')

    def generate_financial_report(
        self,
        days_back: int = 30,
        format: str = 'html'
    ) -> str:
        """Generate financial performance report."""

        with DashboardService() as dashboard:
            financial_data = dashboard.get_financial_dashboard_data(days_back=days_back)
            dept_performance = dashboard.get_department_performance(days_back=days_back)

        # Generate financial charts
        charts = self._generate_financial_charts(financial_data, dept_performance)

        report_data = {
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': f"Last {days_back} days",
            'financial_summary': financial_data,
            'department_financials': dept_performance,
            'charts': charts,
            'financial_insights': self._generate_financial_insights(financial_data, dept_performance)
        }

        if format.lower() == 'html':
            return self._generate_html_report(report_data, 'financial')
        else:
            return self._generate_json_report(report_data, 'financial')

    def generate_patient_satisfaction_report(
        self,
        days_back: int = 30,
        format: str = 'html'
    ) -> str:
        """Generate patient satisfaction report."""

        with DashboardService() as dashboard:
            satisfaction_data = dashboard.get_patient_satisfaction_overview(days_back=days_back)
            doctor_metrics = dashboard.get_doctor_efficiency_metrics(days_back=days_back, limit=20)

        # Generate satisfaction charts
        charts = self._generate_satisfaction_charts(satisfaction_data, doctor_metrics)

        report_data = {
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period': f"Last {days_back} days",
            'satisfaction_data': satisfaction_data,
            'doctor_satisfaction': [
                {
                    'name': doc['doctor_name'],
                    'department': doc['department_name'],
                    'satisfaction': doc['patient_satisfaction']
                }
                for doc in doctor_metrics
            ],
            'charts': charts,
            'satisfaction_insights': self._generate_satisfaction_insights(satisfaction_data)
        }

        if format.lower() == 'html':
            return self._generate_html_report(report_data, 'patient_satisfaction')
        else:
            return self._generate_json_report(report_data, 'patient_satisfaction')

    def _generate_performance_charts(
        self, hospital_kpis, dept_performance, doctor_metrics,
        financial_data, satisfaction_data, trends_data
    ) -> Dict[str, str]:
        """Generate charts for performance report."""
        charts = {}

        # Hospital KPIs gauge chart
        fig = go.Figure()

        metrics = ['Completion Rate', 'Patient Satisfaction', 'Bed Occupancy']
        values = [
            hospital_kpis['completion_rate'],
            hospital_kpis['avg_patient_satisfaction'] * 20,  # Scale to 100
            hospital_kpis['bed_occupancy_rate']
        ]

        for i, (metric, value) in enumerate(zip(metrics, values)):
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': metric},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#1f77b4"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                },
                domain={'row': i // 2, 'column': i % 2}
            ))

        fig.update_layout(
            grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
            height=400,
            title="Hospital Key Performance Indicators"
        )
        charts['hospital_kpis'] = pio.to_html(fig, include_plotlyjs='cdn', div_id="hospital_kpis")

        # Department performance comparison
        if dept_performance:
            dept_df = pd.DataFrame(dept_performance)

            fig = px.bar(
                dept_df,
                x='department_name',
                y='total_appointments',
                color='patient_satisfaction',
                title="Department Performance Overview",
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            charts['department_performance'] = pio.to_html(fig, include_plotlyjs='cdn', div_id="dept_perf")

        # Top doctors chart
        if doctor_metrics:
            doctor_df = pd.DataFrame(doctor_metrics[:10])

            fig = px.scatter(
                doctor_df,
                x='total_appointments',
                y='efficiency_score',
                size='patient_satisfaction',
                color='utilization_rate',
                hover_name='doctor_name',
                title="Top Doctor Performance",
                color_continuous_scale='viridis'
            )
            fig.update_layout(height=400)
            charts['top_doctors'] = pio.to_html(fig, include_plotlyjs='cdn', div_id="top_doctors")

        return charts

    def _generate_doctor_efficiency_charts(self, doctor_metrics: List[Dict]) -> Dict[str, str]:
        """Generate charts for doctor efficiency report."""
        charts = {}

        if doctor_metrics:
            doctor_df = pd.DataFrame(doctor_metrics[:15])

            # Efficiency vs Volume scatter
            fig = px.scatter(
                doctor_df,
                x='total_appointments',
                y='efficiency_score',
                size='patient_satisfaction',
                color='completion_rate',
                hover_name='doctor_name',
                title="Doctor Efficiency vs Appointment Volume",
                color_continuous_scale='RdYlGn'
            )
            charts['efficiency_scatter'] = pio.to_html(fig, include_plotlyjs='cdn')

            # Top performers bar chart
            fig = px.bar(
                doctor_df.head(10),
                x='doctor_name',
                y='efficiency_score',
                color='patient_satisfaction',
                title="Top 10 Doctors by Efficiency Score",
                color_continuous_scale='viridis'
            )
            fig.update_layout(xaxis_tickangle=-45)
            charts['top_performers'] = pio.to_html(fig, include_plotlyjs='cdn')

        return charts

    def _generate_financial_charts(self, financial_data, dept_performance) -> Dict[str, str]:
        """Generate charts for financial report."""
        charts = {}

        # Revenue vs Costs
        if dept_performance:
            dept_df = pd.DataFrame(dept_performance)

            fig = px.scatter(
                dept_df,
                x='revenue_generated',
                y='total_appointments',
                size='staff_utilization',
                color='completion_rate',
                hover_name='department_name',
                title="Department Revenue vs Activity",
                labels={'revenue_generated': 'Revenue ($)', 'total_appointments': 'Total Appointments'}
            )
            charts['revenue_scatter'] = pio.to_html(fig, include_plotlyjs='cdn')

        # Financial summary pie chart
        if financial_data.get('department_breakdown'):
            dept_financial = financial_data['department_breakdown']
            dept_names = [dept['department_name'] for dept in dept_financial]
            revenues = [dept['revenue'] for dept in dept_financial]

            fig = px.pie(
                values=revenues,
                names=dept_names,
                title="Revenue Distribution by Department"
            )
            charts['revenue_pie'] = pio.to_html(fig, include_plotlyjs='cdn')

        return charts

    def _generate_satisfaction_charts(self, satisfaction_data, doctor_metrics) -> Dict[str, str]:
        """Generate charts for satisfaction report."""
        charts = {}

        # Satisfaction categories bar chart
        categories = ['Overall', 'Wait Time', 'Doctor', 'Facility', 'Communication']
        scores = [
            satisfaction_data['overall_satisfaction'],
            satisfaction_data['wait_time_satisfaction'],
            satisfaction_data['doctor_satisfaction'],
            satisfaction_data['facility_satisfaction'],
            satisfaction_data['communication_satisfaction']
        ]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=scores,
            marker_color=['#10b981' if score >= 4.0 else '#f59e0b' if score >= 3.0 else '#ef4444'
                         for score in scores],
            text=[f"{score:.1f}" for score in scores],
            textposition='auto'
        ))

        fig.update_layout(
            title="Patient Satisfaction by Category",
            yaxis_title="Score (out of 5)",
            yaxis_range=[0, 5]
        )
        charts['satisfaction_categories'] = pio.to_html(fig, include_plotlyjs='cdn')

        return charts

    def _generate_html_report(self, data: Dict[str, Any], template_name: str) -> str:
        """Generate HTML report from template."""
        # Create default template if it doesn't exist
        template_path = f"{self.templates_dir}/{template_name}_report.html"

        if not os.path.exists(template_path):
            self._create_default_template(template_name)

        try:
            template = self.jinja_env.get_template(f"{template_name}_report.html")
            html_content = template.render(data)
        except Exception:
            # Fallback to basic template
            html_content = self._generate_basic_html_report(data, template_name)

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.reports_dir}/{template_name}_report_{timestamp}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return filename

    def _generate_json_report(self, data: Dict[str, Any], template_name: str) -> str:
        """Generate JSON report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.reports_dir}/{template_name}_report_{timestamp}.json"

        # Remove HTML charts for JSON
        if 'charts' in data:
            del data['charts']

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        return filename

    def _create_default_template(self, template_name: str):
        """Create a default HTML template."""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ template_name|title }} Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }
        .header {
            background: #2563eb;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }
        .metric {
            display: inline-block;
            margin: 10px 15px;
            padding: 10px;
            background: #f3f4f6;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ template_name|title|replace('_', ' ') }} Report</h1>
        <p>Generated: {{ generation_date }}</p>
        <p>Period: {{ period }}</p>
    </div>

    {% if executive_summary %}
    <div class="section">
        <h2>Executive Summary</h2>
        <p>{{ executive_summary }}</p>
    </div>
    {% endif %}

    {% if hospital_kpis %}
    <div class="section">
        <h2>Hospital KPIs</h2>
        <div class="metric">Total Appointments: {{ hospital_kpis.total_appointments }}</div>
        <div class="metric">Completion Rate: {{ hospital_kpis.completion_rate }}%</div>
        <div class="metric">Patient Satisfaction: {{ hospital_kpis.avg_patient_satisfaction }}/5</div>
        <div class="metric">Bed Occupancy: {{ hospital_kpis.bed_occupancy_rate }}%</div>
    </div>
    {% endif %}

    {% if charts.hospital_kpis %}
    <div class="chart-container">
        {{ charts.hospital_kpis|safe }}
    </div>
    {% endif %}

    {% if department_performance %}
    <div class="section">
        <h2>Department Performance</h2>
        <table>
            <thead>
                <tr>
                    <th>Department</th>
                    <th>Appointments</th>
                    <th>Completion Rate</th>
                    <th>Satisfaction</th>
                    <th>Revenue</th>
                </tr>
            </thead>
            <tbody>
                {% for dept in department_performance %}
                <tr>
                    <td>{{ dept.department_name }}</td>
                    <td>{{ dept.total_appointments }}</td>
                    <td>{{ dept.completion_rate }}%</td>
                    <td>{{ dept.patient_satisfaction }}/5</td>
                    <td>${{ dept.revenue_generated|round|int }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}

    {% if top_doctors %}
    <div class="section">
        <h2>Top Performing Doctors</h2>
        <table>
            <thead>
                <tr>
                    <th>Doctor</th>
                    <th>Department</th>
                    <th>Appointments</th>
                    <th>Satisfaction</th>
                    <th>Efficiency Score</th>
                </tr>
            </thead>
            <tbody>
                {% for doctor in top_doctors[:10] %}
                <tr>
                    <td>{{ doctor.doctor_name }}</td>
                    <td>{{ doctor.department_name }}</td>
                    <td>{{ doctor.total_appointments }}</td>
                    <td>{{ doctor.patient_satisfaction }}/5</td>
                    <td>{{ doctor.efficiency_score }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% endif %}

    <div class="section">
        <p><em>Report generated by Hospital Analytics System on {{ generation_date }}</em></p>
    </div>
</body>
</html>
        """.strip()

        with open(f"{self.templates_dir}/{template_name}_report.html", 'w') as f:
            f.write(template_content)

    def _generate_basic_html_report(self, data: Dict[str, Any], template_name: str) -> str:
        """Generate basic HTML report when template fails."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{template_name.title()} Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ padding: 10px; margin: 5px; background: #f0f0f0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{template_name.replace('_', ' ').title()} Report</h1>
            <p>Generated: {data.get('generation_date', 'Unknown')}</p>
            <p>Period: {data.get('period', 'Unknown')}</p>

            <h2>Data Summary</h2>
            <pre>{json.dumps(data, indent=2, default=str)}</pre>
        </body>
        </html>
        """
        return html

    def _generate_executive_summary(
        self, hospital_kpis, dept_performance, doctor_metrics, financial_data
    ) -> str:
        """Generate executive summary text."""
        summary_parts = []

        # Hospital performance
        if hospital_kpis['completion_rate'] >= 80:
            summary_parts.append(f"Hospital is performing well with a {hospital_kpis['completion_rate']:.1f}% appointment completion rate.")
        else:
            summary_parts.append(f"Hospital completion rate of {hospital_kpis['completion_rate']:.1f}% needs improvement.")

        # Patient satisfaction
        if hospital_kpis['avg_patient_satisfaction'] >= 4.0:
            summary_parts.append(f"Patient satisfaction is excellent at {hospital_kpis['avg_patient_satisfaction']:.1f}/5.")
        elif hospital_kpis['avg_patient_satisfaction'] >= 3.5:
            summary_parts.append(f"Patient satisfaction is good at {hospital_kpis['avg_patient_satisfaction']:.1f}/5.")
        else:
            summary_parts.append(f"Patient satisfaction at {hospital_kpis['avg_patient_satisfaction']:.1f}/5 requires attention.")

        # Financial performance
        if financial_data['profit_margin'] > 20:
            summary_parts.append(f"Financial performance is strong with a {financial_data['profit_margin']:.1f}% profit margin.")
        elif financial_data['profit_margin'] > 10:
            summary_parts.append(f"Financial performance is stable with a {financial_data['profit_margin']:.1f}% profit margin.")
        else:
            summary_parts.append(f"Financial performance needs attention with only a {financial_data['profit_margin']:.1f}% profit margin.")

        # Top department
        if dept_performance:
            top_dept = max(dept_performance, key=lambda x: x['total_appointments'])
            summary_parts.append(f"The {top_dept['department_name']} department leads in activity with {top_dept['total_appointments']} appointments.")

        return " ".join(summary_parts)

    def _identify_improvement_opportunities(self, doctor_metrics: List[Dict]) -> List[str]:
        """Identify improvement opportunities for doctors."""
        opportunities = []

        low_satisfaction = [
            doc for doc in doctor_metrics
            if doc['patient_satisfaction'] < 3.5
        ]

        if low_satisfaction:
            opportunities.append(f"{len(low_satisfaction)} doctors have patient satisfaction below 3.5/5 and need improvement.")

        low_utilization = [
            doc for doc in doctor_metrics
            if doc['utilization_rate'] < 60
        ]

        if low_utilization:
            opportunities.append(f"{len(low_utilization)} doctors have utilization rates below 60% and could take more appointments.")

        low_completion = [
            doc for doc in doctor_metrics
            if doc['completion_rate'] < 80
        ]

        if low_completion:
            opportunities.append(f"{len(low_completion)} doctors have completion rates below 80% and should focus on reducing cancellations.")

        return opportunities

    def _generate_financial_insights(self, financial_data, dept_performance) -> List[str]:
        """Generate financial insights."""
        insights = []

        if financial_data['profit_margin'] < 15:
            insights.append("Profit margin is below industry standard of 15%. Consider cost optimization.")

        if dept_performance:
            # Find most and least profitable departments
            sorted_depts = sorted(dept_performance, key=lambda x: x['revenue_generated'], reverse=True)
            top_dept = sorted_depts[0]
            insights.append(f"The {top_dept['department_name']} department generates the highest revenue at ${top_dept['revenue_generated']:,.0f}.")

            if len(sorted_depts) > 1:
                bottom_dept = sorted_depts[-1]
                insights.append(f"The {bottom_dept['department_name']} department has the lowest revenue at ${bottom_dept['revenue_generated']:,.0f}.")

        return insights

    def _generate_satisfaction_insights(self, satisfaction_data) -> List[str]:
        """Generate patient satisfaction insights."""
        insights = []

        if satisfaction_data['overall_satisfaction'] >= 4.0:
            insights.append("Overall patient satisfaction is excellent.")
        elif satisfaction_data['overall_satisfaction'] >= 3.5:
            insights.append("Overall patient satisfaction is good but has room for improvement.")
        else:
            insights.append("Overall patient satisfaction needs significant improvement.")

        # Identify lowest scoring areas
        categories = {
            'Wait Time': satisfaction_data['wait_time_satisfaction'],
            'Doctor': satisfaction_data['doctor_satisfaction'],
            'Facility': satisfaction_data['facility_satisfaction'],
            'Communication': satisfaction_data['communication_satisfaction']
        }

        lowest_category = min(categories, key=categories.get)
        if categories[lowest_category] < 3.5:
            insights.append(f"{lowest_category} satisfaction is the lowest area at {categories[lowest_category]:.1f}/5.")

        if satisfaction_data['recommendation_rate'] < 80:
            insights.append(f"Patient recommendation rate of {satisfaction_data['recommendation_rate']:.1f}% is below target.")

        return insights


# Convenience functions for easy use
def generate_daily_report() -> str:
    """Generate daily hospital performance report."""
    generator = ReportGenerator()
    return generator.generate_hospital_performance_report(days_back=1, format='html')

def generate_weekly_report() -> str:
    """Generate weekly hospital performance report."""
    generator = ReportGenerator()
    return generator.generate_hospital_performance_report(days_back=7, format='html')

def generate_monthly_report() -> str:
    """Generate monthly hospital performance report."""
    generator = ReportGenerator()
    return generator.generate_hospital_performance_report(days_back=30, format='html')
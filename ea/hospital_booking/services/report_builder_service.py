"""
Enhanced Report Builder Service for Hospital Booking System
Provides dynamic report generation with customizable charts, filters, and templates
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from database.models import (
    Hospital, Department, Doctor, Appointment, Patient,
    DoctorPerformanceAnalytics, DepartmentPerformanceAnalytics,
    HospitalPerformanceAnalytics, PatientSatisfactionSurvey,
    FinancialMetrics, ReportTemplate
)
from services.dashboard_service import DashboardService


class ReportBuilderService:
    """Enhanced report builder with dynamic chart generation and template management"""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.dashboard_service = DashboardService(db_session)

        # Chart type configurations
        self.chart_types = {
            'line': {'plotly_func': px.line, 'supports_time_series': True},
            'bar': {'plotly_func': px.bar, 'supports_categories': True},
            'pie': {'plotly_func': px.pie, 'supports_categories': True},
            'scatter': {'plotly_func': px.scatter, 'supports_correlation': True},
            'histogram': {'plotly_func': px.histogram, 'supports_distribution': True},
            'box': {'plotly_func': px.box, 'supports_comparison': True},
            'heatmap': {'plotly_func': px.imshow, 'supports_correlation': True}
        }

        # Data source configurations
        self.data_sources = {
            'appointments': {
                'model': Appointment,
                'metrics': ['count', 'duration', 'status_distribution', 'hourly_pattern'],
                'filters': ['date_range', 'department', 'doctor', 'status', 'priority']
            },
            'doctors': {
                'model': Doctor,
                'metrics': ['performance_score', 'patient_count', 'satisfaction_rating'],
                'filters': ['department', 'specialization', 'experience_level']
            },
            'departments': {
                'model': Department,
                'metrics': ['occupancy_rate', 'efficiency_score', 'patient_throughput'],
                'filters': ['department_type', 'date_range']
            },
            'patients': {
                'model': Patient,
                'metrics': ['satisfaction_score', 'wait_time', 'demographics'],
                'filters': ['age_group', 'date_range', 'department']
            },
            'financials': {
                'model': FinancialMetrics,
                'metrics': ['revenue', 'costs', 'profit_margin', 'budget_variance'],
                'filters': ['date_range', 'department', 'cost_center']
            }
        }

    def get_available_data_sources(self) -> Dict[str, Any]:
        """Get all available data sources for report building"""
        return {
            source: {
                'name': source.replace('_', ' ').title(),
                'metrics': config['metrics'],
                'filters': config['filters']
            }
            for source, config in self.data_sources.items()
        }

    def get_chart_types(self) -> Dict[str, Any]:
        """Get available chart types and their capabilities"""
        return {
            chart_type: {
                'name': chart_type.replace('_', ' ').title(),
                'capabilities': [k for k, v in config.items() if k.startswith('supports_') and v]
            }
            for chart_type, config in self.chart_types.items()
        }

    def generate_dynamic_chart(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a chart based on dynamic configuration"""
        try:
            # Extract configuration
            data_source = config['data_source']
            chart_type = config['chart_type']
            metrics = config['metrics']
            filters = config.get('filters', {})
            grouping = config.get('grouping', None)
            time_range = config.get('time_range', 'last_30_days')

            # Get data based on source and filters
            data = self._get_filtered_data(data_source, filters, time_range)

            if data.empty:
                return {'error': 'No data available for the selected criteria'}

            # Generate chart based on type and metrics
            chart_config = self.chart_types.get(chart_type)
            if not chart_config:
                return {'error': f'Unsupported chart type: {chart_type}'}

            # Create the chart
            fig = self._create_chart(data, chart_type, metrics, grouping, config)

            # Convert to JSON for frontend
            chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)

            return {
                'success': True,
                'chart_json': chart_json,
                'data_summary': {
                    'total_records': len(data),
                    'date_range': f"{data.index.min()} to {data.index.max()}" if hasattr(data.index, 'min') else 'N/A',
                    'metrics_included': metrics
                }
            }

        except Exception as e:
            return {'error': f'Chart generation failed: {str(e)}'}

    def _get_filtered_data(self, data_source: str, filters: Dict, time_range: str) -> pd.DataFrame:
        """Get filtered data from the specified source"""
        # Define time range
        end_date = datetime.now()
        if time_range == 'last_7_days':
            start_date = end_date - timedelta(days=7)
        elif time_range == 'last_30_days':
            start_date = end_date - timedelta(days=30)
        elif time_range == 'last_90_days':
            start_date = end_date - timedelta(days=90)
        elif time_range == 'last_year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)

        if data_source == 'appointments':
            return self._get_appointments_data(filters, start_date, end_date)
        elif data_source == 'doctors':
            return self._get_doctors_data(filters)
        elif data_source == 'departments':
            return self._get_departments_data(filters, start_date, end_date)
        elif data_source == 'patients':
            return self._get_patients_data(filters, start_date, end_date)
        elif data_source == 'financials':
            return self._get_financials_data(filters, start_date, end_date)
        else:
            return pd.DataFrame()

    def _get_appointments_data(self, filters: Dict, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get appointments data with filters"""
        query = self.db_session.query(Appointment).filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        )

        if filters.get('department'):
            query = query.join(Doctor).filter(Doctor.department_id == filters['department'])
        if filters.get('doctor'):
            query = query.filter(Appointment.doctor_id == filters['doctor'])
        if filters.get('status'):
            query = query.filter(Appointment.status == filters['status'])
        if filters.get('priority'):
            query = query.filter(Appointment.priority == filters['priority'])

        appointments = query.all()

        # Convert to DataFrame
        data = []
        for apt in appointments:
            data.append({
                'date': apt.appointment_date,
                'department': apt.doctor.department.name if apt.doctor and apt.doctor.department else 'Unknown',
                'doctor': f"{apt.doctor.first_name} {apt.doctor.last_name}" if apt.doctor else 'Unknown',
                'status': apt.status,
                'priority': apt.priority,
                'duration': apt.duration_minutes or 30,
                'hour': apt.appointment_date.hour if apt.appointment_date else 9
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    def _get_doctors_data(self, filters: Dict) -> pd.DataFrame:
        """Get doctors performance data with filters"""
        query = self.db_session.query(Doctor)

        if filters.get('department'):
            query = query.filter(Doctor.department_id == filters['department'])
        if filters.get('specialization'):
            query = query.filter(Doctor.specialization.contains(filters['specialization']))

        doctors = query.all()

        # Get performance analytics
        data = []
        for doctor in doctors:
            perf = self.db_session.query(DoctorPerformanceAnalytics).filter_by(
                doctor_id=doctor.id
            ).order_by(DoctorPerformanceAnalytics.date.desc()).first()

            data.append({
                'doctor_name': f"{doctor.first_name} {doctor.last_name}",
                'department': doctor.department.name if doctor.department else 'Unknown',
                'specialization': doctor.specialization or 'General',
                'performance_score': perf.efficiency_score if perf else 75.0,
                'patient_count': perf.total_patients if perf else 0,
                'satisfaction_rating': perf.avg_satisfaction if perf else 4.0,
                'experience_years': doctor.experience_years or 5
            })

        return pd.DataFrame(data)

    def _get_departments_data(self, filters: Dict, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get departments performance data with filters"""
        query = self.db_session.query(Department)

        if filters.get('department_type'):
            query = query.filter(Department.name.contains(filters['department_type']))

        departments = query.all()

        data = []
        for dept in departments:
            perf = self.db_session.query(DepartmentPerformanceAnalytics).filter(
                DepartmentPerformanceAnalytics.department_id == dept.id,
                DepartmentPerformanceAnalytics.date >= start_date,
                DepartmentPerformanceAnalytics.date <= end_date
            ).order_by(DepartmentPerformanceAnalytics.date.desc()).first()

            data.append({
                'department': dept.name,
                'occupancy_rate': perf.occupancy_rate if perf else 75.0,
                'efficiency_score': perf.efficiency_score if perf else 80.0,
                'patient_throughput': perf.total_patients if perf else 50,
                'avg_wait_time': perf.avg_wait_time if perf else 15.0,
                'staff_count': len(dept.doctors) if dept.doctors else 5
            })

        return pd.DataFrame(data)

    def _get_patients_data(self, filters: Dict, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get patients satisfaction data with filters"""
        query = self.db_session.query(PatientSatisfactionSurvey).filter(
            PatientSatisfactionSurvey.survey_date >= start_date,
            PatientSatisfactionSurvey.survey_date <= end_date
        )

        if filters.get('department'):
            query = query.filter(PatientSatisfactionSurvey.department_id == filters['department'])

        surveys = query.all()

        data = []
        for survey in surveys:
            data.append({
                'date': survey.survey_date,
                'satisfaction_score': survey.overall_satisfaction,
                'wait_time': survey.wait_time_rating,
                'care_quality': survey.care_quality_rating,
                'facility_rating': survey.facility_rating,
                'department': survey.department.name if survey.department else 'Unknown'
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    def _get_financials_data(self, filters: Dict, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get financial metrics data with filters"""
        query = self.db_session.query(FinancialMetrics).filter(
            FinancialMetrics.date >= start_date,
            FinancialMetrics.date <= end_date
        )

        if filters.get('department'):
            query = query.filter(FinancialMetrics.department_id == filters['department'])

        metrics = query.all()

        data = []
        for metric in metrics:
            data.append({
                'date': metric.date,
                'revenue': metric.total_revenue,
                'costs': metric.total_costs,
                'profit_margin': ((metric.total_revenue - metric.total_costs) / metric.total_revenue * 100) if metric.total_revenue > 0 else 0,
                'budget_variance': metric.budget_variance,
                'department': metric.department.name if metric.department else 'Hospital-wide'
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    def _create_chart(self, data: pd.DataFrame, chart_type: str, metrics: List[str], grouping: str, config: Dict) -> go.Figure:
        """Create a chart based on the specified configuration"""
        if chart_type == 'line':
            return self._create_line_chart(data, metrics, grouping, config)
        elif chart_type == 'bar':
            return self._create_bar_chart(data, metrics, grouping, config)
        elif chart_type == 'pie':
            return self._create_pie_chart(data, metrics[0], grouping, config)
        elif chart_type == 'scatter':
            return self._create_scatter_chart(data, metrics, config)
        elif chart_type == 'histogram':
            return self._create_histogram_chart(data, metrics[0], config)
        elif chart_type == 'box':
            return self._create_box_chart(data, metrics, grouping, config)
        elif chart_type == 'heatmap':
            return self._create_heatmap_chart(data, metrics, config)
        else:
            # Default to bar chart
            return self._create_bar_chart(data, metrics, grouping, config)

    def _create_line_chart(self, data: pd.DataFrame, metrics: List[str], grouping: str, config: Dict) -> go.Figure:
        """Create a line chart"""
        fig = go.Figure()

        if grouping and grouping in data.columns:
            for group in data[grouping].unique():
                group_data = data[data[grouping] == group]
                for metric in metrics:
                    if metric in group_data.columns:
                        fig.add_trace(go.Scatter(
                            x=group_data.index,
                            y=group_data[metric],
                            mode='lines+markers',
                            name=f"{group} - {metric}",
                            line=dict(width=2)
                        ))
        else:
            for metric in metrics:
                if metric in data.columns:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data[metric],
                        mode='lines+markers',
                        name=metric,
                        line=dict(width=2)
                    ))

        fig.update_layout(
            title=config.get('title', 'Line Chart'),
            xaxis_title=config.get('x_axis_title', 'Date'),
            yaxis_title=config.get('y_axis_title', 'Value'),
            hovermode='x unified'
        )

        return fig

    def _create_bar_chart(self, data: pd.DataFrame, metrics: List[str], grouping: str, config: Dict) -> go.Figure:
        """Create a bar chart"""
        fig = go.Figure()

        if grouping and grouping in data.columns:
            grouped_data = data.groupby(grouping)[metrics].mean()
            for metric in metrics:
                if metric in grouped_data.columns:
                    fig.add_trace(go.Bar(
                        x=grouped_data.index,
                        y=grouped_data[metric],
                        name=metric
                    ))
        else:
            # Use index as x-axis
            for metric in metrics:
                if metric in data.columns:
                    fig.add_trace(go.Bar(
                        x=data.index,
                        y=data[metric],
                        name=metric
                    ))

        fig.update_layout(
            title=config.get('title', 'Bar Chart'),
            xaxis_title=config.get('x_axis_title', 'Category'),
            yaxis_title=config.get('y_axis_title', 'Value'),
            barmode='group'
        )

        return fig

    def _create_pie_chart(self, data: pd.DataFrame, metric: str, grouping: str, config: Dict) -> go.Figure:
        """Create a pie chart"""
        if grouping and grouping in data.columns:
            grouped_data = data.groupby(grouping)[metric].sum()
        else:
            # Use the metric values directly
            grouped_data = data[metric].value_counts() if metric in data.columns else pd.Series()

        fig = go.Figure(data=[go.Pie(
            labels=grouped_data.index,
            values=grouped_data.values,
            hole=0.3
        )])

        fig.update_layout(
            title=config.get('title', f'{metric} Distribution')
        )

        return fig

    def _create_scatter_chart(self, data: pd.DataFrame, metrics: List[str], config: Dict) -> go.Figure:
        """Create a scatter chart"""
        fig = go.Figure()

        if len(metrics) >= 2:
            x_metric = metrics[0]
            y_metric = metrics[1]

            if x_metric in data.columns and y_metric in data.columns:
                fig.add_trace(go.Scatter(
                    x=data[x_metric],
                    y=data[y_metric],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=data[metrics[2]] if len(metrics) > 2 and metrics[2] in data.columns else 'blue',
                        colorscale='Viridis',
                        showscale=len(metrics) > 2
                    ),
                    name='Data Points'
                ))

        fig.update_layout(
            title=config.get('title', 'Scatter Plot'),
            xaxis_title=config.get('x_axis_title', metrics[0] if metrics else 'X'),
            yaxis_title=config.get('y_axis_title', metrics[1] if len(metrics) > 1 else 'Y')
        )

        return fig

    def _create_histogram_chart(self, data: pd.DataFrame, metric: str, config: Dict) -> go.Figure:
        """Create a histogram"""
        fig = go.Figure()

        if metric in data.columns:
            fig.add_trace(go.Histogram(
                x=data[metric],
                nbinsx=config.get('bins', 20),
                name=metric
            ))

        fig.update_layout(
            title=config.get('title', f'{metric} Distribution'),
            xaxis_title=config.get('x_axis_title', metric),
            yaxis_title='Frequency'
        )

        return fig

    def _create_box_chart(self, data: pd.DataFrame, metrics: List[str], grouping: str, config: Dict) -> go.Figure:
        """Create a box plot"""
        fig = go.Figure()

        for metric in metrics:
            if metric in data.columns:
                if grouping and grouping in data.columns:
                    for group in data[grouping].unique():
                        group_data = data[data[grouping] == group]
                        fig.add_trace(go.Box(
                            y=group_data[metric],
                            name=f"{group} - {metric}",
                            boxmean=True
                        ))
                else:
                    fig.add_trace(go.Box(
                        y=data[metric],
                        name=metric,
                        boxmean=True
                    ))

        fig.update_layout(
            title=config.get('title', 'Box Plot'),
            yaxis_title=config.get('y_axis_title', 'Value')
        )

        return fig

    def _create_heatmap_chart(self, data: pd.DataFrame, metrics: List[str], config: Dict) -> go.Figure:
        """Create a heatmap"""
        # Create correlation matrix for numeric columns
        numeric_data = data[metrics].select_dtypes(include=['number'])
        correlation_matrix = numeric_data.corr()

        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0
        ))

        fig.update_layout(
            title=config.get('title', 'Correlation Heatmap'),
            xaxis_title='Metrics',
            yaxis_title='Metrics'
        )

        return fig

    def save_report_template(self, template_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Save a report template for reuse"""
        try:
            template = ReportTemplate(
                name=template_data['name'],
                description=template_data.get('description', ''),
                template_config=json.dumps(template_data['config']),
                created_by=user_id,
                created_at=datetime.now()
            )

            self.db_session.add(template)
            self.db_session.commit()

            return {
                'success': True,
                'template_id': template.id,
                'message': 'Report template saved successfully'
            }

        except Exception as e:
            self.db_session.rollback()
            return {'error': f'Failed to save template: {str(e)}'}

    def get_report_templates(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all report templates for a user"""
        templates = self.db_session.query(ReportTemplate).filter_by(created_by=user_id).all()

        return [
            {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'config': json.loads(template.template_config),
                'created_at': template.created_at.isoformat()
            }
            for template in templates
        ]

    def generate_report_from_template(self, template_id: int) -> Dict[str, Any]:
        """Generate a report using a saved template"""
        template = self.db_session.query(ReportTemplate).filter_by(id=template_id).first()

        if not template:
            return {'error': 'Template not found'}

        try:
            config = json.loads(template.template_config)
            return self.generate_dynamic_chart(config)
        except Exception as e:
            return {'error': f'Failed to generate report from template: {str(e)}'}
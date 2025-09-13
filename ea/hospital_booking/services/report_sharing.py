"""
Report Sharing and Export Service for Hospital Booking System
Handles report distribution, sharing permissions, and various export formats
"""

import json
import os
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import plotly.io as pio
import plotly.graph_objects as go
from jinja2 import Template
import pdfkit
from database.models import (
    ReportShare, ReportTemplate, Doctor, Patient,
    Hospital, User, ScheduledReport
)
from services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)


class ReportSharingService:
    """Handles report sharing, permissions, and export functionality"""

    def __init__(self, db_session: Session, email_service: Optional[EmailService] = None):
        self.db_session = db_session
        self.email_service = email_service

        # Export formats supported
        self.export_formats = {
            'json': {
                'mime_type': 'application/json',
                'extension': '.json',
                'handler': self._export_json
            },
            'html': {
                'mime_type': 'text/html',
                'extension': '.html',
                'handler': self._export_html
            },
            'pdf': {
                'mime_type': 'application/pdf',
                'extension': '.pdf',
                'handler': self._export_pdf
            },
            'png': {
                'mime_type': 'image/png',
                'extension': '.png',
                'handler': self._export_image
            },
            'svg': {
                'mime_type': 'image/svg+xml',
                'extension': '.svg',
                'handler': self._export_image
            },
            'csv': {
                'mime_type': 'text/csv',
                'extension': '.csv',
                'handler': self._export_csv
            }
        }

    def create_shareable_link(self, report_data: Dict[str, Any], creator_id: int,
                            permissions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a shareable link for a report"""
        try:
            # Generate unique share token
            share_token = self._generate_share_token(report_data, creator_id)

            # Set expiration based on permissions
            expires_at = None
            if permissions.get('expires_in_days'):
                expires_at = datetime.now() + timedelta(days=permissions['expires_in_days'])

            # Create share record
            report_share = ReportShare(
                share_token=share_token,
                report_data=json.dumps(report_data),
                created_by=creator_id,
                permissions=json.dumps(permissions),
                expires_at=expires_at,
                is_public=permissions.get('is_public', False),
                requires_authentication=permissions.get('requires_auth', True),
                allowed_views=permissions.get('max_views', None),
                created_at=datetime.now()
            )

            self.db_session.add(report_share)
            self.db_session.commit()

            share_url = f"/shared-report/{share_token}"

            return {
                'success': True,
                'share_token': share_token,
                'share_url': share_url,
                'expires_at': expires_at.isoformat() if expires_at else None,
                'permissions': permissions
            }

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error creating shareable link: {str(e)}")
            return {'error': f'Failed to create shareable link: {str(e)}'}

    def access_shared_report(self, share_token: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Access a shared report using the share token"""
        try:
            # Find the shared report
            shared_report = self.db_session.query(ReportShare).filter_by(
                share_token=share_token,
                is_active=True
            ).first()

            if not shared_report:
                return {'error': 'Shared report not found or has been deactivated'}

            # Check expiration
            if shared_report.expires_at and datetime.now() > shared_report.expires_at:
                return {'error': 'Shared report has expired'}

            # Check view limits
            if shared_report.allowed_views is not None:
                if shared_report.view_count >= shared_report.allowed_views:
                    return {'error': 'Maximum view limit reached for this shared report'}

            # Check authentication requirements
            permissions = json.loads(shared_report.permissions) if shared_report.permissions else {}

            if shared_report.requires_authentication and not user_id:
                return {'error': 'Authentication required to view this report'}

            # Check user permissions
            if not shared_report.is_public and user_id:
                if not self._check_user_access(shared_report, user_id, permissions):
                    return {'error': 'You do not have permission to view this report'}

            # Increment view count
            shared_report.view_count = (shared_report.view_count or 0) + 1
            shared_report.last_accessed_at = datetime.now()
            self.db_session.commit()

            # Return report data
            report_data = json.loads(shared_report.report_data)

            return {
                'success': True,
                'report_data': report_data,
                'share_info': {
                    'created_by': shared_report.created_by,
                    'created_at': shared_report.created_at.isoformat(),
                    'view_count': shared_report.view_count,
                    'expires_at': shared_report.expires_at.isoformat() if shared_report.expires_at else None
                }
            }

        except Exception as e:
            logger.error(f"Error accessing shared report: {str(e)}")
            return {'error': f'Failed to access shared report: {str(e)}'}

    def export_report(self, report_data: Dict[str, Any], format_type: str,
                     export_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export a report to the specified format"""
        try:
            if format_type not in self.export_formats:
                return {'error': f'Unsupported export format: {format_type}'}

            export_config = self.export_formats[format_type]
            handler = export_config['handler']

            # Call the appropriate export handler
            result = handler(report_data, export_options or {})

            if result.get('success'):
                result.update({
                    'format': format_type,
                    'mime_type': export_config['mime_type'],
                    'extension': export_config['extension']
                })

            return result

        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            return {'error': f'Failed to export report: {str(e)}'}

    def share_via_email(self, report_data: Dict[str, Any], email_config: Dict[str, Any],
                       sender_id: int) -> Dict[str, Any]:
        """Share a report via email"""
        try:
            if not self.email_service:
                return {'error': 'Email service not configured'}

            recipients = email_config.get('recipients', [])
            if not recipients:
                return {'error': 'No recipients specified'}

            subject = email_config.get('subject', 'Hospital Analytics Report')
            message = email_config.get('message', 'Please find the attached hospital analytics report.')
            format_type = email_config.get('format', 'html')

            # Export report in requested format
            export_result = self.export_report(report_data, format_type)
            if not export_result.get('success'):
                return {'error': f'Failed to export report: {export_result.get("error")}'}

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f"hospital_report_{timestamp}{export_result['extension']}"

            # Send emails
            sent_count = 0
            failed_recipients = []

            for recipient in recipients:
                try:
                    email_result = self.email_service.send_report_email(
                        to_email=recipient,
                        subject=subject,
                        message=message,
                        report_content=export_result['content'],
                        filename=filename,
                        content_type=export_result['mime_type']
                    )

                    if email_result.get('success'):
                        sent_count += 1
                    else:
                        failed_recipients.append(recipient)

                except Exception as e:
                    logger.error(f"Failed to send email to {recipient}: {str(e)}")
                    failed_recipients.append(recipient)

            return {
                'success': True,
                'sent_count': sent_count,
                'total_recipients': len(recipients),
                'failed_recipients': failed_recipients,
                'message': f'Report sent to {sent_count} out of {len(recipients)} recipients'
            }

        except Exception as e:
            logger.error(f"Error sharing report via email: {str(e)}")
            return {'error': f'Failed to share report via email: {str(e)}'}

    def get_user_shared_reports(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all reports shared by a user"""
        try:
            shared_reports = self.db_session.query(ReportShare).filter_by(
                created_by=user_id,
                is_active=True
            ).order_by(ReportShare.created_at.desc()).all()

            result = []
            for share in shared_reports:
                permissions = json.loads(share.permissions) if share.permissions else {}

                result.append({
                    'id': share.id,
                    'share_token': share.share_token,
                    'share_url': f"/shared-report/{share.share_token}",
                    'created_at': share.created_at.isoformat(),
                    'expires_at': share.expires_at.isoformat() if share.expires_at else None,
                    'view_count': share.view_count or 0,
                    'last_accessed_at': share.last_accessed_at.isoformat() if share.last_accessed_at else None,
                    'is_public': share.is_public,
                    'permissions': permissions
                })

            return result

        except Exception as e:
            logger.error(f"Error getting user shared reports: {str(e)}")
            return []

    def revoke_shared_report(self, share_token: str, user_id: int) -> Dict[str, Any]:
        """Revoke access to a shared report"""
        try:
            shared_report = self.db_session.query(ReportShare).filter_by(
                share_token=share_token,
                created_by=user_id,
                is_active=True
            ).first()

            if not shared_report:
                return {'error': 'Shared report not found or access denied'}

            shared_report.is_active = False
            shared_report.revoked_at = datetime.now()
            self.db_session.commit()

            return {
                'success': True,
                'message': 'Shared report access revoked successfully'
            }

        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error revoking shared report: {str(e)}")
            return {'error': f'Failed to revoke shared report: {str(e)}'}

    def _generate_share_token(self, report_data: Dict[str, Any], creator_id: int) -> str:
        """Generate a unique share token"""
        content = f"{json.dumps(report_data, sort_keys=True)}{creator_id}{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def _check_user_access(self, shared_report: ReportShare, user_id: int,
                          permissions: Dict[str, Any]) -> bool:
        """Check if a user has access to a shared report"""
        # Creator always has access
        if shared_report.created_by == user_id:
            return True

        # Check specific user permissions
        allowed_users = permissions.get('allowed_users', [])
        if allowed_users and user_id not in allowed_users:
            return False

        # Check department permissions
        allowed_departments = permissions.get('allowed_departments', [])
        if allowed_departments:
            user = self.db_session.query(Doctor).filter_by(id=user_id).first()
            if user and user.department_id not in allowed_departments:
                return False

        return True

    def _export_json(self, report_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Export report as JSON"""
        try:
            json_content = json.dumps(report_data, indent=2, default=str)
            return {
                'success': True,
                'content': json_content,
                'size': len(json_content.encode())
            }
        except Exception as e:
            return {'error': f'JSON export failed: {str(e)}'}

    def _export_html(self, report_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Export report as HTML"""
        try:
            html_template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ title }}</title>
                <meta charset="utf-8">
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .header {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                    }
                    .content {
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    .chart-container {
                        margin: 20px 0;
                    }
                    .summary {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    .summary-card {
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 8px;
                        border-left: 4px solid #667eea;
                    }
                    .footer {
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{{ title }}</h1>
                    <p>{{ description }}</p>
                    <small>Generated on {{ generated_at }}</small>
                </div>

                <div class="content">
                    {% if data_summary %}
                    <div class="summary">
                        {% for key, value in data_summary.items() %}
                        <div class="summary-card">
                            <h3>{{ key.replace('_', ' ').title() }}</h3>
                            <p><strong>{{ value }}</strong></p>
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}

                    {% if chart_json %}
                    <div class="chart-container">
                        <div id="chart" style="width:100%;height:600px;"></div>
                    </div>
                    {% endif %}
                </div>

                <div class="footer">
                    <p>Hospital Analytics Report - Confidential</p>
                </div>

                {% if chart_json %}
                <script>
                    Plotly.newPlot('chart', {{ chart_json|safe }});
                </script>
                {% endif %}
            </body>
            </html>
            """)

            html_content = html_template.render(
                title=report_data.get('title', 'Hospital Report'),
                description=report_data.get('description', 'Analytics report'),
                generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                chart_json=report_data.get('chart_json'),
                data_summary=report_data.get('data_summary', {})
            )

            return {
                'success': True,
                'content': html_content,
                'size': len(html_content.encode())
            }

        except Exception as e:
            return {'error': f'HTML export failed: {str(e)}'}

    def _export_pdf(self, report_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Export report as PDF"""
        try:
            # First generate HTML
            html_result = self._export_html(report_data, options)
            if not html_result.get('success'):
                return html_result

            # Convert HTML to PDF using pdfkit
            pdf_options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }

            pdf_content = pdfkit.from_string(
                html_result['content'],
                False,
                options=pdf_options
            )

            return {
                'success': True,
                'content': pdf_content,
                'size': len(pdf_content)
            }

        except Exception as e:
            return {'error': f'PDF export failed: {str(e)}'}

    def _export_image(self, report_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Export chart as image (PNG/SVG)"""
        try:
            chart_json = report_data.get('chart_json')
            if not chart_json:
                return {'error': 'No chart data available for image export'}

            # Parse chart data
            if isinstance(chart_json, str):
                chart_data = json.loads(chart_json)
            else:
                chart_data = chart_json

            # Create figure
            fig = go.Figure(chart_data)

            # Export based on format
            format_type = options.get('format', 'png')
            if format_type == 'svg':
                image_content = pio.to_html(fig, include_plotlyjs='cdn')
            else:
                image_content = pio.to_image(fig, format=format_type, width=1200, height=800)

            return {
                'success': True,
                'content': image_content,
                'size': len(image_content) if isinstance(image_content, bytes) else len(image_content.encode())
            }

        except Exception as e:
            return {'error': f'Image export failed: {str(e)}'}

    def _export_csv(self, report_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Export report data as CSV"""
        try:
            # Extract tabular data from report
            data_summary = report_data.get('data_summary', {})

            # Create CSV content
            csv_lines = ['Metric,Value']

            for key, value in data_summary.items():
                csv_lines.append(f"{key.replace('_', ' ').title()},{value}")

            csv_content = '\\n'.join(csv_lines)

            return {
                'success': True,
                'content': csv_content,
                'size': len(csv_content.encode())
            }

        except Exception as e:
            return {'error': f'CSV export failed: {str(e)}'}
"""
Report Scheduling Service for Hospital Booking System
Handles automated report generation, scheduling, and delivery
"""

import json
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session, sessionmaker
from database.models import ScheduledReport, ReportTemplate, Doctor, Patient, Hospital
from services.report_builder_service import ReportBuilderService
from services.report_generator import ReportGenerator
from services.email_service import EmailService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportScheduler:
    """Manages scheduled report generation and delivery"""

    def __init__(self, db_session_factory: sessionmaker, email_service: EmailService):
        self.db_session_factory = db_session_factory
        self.email_service = email_service
        self.scheduler_thread = None
        self.running = False

        # Schedule frequencies
        self.frequency_mapping = {
            'daily': schedule.every().day,
            'weekly': schedule.every().week,
            'monthly': schedule.every(30).days,
            'quarterly': schedule.every(90).days
        }

    def start_scheduler(self):
        """Start the background scheduler thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Report scheduler started")

    def stop_scheduler(self):
        """Stop the background scheduler thread"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Report scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduler in a background thread"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)

    def create_scheduled_report(self, schedule_config: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a new scheduled report"""
        try:
            db_session = self.db_session_factory()

            # Validate template exists
            template = db_session.query(ReportTemplate).filter_by(
                id=schedule_config['template_id']
            ).first()

            if not template:
                return {'error': 'Report template not found'}

            # Create scheduled report
            scheduled_report = ScheduledReport(
                name=schedule_config['name'],
                description=schedule_config.get('description', ''),
                template_id=schedule_config['template_id'],
                schedule_frequency=schedule_config['frequency'],
                schedule_time=datetime.strptime(schedule_config['time'], '%H:%M').time(),
                recipients=json.dumps(schedule_config['recipients']),
                format_type=schedule_config.get('format', 'html'),
                is_active=schedule_config.get('is_active', True),
                created_by=user_id,
                created_at=datetime.now()
            )

            # Set next run time
            scheduled_report.next_run = self._calculate_next_run(
                schedule_config['frequency'],
                scheduled_report.schedule_time
            )

            db_session.add(scheduled_report)
            db_session.commit()

            # Register with scheduler
            self._register_scheduled_report(scheduled_report)

            db_session.close()

            return {
                'success': True,
                'schedule_id': scheduled_report.id,
                'next_run': scheduled_report.next_run.isoformat(),
                'message': 'Scheduled report created successfully'
            }

        except Exception as e:
            logger.error(f"Error creating scheduled report: {str(e)}")
            return {'error': f'Failed to create scheduled report: {str(e)}'}

    def update_scheduled_report(self, schedule_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing scheduled report"""
        try:
            db_session = self.db_session_factory()

            scheduled_report = db_session.query(ScheduledReport).filter_by(id=schedule_id).first()

            if not scheduled_report:
                return {'error': 'Scheduled report not found'}

            # Update fields
            if 'name' in updates:
                scheduled_report.name = updates['name']
            if 'description' in updates:
                scheduled_report.description = updates['description']
            if 'frequency' in updates:
                scheduled_report.schedule_frequency = updates['frequency']
            if 'time' in updates:
                scheduled_report.schedule_time = datetime.strptime(updates['time'], '%H:%M').time()
            if 'recipients' in updates:
                scheduled_report.recipients = json.dumps(updates['recipients'])
            if 'format' in updates:
                scheduled_report.format_type = updates['format']
            if 'is_active' in updates:
                scheduled_report.is_active = updates['is_active']

            # Recalculate next run time
            if 'frequency' in updates or 'time' in updates:
                scheduled_report.next_run = self._calculate_next_run(
                    scheduled_report.schedule_frequency,
                    scheduled_report.schedule_time
                )

            scheduled_report.updated_at = datetime.now()
            db_session.commit()

            # Re-register with scheduler
            self._unregister_scheduled_report(schedule_id)
            if scheduled_report.is_active:
                self._register_scheduled_report(scheduled_report)

            db_session.close()

            return {
                'success': True,
                'message': 'Scheduled report updated successfully'
            }

        except Exception as e:
            logger.error(f"Error updating scheduled report: {str(e)}")
            return {'error': f'Failed to update scheduled report: {str(e)}'}

    def delete_scheduled_report(self, schedule_id: int) -> Dict[str, Any]:
        """Delete a scheduled report"""
        try:
            db_session = self.db_session_factory()

            scheduled_report = db_session.query(ScheduledReport).filter_by(id=schedule_id).first()

            if not scheduled_report:
                return {'error': 'Scheduled report not found'}

            # Unregister from scheduler
            self._unregister_scheduled_report(schedule_id)

            # Delete from database
            db_session.delete(scheduled_report)
            db_session.commit()
            db_session.close()

            return {
                'success': True,
                'message': 'Scheduled report deleted successfully'
            }

        except Exception as e:
            logger.error(f"Error deleting scheduled report: {str(e)}")
            return {'error': f'Failed to delete scheduled report: {str(e)}'}

    def get_scheduled_reports(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all scheduled reports for a user"""
        try:
            db_session = self.db_session_factory()

            reports = db_session.query(ScheduledReport).filter_by(created_by=user_id).all()

            result = []
            for report in reports:
                result.append({
                    'id': report.id,
                    'name': report.name,
                    'description': report.description,
                    'template_name': report.template.name if report.template else 'Unknown',
                    'frequency': report.schedule_frequency,
                    'time': report.schedule_time.strftime('%H:%M'),
                    'recipients': json.loads(report.recipients) if report.recipients else [],
                    'format': report.format_type,
                    'is_active': report.is_active,
                    'next_run': report.next_run.isoformat() if report.next_run else None,
                    'last_run': report.last_run.isoformat() if report.last_run else None,
                    'created_at': report.created_at.isoformat()
                })

            db_session.close()
            return result

        except Exception as e:
            logger.error(f"Error getting scheduled reports: {str(e)}")
            return []

    def run_scheduled_report(self, schedule_id: int) -> Dict[str, Any]:
        """Manually run a scheduled report"""
        try:
            db_session = self.db_session_factory()

            scheduled_report = db_session.query(ScheduledReport).filter_by(id=schedule_id).first()

            if not scheduled_report:
                return {'error': 'Scheduled report not found'}

            # Generate the report
            result = self._generate_and_send_report(scheduled_report)

            # Update last run time
            scheduled_report.last_run = datetime.now()
            if result.get('success'):
                scheduled_report.last_run_status = 'success'
            else:
                scheduled_report.last_run_status = 'failed'
                scheduled_report.last_error = result.get('error', 'Unknown error')

            db_session.commit()
            db_session.close()

            return result

        except Exception as e:
            logger.error(f"Error running scheduled report: {str(e)}")
            return {'error': f'Failed to run scheduled report: {str(e)}'}

    def _calculate_next_run(self, frequency: str, schedule_time: time) -> datetime:
        """Calculate the next run time for a scheduled report"""
        now = datetime.now()
        today = now.date()

        # Create datetime for today at the scheduled time
        next_run = datetime.combine(today, schedule_time)

        # If the time has already passed today, start from tomorrow
        if next_run <= now:
            next_run += timedelta(days=1)

        # Adjust based on frequency
        if frequency == 'weekly':
            # Run every Monday at the scheduled time
            days_ahead = 0 - next_run.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_run += timedelta(days=days_ahead)
        elif frequency == 'monthly':
            # Run on the first day of next month
            if next_run.day != 1:
                next_month = next_run.replace(day=28) + timedelta(days=4)
                next_run = next_month.replace(day=1, hour=schedule_time.hour, minute=schedule_time.minute)
        elif frequency == 'quarterly':
            # Run on the first day of next quarter
            quarter_months = [1, 4, 7, 10]
            current_month = next_run.month
            next_quarter_month = min([m for m in quarter_months if m > current_month], default=quarter_months[0])
            if next_quarter_month == quarter_months[0]:  # Next year
                next_run = next_run.replace(year=next_run.year + 1, month=1, day=1,
                                          hour=schedule_time.hour, minute=schedule_time.minute)
            else:
                next_run = next_run.replace(month=next_quarter_month, day=1,
                                          hour=schedule_time.hour, minute=schedule_time.minute)

        return next_run

    def _register_scheduled_report(self, scheduled_report: ScheduledReport):
        """Register a scheduled report with the scheduler"""
        try:
            frequency = scheduled_report.schedule_frequency
            schedule_time = scheduled_report.schedule_time

            if frequency in self.frequency_mapping:
                scheduler_job = self.frequency_mapping[frequency].at(schedule_time.strftime('%H:%M'))
                scheduler_job.do(self._execute_scheduled_report, scheduled_report.id)

                # Tag the job with the report ID for easy removal
                scheduler_job.tag(f"report_{scheduled_report.id}")

                logger.info(f"Registered scheduled report {scheduled_report.id} for {frequency} at {schedule_time}")
            else:
                logger.warning(f"Unsupported frequency: {frequency}")

        except Exception as e:
            logger.error(f"Error registering scheduled report: {str(e)}")

    def _unregister_scheduled_report(self, schedule_id: int):
        """Unregister a scheduled report from the scheduler"""
        try:
            schedule.clear(f"report_{schedule_id}")
            logger.info(f"Unregistered scheduled report {schedule_id}")
        except Exception as e:
            logger.error(f"Error unregistering scheduled report: {str(e)}")

    def _execute_scheduled_report(self, schedule_id: int):
        """Execute a scheduled report (called by scheduler)"""
        try:
            db_session = self.db_session_factory()

            scheduled_report = db_session.query(ScheduledReport).filter_by(id=schedule_id).first()

            if not scheduled_report or not scheduled_report.is_active:
                db_session.close()
                return

            logger.info(f"Executing scheduled report: {scheduled_report.name}")

            # Generate and send the report
            result = self._generate_and_send_report(scheduled_report)

            # Update execution status
            scheduled_report.last_run = datetime.now()
            scheduled_report.next_run = self._calculate_next_run(
                scheduled_report.schedule_frequency,
                scheduled_report.schedule_time
            )

            if result.get('success'):
                scheduled_report.last_run_status = 'success'
                scheduled_report.last_error = None
                logger.info(f"Successfully executed scheduled report: {scheduled_report.name}")
            else:
                scheduled_report.last_run_status = 'failed'
                scheduled_report.last_error = result.get('error', 'Unknown error')
                logger.error(f"Failed to execute scheduled report: {scheduled_report.name} - {scheduled_report.last_error}")

            db_session.commit()
            db_session.close()

        except Exception as e:
            logger.error(f"Error executing scheduled report {schedule_id}: {str(e)}")

    def _generate_and_send_report(self, scheduled_report: ScheduledReport) -> Dict[str, Any]:
        """Generate and send a report via email"""
        try:
            db_session = self.db_session_factory()

            # Initialize services
            report_builder = ReportBuilderService(db_session)
            report_generator = ReportGenerator(db_session)

            # Get template configuration
            template_config = json.loads(scheduled_report.template.template_config)

            # Generate the chart/data
            chart_result = report_builder.generate_dynamic_chart(template_config)

            if not chart_result.get('success'):
                return {'error': f"Failed to generate chart: {chart_result.get('error')}"}

            # Generate report content based on format
            if scheduled_report.format_type == 'pdf':
                # Generate PDF report
                report_content = report_generator.generate_pdf_report({
                    'title': scheduled_report.name,
                    'description': scheduled_report.description,
                    'chart_json': chart_result['chart_json'],
                    'data_summary': chart_result['data_summary'],
                    'generated_at': datetime.now().isoformat()
                })
                content_type = 'application/pdf'
                filename = f"{scheduled_report.name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            else:
                # Generate HTML report
                report_content = report_generator.generate_html_report({
                    'title': scheduled_report.name,
                    'description': scheduled_report.description,
                    'chart_json': chart_result['chart_json'],
                    'data_summary': chart_result['data_summary'],
                    'generated_at': datetime.now().isoformat()
                })
                content_type = 'text/html'
                filename = f"{scheduled_report.name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html"

            # Send via email
            recipients = json.loads(scheduled_report.recipients) if scheduled_report.recipients else []

            for recipient in recipients:
                email_result = self.email_service.send_scheduled_report(
                    to_email=recipient,
                    report_name=scheduled_report.name,
                    report_content=report_content,
                    content_type=content_type,
                    filename=filename
                )

                if not email_result.get('success'):
                    logger.error(f"Failed to send report to {recipient}: {email_result.get('error')}")

            db_session.close()

            return {
                'success': True,
                'message': f'Report sent to {len(recipients)} recipients'
            }

        except Exception as e:
            logger.error(f"Error generating and sending report: {str(e)}")
            return {'error': f'Failed to generate and send report: {str(e)}'}

    def load_and_register_all_scheduled_reports(self):
        """Load all active scheduled reports and register them with the scheduler"""
        try:
            db_session = self.db_session_factory()

            active_reports = db_session.query(ScheduledReport).filter_by(is_active=True).all()

            for report in active_reports:
                self._register_scheduled_report(report)

            db_session.close()
            logger.info(f"Loaded and registered {len(active_reports)} scheduled reports")

        except Exception as e:
            logger.error(f"Error loading scheduled reports: {str(e)}")
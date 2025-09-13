"""
Email Service
Comprehensive email management for hospital booking system
"""

import smtplib
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import email.mime.text
import email.mime.multipart
import email.mime.base
import email.encoders
import logging
from jinja2 import Environment, FileSystemLoader, Template

from database.connection import get_db_session
from database.models import Appointment, Patient, Doctor, Department

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending and managing emails."""

    def __init__(self):
        # Email configuration from environment variables
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('FROM_NAME', 'City General Hospital')

        # Create templates directory
        self.templates_dir = "templates/email"
        os.makedirs(self.templates_dir, exist_ok=True)

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Create default templates if they don't exist
        self._create_default_templates()

    def send_appointment_confirmation(self, appointment_id: int) -> bool:
        """Send appointment confirmation email."""
        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id
                ).first()

                if not appointment or not appointment.patient.email:
                    logger.error(f"Appointment {appointment_id} not found or no patient email")
                    return False

                # Prepare email data
                email_data = {
                    'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
                    'doctor_name': appointment.doctor.name,
                    'doctor_title': appointment.doctor.title or 'Dr.',
                    'department': appointment.doctor.department.name,
                    'appointment_date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
                    'appointment_time': appointment.start_time.strftime('%I:%M %p'),
                    'appointment_duration': self._calculate_duration(appointment),
                    'location': appointment.location or appointment.doctor.department.location,
                    'reason': appointment.reason_for_visit or 'Consultation',
                    'hospital_name': 'City General Hospital',
                    'hospital_address': '123 Healthcare Drive, Medical City, MC 12345',
                    'hospital_phone': '(555) 123-CARE',
                    'confirmation_number': f"CONF-{appointment.id:06d}",
                    'appointment_id': appointment.id
                }

                subject = f"Appointment Confirmation - {email_data['appointment_date']}"

                # Generate email content
                html_content = self._render_template('appointment_confirmation.html', email_data)
                text_content = self._render_template('appointment_confirmation.txt', email_data)

                # Generate iCal attachment
                ical_content = self._generate_ical(appointment)

                return self._send_email(
                    to_email=appointment.patient.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    attachments=[('appointment.ics', ical_content, 'text/calendar')]
                )

        except Exception as e:
            logger.error(f"Error sending appointment confirmation: {e}")
            return False

    def send_appointment_reminder(self, appointment_id: int, reminder_type: str = '24h') -> bool:
        """Send appointment reminder email."""
        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id
                ).first()

                if not appointment or not appointment.patient.email:
                    return False

                reminder_messages = {
                    '24h': 'Tomorrow',
                    '2h': 'In 2 hours',
                    '30m': 'In 30 minutes'
                }

                email_data = {
                    'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
                    'doctor_name': appointment.doctor.name,
                    'doctor_title': appointment.doctor.title or 'Dr.',
                    'department': appointment.doctor.department.name,
                    'appointment_date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
                    'appointment_time': appointment.start_time.strftime('%I:%M %p'),
                    'location': appointment.location or appointment.doctor.department.location,
                    'reminder_message': reminder_messages.get(reminder_type, 'Soon'),
                    'hospital_name': 'City General Hospital',
                    'hospital_phone': '(555) 123-CARE',
                    'confirmation_number': f"CONF-{appointment.id:06d}",
                    'appointment_id': appointment.id
                }

                subject = f"Appointment Reminder - {email_data['reminder_message']}"

                html_content = self._render_template('appointment_reminder.html', email_data)
                text_content = self._render_template('appointment_reminder.txt', email_data)

                return self._send_email(
                    to_email=appointment.patient.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )

        except Exception as e:
            logger.error(f"Error sending appointment reminder: {e}")
            return False

    def send_appointment_cancellation(self, appointment_id: int, cancellation_reason: str = '') -> bool:
        """Send appointment cancellation email."""
        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id
                ).first()

                if not appointment or not appointment.patient.email:
                    return False

                email_data = {
                    'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
                    'doctor_name': appointment.doctor.name,
                    'doctor_title': appointment.doctor.title or 'Dr.',
                    'appointment_date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
                    'appointment_time': appointment.start_time.strftime('%I:%M %p'),
                    'cancellation_reason': cancellation_reason,
                    'hospital_name': 'City General Hospital',
                    'hospital_phone': '(555) 123-CARE',
                    'rebooking_url': 'https://hospital.example.com/book-appointment',
                    'confirmation_number': f"CONF-{appointment.id:06d}"
                }

                subject = "Appointment Cancellation Notice"

                html_content = self._render_template('appointment_cancellation.html', email_data)
                text_content = self._render_template('appointment_cancellation.txt', email_data)

                return self._send_email(
                    to_email=appointment.patient.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )

        except Exception as e:
            logger.error(f"Error sending appointment cancellation: {e}")
            return False

    def send_satisfaction_survey(self, appointment_id: int) -> bool:
        """Send patient satisfaction survey email."""
        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id,
                    Appointment.status == 'completed'
                ).first()

                if not appointment or not appointment.patient.email:
                    return False

                email_data = {
                    'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
                    'doctor_name': appointment.doctor.name,
                    'doctor_title': appointment.doctor.title or 'Dr.',
                    'appointment_date': appointment.appointment_date.strftime('%A, %B %d, %Y'),
                    'hospital_name': 'City General Hospital',
                    'survey_url': f'https://hospital.example.com/survey/{appointment.id}',
                    'survey_deadline': (datetime.now().date() +
                                      datetime.timedelta(days=7)).strftime('%B %d, %Y')
                }

                subject = "How was your visit? - Patient Satisfaction Survey"

                html_content = self._render_template('satisfaction_survey.html', email_data)
                text_content = self._render_template('satisfaction_survey.txt', email_data)

                return self._send_email(
                    to_email=appointment.patient.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )

        except Exception as e:
            logger.error(f"Error sending satisfaction survey: {e}")
            return False

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        attachments: List[tuple] = None
    ) -> bool:
        """Send email with HTML and text content."""
        try:
            # Create message
            msg = email.mime.multipart.MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text and HTML parts
            text_part = email.mime.text.MIMEText(text_content, 'plain')
            html_part = email.mime.text.MIMEText(html_content, 'html')

            msg.attach(text_part)
            msg.attach(html_part)

            # Add attachments if provided
            if attachments:
                for filename, content, content_type in attachments:
                    attachment = email.mime.base.MIMEBase('application', 'octet-stream')
                    attachment.set_payload(content.encode())
                    email.encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(attachment)

            # Send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()

            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)

            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False

    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render email template with data."""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(data)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            # Return basic fallback content
            if 'confirmation' in template_name:
                return f"Your appointment with {data.get('doctor_name', 'the doctor')} on {data.get('appointment_date', '')} at {data.get('appointment_time', '')} has been confirmed."
            elif 'reminder' in template_name:
                return f"Reminder: You have an appointment with {data.get('doctor_name', 'the doctor')} {data.get('reminder_message', 'soon')}."
            elif 'cancellation' in template_name:
                return f"Your appointment with {data.get('doctor_name', 'the doctor')} has been cancelled."
            else:
                return "Thank you for choosing City General Hospital."

    def _calculate_duration(self, appointment) -> str:
        """Calculate appointment duration in minutes."""
        if appointment.start_time and appointment.end_time:
            duration = datetime.combine(date.today(), appointment.end_time) - \
                      datetime.combine(date.today(), appointment.start_time)
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes"
        return "30 minutes"

    def _generate_ical(self, appointment) -> str:
        """Generate iCal content for appointment."""
        start_datetime = datetime.combine(appointment.appointment_date, appointment.start_time)
        end_datetime = datetime.combine(appointment.appointment_date, appointment.end_time)

        ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//City General Hospital//Appointment System//EN
BEGIN:VEVENT
UID:appointment-{appointment.id}@citygeneralhospital.com
DTSTART:{start_datetime.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_datetime.strftime('%Y%m%dT%H%M%S')}
SUMMARY:Medical Appointment - {appointment.doctor.name}
DESCRIPTION:Appointment with {appointment.doctor.title} {appointment.doctor.name}\\nDepartment: {appointment.doctor.department.name}\\nReason: {appointment.reason_for_visit or 'Consultation'}
LOCATION:{appointment.location or appointment.doctor.department.location}
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Appointment reminder
END:VALARM
END:VEVENT
END:VCALENDAR"""

        return ical_content

    def _create_default_templates(self):
        """Create default email templates."""
        templates = {
            'appointment_confirmation.html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Appointment Confirmation</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .appointment-details { background: white; padding: 15px; border-left: 4px solid #2563eb; margin: 15px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        .button { display: inline-block; padding: 10px 20px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ hospital_name }}</h1>
            <h2>Appointment Confirmed</h2>
        </div>

        <div class="content">
            <p>Dear {{ patient_name }},</p>

            <p>Your appointment has been confirmed. Here are the details:</p>

            <div class="appointment-details">
                <h3>Appointment Details</h3>
                <p><strong>Doctor:</strong> {{ doctor_title }} {{ doctor_name }}</p>
                <p><strong>Department:</strong> {{ department }}</p>
                <p><strong>Date:</strong> {{ appointment_date }}</p>
                <p><strong>Time:</strong> {{ appointment_time }}</p>
                <p><strong>Duration:</strong> {{ appointment_duration }}</p>
                <p><strong>Location:</strong> {{ location }}</p>
                <p><strong>Reason:</strong> {{ reason }}</p>
                <p><strong>Confirmation #:</strong> {{ confirmation_number }}</p>
            </div>

            <p><strong>Please arrive 15 minutes early</strong> for check-in and bring:</p>
            <ul>
                <li>Valid photo ID</li>
                <li>Insurance card</li>
                <li>List of current medications</li>
            </ul>

            <p>If you need to reschedule or cancel, please call us at {{ hospital_phone }} at least 24 hours in advance.</p>
        </div>

        <div class="footer">
            <p>{{ hospital_name }}<br>
            {{ hospital_address }}<br>
            Phone: {{ hospital_phone }}</p>
        </div>
    </div>
</body>
</html>
            ''',

            'appointment_confirmation.txt': '''
{{ hospital_name }}
APPOINTMENT CONFIRMATION

Dear {{ patient_name }},

Your appointment has been confirmed. Here are the details:

Doctor: {{ doctor_title }} {{ doctor_name }}
Department: {{ department }}
Date: {{ appointment_date }}
Time: {{ appointment_time }}
Duration: {{ appointment_duration }}
Location: {{ location }}
Reason: {{ reason }}
Confirmation #: {{ confirmation_number }}

Please arrive 15 minutes early for check-in and bring:
- Valid photo ID
- Insurance card
- List of current medications

If you need to reschedule or cancel, please call us at {{ hospital_phone }} at least 24 hours in advance.

{{ hospital_name }}
{{ hospital_address }}
Phone: {{ hospital_phone }}
            ''',

            'appointment_reminder.html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Appointment Reminder</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f59e0b; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .reminder-box { background: white; padding: 15px; border-left: 4px solid #f59e0b; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ hospital_name }}</h1>
            <h2>Appointment Reminder</h2>
        </div>

        <div class="content">
            <p>Dear {{ patient_name }},</p>

            <div class="reminder-box">
                <h3>Reminder: Appointment {{ reminder_message }}</h3>
                <p><strong>Doctor:</strong> {{ doctor_title }} {{ doctor_name }}</p>
                <p><strong>Department:</strong> {{ department }}</p>
                <p><strong>Date:</strong> {{ appointment_date }}</p>
                <p><strong>Time:</strong> {{ appointment_time }}</p>
                <p><strong>Location:</strong> {{ location }}</p>
                <p><strong>Confirmation #:</strong> {{ confirmation_number }}</p>
            </div>

            <p>Please arrive 15 minutes early for check-in.</p>

            <p>Need to reschedule? Call {{ hospital_phone }}</p>
        </div>
    </div>
</body>
</html>
            ''',

            'appointment_reminder.txt': '''
{{ hospital_name }}
APPOINTMENT REMINDER

Dear {{ patient_name }},

Reminder: Appointment {{ reminder_message }}

Doctor: {{ doctor_title }} {{ doctor_name }}
Department: {{ department }}
Date: {{ appointment_date }}
Time: {{ appointment_time }}
Location: {{ location }}
Confirmation #: {{ confirmation_number }}

Please arrive 15 minutes early for check-in.

Need to reschedule? Call {{ hospital_phone }}

{{ hospital_name }}
            '''
        }

        for filename, content in templates.items():
            filepath = os.path.join(self.templates_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content.strip())

    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration and connectivity."""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()

            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)

            server.quit()

            return {
                'status': 'success',
                'message': 'Email configuration is working correctly',
                'smtp_host': self.smtp_host,
                'smtp_port': self.smtp_port,
                'from_email': self.from_email
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Email configuration test failed: {str(e)}',
                'smtp_host': self.smtp_host,
                'smtp_port': self.smtp_port
            }


# Convenience functions
def send_appointment_confirmation(appointment_id: int) -> bool:
    """Send appointment confirmation email."""
    email_service = EmailService()
    return email_service.send_appointment_confirmation(appointment_id)

def send_appointment_reminder(appointment_id: int, reminder_type: str = '24h') -> bool:
    """Send appointment reminder email."""
    email_service = EmailService()
    return email_service.send_appointment_reminder(appointment_id, reminder_type)

def send_appointment_cancellation(appointment_id: int, reason: str = '') -> bool:
    """Send appointment cancellation email."""
    email_service = EmailService()
    return email_service.send_appointment_cancellation(appointment_id, reason)
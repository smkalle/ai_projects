"""
Calendar Integration Service
Google Calendar, Outlook, and iCal integration for appointments
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from dataclasses import dataclass

# Google Calendar API
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Microsoft Graph API (Outlook)
try:
    import msal
    import requests
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False

from database.connection import get_db_session
from database.models import Appointment, Patient, Doctor

logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Represents a calendar event."""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str
    location: str
    attendees: List[str]
    appointment_id: Optional[int] = None


class GoogleCalendarService:
    """Google Calendar integration service."""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        self.creds_file = 'credentials/google_calendar_credentials.json'
        self.token_file = 'credentials/google_calendar_token.json'
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')

        # Create credentials directory
        os.makedirs('credentials', exist_ok=True)

        self.service = None
        if GOOGLE_AVAILABLE:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None

        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(self.creds_file):
                    flow = InstalledAppFlow.from_client_secrets_file(self.creds_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    logger.warning("Google Calendar credentials file not found")
                    return

            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)

    def create_appointment_event(self, appointment_id: int) -> Optional[str]:
        """Create calendar event for appointment."""
        if not self.service:
            return None

        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id
                ).first()

                if not appointment:
                    return None

                # Create event
                start_datetime = datetime.combine(appointment.appointment_date, appointment.start_time)
                end_datetime = datetime.combine(appointment.appointment_date, appointment.end_time)

                event = {
                    'summary': f'Medical Appointment - {appointment.doctor.name}',
                    'location': appointment.location or appointment.doctor.department.location,
                    'description': f'''
Medical Appointment Details:
Doctor: {appointment.doctor.title} {appointment.doctor.name}
Department: {appointment.doctor.department.name}
Reason: {appointment.reason_for_visit or 'Consultation'}
Patient: {appointment.patient.first_name} {appointment.patient.last_name}
Confirmation: CONF-{appointment.id:06d}

City General Hospital
Phone: (555) 123-CARE
                    '''.strip(),
                    'start': {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'America/New_York',
                    },
                    'end': {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'America/New_York',
                    },
                    'attendees': [
                        {'email': appointment.patient.email} if appointment.patient.email else None,
                        {'email': appointment.doctor.email} if appointment.doctor.email else None,
                    ],
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 24 * 60},  # 24 hours
                            {'method': 'email', 'minutes': 60},       # 1 hour
                        ],
                    },
                    'extendedProperties': {
                        'private': {
                            'hospitalAppointmentId': str(appointment.id),
                            'system': 'hospital-booking'
                        }
                    }
                }

                # Filter out None attendees
                event['attendees'] = [a for a in event['attendees'] if a is not None]

                created_event = self.service.events().insert(
                    calendarId=self.calendar_id,
                    body=event
                ).execute()

                logger.info(f"Google Calendar event created: {created_event['id']}")
                return created_event['id']

        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {e}")
            return None

    def update_appointment_event(self, calendar_event_id: str, appointment_id: int) -> bool:
        """Update existing calendar event."""
        if not self.service:
            return False

        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id
                ).first()

                if not appointment:
                    return False

                # Get existing event
                existing_event = self.service.events().get(
                    calendarId=self.calendar_id,
                    eventId=calendar_event_id
                ).execute()

                # Update event details
                start_datetime = datetime.combine(appointment.appointment_date, appointment.start_time)
                end_datetime = datetime.combine(appointment.appointment_date, appointment.end_time)

                existing_event.update({
                    'summary': f'Medical Appointment - {appointment.doctor.name}',
                    'location': appointment.location or appointment.doctor.department.location,
                    'start': {
                        'dateTime': start_datetime.isoformat(),
                        'timeZone': 'America/New_York',
                    },
                    'end': {
                        'dateTime': end_datetime.isoformat(),
                        'timeZone': 'America/New_York',
                    },
                })

                updated_event = self.service.events().update(
                    calendarId=self.calendar_id,
                    eventId=calendar_event_id,
                    body=existing_event
                ).execute()

                logger.info(f"Google Calendar event updated: {calendar_event_id}")
                return True

        except Exception as e:
            logger.error(f"Error updating Google Calendar event: {e}")
            return False

    def delete_appointment_event(self, calendar_event_id: str) -> bool:
        """Delete calendar event."""
        if not self.service:
            return False

        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=calendar_event_id
            ).execute()

            logger.info(f"Google Calendar event deleted: {calendar_event_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting Google Calendar event: {e}")
            return False

    def get_events(self, start_date: date, end_date: date) -> List[CalendarEvent]:
        """Get events from calendar for date range."""
        if not self.service:
            return []

        try:
            start_datetime = datetime.combine(start_date, datetime.min.time()).isoformat() + 'Z'
            end_datetime = datetime.combine(end_date, datetime.max.time()).isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_datetime,
                timeMax=end_datetime,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            calendar_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                # Parse datetime
                if 'T' in start:
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                else:
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)

                appointment_id = None
                if 'extendedProperties' in event:
                    private_props = event['extendedProperties'].get('private', {})
                    if private_props.get('system') == 'hospital-booking':
                        appointment_id = int(private_props.get('hospitalAppointmentId', 0))

                calendar_events.append(CalendarEvent(
                    id=event['id'],
                    title=event.get('summary', 'No Title'),
                    start_time=start_dt,
                    end_time=end_dt,
                    description=event.get('description', ''),
                    location=event.get('location', ''),
                    attendees=[a.get('email', '') for a in event.get('attendees', [])],
                    appointment_id=appointment_id
                ))

            return calendar_events

        except Exception as e:
            logger.error(f"Error getting Google Calendar events: {e}")
            return []


class OutlookCalendarService:
    """Microsoft Outlook/Office 365 calendar integration service."""

    def __init__(self):
        self.client_id = os.getenv('OUTLOOK_CLIENT_ID', '')
        self.client_secret = os.getenv('OUTLOOK_CLIENT_SECRET', '')
        self.tenant_id = os.getenv('OUTLOOK_TENANT_ID', 'common')
        self.redirect_uri = os.getenv('OUTLOOK_REDIRECT_URI', 'http://localhost:8080/callback')

        self.token_file = 'credentials/outlook_token.json'

        # Create credentials directory
        os.makedirs('credentials', exist_ok=True)

        self.app = None
        self.access_token = None

        if OUTLOOK_AVAILABLE:
            self._initialize_app()

    def _initialize_app(self):
        """Initialize MSAL app."""
        if not self.client_id:
            logger.warning("Outlook client ID not configured")
            return

        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )

    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph API."""
        if not self.app:
            return False

        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
                self.access_token = token_data.get('access_token')

                # Check if token is still valid
                if self._test_token():
                    return True

        # Get new token
        scopes = ["https://graph.microsoft.com/Calendars.ReadWrite"]

        # For demonstration, we'll use client credentials flow
        # In production, you'd use authorization code flow for user consent
        result = self.app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            self.access_token = result["access_token"]

            # Save token
            with open(self.token_file, 'w') as f:
                json.dump(result, f)

            return True
        else:
            logger.error(f"Outlook authentication failed: {result.get('error_description')}")
            return False

    def _test_token(self) -> bool:
        """Test if current token is valid."""
        if not self.access_token:
            return False

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        return response.status_code == 200

    def create_appointment_event(self, appointment_id: int, user_id: str = 'me') -> Optional[str]:
        """Create Outlook calendar event for appointment."""
        if not self.access_token:
            return None

        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id
                ).first()

                if not appointment:
                    return None

                start_datetime = datetime.combine(appointment.appointment_date, appointment.start_time)
                end_datetime = datetime.combine(appointment.appointment_date, appointment.end_time)

                event_data = {
                    "subject": f"Medical Appointment - {appointment.doctor.name}",
                    "body": {
                        "contentType": "HTML",
                        "content": f"""
                        <h3>Medical Appointment Details</h3>
                        <p><strong>Doctor:</strong> {appointment.doctor.title} {appointment.doctor.name}</p>
                        <p><strong>Department:</strong> {appointment.doctor.department.name}</p>
                        <p><strong>Reason:</strong> {appointment.reason_for_visit or 'Consultation'}</p>
                        <p><strong>Patient:</strong> {appointment.patient.first_name} {appointment.patient.last_name}</p>
                        <p><strong>Confirmation:</strong> CONF-{appointment.id:06d}</p>
                        <hr>
                        <p>City General Hospital<br>Phone: (555) 123-CARE</p>
                        """
                    },
                    "start": {
                        "dateTime": start_datetime.isoformat(),
                        "timeZone": "America/New_York"
                    },
                    "end": {
                        "dateTime": end_datetime.isoformat(),
                        "timeZone": "America/New_York"
                    },
                    "location": {
                        "displayName": appointment.location or appointment.doctor.department.location
                    },
                    "attendees": []
                }

                # Add attendees if emails are available
                if appointment.patient.email:
                    event_data["attendees"].append({
                        "emailAddress": {"address": appointment.patient.email, "name": f"{appointment.patient.first_name} {appointment.patient.last_name}"}
                    })

                if appointment.doctor.email:
                    event_data["attendees"].append({
                        "emailAddress": {"address": appointment.doctor.email, "name": appointment.doctor.name}
                    })

                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }

                response = requests.post(
                    f'https://graph.microsoft.com/v1.0/users/{user_id}/events',
                    headers=headers,
                    json=event_data
                )

                if response.status_code == 201:
                    event = response.json()
                    logger.info(f"Outlook calendar event created: {event['id']}")
                    return event['id']
                else:
                    logger.error(f"Error creating Outlook event: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error creating Outlook calendar event: {e}")
            return None


class iCalService:
    """iCal export service for calendar integration."""

    @staticmethod
    def generate_appointment_ical(appointment_id: int) -> str:
        """Generate iCal content for a single appointment."""
        try:
            with get_db_session() as session:
                appointment = session.query(Appointment).filter(
                    Appointment.id == appointment_id
                ).first()

                if not appointment:
                    return ""

                start_datetime = datetime.combine(appointment.appointment_date, appointment.start_time)
                end_datetime = datetime.combine(appointment.appointment_date, appointment.end_time)
                created_datetime = appointment.created_at or datetime.now()

                ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//City General Hospital//Appointment System//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:appointment-{appointment.id}@citygeneralhospital.com
DTSTART:{start_datetime.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_datetime.strftime('%Y%m%dT%H%M%S')}
DTSTAMP:{created_datetime.strftime('%Y%m%dT%H%M%S')}
CREATED:{created_datetime.strftime('%Y%m%dT%H%M%S')}
SUMMARY:Medical Appointment - {appointment.doctor.name}
DESCRIPTION:Appointment with {appointment.doctor.title or 'Dr.'} {appointment.doctor.name}\\n\\nDepartment: {appointment.doctor.department.name}\\nReason: {appointment.reason_for_visit or 'Consultation'}\\nPatient: {appointment.patient.first_name} {appointment.patient.last_name}\\nConfirmation: CONF-{appointment.id:06d}\\n\\nCity General Hospital\\nPhone: (555) 123-CARE
LOCATION:{appointment.location or appointment.doctor.department.location or 'City General Hospital'}
STATUS:CONFIRMED
TRANSP:OPAQUE
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Appointment reminder - 1 hour
END:VALARM
BEGIN:VALARM
TRIGGER:-PT1440M
ACTION:EMAIL
DESCRIPTION:Appointment reminder - 24 hours
SUMMARY:Medical Appointment Tomorrow
ATTENDEE:MAILTO:{appointment.patient.email or 'patient@example.com'}
END:VALARM
END:VEVENT
END:VCALENDAR"""

                return ical_content

        except Exception as e:
            logger.error(f"Error generating iCal for appointment {appointment_id}: {e}")
            return ""

    @staticmethod
    def generate_multiple_appointments_ical(appointment_ids: List[int]) -> str:
        """Generate iCal content for multiple appointments."""
        try:
            ical_events = []

            for appointment_id in appointment_ids:
                event_content = iCalService.generate_appointment_ical(appointment_id)
                if event_content:
                    # Extract just the VEVENT part
                    lines = event_content.split('\n')
                    event_lines = []
                    in_vevent = False

                    for line in lines:
                        if line.startswith('BEGIN:VEVENT'):
                            in_vevent = True
                        if in_vevent:
                            event_lines.append(line)
                        if line.startswith('END:VEVENT'):
                            in_vevent = False

                    ical_events.append('\n'.join(event_lines))

            # Combine all events in one calendar
            calendar_header = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//City General Hospital//Appointment System//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH"""

            calendar_footer = "END:VCALENDAR"

            full_calendar = f"{calendar_header}\n" + '\n'.join(ical_events) + f"\n{calendar_footer}"

            return full_calendar

        except Exception as e:
            logger.error(f"Error generating multi-appointment iCal: {e}")
            return ""


class CalendarIntegrationService:
    """Main calendar integration service that coordinates all calendar services."""

    def __init__(self):
        self.google_service = GoogleCalendarService() if GOOGLE_AVAILABLE else None
        self.outlook_service = OutlookCalendarService() if OUTLOOK_AVAILABLE else None
        self.ical_service = iCalService()

    def sync_appointment_to_calendars(self, appointment_id: int) -> Dict[str, Any]:
        """Sync appointment to all configured calendar services."""
        results = {
            'google': {'status': 'not_configured', 'event_id': None},
            'outlook': {'status': 'not_configured', 'event_id': None},
            'ical': {'status': 'success', 'content': None}
        }

        # Google Calendar
        if self.google_service and self.google_service.service:
            try:
                event_id = self.google_service.create_appointment_event(appointment_id)
                if event_id:
                    results['google'] = {'status': 'success', 'event_id': event_id}
                else:
                    results['google'] = {'status': 'error', 'event_id': None}
            except Exception as e:
                results['google'] = {'status': 'error', 'event_id': None, 'error': str(e)}

        # Outlook Calendar
        if self.outlook_service and self.outlook_service.access_token:
            try:
                event_id = self.outlook_service.create_appointment_event(appointment_id)
                if event_id:
                    results['outlook'] = {'status': 'success', 'event_id': event_id}
                else:
                    results['outlook'] = {'status': 'error', 'event_id': None}
            except Exception as e:
                results['outlook'] = {'status': 'error', 'event_id': None, 'error': str(e)}

        # iCal Export
        try:
            ical_content = self.ical_service.generate_appointment_ical(appointment_id)
            results['ical'] = {'status': 'success', 'content': ical_content}
        except Exception as e:
            results['ical'] = {'status': 'error', 'content': None, 'error': str(e)}

        return results

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all calendar integrations."""
        status = {
            'google': {
                'available': GOOGLE_AVAILABLE,
                'configured': False,
                'authenticated': False
            },
            'outlook': {
                'available': OUTLOOK_AVAILABLE,
                'configured': False,
                'authenticated': False
            },
            'ical': {
                'available': True,
                'configured': True,
                'authenticated': True
            }
        }

        # Check Google
        if self.google_service:
            status['google']['configured'] = True
            status['google']['authenticated'] = self.google_service.service is not None

        # Check Outlook
        if self.outlook_service:
            status['outlook']['configured'] = bool(self.outlook_service.client_id)
            status['outlook']['authenticated'] = self.outlook_service.access_token is not None

        return status
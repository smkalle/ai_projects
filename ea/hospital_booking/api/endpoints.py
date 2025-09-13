"""
REST API Endpoints
External API for hospital booking system integration
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import os
import logging
import hashlib
import hmac
import jwt

from database.connection import get_db_session
from database.models import (
    Hospital, Department, Doctor, Appointment, Patient,
    DoctorAvailability, AppointmentAnalytics, DoctorPerformanceAnalytics
)
from services.dashboard_service import DashboardService
from services.email_service import EmailService
from services.calendar_service import CalendarIntegrationService

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-secret-key-here')
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'


def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        # In production, store API keys in database with proper hashing
        expected_key = os.getenv('API_KEY', 'hospital-api-key-2024')
        if api_key != expected_key:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)

    return decorated_function


def require_jwt_token(f):
    """Decorator to require JWT token authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Authorization token required'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]

            payload = jwt.decode(token, API_SECRET_KEY, algorithms=['HS256'])
            request.user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated_function


# Health Check Endpoint
@app.route(f'{API_PREFIX}/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': API_VERSION,
        'service': 'hospital-booking-api'
    })


# Authentication Endpoints
@app.route(f'{API_PREFIX}/auth/token', methods=['POST'])
def get_auth_token():
    """Generate JWT token for API access."""
    data = request.get_json()

    if not data or not data.get('client_id') or not data.get('client_secret'):
        return jsonify({'error': 'Client credentials required'}), 400

    # In production, validate client credentials against database
    client_id = data['client_id']
    client_secret = data['client_secret']

    # Simple validation (replace with proper database lookup)
    if client_id == 'hospital-client' and client_secret == 'hospital-secret':
        payload = {
            'client_id': client_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }

        token = jwt.encode(payload, API_SECRET_KEY, algorithm='HS256')

        return jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': 86400  # 24 hours
        })
    else:
        return jsonify({'error': 'Invalid client credentials'}), 401


# Hospital Information Endpoints
@app.route(f'{API_PREFIX}/hospital/info', methods=['GET'])
@require_api_key
def get_hospital_info():
    """Get hospital information."""
    try:
        with get_db_session() as session:
            hospital = session.query(Hospital).first()

            if not hospital:
                return jsonify({'error': 'Hospital information not found'}), 404

            return jsonify({
                'id': hospital.id,
                'name': hospital.name,
                'address': hospital.address,
                'phone': hospital.phone,
                'total_beds': hospital.total_beds,
                'current_occupancy': hospital.current_occupancy,
                'occupancy_rate': (hospital.current_occupancy / hospital.total_beds * 100) if hospital.total_beds > 0 else 0
            })

    except Exception as e:
        logger.error(f"Error getting hospital info: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Department Endpoints
@app.route(f'{API_PREFIX}/departments', methods=['GET'])
@require_api_key
def get_departments():
    """Get list of all departments."""
    try:
        with get_db_session() as session:
            departments = session.query(Department).all()

            department_list = []
            for dept in departments:
                department_list.append({
                    'id': dept.id,
                    'name': dept.name,
                    'location': dept.location,
                    'total_staff': dept.total_staff,
                    'active_staff': dept.active_staff,
                    'head_doctor_id': dept.head_doctor_id,
                    'head_doctor_name': dept.head_doctor.name if dept.head_doctor else None
                })

            return jsonify({
                'departments': department_list,
                'total_count': len(department_list)
            })

    except Exception as e:
        logger.error(f"Error getting departments: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route(f'{API_PREFIX}/departments/<department_id>', methods=['GET'])
@require_api_key
def get_department(department_id):
    """Get specific department information."""
    try:
        with get_db_session() as session:
            department = session.query(Department).filter(
                Department.id == department_id
            ).first()

            if not department:
                return jsonify({'error': 'Department not found'}), 404

            # Get doctors in department
            doctors = session.query(Doctor).filter(
                Doctor.department_id == department_id,
                Doctor.status == 'active'
            ).all()

            doctor_list = []
            for doctor in doctors:
                doctor_list.append({
                    'id': doctor.id,
                    'name': doctor.name,
                    'title': doctor.title,
                    'specialization': doctor.specialization,
                    'years_experience': doctor.years_experience,
                    'available_for_booking': doctor.available_for_booking
                })

            return jsonify({
                'id': department.id,
                'name': department.name,
                'location': department.location,
                'total_staff': department.total_staff,
                'active_staff': department.active_staff,
                'head_doctor_id': department.head_doctor_id,
                'head_doctor_name': department.head_doctor.name if department.head_doctor else None,
                'doctors': doctor_list
            })

    except Exception as e:
        logger.error(f"Error getting department {department_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Doctor Endpoints
@app.route(f'{API_PREFIX}/doctors', methods=['GET'])
@require_api_key
def get_doctors():
    """Get list of all doctors with optional filtering."""
    try:
        department_id = request.args.get('department_id')
        available_only = request.args.get('available_only', 'false').lower() == 'true'

        with get_db_session() as session:
            query = session.query(Doctor).filter(Doctor.status == 'active')

            if department_id:
                query = query.filter(Doctor.department_id == department_id)

            if available_only:
                query = query.filter(Doctor.available_for_booking == True)

            doctors = query.all()

            doctor_list = []
            for doctor in doctors:
                doctor_list.append({
                    'id': doctor.id,
                    'name': doctor.name,
                    'title': doctor.title,
                    'department_id': doctor.department_id,
                    'department_name': doctor.department.name if doctor.department else None,
                    'specialization': doctor.specialization,
                    'years_experience': doctor.years_experience,
                    'available_for_booking': doctor.available_for_booking,
                    'email': doctor.email,
                    'phone': doctor.phone
                })

            return jsonify({
                'doctors': doctor_list,
                'total_count': len(doctor_list)
            })

    except Exception as e:
        logger.error(f"Error getting doctors: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route(f'{API_PREFIX}/doctors/<doctor_id>/availability', methods=['GET'])
@require_api_key
def get_doctor_availability(doctor_id):
    """Get doctor availability schedule."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Default to next 7 days if no dates provided
        if not start_date:
            start_date = date.today()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        if not end_date:
            end_date = start_date + timedelta(days=7)
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        with get_db_session() as session:
            doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()

            if not doctor:
                return jsonify({'error': 'Doctor not found'}), 404

            # Get doctor's regular availability
            availability = session.query(DoctorAvailability).filter(
                DoctorAvailability.doctor_id == doctor_id,
                DoctorAvailability.is_active == True
            ).all()

            # Get existing appointments in date range
            appointments = session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date,
                Appointment.status.in_(['scheduled', 'confirmed'])
            ).all()

            # Calculate available slots
            available_slots = []
            current_date = start_date

            while current_date <= end_date:
                day_of_week = current_date.weekday()  # 0=Monday

                # Find availability for this day
                day_availability = [a for a in availability if a.day_of_week == day_of_week]

                if day_availability:
                    for avail in day_availability:
                        # Generate time slots
                        current_time = datetime.combine(current_date, avail.start_time)
                        end_time = datetime.combine(current_date, avail.end_time)
                        slot_duration = timedelta(minutes=avail.appointment_duration)

                        while current_time + slot_duration <= end_time:
                            # Check if slot is already booked
                            is_booked = any(
                                apt.appointment_date == current_date and
                                apt.start_time <= current_time.time() < apt.end_time
                                for apt in appointments
                            )

                            if not is_booked:
                                available_slots.append({
                                    'date': current_date.isoformat(),
                                    'start_time': current_time.time().isoformat(),
                                    'end_time': (current_time + slot_duration).time().isoformat(),
                                    'duration_minutes': avail.appointment_duration
                                })

                            current_time += slot_duration

                current_date += timedelta(days=1)

            return jsonify({
                'doctor_id': doctor_id,
                'doctor_name': doctor.name,
                'department': doctor.department.name if doctor.department else None,
                'available_slots': available_slots,
                'total_slots': len(available_slots)
            })

    except Exception as e:
        logger.error(f"Error getting doctor availability: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Appointment Endpoints
@app.route(f'{API_PREFIX}/appointments', methods=['GET'])
@require_api_key
def get_appointments():
    """Get list of appointments with filtering options."""
    try:
        # Query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        doctor_id = request.args.get('doctor_id')
        department_id = request.args.get('department_id')
        status = request.args.get('status')
        patient_email = request.args.get('patient_email')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        with get_db_session() as session:
            query = session.query(Appointment)

            # Apply filters
            if start_date:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Appointment.appointment_date >= start)

            if end_date:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Appointment.appointment_date <= end)

            if doctor_id:
                query = query.filter(Appointment.doctor_id == doctor_id)

            if department_id:
                query = query.join(Doctor).filter(Doctor.department_id == department_id)

            if status:
                query = query.filter(Appointment.status == status)

            if patient_email:
                query = query.join(Patient).filter(Patient.email == patient_email)

            # Get total count before pagination
            total_count = query.count()

            # Apply pagination
            appointments = query.offset(offset).limit(limit).all()

            appointment_list = []
            for apt in appointments:
                appointment_list.append({
                    'id': apt.id,
                    'patient': {
                        'id': apt.patient.id,
                        'name': f"{apt.patient.first_name} {apt.patient.last_name}",
                        'email': apt.patient.email,
                        'phone': apt.patient.phone
                    },
                    'doctor': {
                        'id': apt.doctor.id,
                        'name': apt.doctor.name,
                        'title': apt.doctor.title,
                        'department': apt.doctor.department.name if apt.doctor.department else None
                    },
                    'appointment_date': apt.appointment_date.isoformat(),
                    'start_time': apt.start_time.isoformat(),
                    'end_time': apt.end_time.isoformat(),
                    'appointment_type': apt.appointment_type,
                    'priority': apt.priority,
                    'status': apt.status,
                    'reason_for_visit': apt.reason_for_visit,
                    'location': apt.location,
                    'notes': apt.notes,
                    'created_at': apt.created_at.isoformat() if apt.created_at else None,
                    'updated_at': apt.updated_at.isoformat() if apt.updated_at else None
                })

            return jsonify({
                'appointments': appointment_list,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': total_count > offset + limit
                }
            })

    except Exception as e:
        logger.error(f"Error getting appointments: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route(f'{API_PREFIX}/appointments', methods=['POST'])
@require_jwt_token
def create_appointment():
    """Create a new appointment."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['patient_email', 'doctor_id', 'appointment_date', 'start_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400

        with get_db_session() as session:
            # Find or create patient
            patient = session.query(Patient).filter(
                Patient.email == data['patient_email']
            ).first()

            if not patient:
                # Create new patient
                patient = Patient(
                    first_name=data.get('patient_first_name', 'Unknown'),
                    last_name=data.get('patient_last_name', 'Unknown'),
                    email=data['patient_email'],
                    phone=data.get('patient_phone', ''),
                    date_of_birth=datetime.strptime(data['patient_dob'], '%Y-%m-%d').date() if data.get('patient_dob') else None
                )
                session.add(patient)
                session.flush()

            # Validate doctor exists and is available
            doctor = session.query(Doctor).filter(
                Doctor.id == data['doctor_id'],
                Doctor.status == 'active',
                Doctor.available_for_booking == True
            ).first()

            if not doctor:
                return jsonify({'error': 'Doctor not found or not available'}), 400

            # Parse appointment details
            appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()

            # Calculate end time (default 30 minutes)
            duration_minutes = data.get('duration_minutes', 30)
            start_datetime = datetime.combine(appointment_date, start_time)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            end_time = end_datetime.time()

            # Check for conflicts
            conflicting_appointments = session.query(Appointment).filter(
                Appointment.doctor_id == data['doctor_id'],
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_(['scheduled', 'confirmed']),
                Appointment.start_time < end_time,
                Appointment.end_time > start_time
            ).first()

            if conflicting_appointments:
                return jsonify({'error': 'Time slot not available - conflicts with existing appointment'}), 400

            # Create appointment
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=data['doctor_id'],
                appointment_date=appointment_date,
                start_time=start_time,
                end_time=end_time,
                appointment_type=data.get('appointment_type', 'patient_care'),
                priority=data.get('priority', 'routine'),
                status='scheduled',
                reason_for_visit=data.get('reason_for_visit', ''),
                location=data.get('location', ''),
                notes=data.get('notes', '')
            )

            session.add(appointment)
            session.commit()

            # Send confirmation email if configured
            try:
                email_service = EmailService()
                email_service.send_appointment_confirmation(appointment.id)
            except Exception as email_error:
                logger.warning(f"Failed to send confirmation email: {email_error}")

            # Sync to calendars if configured
            try:
                calendar_service = CalendarIntegrationService()
                calendar_service.sync_appointment_to_calendars(appointment.id)
            except Exception as calendar_error:
                logger.warning(f"Failed to sync to calendars: {calendar_error}")

            return jsonify({
                'id': appointment.id,
                'status': 'created',
                'confirmation_number': f"CONF-{appointment.id:06d}",
                'appointment_date': appointment.appointment_date.isoformat(),
                'start_time': appointment.start_time.isoformat(),
                'end_time': appointment.end_time.isoformat(),
                'doctor': {
                    'name': doctor.name,
                    'department': doctor.department.name if doctor.department else None
                },
                'patient': {
                    'name': f"{patient.first_name} {patient.last_name}",
                    'email': patient.email
                }
            }), 201

    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route(f'{API_PREFIX}/appointments/<int:appointment_id>', methods=['PUT'])
@require_jwt_token
def update_appointment(appointment_id):
    """Update an existing appointment."""
    try:
        data = request.get_json()

        with get_db_session() as session:
            appointment = session.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()

            if not appointment:
                return jsonify({'error': 'Appointment not found'}), 404

            # Update allowed fields
            if 'status' in data:
                appointment.status = data['status']

            if 'notes' in data:
                appointment.notes = data['notes']

            if 'reason_for_visit' in data:
                appointment.reason_for_visit = data['reason_for_visit']

            # Handle rescheduling
            if 'appointment_date' in data or 'start_time' in data:
                new_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date() if 'appointment_date' in data else appointment.appointment_date
                new_start_time = datetime.strptime(data['start_time'], '%H:%M').time() if 'start_time' in data else appointment.start_time

                # Check for conflicts if rescheduling
                if new_date != appointment.appointment_date or new_start_time != appointment.start_time:
                    duration = datetime.combine(date.today(), appointment.end_time) - datetime.combine(date.today(), appointment.start_time)
                    new_end_time = (datetime.combine(new_date, new_start_time) + duration).time()

                    conflicting_appointments = session.query(Appointment).filter(
                        Appointment.doctor_id == appointment.doctor_id,
                        Appointment.appointment_date == new_date,
                        Appointment.id != appointment_id,
                        Appointment.status.in_(['scheduled', 'confirmed']),
                        Appointment.start_time < new_end_time,
                        Appointment.end_time > new_start_time
                    ).first()

                    if conflicting_appointments:
                        return jsonify({'error': 'New time slot not available'}), 400

                    appointment.appointment_date = new_date
                    appointment.start_time = new_start_time
                    appointment.end_time = new_end_time

            appointment.updated_at = datetime.now()
            session.commit()

            return jsonify({
                'id': appointment.id,
                'status': 'updated',
                'appointment_date': appointment.appointment_date.isoformat(),
                'start_time': appointment.start_time.isoformat(),
                'end_time': appointment.end_time.isoformat()
            })

    except Exception as e:
        logger.error(f"Error updating appointment {appointment_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# Analytics Endpoints
@app.route(f'{API_PREFIX}/analytics/hospital', methods=['GET'])
@require_api_key
def get_hospital_analytics():
    """Get hospital analytics data."""
    try:
        days_back = int(request.args.get('days_back', 30))

        with DashboardService() as dashboard:
            analytics = dashboard.get_hospital_kpis(days_back=days_back)

        return jsonify({
            'period_days': days_back,
            'analytics': analytics,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting hospital analytics: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route(f'{API_PREFIX}/analytics/departments', methods=['GET'])
@require_api_key
def get_department_analytics():
    """Get department performance analytics."""
    try:
        days_back = int(request.args.get('days_back', 30))

        with DashboardService() as dashboard:
            analytics = dashboard.get_department_performance(days_back=days_back)

        return jsonify({
            'period_days': days_back,
            'departments': analytics,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting department analytics: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# API Documentation Endpoint
@app.route(f'{API_PREFIX}/docs', methods=['GET'])
def api_documentation():
    """Get API documentation."""
    docs = {
        'title': 'Hospital Booking System API',
        'version': API_VERSION,
        'description': 'REST API for hospital appointment booking and management',
        'base_url': f'/api/{API_VERSION}',
        'authentication': {
            'api_key': {
                'type': 'header',
                'name': 'X-API-Key',
                'description': 'API key for basic authentication'
            },
            'jwt_token': {
                'type': 'header',
                'name': 'Authorization',
                'description': 'Bearer JWT token for authenticated endpoints'
            }
        },
        'endpoints': {
            'GET /health': 'API health check',
            'POST /auth/token': 'Get JWT token',
            'GET /hospital/info': 'Get hospital information',
            'GET /departments': 'List all departments',
            'GET /departments/{id}': 'Get specific department',
            'GET /doctors': 'List doctors with filtering',
            'GET /doctors/{id}/availability': 'Get doctor availability',
            'GET /appointments': 'List appointments with filtering',
            'POST /appointments': 'Create new appointment',
            'PUT /appointments/{id}': 'Update appointment',
            'GET /analytics/hospital': 'Get hospital analytics',
            'GET /analytics/departments': 'Get department analytics'
        }
    }

    return jsonify(docs)


if __name__ == '__main__':
    # Run the API server
    app.run(
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 5000)),
        debug=os.getenv('API_DEBUG', 'False').lower() == 'true'
    )
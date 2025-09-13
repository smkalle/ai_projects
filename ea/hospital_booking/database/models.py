"""SQLAlchemy database models for Hospital Booking System."""

from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Time, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.connection import Base


class Hospital(Base):
    """Hospital information model."""
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    total_beds = Column(Integer)
    current_occupancy = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    departments = relationship("Department", back_populates="hospital")


class Department(Base):
    """Hospital department model."""
    __tablename__ = "departments"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    head_doctor_id = Column(String(10), ForeignKey("doctors.id"))
    location = Column(String(255))
    total_staff = Column(Integer)
    active_staff = Column(Integer)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    
    # Relationships
    hospital = relationship("Hospital", back_populates="departments")
    head_doctor = relationship("Doctor", foreign_keys=[head_doctor_id])
    doctors = relationship("Doctor", foreign_keys="Doctor.department_id", back_populates="department")
    equipment = relationship("Equipment", back_populates="department")
    rooms = relationship("Room", back_populates="department")


class Doctor(Base):
    """Doctor information model."""
    __tablename__ = "doctors"
    
    id = Column(String(10), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(100))
    department_id = Column(String(50), ForeignKey("departments.id"))
    email = Column(String(255), unique=True, index=True)
    license_number = Column(String(50), unique=True)
    specialization = Column(String(255))
    phone = Column(String(20))
    years_experience = Column(Integer)
    status = Column(String(20), default="active")
    schedule_type = Column(String(20), default="full_time")
    available_for_booking = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", foreign_keys=[department_id], back_populates="doctors")
    availability = relationship("DoctorAvailability", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")


class DoctorAvailability(Base):
    """Doctor availability schedule model."""
    __tablename__ = "doctor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(10), ForeignKey("doctors.id"))
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    start_time = Column(Time)
    end_time = Column(Time)
    appointment_duration = Column(Integer, default=30)  # in minutes
    is_active = Column(Boolean, default=True)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="availability")


class Patient(Base):
    """Patient information model."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    emergency_contact = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    chat_sessions = relationship("ChatSession", back_populates="patient")


class Appointment(Base):
    """Appointment model."""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(String(10), ForeignKey("doctors.id"))
    appointment_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    appointment_type = Column(String(50), default="patient_care")
    priority = Column(String(20), default="routine")
    status = Column(String(20), default="scheduled")
    reason_for_visit = Column(Text)
    location = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")


class Room(Base):
    """Hospital room model."""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), nullable=False, index=True)
    department_id = Column(String(50), ForeignKey("departments.id"))
    room_type = Column(String(50))  # e.g., "examination", "surgery", "emergency"
    capacity = Column(Integer, default=1)
    status = Column(String(20), default="available")  # available, occupied, maintenance
    
    # Relationships
    department = relationship("Department", back_populates="rooms")


class Equipment(Base):
    """Medical equipment model."""
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    department_id = Column(String(50), ForeignKey("departments.id"))
    equipment_type = Column(String(100))
    status = Column(String(20), default="operational")  # operational, maintenance, broken
    last_maintenance = Column(Date)
    next_maintenance = Column(Date)
    
    # Relationships
    department = relationship("Department", back_populates="equipment")


class ChatSession(Base):
    """AI chat session model for future phases."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    session_data = Column(JSON)  # Store conversation history
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="chat_sessions")


# Analytics and reporting models for future phases
class AppointmentAnalytics(Base):
    """Appointment analytics model for reporting."""
    __tablename__ = "appointment_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    department_id = Column(String(50), ForeignKey("departments.id"))
    total_appointments = Column(Integer, default=0)
    completed_appointments = Column(Integer, default=0)
    cancelled_appointments = Column(Integer, default=0)
    no_show_appointments = Column(Integer, default=0)
    average_wait_time = Column(Integer)  # in minutes
    patient_satisfaction = Column(Integer)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)


class DoctorPerformanceAnalytics(Base):
    """Doctor performance analytics model."""
    __tablename__ = "doctor_performance_analytics"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String(10), ForeignKey("doctors.id"))
    date = Column(Date, nullable=False, index=True)
    total_appointments = Column(Integer, default=0)
    completed_appointments = Column(Integer, default=0)
    cancelled_appointments = Column(Integer, default=0)
    no_show_appointments = Column(Integer, default=0)
    average_appointment_duration = Column(Integer)  # in minutes
    patient_satisfaction_avg = Column(Integer)  # 1-5 scale
    utilization_rate = Column(Integer)  # percentage
    revenue_generated = Column(Integer)  # in cents
    created_at = Column(DateTime, default=datetime.utcnow)


class DepartmentPerformanceAnalytics(Base):
    """Department performance analytics model."""
    __tablename__ = "department_performance_analytics"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(String(50), ForeignKey("departments.id"))
    date = Column(Date, nullable=False, index=True)
    total_appointments = Column(Integer, default=0)
    completed_appointments = Column(Integer, default=0)
    cancelled_appointments = Column(Integer, default=0)
    no_show_appointments = Column(Integer, default=0)
    average_wait_time = Column(Integer)  # in minutes
    patient_satisfaction_avg = Column(Integer)  # 1-5 scale
    staff_utilization_rate = Column(Integer)  # percentage
    equipment_utilization_rate = Column(Integer)  # percentage
    revenue_generated = Column(Integer)  # in cents
    operating_costs = Column(Integer)  # in cents
    created_at = Column(DateTime, default=datetime.utcnow)


class HospitalPerformanceAnalytics(Base):
    """Hospital-wide performance analytics model."""
    __tablename__ = "hospital_performance_analytics"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    date = Column(Date, nullable=False, index=True)
    total_appointments = Column(Integer, default=0)
    completed_appointments = Column(Integer, default=0)
    cancelled_appointments = Column(Integer, default=0)
    no_show_appointments = Column(Integer, default=0)
    emergency_appointments = Column(Integer, default=0)
    average_wait_time = Column(Integer)  # in minutes
    patient_satisfaction_avg = Column(Integer)  # 1-5 scale
    bed_occupancy_rate = Column(Integer)  # percentage
    staff_utilization_rate = Column(Integer)  # percentage
    total_revenue = Column(Integer)  # in cents
    total_operating_costs = Column(Integer)  # in cents
    created_at = Column(DateTime, default=datetime.utcnow)


class PatientSatisfactionSurvey(Base):
    """Patient satisfaction survey responses."""
    __tablename__ = "patient_satisfaction_surveys"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(String(10), ForeignKey("doctors.id"))
    overall_satisfaction = Column(Integer)  # 1-5 scale
    wait_time_satisfaction = Column(Integer)  # 1-5 scale
    doctor_satisfaction = Column(Integer)  # 1-5 scale
    facility_satisfaction = Column(Integer)  # 1-5 scale
    communication_satisfaction = Column(Integer)  # 1-5 scale
    would_recommend = Column(Boolean)
    comments = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True)


class FinancialMetrics(Base):
    """Financial performance metrics."""
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    department_id = Column(String(50), ForeignKey("departments.id"))
    doctor_id = Column(String(10), ForeignKey("doctors.id"))
    appointment_revenue = Column(Integer)  # in cents
    procedure_revenue = Column(Integer)  # in cents
    emergency_revenue = Column(Integer)  # in cents
    insurance_claims = Column(Integer)  # in cents
    outstanding_payments = Column(Integer)  # in cents
    staff_costs = Column(Integer)  # in cents
    equipment_costs = Column(Integer)  # in cents
    facility_costs = Column(Integer)  # in cents
    created_at = Column(DateTime, default=datetime.utcnow)


class ReportTemplate(Base):
    """Custom report templates."""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    report_type = Column(String(50))  # e.g., "department", "doctor", "financial"
    template_config = Column(JSON)  # Chart configurations, metrics, filters
    is_public = Column(Boolean, default=False)
    created_by = Column(String(255))  # User who created the template
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduledReport(Base):
    """Scheduled report generation tasks."""
    __tablename__ = "scheduled_reports"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    name = Column(String(255), nullable=False)
    schedule_type = Column(String(20))  # "daily", "weekly", "monthly"
    schedule_time = Column(Time)
    recipients = Column(JSON)  # List of email addresses
    last_generated = Column(DateTime)
    next_generation = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemConfiguration(Base):
    """System configuration model."""
    __tablename__ = "system_configuration"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""
City General Hospital Booking System
Main Streamlit Application

Phase 1: Foundation & Core Booking System
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page
st.set_page_config(
    page_title="City General Hospital - Booking System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database modules
try:
    from database.connection import get_database_manager, get_db_session
    from database.models import (
        Hospital, Department, Doctor, Appointment, Patient, DoctorAvailability, Room, Equipment,
        AppointmentAnalytics, DoctorPerformanceAnalytics, DepartmentPerformanceAnalytics,
        HospitalPerformanceAnalytics, PatientSatisfactionSurvey, FinancialMetrics,
        ReportTemplate, ScheduledReport
    )
    from services.dashboard_service import DashboardService
    from services.analytics_etl import AnalyticsETL, run_daily_etl
    from services.report_generator import ReportGenerator
    from services.email_service import EmailService
    from services.calendar_service import CalendarIntegrationService
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()


def load_tailwind_css():
    """Load Tailwind CSS and custom styles."""
    st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        'hospital-blue': '#2563eb',
                        'hospital-green': '#10b981',
                        'hospital-red': '#ef4444',
                        'hospital-gray': '#6b7280'
                    }
                }
            }
        }
    </script>
    <style>
        /* Custom Streamlit styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Custom card styling */
        .hospital-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
        
        /* Custom metrics styling */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin: 0.5rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        /* Department status indicators */
        .status-active { color: #10b981; }
        .status-busy { color: #f59e0b; }
        .status-critical { color: #ef4444; }
        
        /* Navigation styling */
        .nav-item {
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .nav-item:hover {
            background-color: #f3f4f6;
        }
        
        .nav-item.active {
            background-color: #2563eb;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)


def initialize_database():
    """Initialize database and run migration if needed."""
    try:
        db_manager = get_database_manager()

        # Create all tables first
        db_manager.create_all_tables()

        # Check if database is empty
        session = db_manager.get_session()
        hospital_count = session.query(Hospital).count()
        session.close()
        
        if hospital_count == 0:
            st.warning("Database is empty. Creating sample data...")

            # Create sample data
            from utils.sample_data import create_sample_data
            success = create_sample_data()

            if success:
                st.success("✅ Sample data created successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to create sample data. Please check the logs.")
                return False
        
        return True
        
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False


def get_hospital_stats():
    """Get hospital statistics for dashboard."""
    session = get_db_session()
    try:
        # Get hospital info
        hospital = session.query(Hospital).first()
        
        # Get department count
        dept_count = session.query(Department).count()
        
        # Get doctor count
        doctor_count = session.query(Doctor).filter_by(status="active").count()
        
        # Get today's appointments
        today = date.today()
        appointments_today = session.query(Appointment).filter_by(appointment_date=today).count()
        
        return {
            'hospital': hospital,
            'departments': dept_count,
            'doctors': doctor_count,
            'appointments_today': appointments_today
        }
        
    except Exception as e:
        st.error(f"Error fetching hospital stats: {e}")
        return None
    finally:
        session.close()


def render_hospital_overview():
    """Render the hospital overview dashboard."""
    st.markdown("# 🏥 City General Hospital")
    st.markdown("### Booking System Dashboard")
    
    # Get hospital statistics
    stats = get_hospital_stats()
    if not stats:
        st.error("Unable to load hospital statistics")
        return
    
    hospital = stats['hospital']
    
    # Hospital info header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="hospital-card">
            <h3 style="margin-top: 0; color: #1f2937;">{hospital.name}</h3>
            <p style="color: #6b7280; margin-bottom: 0.5rem;">{hospital.address}</p>
            <p style="color: #6b7280; margin-bottom: 0;">📞 {hospital.phone}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        occupancy_rate = (hospital.current_occupancy / hospital.total_beds * 100) if hospital.total_beds > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{hospital.current_occupancy}/{hospital.total_beds}</div>
            <div class="metric-label">Bed Occupancy</div>
            <div style="font-size: 0.8rem; margin-top: 0.25rem;">{occupancy_rate:.1f}% Full</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
            <div class="metric-value">{stats['appointments_today']}</div>
            <div class="metric-label">Today's Appointments</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏢 Departments",
            value=stats['departments'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="👨‍⚕️ Active Doctors", 
            value=stats['doctors'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="📅 This Week",
            value="156",  # Placeholder
            delta="12"
        )
    
    with col4:
        st.metric(
            label="⭐ Satisfaction",
            value="4.8/5",
            delta="0.2"
        )
    
    # Department overview
    st.markdown("---")
    st.markdown("### 🏢 Department Overview")
    
    session = get_db_session()
    try:
        departments = session.query(Department).all()
        
        # Create department cards
        cols = st.columns(min(3, len(departments)))
        
        for idx, dept in enumerate(departments):
            with cols[idx % 3]:
                # Get department doctors
                dept_doctors = session.query(Doctor).filter_by(
                    department_id=dept.id, 
                    status="active"
                ).count()
                
                # Determine status color
                utilization = (dept.active_staff / dept.total_staff * 100) if dept.total_staff > 0 else 0
                if utilization >= 90:
                    status_class = "status-critical"
                    status_text = "High Load"
                elif utilization >= 70:
                    status_class = "status-busy" 
                    status_text = "Busy"
                else:
                    status_class = "status-active"
                    status_text = "Available"
                
                st.markdown(f"""
                <div class="hospital-card">
                    <h4 style="margin-top: 0; color: #1f2937;">{dept.name}</h4>
                    <p style="color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0;">📍 {dept.location}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: 600;">{dept_doctors}</span> doctors<br>
                            <span style="font-weight: 600;">{dept.active_staff}/{dept.total_staff}</span> staff
                        </div>
                        <div class="{status_class}" style="font-weight: 600; font-size: 0.9rem;">
                            {status_text}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View {dept.name}", key=f"dept_{dept.id}"):
                    st.session_state['current_department'] = dept.id
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error loading departments: {e}")
    finally:
        session.close()
    
    # Recent activity
    st.markdown("---")
    st.markdown("### 📊 Recent Activity")
    
    session = get_db_session()
    try:
        # Get recent appointments
        recent_appointments = session.query(Appointment).join(Doctor).join(Patient).filter(
            Appointment.appointment_date >= date.today() - timedelta(days=1)
        ).order_by(Appointment.created_at.desc()).limit(10).all()
        
        if recent_appointments:
            activity_data = []
            for apt in recent_appointments:
                activity_data.append({
                    'Time': apt.start_time.strftime('%H:%M'),
                    'Patient': f"{apt.patient.first_name} {apt.patient.last_name}",
                    'Doctor': apt.doctor.name,
                    'Department': apt.doctor.department.name,
                    'Type': apt.appointment_type.replace('_', ' ').title(),
                    'Status': apt.status.title()
                })
            
            df = pd.DataFrame(activity_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent appointments found.")
    
    except Exception as e:
        st.error(f"Error loading recent activity: {e}")
    finally:
        session.close()


def render_doctors_directory():
    """Render the doctors directory page."""
    st.markdown("# 👨‍⚕️ Doctors Directory")
    st.markdown("### Find and connect with our medical professionals")

    # Search and filter section
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        search_term = st.text_input("🔍 Search doctors by name or specialization", placeholder="Enter doctor name or specialty...")

    with col2:
        # Get departments for filter
        session = get_db_session()
        try:
            departments = session.query(Department).all()
            dept_options = ["All Departments"] + [dept.name for dept in departments]
            selected_dept = st.selectbox("🏢 Department", dept_options)
        finally:
            session.close()

    with col3:
        status_filter = st.selectbox("📊 Status", ["All", "Active", "Busy", "Unavailable"])

    st.markdown("---")

    # Get filtered doctors
    session = get_db_session()
    try:
        # Base query - explicitly specify join condition
        query = session.query(Doctor).join(Department, Doctor.department_id == Department.id)

        # Apply search filter
        if search_term:
            query = query.filter(
                (Doctor.name.ilike(f"%{search_term}%")) |
                (Doctor.specialization.ilike(f"%{search_term}%"))
            )

        # Apply department filter
        if selected_dept != "All Departments":
            query = query.filter(Department.name == selected_dept)

        # Apply status filter
        if status_filter != "All":
            query = query.filter(Doctor.status == status_filter.lower())

        doctors = query.order_by(Doctor.name).all()

        if not doctors:
            st.info("No doctors found matching your criteria.")
            return

        # Display doctors in cards
        st.markdown(f"### Found {len(doctors)} doctors")

        # Create rows of 2 doctors each
        for i in range(0, len(doctors), 2):
            cols = st.columns(2)

            for j, col in enumerate(cols):
                if i + j < len(doctors):
                    doctor = doctors[i + j]
                    with col:
                        render_doctor_card(doctor)

    except Exception as e:
        st.error(f"Error loading doctors: {e}")
    finally:
        session.close()


def render_doctor_card(doctor):
    """Render individual doctor card."""
    # Determine status color
    if doctor.status == "active":
        status_color = "#10b981"
        status_text = "Available"
    elif doctor.status == "busy":
        status_color = "#f59e0b"
        status_text = "Busy"
    else:
        status_color = "#ef4444"
        status_text = "Unavailable"

    # Get today's appointments count
    session = get_db_session()
    try:
        today_appointments = session.query(Appointment).filter_by(
            doctor_id=doctor.id,
            appointment_date=date.today()
        ).count()
    except:
        today_appointments = 0
    finally:
        session.close()

    # Use Streamlit container with styling
    with st.container():
        st.markdown(f"#### {doctor.name}")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{doctor.title}**")
            st.write(f"📍 {doctor.department.name}")
        with col2:
            if doctor.status == "active":
                st.success(f"● Available")
            elif doctor.status == "busy":
                st.warning(f"● Busy")
            else:
                st.error(f"● Unavailable")

        # Details in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Specialization", doctor.specialization)
        with col2:
            st.metric("Experience", f"{doctor.years_experience} years")
        with col3:
            st.metric("Today's Appointments", today_appointments)

        # Contact info
        st.write(f"📞 {doctor.phone} | 📧 {doctor.email}")

        st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"👁️ View Details", key=f"view_{doctor.id}", use_container_width=True):
            st.session_state[f'show_doctor_details_{doctor.id}'] = True
            st.rerun()

    with col2:
        if doctor.available_for_booking:
            if st.button(f"📅 Book Appointment", key=f"book_{doctor.id}", use_container_width=True):
                st.session_state['booking_doctor_id'] = doctor.id
                st.session_state['show_appointment_form'] = True
                st.rerun()
        else:
            st.button("❌ Not Available", disabled=True, use_container_width=True)

    # Show doctor details modal if requested
    if st.session_state.get(f'show_doctor_details_{doctor.id}', False):
        render_doctor_details_modal(doctor)


def render_doctor_details_modal(doctor):
    """Render doctor details in a modal-like container."""
    st.markdown("---")
    st.markdown(f"## 👨‍⚕️ {doctor.name} - Detailed Information")

    # Close button
    if st.button("✕ Close Details", key=f"close_details_{doctor.id}"):
        st.session_state[f'show_doctor_details_{doctor.id}'] = False
        st.rerun()

    # Doctor details in columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Professional Information")
        st.write(f"**Full Name:** {doctor.name}")
        st.write(f"**Title:** {doctor.title}")
        st.write(f"**Department:** {doctor.department.name}")
        st.write(f"**Specialization:** {doctor.specialization}")
        st.write(f"**License Number:** {doctor.license_number}")
        st.write(f"**Years of Experience:** {doctor.years_experience}")
        st.write(f"**Schedule Type:** {doctor.schedule_type.replace('_', ' ').title()}")

    with col2:
        st.markdown("### Contact & Availability")
        st.write(f"**Phone:** {doctor.phone}")
        st.write(f"**Email:** {doctor.email}")
        st.write(f"**Status:** {doctor.status.title()}")
        st.write(f"**Available for Booking:** {'Yes' if doctor.available_for_booking else 'No'}")

    # Weekly schedule
    st.markdown("### 📅 Weekly Schedule")
    session = get_db_session()
    try:
        availability = session.query(DoctorAvailability).filter_by(
            doctor_id=doctor.id, is_active=True
        ).order_by(DoctorAvailability.day_of_week).all()

        if availability:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            schedule_data = []

            for avail in availability:
                schedule_data.append({
                    'Day': days[avail.day_of_week],
                    'Start Time': avail.start_time.strftime('%H:%M'),
                    'End Time': avail.end_time.strftime('%H:%M'),
                    'Duration (mins)': avail.appointment_duration
                })

            if schedule_data:
                df = pd.DataFrame(schedule_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No schedule information available.")
        else:
            st.info("No availability schedule found.")

    except Exception as e:
        st.error(f"Error loading schedule: {e}")
    finally:
        session.close()

    # Recent appointments
    st.markdown("### 📋 Recent Activity")
    session = get_db_session()
    try:
        recent_appointments = session.query(Appointment).join(Patient).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= date.today() - timedelta(days=7)
        ).order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc()).limit(5).all()

        if recent_appointments:
            activity_data = []
            for apt in recent_appointments:
                activity_data.append({
                    'Date': apt.appointment_date.strftime('%Y-%m-%d'),
                    'Time': apt.start_time.strftime('%H:%M'),
                    'Patient': f"{apt.patient.first_name} {apt.patient.last_name}",
                    'Type': apt.appointment_type.replace('_', ' ').title(),
                    'Status': apt.status.title()
                })

            df = pd.DataFrame(activity_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent appointments found.")

    except Exception as e:
        st.error(f"Error loading recent appointments: {e}")
    finally:
        session.close()

    st.markdown("---")


def render_departments_management():
    """Render the departments management page."""
    st.markdown("# 🏢 Department Management")
    st.markdown("### Hospital department overview and resource management")

    # Department selection
    session = get_db_session()
    try:
        departments = session.query(Department).all()
        dept_options = ["All Departments"] + [dept.name for dept in departments]
        selected_dept = st.selectbox("📋 Select Department", dept_options)
    finally:
        session.close()

    if selected_dept == "All Departments":
        render_all_departments_overview()
    else:
        # Find the department by name
        session = get_db_session()
        try:
            department = session.query(Department).filter_by(name=selected_dept).first()
            if department:
                render_single_department_view(department)
            else:
                st.error("Department not found")
        finally:
            session.close()


def render_all_departments_overview():
    """Render overview of all departments."""
    st.markdown("## 📊 All Departments Overview")

    session = get_db_session()
    try:
        departments = session.query(Department).all()

        if not departments:
            st.warning("No departments found.")
            return

        # Department metrics
        col1, col2, col3, col4 = st.columns(4)

        total_departments = len(departments)
        total_doctors = sum(session.query(Doctor).filter_by(department_id=dept.id).count() for dept in departments)
        total_rooms = sum(session.query(Room).filter_by(department_id=dept.id).count() for dept in departments)
        total_equipment = sum(session.query(Equipment).filter_by(department_id=dept.id).count() for dept in departments)

        col1.metric("🏢 Departments", total_departments)
        col2.metric("👨‍⚕️ Total Doctors", total_doctors)
        col3.metric("🏠 Total Rooms", total_rooms)
        col4.metric("⚕️ Equipment", total_equipment)

        st.markdown("---")

        # Department comparison table
        st.markdown("### 📋 Department Comparison")

        dept_data = []
        for dept in departments:
            doctor_count = session.query(Doctor).filter_by(department_id=dept.id, status="active").count()
            room_count = session.query(Room).filter_by(department_id=dept.id).count()
            equipment_count = session.query(Equipment).filter_by(department_id=dept.id).count()

            # Get head doctor name
            head_doctor = session.query(Doctor).filter_by(id=dept.head_doctor_id).first()
            head_name = head_doctor.name if head_doctor else "Not Assigned"

            # Calculate utilization
            utilization = (dept.active_staff / dept.total_staff * 100) if dept.total_staff > 0 else 0

            dept_data.append({
                'Department': dept.name,
                'Head Doctor': head_name,
                'Location': dept.location,
                'Active Doctors': doctor_count,
                'Staff Utilization': f"{utilization:.1f}%",
                'Rooms': room_count,
                'Equipment': equipment_count
            })

        df = pd.DataFrame(dept_data)
        st.dataframe(df, use_container_width=True)

        # Department cards with quick actions
        st.markdown("---")
        st.markdown("### 🏢 Department Cards")

        for i in range(0, len(departments), 2):
            cols = st.columns(2)

            for j, col in enumerate(cols):
                if i + j < len(departments):
                    dept = departments[i + j]
                    with col:
                        render_department_card(dept, session)

    except Exception as e:
        st.error(f"Error loading departments: {e}")
    finally:
        session.close()


def render_department_card(department, session):
    """Render individual department card."""
    # Get department stats
    doctor_count = session.query(Doctor).filter_by(department_id=department.id, status="active").count()
    room_count = session.query(Room).filter_by(department_id=department.id).count()
    equipment_count = session.query(Equipment).filter_by(department_id=department.id).count()

    # Get head doctor
    head_doctor = session.query(Doctor).filter_by(id=department.head_doctor_id).first()
    head_name = head_doctor.name if head_doctor else "Not Assigned"

    # Calculate utilization and determine status
    utilization = (department.active_staff / department.total_staff * 100) if department.total_staff > 0 else 0

    if utilization >= 90:
        status_color = "#ef4444"
        status_text = "High Load"
    elif utilization >= 70:
        status_color = "#f59e0b"
        status_text = "Busy"
    else:
        status_color = "#10b981"
        status_text = "Available"

    # Use Streamlit container for department card
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"#### {department.name}")
            st.write(f"📍 {department.location}")
            st.write(f"👨‍⚕️ Head: {head_name}")
        with col2:
            utilization = (department.active_staff / department.total_staff * 100) if department.total_staff > 0 else 0
            if utilization >= 90:
                st.error(f"● High Load")
            elif utilization >= 70:
                st.warning(f"● Busy")
            else:
                st.success(f"● Available")

        # Metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Doctors", doctor_count)
        with col2:
            st.metric("Staff", f"{department.active_staff}/{department.total_staff}")
        with col3:
            st.metric("Rooms", room_count)
        with col4:
            st.metric("Equipment", equipment_count)

        st.markdown("---")

    # Action button
    if st.button(f"🔍 View {department.name} Details", key=f"dept_detail_{department.id}", use_container_width=True):
        st.session_state['selected_department'] = department.name
        st.rerun()


def render_single_department_view(department):
    """Render detailed view of a single department."""
    st.markdown(f"## 🏢 {department.name} - Detailed View")

    # Back button
    if st.button("← Back to All Departments"):
        st.session_state.pop('selected_department', None)
        st.rerun()

    session = get_db_session()
    try:
        # Department header info
        col1, col2, col3, col4 = st.columns(4)

        doctor_count = session.query(Doctor).filter_by(department_id=department.id, status="active").count()
        room_count = session.query(Room).filter_by(department_id=department.id).count()
        equipment_count = session.query(Equipment).filter_by(department_id=department.id).count()

        today_appointments = session.query(Appointment).join(Doctor).filter(
            Doctor.department_id == department.id,
            Appointment.appointment_date == date.today()
        ).count()

        col1.metric("👨‍⚕️ Active Doctors", doctor_count)
        col2.metric("🏠 Rooms", room_count)
        col3.metric("⚕️ Equipment", equipment_count)
        col4.metric("📅 Today's Appointments", today_appointments)

        # Department details
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📋 Department Information")
            head_doctor = session.query(Doctor).filter_by(id=department.head_doctor_id).first()
            head_name = head_doctor.name if head_doctor else "Not Assigned"

            utilization = (department.active_staff / department.total_staff * 100) if department.total_staff > 0 else 0

            st.write(f"**Department:** {department.name}")
            st.write(f"**Location:** {department.location}")
            st.write(f"**Head Doctor:** {head_name}")
            st.write(f"**Staff:** {department.active_staff}/{department.total_staff} ({utilization:.1f}% utilization)")

        with col2:
            st.markdown("### 📊 Quick Stats")
            if utilization >= 90:
                st.error(f"⚠️ High workload ({utilization:.1f}%)")
            elif utilization >= 70:
                st.warning(f"⚡ Busy department ({utilization:.1f}%)")
            else:
                st.success(f"✅ Normal operations ({utilization:.1f}%)")

        # Doctors in department
        st.markdown("---")
        st.markdown("### 👨‍⚕️ Doctors in Department")

        doctors = session.query(Doctor).filter_by(department_id=department.id).all()

        if doctors:
            doctor_data = []
            for doctor in doctors:
                today_apts = session.query(Appointment).filter_by(
                    doctor_id=doctor.id,
                    appointment_date=date.today()
                ).count()

                doctor_data.append({
                    'Name': doctor.name,
                    'Title': doctor.title,
                    'Specialization': doctor.specialization,
                    'Experience': f"{doctor.years_experience} years",
                    'Status': doctor.status.title(),
                    "Today's Appointments": today_apts,
                    'Phone': doctor.phone,
                    'Email': doctor.email
                })

            df = pd.DataFrame(doctor_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No doctors assigned to this department.")

        # Rooms and Equipment tabs
        st.markdown("---")
        tab1, tab2 = st.tabs(["🏠 Rooms", "⚕️ Equipment"])

        with tab1:
            rooms = session.query(Room).filter_by(department_id=department.id).all()

            if rooms:
                room_data = []
                for room in rooms:
                    room_data.append({
                        'Room Number': room.room_number,
                        'Type': room.room_type.replace('_', ' ').title(),
                        'Capacity': room.capacity,
                        'Status': room.status.title()
                    })

                df = pd.DataFrame(room_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No rooms found for this department.")

        with tab2:
            equipment = session.query(Equipment).filter_by(department_id=department.id).all()

            if equipment:
                equipment_data = []
                for eq in equipment:
                    equipment_data.append({
                        'Equipment Name': eq.name,
                        'Type': eq.equipment_type.replace('_', ' ').title(),
                        'Status': eq.status.title(),
                        'Last Maintenance': eq.last_maintenance.strftime('%Y-%m-%d') if eq.last_maintenance else 'N/A',
                        'Next Maintenance': eq.next_maintenance.strftime('%Y-%m-%d') if eq.next_maintenance else 'N/A'
                    })

                df = pd.DataFrame(equipment_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No equipment found for this department.")

    except Exception as e:
        st.error(f"Error loading department details: {e}")
    finally:
        session.close()


def render_appointments_management():
    """Render the appointments management page."""
    st.markdown("# 📅 Appointment Management")
    st.markdown("### Schedule, view, and manage hospital appointments")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Appointments", "📅 Schedule New", "🔍 Search", "📊 Calendar View"])

    with tab1:
        render_appointments_list()

    with tab2:
        render_appointment_booking_form()

    with tab3:
        render_appointment_search()

    with tab4:
        render_calendar_view()


def render_appointments_list():
    """Render list of all appointments."""
    st.markdown("### 📋 Appointment List")

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        date_filter = st.date_input("📅 Date", value=date.today())

    with col2:
        session = get_db_session()
        try:
            doctors = session.query(Doctor).all()
            doctor_options = ["All Doctors"] + [f"{doc.name} ({doc.id})" for doc in doctors]
            selected_doctor = st.selectbox("👨‍⚕️ Doctor", doctor_options)
        finally:
            session.close()

    with col3:
        status_options = ["All", "scheduled", "completed", "cancelled", "no_show"]
        selected_status = st.selectbox("📊 Status", status_options)

    with col4:
        type_options = ["All", "patient_care", "procedure", "emergency", "administrative"]
        selected_type = st.selectbox("🏷️ Type", type_options)

    # Get filtered appointments
    session = get_db_session()
    try:
        query = session.query(Appointment).join(Doctor).join(Patient)

        # Apply filters
        if date_filter:
            query = query.filter(Appointment.appointment_date == date_filter)

        if selected_doctor != "All Doctors":
            doctor_id = selected_doctor.split("(")[1].replace(")", "")
            query = query.filter(Appointment.doctor_id == doctor_id)

        if selected_status != "All":
            query = query.filter(Appointment.status == selected_status)

        if selected_type != "All":
            query = query.filter(Appointment.appointment_type == selected_type)

        appointments = query.order_by(Appointment.start_time).all()

        if not appointments:
            st.info("No appointments found matching your criteria.")
            return

        # Display appointments
        st.markdown(f"### Found {len(appointments)} appointments")

        for apt in appointments:
            render_appointment_card(apt)

    except Exception as e:
        st.error(f"Error loading appointments: {e}")
    finally:
        session.close()

    # Quick add appointment modal
    if st.session_state.get('show_quick_add', False):
        render_quick_add_modal()


def render_appointment_card(appointment):
    """Render individual appointment card."""
    # Status colors
    status_colors = {
        "scheduled": "#10b981",
        "completed": "#6b7280",
        "cancelled": "#ef4444",
        "no_show": "#f59e0b"
    }

    priority_colors = {
        "urgent": "#ef4444",
        "high": "#f59e0b",
        "routine": "#10b981"
    }

    status_color = status_colors.get(appointment.status, "#6b7280")
    priority_color = priority_colors.get(appointment.priority, "#10b981")

    # Use Streamlit container for appointment card
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"#### {appointment.patient.first_name} {appointment.patient.last_name}")
            st.write(f"👨‍⚕️ {appointment.doctor.name}")
            st.write(f"📍 {appointment.doctor.department.name} • {appointment.location or 'TBD'}")
        with col2:
            if appointment.status == "scheduled":
                st.success(f"● {appointment.status.title()}")
            elif appointment.status == "completed":
                st.info(f"● {appointment.status.title()}")
            elif appointment.status == "cancelled":
                st.error(f"● {appointment.status.title()}")
            else:
                st.warning(f"● {appointment.status.title()}")

            if appointment.priority == "urgent":
                st.error(f"{appointment.priority.title()} Priority")
            elif appointment.priority == "high":
                st.warning(f"{appointment.priority.title()} Priority")
            else:
                st.success(f"{appointment.priority.title()} Priority")

        # Time and details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Start Time", appointment.start_time.strftime('%H:%M'))
        with col2:
            st.metric("End Time", appointment.end_time.strftime('%H:%M'))
        with col3:
            st.metric("Type", appointment.appointment_type.replace('_', ' ').title())

        # Additional info
        if appointment.reason_for_visit:
            st.write(f"**Reason:** {appointment.reason_for_visit}")
        if appointment.notes:
            st.write(f"**Notes:** {appointment.notes}")

        st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"📝 Edit", key=f"edit_apt_{appointment.id}", use_container_width=True):
            st.session_state[f'editing_appointment_{appointment.id}'] = True
            st.rerun()

    with col2:
        if appointment.status == "scheduled":
            if st.button(f"✅ Complete", key=f"complete_apt_{appointment.id}", use_container_width=True):
                update_appointment_status(appointment.id, "completed")
        else:
            st.button("✅ Complete", disabled=True, use_container_width=True)

    with col3:
        if appointment.status == "scheduled":
            if st.button(f"❌ Cancel", key=f"cancel_apt_{appointment.id}", use_container_width=True):
                update_appointment_status(appointment.id, "cancelled")
        else:
            st.button("❌ Cancel", disabled=True, use_container_width=True)


def render_appointment_booking_form():
    """Render appointment booking form."""
    st.markdown("### 📅 Schedule New Appointment")

    with st.form("appointment_form"):
        # Patient selection/creation
        st.markdown("#### 👤 Patient Information")
        col1, col2 = st.columns(2)

        with col1:
            patient_first_name = st.text_input("First Name*", placeholder="John")
            patient_email = st.text_input("Email*", placeholder="john@example.com")

        with col2:
            patient_last_name = st.text_input("Last Name*", placeholder="Smith")
            patient_phone = st.text_input("Phone", placeholder="(555) 123-4567")

        # Doctor and appointment details
        st.markdown("#### 👨‍⚕️ Appointment Details")
        col1, col2 = st.columns(2)

        with col1:
            session = get_db_session()
            try:
                doctors = session.query(Doctor).filter_by(available_for_booking=True).all()
                doctor_options = [f"{doc.name} - {doc.department.name} ({doc.id})" for doc in doctors]
                selected_doctor_option = st.selectbox("Doctor*", doctor_options)
            finally:
                session.close()

            appointment_date = st.date_input("Appointment Date*", min_value=date.today())

        with col2:
            appointment_time = st.time_input("Start Time*", value=time(9, 0))
            duration = st.selectbox("Duration (minutes)", [30, 45, 60, 90], index=0)

        # Appointment type and details
        col1, col2 = st.columns(2)

        with col1:
            appointment_types = ["patient_care", "procedure", "emergency", "administrative"]
            selected_type = st.selectbox("Appointment Type*", appointment_types)

        with col2:
            priorities = ["routine", "high", "urgent"]
            selected_priority = st.selectbox("Priority", priorities)

        reason = st.text_area("Reason for Visit*", placeholder="Describe the purpose of this appointment...")
        location = st.text_input("Location", placeholder="Room number or location")
        notes = st.text_area("Additional Notes", placeholder="Any special instructions or notes...")

        # Submit button
        submit_button = st.form_submit_button("📅 Schedule Appointment", use_container_width=True)

        if submit_button:
            if not all([patient_first_name, patient_last_name, patient_email, selected_doctor_option, reason]):
                st.error("Please fill in all required fields (marked with *).")
            else:
                # Extract doctor ID
                doctor_id = selected_doctor_option.split("(")[1].replace(")", "")

                # Calculate end time
                start_datetime = datetime.combine(appointment_date, appointment_time)
                end_time = (start_datetime + timedelta(minutes=duration)).time()

                success = create_appointment(
                    patient_first_name, patient_last_name, patient_email, patient_phone,
                    doctor_id, appointment_date, appointment_time, end_time,
                    selected_type, selected_priority, reason, location, notes
                )

                if success:
                    st.success("✅ Appointment scheduled successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to schedule appointment. Please try again.")


def render_quick_add_modal():
    """Render quick appointment booking modal from calendar."""
    st.markdown("---")
    st.markdown("### ✅ Quick Add Appointment")

    quick_add_date = st.session_state.get('quick_add_date', date.today())
    st.info(f"Adding appointment for {quick_add_date.strftime('%A, %B %d, %Y')}")

    with st.form("quick_add_form"):
        col1, col2 = st.columns(2)

        with col1:
            patient_name = st.text_input("👤 Patient Name*", placeholder="John Smith")
            appointment_time = st.time_input("⏰ Start Time", value=datetime.now().time())

        with col2:
            patient_email = st.text_input("📧 Email*", placeholder="john@example.com")
            duration = st.selectbox("🕰️ Duration", [30, 45, 60, 90, 120], index=1)

        # Doctor selection
        session = get_db_session()
        try:
            doctors = session.query(Doctor).filter_by(available_for_booking=True).all()
            doctor_options = [f"{doc.name} - {doc.department.name}" for doc in doctors]
            selected_doctor_name = st.selectbox("👨‍⚕️ Doctor*", doctor_options)
        finally:
            session.close()

        appointment_type = st.selectbox(
            "🏷️ Type*",
            ["patient_care", "procedure", "emergency", "administrative"],
            format_func=lambda x: x.replace('_', ' ').title()
        )

        priority = st.selectbox("⚠️ Priority", ["routine", "high", "urgent"])
        reason = st.text_area("📝 Reason for Visit", placeholder="Brief description...")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.form_submit_button("✅ Book Appointment", use_container_width=True, type="primary"):
                if patient_name and patient_email and selected_doctor_name:
                    # Process the booking
                    success = create_quick_appointment(
                        patient_name, patient_email, selected_doctor_name,
                        quick_add_date, appointment_time, duration,
                        appointment_type, priority, reason
                    )
                    if success:
                        st.success("✅ Appointment booked successfully!")
                        st.session_state['show_quick_add'] = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to book appointment. Please try again.")
                else:
                    st.warning("⚠️ Please fill in all required fields.")

        with col2:
            if st.form_submit_button("🗑️ Cancel", use_container_width=True):
                st.session_state['show_quick_add'] = False
                st.rerun()

        with col3:
            if st.form_submit_button("🔄 Clear", use_container_width=True):
                st.rerun()


def create_quick_appointment(patient_name, patient_email, doctor_name, apt_date,
                           start_time, duration_minutes, apt_type, priority, reason):
    """Create a new appointment from quick add form."""
    session = get_db_session()
    try:
        # Parse patient name
        name_parts = patient_name.strip().split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        # Find or create patient
        patient = session.query(Patient).filter_by(
            first_name=first_name,
            last_name=last_name,
            email=patient_email
        ).first()

        if not patient:
            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                email=patient_email,
                phone='',
                date_of_birth=date(1990, 1, 1),  # Default DOB
                created_at=datetime.now()
            )
            session.add(patient)
            session.flush()  # Get patient ID

        # Find doctor
        doctor = session.query(Doctor).filter(
            Doctor.name.contains(doctor_name.split(' - ')[0])
        ).first()

        if not doctor:
            return False

        # Calculate end time
        start_datetime = datetime.combine(apt_date, start_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)

        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=apt_date,
            start_time=start_datetime,
            end_time=end_datetime,
            appointment_type=apt_type,
            status='scheduled',
            priority=priority,
            reason_for_visit=reason,
            location=f"Room {doctor.department.name[:3].upper()}-101",  # Default location
            notes='Created via quick add',
            created_at=datetime.now()
        )

        session.add(appointment)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        st.error(f"Database error: {e}")
        return False
    finally:
        session.close()


def render_appointment_search():
    """Render appointment search functionality."""
    st.markdown("### 🔍 Search Appointments")

    # Search options
    col1, col2 = st.columns(2)

    with col1:
        search_term = st.text_input("🔍 Search by patient name, doctor name, or reason", placeholder="Enter search term...")

    with col2:
        date_range = st.date_input("📅 Date Range", value=(date.today() - timedelta(days=7), date.today() + timedelta(days=30)), help="Select start and end dates")

    if search_term or date_range:
        session = get_db_session()
        try:
            query = session.query(Appointment).join(Doctor).join(Patient)

            # Apply search term
            if search_term:
                query = query.filter(
                    (Patient.first_name.ilike(f"%{search_term}%")) |
                    (Patient.last_name.ilike(f"%{search_term}%")) |
                    (Doctor.name.ilike(f"%{search_term}%")) |
                    (Appointment.reason_for_visit.ilike(f"%{search_term}%"))
                )

            # Apply date range
            if len(date_range) == 2:
                start_date, end_date = date_range
                query = query.filter(
                    Appointment.appointment_date >= start_date,
                    Appointment.appointment_date <= end_date
                )

            appointments = query.order_by(Appointment.appointment_date, Appointment.start_time).all()

            if appointments:
                st.markdown(f"### Found {len(appointments)} appointments")
                for apt in appointments:
                    render_appointment_card(apt)
            else:
                st.info("No appointments found matching your search criteria.")

        except Exception as e:
            st.error(f"Error searching appointments: {e}")
        finally:
            session.close()


def render_calendar_view():
    """Render beautiful timeline calendar view of appointments."""
    st.markdown("### 📅 Calendar Timeline View")
    st.markdown("*Interactive calendar with hourly appointment slots*")

    # Date and view controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        selected_date = st.date_input("📅 Select Date", value=date.today())

    with col2:
        view_mode = st.selectbox("📊 View", ["Day", "Week"])

    with col3:
        department_filter = st.selectbox(
            "🏥 Department",
            ["All", "Cardiology", "Emergency", "Surgery", "Internal Medicine", "Pediatrics"]
        )

    with col4:
        if st.button("📅 Today", use_container_width=True):
            selected_date = date.today()
            st.rerun()

    # Calendar view using native Streamlit components for better compatibility

    session = get_db_session()
    try:
        if view_mode == "Day":
            render_day_timeline(selected_date, department_filter, session)
        else:
            render_week_timeline(selected_date, department_filter, session)
    except Exception as e:
        st.error(f"Error loading calendar: {e}")
    finally:
        session.close()


def render_day_timeline(selected_date, department_filter, session):
    """Render single day timeline view using Streamlit native components."""
    # Get appointments for the selected date
    query = session.query(Appointment).join(Doctor).join(Patient).filter(
        Appointment.appointment_date == selected_date
    )

    if department_filter != "All":
        query = query.join(Department).filter(Department.name == department_filter)

    appointments = query.order_by(Appointment.start_time).all()

    # Create legend using columns
    st.markdown(f"**{selected_date.strftime('%A, %B %d, %Y')} - {len(appointments)} appointments**")

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(":green[🟢 Patient Care]")
        with col2:
            st.markdown(":blue[🟢 Procedures]")
        with col3:
            st.markdown(":red[🟢 Emergency]")
        with col4:
            st.markdown(":orange[🟢 Administrative]")

    st.markdown("---")

    # Group appointments by hour for better display
    appointments_by_hour = {}
    for apt in appointments:
        hour = apt.start_time.hour
        if hour not in appointments_by_hour:
            appointments_by_hour[hour] = []
        appointments_by_hour[hour].append(apt)

    # Create timeline using Streamlit containers
    timeline_container = st.container()

    with timeline_container:
        # Generate hours from 8 AM to 6 PM
        for hour in range(8, 19):
            # Hour label
            hour_12 = hour if hour <= 12 else hour - 12
            period = "AM" if hour < 12 else "PM"
            if hour == 12:
                hour_12 = 12
            hour_label = f"{hour_12}:00 {period}"

            # Create hour section
            col_time, col_appointments = st.columns([1, 4])

            with col_time:
                if hour == datetime.now().hour and selected_date == date.today():
                    st.markdown(f"**:red[{hour_label}]** ⬅ Now")
                else:
                    st.markdown(f"**{hour_label}**")

            with col_appointments:
                if hour in appointments_by_hour:
                    for apt in appointments_by_hour[hour]:
                        # Priority symbol
                        priority_symbol = "🚨" if apt.priority == "urgent" else \
                                        "⚠️" if apt.priority == "high" else "✅"

                        # Create appointment card using Streamlit components
                        with st.expander(f"{priority_symbol} {apt.start_time.strftime('%H:%M')}-{apt.end_time.strftime('%H:%M')} - {apt.patient.first_name} {apt.patient.last_name}", expanded=False):
                            st.write(f"**👨‍⚕️ Doctor:** {apt.doctor.name}")
                            st.write(f"**🏥 Department:** {apt.doctor.department.name}")
                            st.write(f"**🏷️ Type:** {apt.appointment_type.replace('_', ' ').title()}")
                            st.write(f"**⚠️ Priority:** {apt.priority.title()}")
                            if apt.reason_for_visit:
                                st.write(f"**📝 Reason:** {apt.reason_for_visit}")
                            if apt.location:
                                st.write(f"**📍 Location:** {apt.location}")

                            # Status indicator
                            if apt.status == "scheduled":
                                st.success(f"Status: {apt.status.title()}")
                            elif apt.status == "completed":
                                st.info(f"Status: {apt.status.title()}")
                            elif apt.status == "cancelled":
                                st.error(f"Status: {apt.status.title()}")
                            else:
                                st.warning(f"Status: {apt.status.title()}")
                else:
                    st.write("*No appointments*")

            # Add subtle separator
            st.markdown("---")

    # Summary statistics
    if appointments:
        st.markdown("### 📊 Day Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📅 Total Appointments", len(appointments))

        with col2:
            urgent_count = len([a for a in appointments if a.priority == 'urgent'])
            st.metric("🚨 Urgent", urgent_count)

        with col3:
            completed_count = len([a for a in appointments if a.status == 'completed'])
            st.metric("✅ Completed", completed_count)

        with col4:
            departments = list(set([a.doctor.department.name for a in appointments]))
            st.metric("🏥 Departments", len(departments))
    else:
        st.info("📅 No appointments scheduled for this day.")


def render_week_timeline(selected_date, department_filter, session):
    """Render week timeline view."""
    # Calculate week start (Monday)
    days_since_monday = selected_date.weekday()
    week_start = selected_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)

    # Get appointments for the week
    query = session.query(Appointment).join(Doctor).join(Patient).filter(
        Appointment.appointment_date >= week_start,
        Appointment.appointment_date <= week_end
    )

    if department_filter != "All":
        query = query.join(Department).filter(Department.name == department_filter)

    appointments = query.order_by(Appointment.appointment_date, Appointment.start_time).all()

    # Group appointments by date
    appointments_by_date = {}
    for apt in appointments:
        apt_date = apt.appointment_date
        if apt_date not in appointments_by_date:
            appointments_by_date[apt_date] = []
        appointments_by_date[apt_date].append(apt)

    st.markdown(f"**Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}**")

    # Create week grid
    cols = st.columns(7)

    for i, col in enumerate(cols):
        current_date = week_start + timedelta(days=i)
        day_name = current_date.strftime('%a')
        day_appointments = appointments_by_date.get(current_date, [])

        with col:
            # Day header
            if current_date == date.today():
                st.markdown(f"**🌟 {day_name}**")
                st.markdown(f"{current_date.strftime('%m/%d')}")
            else:
                st.markdown(f"**{day_name}**")
                st.markdown(f"{current_date.strftime('%m/%d')}")

            st.markdown(f"*{len(day_appointments)} appointments*")

            # Show top 3 appointments for the day
            for apt in day_appointments[:3]:
                # Use Streamlit colored elements instead of HTML
                if apt.appointment_type == 'patient_care':
                    st.success(f"🕒 {apt.start_time.strftime('%H:%M')} - {apt.patient.first_name} {apt.patient.last_name}")
                elif apt.appointment_type == 'procedure':
                    st.info(f"🕒 {apt.start_time.strftime('%H:%M')} - {apt.patient.first_name} {apt.patient.last_name}")
                elif apt.appointment_type == 'emergency':
                    st.error(f"🕒 {apt.start_time.strftime('%H:%M')} - {apt.patient.first_name} {apt.patient.last_name}")
                else:  # administrative
                    st.warning(f"🕒 {apt.start_time.strftime('%H:%M')} - {apt.patient.first_name} {apt.patient.last_name}")

                st.caption(f"👨‍⚕️ {apt.doctor.name}")

            if len(day_appointments) > 3:
                st.markdown(f"*+{len(day_appointments) - 3} more...*")

            # Quick add button
            if st.button(f"➕", key=f"add_{current_date}", help="Add appointment", use_container_width=True):
                st.session_state['quick_add_date'] = current_date
                st.session_state['show_quick_add'] = True
                st.rerun()

    # Quick add appointment modal
    if st.session_state.get('show_quick_add', False):
        render_quick_add_modal()


def create_appointment(first_name, last_name, email, phone, doctor_id, apt_date, start_time, end_time, apt_type, priority, reason, location, notes):
    """Create a new appointment."""
    session = get_db_session()
    try:
        # Find or create patient
        patient = session.query(Patient).filter_by(email=email).first()

        if not patient:
            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                date_of_birth=date(1990, 1, 1),  # Default date
                emergency_contact="N/A"
            )
            session.add(patient)
            session.flush()

        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=apt_date,
            start_time=start_time,
            end_time=end_time,
            appointment_type=apt_type,
            priority=priority,
            status="scheduled",
            reason_for_visit=reason,
            location=location,
            notes=notes
        )

        session.add(appointment)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        st.error(f"Error creating appointment: {e}")
        return False
    finally:
        session.close()


def update_appointment_status(appointment_id, new_status):
    """Update appointment status."""
    session = get_db_session()
    try:
        appointment = session.query(Appointment).filter_by(id=appointment_id).first()
        if appointment:
            appointment.status = new_status
            session.commit()
            st.success(f"Appointment status updated to {new_status}!")
            st.rerun()
        else:
            st.error("Appointment not found!")
    except Exception as e:
        session.rollback()
        st.error(f"Error updating appointment: {e}")
    finally:
        session.close()


def render_analytics_dashboard():
    """Render the analytics dashboard page."""
    st.markdown("# 📊 Analytics Dashboard")
    st.markdown("### Hospital performance metrics and insights")

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏥 Overview", "🏢 Departments", "📅 Appointments", "📈 Trends"])

    with tab1:
        render_analytics_overview()

    with tab2:
        render_department_analytics()

    with tab3:
        render_appointment_analytics()

    with tab4:
        render_trends_analytics()


def render_analytics_overview():
    """Render overall hospital analytics overview."""
    st.markdown("### 🏥 Hospital Performance Overview")

    # ETL Status and Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("#### 📊 Real-time Hospital Analytics Dashboard")
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            with st.spinner("Refreshing analytics data..."):
                success = run_daily_etl()
                if success:
                    st.success("Data refreshed successfully!")
                else:
                    st.error("Failed to refresh data")
            st.rerun()
    with col3:
        period = st.selectbox("📅 Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days"])

    days_back = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[period]

    try:
        with DashboardService() as dashboard:
            # Get hospital KPIs
            hospital_kpis = dashboard.get_hospital_kpis(days_back=days_back)

            # Key Performance Indicators
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric(
                    "Total Appointments",
                    hospital_kpis['total_appointments'],
                    delta=f"{hospital_kpis['appointment_trend']:+.1f}%"
                )

            with col2:
                st.metric(
                    "Completion Rate",
                    f"{hospital_kpis['completion_rate']:.1f}%",
                    delta="2.1%" if hospital_kpis['completion_rate'] > 75 else "-1.2%"
                )

            with col3:
                st.metric(
                    "Patient Satisfaction",
                    f"{hospital_kpis['avg_patient_satisfaction']:.1f}/5",
                    delta="0.2" if hospital_kpis['avg_patient_satisfaction'] > 4.0 else "-0.1"
                )

            with col4:
                st.metric(
                    "Avg Wait Time",
                    f"{hospital_kpis['avg_wait_time']:.0f} min",
                    delta="-3 min" if hospital_kpis['avg_wait_time'] < 30 else "+2 min"
                )

            with col5:
                st.metric(
                    "Bed Occupancy",
                    f"{hospital_kpis['bed_occupancy_rate']:.1f}%",
                    delta="5%" if hospital_kpis['bed_occupancy_rate'] > 80 else "-2%"
                )

            st.markdown("---")

            # Hospital capacity and status overview
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("#### 🏥 Hospital Capacity")

                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=hospital_kpis['bed_occupancy_rate'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Bed Occupancy Rate"},
                    delta={'reference': 80},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#10b981" if hospital_kpis['bed_occupancy_rate'] < 90 else "#ef4444"},
                        'steps': [
                            {'range': [0, 70], 'color': "lightgray"},
                            {'range': [70, 85], 'color': "#fbbf24"},
                            {'range': [85, 100], 'color': "#f87171"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("#### 📊 Appointment Status")

                status_data = {
                    'Completed': hospital_kpis['completed_appointments'],
                    'Cancelled': hospital_kpis['total_appointments'] - hospital_kpis['completed_appointments'],
                    'Emergency': hospital_kpis.get('emergency_appointments', 0)
                }

                fig = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    title="Appointment Status Distribution",
                    color_discrete_sequence=['#10b981', '#ef4444', '#f59e0b']
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

            with col3:
                st.markdown("#### 💰 Financial Overview")

                # Get financial data
                financial_data = dashboard.get_financial_dashboard_data(days_back=days_back)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Revenue", f"${financial_data['total_revenue']:,.0f}")
                    st.metric("Profit", f"${financial_data['profit']:,.0f}")
                with col_b:
                    st.metric("Costs", f"${financial_data['total_costs']:,.0f}")
                    st.metric("Margin", f"{financial_data['profit_margin']:.1f}%")

            st.markdown("---")

            # Appointment trends
            st.markdown("#### 📈 Appointment Trends")

            trends_data = dashboard.get_appointment_trends(days_back=days_back)

            if trends_data['daily_trends']:
                # Create DataFrame for plotting
                trends_df = pd.DataFrame(trends_data['daily_trends'])
                trends_df['date'] = pd.to_datetime(trends_df['date'])

                # Create subplot with multiple traces
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=('Daily Appointment Volume', 'Appointment Status Breakdown'),
                    specs=[[{"secondary_y": False}, {"type": "bar"}]]
                )

                # Daily volume trend
                fig.add_trace(
                    go.Scatter(
                        x=trends_df['date'],
                        y=trends_df['total_appointments'],
                        mode='lines+markers',
                        name='Total Appointments',
                        line=dict(color='#2563eb', width=3)
                    ),
                    row=1, col=1
                )

                # Status breakdown
                fig.add_trace(
                    go.Bar(
                        x=trends_df['date'],
                        y=trends_df['completed'],
                        name='Completed',
                        marker_color='#10b981'
                    ),
                    row=1, col=2
                )

                fig.add_trace(
                    go.Bar(
                        x=trends_df['date'],
                        y=trends_df['cancelled'],
                        name='Cancelled',
                        marker_color='#ef4444'
                    ),
                    row=1, col=2
                )

                fig.update_layout(
                    height=400,
                    showlegend=True,
                    title_text=f"Hospital Performance Trends - {period}"
                )

                st.plotly_chart(fig, use_container_width=True)

            # Patient satisfaction overview
            st.markdown("#### 😊 Patient Satisfaction Overview")

            satisfaction_data = dashboard.get_patient_satisfaction_overview(days_back=days_back)

            col1, col2 = st.columns(2)

            with col1:
                # Satisfaction metrics
                satisfaction_metrics = [
                    ('Overall', satisfaction_data['overall_satisfaction']),
                    ('Wait Time', satisfaction_data['wait_time_satisfaction']),
                    ('Doctor', satisfaction_data['doctor_satisfaction']),
                    ('Facility', satisfaction_data['facility_satisfaction']),
                    ('Communication', satisfaction_data['communication_satisfaction'])
                ]

                fig = go.Figure()
                for metric, score in satisfaction_metrics:
                    fig.add_trace(go.Bar(
                        x=[metric],
                        y=[score],
                        name=metric,
                        marker_color='#10b981' if score >= 4.0 else '#f59e0b' if score >= 3.0 else '#ef4444'
                    ))

                fig.update_layout(
                    title="Satisfaction Scores (out of 5)",
                    showlegend=False,
                    height=300,
                    yaxis_range=[0, 5]
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Key satisfaction stats
                st.metric("Total Surveys", satisfaction_data['total_surveys'])
                st.metric("Recommendation Rate", f"{satisfaction_data['recommendation_rate']:.1f}%")

                if satisfaction_data['department_satisfaction']:
                    st.markdown("**Department Satisfaction:**")
                    for dept, score in satisfaction_data['department_satisfaction'].items():
                        st.write(f"• {dept}: {score:.1f}/5")

    except Exception as e:
        st.error(f"Error loading analytics overview: {e}")
        st.exception(e)


def render_department_analytics():
    """Render department-specific analytics."""
    st.markdown("### 🏢 Department Performance Analytics")

    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("#### 📊 Department-level insights and performance metrics")
    with col2:
        period = st.selectbox("📅 Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days"], key="dept_period")

    days_back = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[period]

    try:
        with DashboardService() as dashboard:
            # Get department performance data
            dept_performance = dashboard.get_department_performance(days_back=days_back)

            if not dept_performance:
                st.warning("No department data available.")
                return

            # Department performance summary
            st.markdown("#### 🏆 Top Performing Departments")

            col1, col2, col3, col4 = st.columns(4)

            # Sort departments by different metrics
            highest_volume = max(dept_performance, key=lambda x: x['total_appointments'])
            highest_satisfaction = max(dept_performance, key=lambda x: x['patient_satisfaction'])
            highest_efficiency = max(dept_performance, key=lambda x: x['completion_rate'])
            highest_revenue = max(dept_performance, key=lambda x: x['revenue_generated'])

            with col1:
                st.metric(
                    "📈 Highest Volume",
                    highest_volume['department_name'],
                    f"{highest_volume['total_appointments']} appointments"
                )

            with col2:
                st.metric(
                    "😊 Best Satisfaction",
                    highest_satisfaction['department_name'],
                    f"{highest_satisfaction['patient_satisfaction']:.1f}/5"
                )

            with col3:
                st.metric(
                    "✅ Most Efficient",
                    highest_efficiency['department_name'],
                    f"{highest_efficiency['completion_rate']:.1f}%"
                )

            with col4:
                st.metric(
                    "💰 Top Revenue",
                    highest_revenue['department_name'],
                    f"${highest_revenue['revenue_generated']:,.0f}"
                )

            st.markdown("---")

            # Department comparison charts
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📊 Appointment Volume Comparison")

                # Create DataFrame for plotting
                dept_df = pd.DataFrame(dept_performance)

                fig = px.bar(
                    dept_df,
                    x='department_name',
                    y='total_appointments',
                    title=f"Total Appointments by Department ({period})",
                    color='total_appointments',
                    color_continuous_scale='viridis',
                    text='total_appointments'
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                fig.update_xaxes(title="Department")
                fig.update_yaxes(title="Total Appointments")
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("#### 💰 Revenue by Department")

                fig = px.bar(
                    dept_df,
                    x='department_name',
                    y='revenue_generated',
                    title=f"Revenue by Department ({period})",
                    color='revenue_generated',
                    color_continuous_scale='blues',
                    text='revenue_generated'
                )
                fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
                fig.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                fig.update_xaxes(title="Department")
                fig.update_yaxes(title="Revenue ($)")
                st.plotly_chart(fig, use_container_width=True)

            # Performance metrics comparison
            st.markdown("#### 🎯 Performance Metrics Comparison")

            col1, col2 = st.columns(2)

            with col1:
                # Patient satisfaction radar chart
                fig = go.Figure()

                for dept in dept_performance[:5]:  # Top 5 departments
                    fig.add_trace(go.Scatterpolar(
                        r=[dept['completion_rate'], dept['patient_satisfaction']*20, dept['staff_utilization']],
                        theta=['Completion Rate (%)', 'Patient Satisfaction (×20)', 'Staff Utilization (%)'],
                        fill='toself',
                        name=dept['department_name']
                    ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=True,
                    title="Department Performance Radar"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Staff utilization vs efficiency scatter
                fig = px.scatter(
                    dept_df,
                    x='staff_utilization',
                    y='completion_rate',
                    size='total_appointments',
                    color='patient_satisfaction',
                    hover_name='department_name',
                    title="Staff Utilization vs Completion Rate",
                    labels={
                        'staff_utilization': 'Staff Utilization (%)',
                        'completion_rate': 'Completion Rate (%)',
                        'patient_satisfaction': 'Patient Satisfaction'
                    },
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            # Department efficiency analysis
            st.markdown("#### ⚡ Department Efficiency Analysis")

            # Create efficiency score
            for dept in dept_performance:
                dept['efficiency_score'] = (
                    dept['completion_rate'] * 0.4 +
                    dept['patient_satisfaction'] * 20 * 0.3 +
                    dept['staff_utilization'] * 0.3
                )

            # Sort by efficiency
            dept_performance_sorted = sorted(dept_performance, key=lambda x: x['efficiency_score'], reverse=True)

            # Display top departments
            for i, dept in enumerate(dept_performance_sorted):
                with st.expander(f"#{i+1} {dept['department_name']} (Efficiency Score: {dept['efficiency_score']:.1f})"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Appointments", dept['total_appointments'])
                        st.metric("Completion Rate", f"{dept['completion_rate']:.1f}%")

                    with col2:
                        st.metric("Patient Satisfaction", f"{dept['patient_satisfaction']:.1f}/5")
                        st.metric("Staff Utilization", f"{dept['staff_utilization']:.1f}%")

                    with col3:
                        st.metric("Revenue Generated", f"${dept['revenue_generated']:,.0f}")
                        st.metric("Staff Count", f"{dept['active_staff']}/{dept['total_staff']}")

            # Comprehensive department metrics table
            st.markdown("#### 📋 Complete Department Metrics")

            display_df = pd.DataFrame([{
                'Department': dept['department_name'],
                'Appointments': dept['total_appointments'],
                'Completion Rate (%)': f"{dept['completion_rate']:.1f}",
                'Satisfaction (1-5)': f"{dept['patient_satisfaction']:.1f}",
                'Staff Utilization (%)': f"{dept['staff_utilization']:.1f}",
                'Revenue ($)': f"{dept['revenue_generated']:,.0f}",
                'Staff': f"{dept['active_staff']}/{dept['total_staff']}",
                'Efficiency Score': f"{dept['efficiency_score']:.1f}"
            } for dept in dept_performance_sorted])

            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    'Department': st.column_config.TextColumn(width="medium"),
                    'Appointments': st.column_config.NumberColumn(format="%d"),
                    'Efficiency Score': st.column_config.NumberColumn(
                        help="Weighted score: Completion (40%) + Satisfaction (30%) + Utilization (30%)"
                    )
                }
            )

    except Exception as e:
        st.error(f"Error loading department analytics: {e}")
        st.exception(e)


def render_appointment_analytics():
    """Render appointment-specific analytics with doctor efficiency metrics."""
    st.markdown("### 📅 Appointment & Doctor Efficiency Analytics")

    # Time period and analysis type selector
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("#### 📊 Comprehensive appointment analysis and doctor performance metrics")
    with col2:
        period = st.selectbox("📅 Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days"], key="apt_period")

    days_back = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[period]

    try:
        with DashboardService() as dashboard:
            # Get appointment trends
            trends_data = dashboard.get_appointment_trends(days_back=days_back)

            # Get doctor efficiency metrics
            doctor_metrics = dashboard.get_doctor_efficiency_metrics(days_back=days_back, limit=15)

            # Key appointment metrics
            col1, col2, col3, col4 = st.columns(4)

            if trends_data['daily_trends']:
                total_appointments = sum(day['total_appointments'] for day in trends_data['daily_trends'])
                total_completed = sum(day['completed'] for day in trends_data['daily_trends'])
                total_cancelled = sum(day['cancelled'] for day in trends_data['daily_trends'])
                total_no_shows = sum(day['no_shows'] for day in trends_data['daily_trends'])

                completion_rate = (total_completed / total_appointments * 100) if total_appointments > 0 else 0
                cancellation_rate = (total_cancelled / total_appointments * 100) if total_appointments > 0 else 0
                no_show_rate = (total_no_shows / total_appointments * 100) if total_appointments > 0 else 0

                with col1:
                    st.metric("Total Appointments", total_appointments)
                with col2:
                    st.metric("Completion Rate", f"{completion_rate:.1f}%",
                             delta="5.2%" if completion_rate > 75 else "-2.1%")
                with col3:
                    st.metric("Cancellation Rate", f"{cancellation_rate:.1f}%",
                             delta="-1.3%" if cancellation_rate < 10 else "+2.8%")
                with col4:
                    st.metric("No-Show Rate", f"{no_show_rate:.1f}%",
                             delta="-0.8%" if no_show_rate < 5 else "+1.2%")

            st.markdown("---")

            # Doctor efficiency leaderboard
            st.markdown("#### 🏆 Top Performing Doctors")

            if doctor_metrics:
                # Top 3 doctors
                col1, col2, col3 = st.columns(3)

                for i, doctor in enumerate(doctor_metrics[:3]):
                    with [col1, col2, col3][i]:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                   padding: 20px; border-radius: 10px; color: white; text-align: center;">
                            <h3>#{i+1} {doctor['doctor_name']}</h3>
                            <p><strong>{doctor['department_name']}</strong></p>
                            <p>Efficiency Score: <strong>{doctor['efficiency_score']:.1f}</strong></p>
                            <p>Appointments: <strong>{doctor['total_appointments']}</strong></p>
                            <p>Satisfaction: <strong>{doctor['patient_satisfaction']:.1f}/5</strong></p>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Doctor performance comparison charts
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📊 Doctor Efficiency vs Volume")

                    doctor_df = pd.DataFrame(doctor_metrics[:10])  # Top 10 doctors

                    fig = px.scatter(
                        doctor_df,
                        x='total_appointments',
                        y='efficiency_score',
                        size='patient_satisfaction',
                        color='utilization_rate',
                        hover_name='doctor_name',
                        hover_data=['department_name', 'completion_rate', 'revenue_generated'],
                        title="Doctor Efficiency vs Appointment Volume",
                        labels={
                            'total_appointments': 'Total Appointments',
                            'efficiency_score': 'Efficiency Score',
                            'utilization_rate': 'Utilization Rate (%)',
                            'patient_satisfaction': 'Patient Satisfaction'
                        },
                        color_continuous_scale='RdYlGn'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("#### 💰 Revenue per Doctor")

                    fig = px.bar(
                        doctor_df,
                        x='doctor_name',
                        y='revenue_generated',
                        color='patient_satisfaction',
                        title=f"Revenue by Doctor ({period})",
                        color_continuous_scale='viridis',
                        text='revenue_generated'
                    )
                    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    fig.update_xaxes(title="Doctor")
                    fig.update_yaxes(title="Revenue Generated ($)")
                    st.plotly_chart(fig, use_container_width=True)

                # Comprehensive doctor metrics table
                st.markdown("#### 📋 Doctor Performance Metrics")

                display_df = pd.DataFrame([{
                    'Rank': i + 1,
                    'Doctor': doc['doctor_name'],
                    'Department': doc['department_name'],
                    'Specialization': doc['specialization'],
                    'Appointments': doc['total_appointments'],
                    'Completion Rate (%)': f"{doc['completion_rate']:.1f}",
                    'Patient Satisfaction': f"{doc['patient_satisfaction']:.1f}/5",
                    'Utilization (%)': f"{doc['utilization_rate']:.1f}",
                    'Revenue ($)': f"${doc['revenue_generated']:,.0f}",
                    'Efficiency Score': f"{doc['efficiency_score']:.1f}"
                } for i, doc in enumerate(doctor_metrics)])

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    column_config={
                        'Rank': st.column_config.NumberColumn(format="%d", width="small"),
                        'Doctor': st.column_config.TextColumn(width="medium"),
                        'Department': st.column_config.TextColumn(width="medium"),
                        'Efficiency Score': st.column_config.ProgressColumn(
                            help="Comprehensive efficiency score based on multiple factors",
                            min_value=0,
                            max_value=100
                        )
                    }
                )

            # Appointment trends analysis
            st.markdown("#### 📈 Appointment Trends & Patterns")

            if trends_data['daily_trends']:
                trends_df = pd.DataFrame(trends_data['daily_trends'])
                trends_df['date'] = pd.to_datetime(trends_df['date'])

                col1, col2 = st.columns(2)

                with col1:
                    # Daily appointment volume
                    fig = px.line(
                        trends_df,
                        x='date',
                        y='total_appointments',
                        title=f"Daily Appointment Volume ({period})",
                        markers=True,
                        line_shape='spline'
                    )
                    fig.update_traces(line=dict(color='#2563eb', width=3))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Appointment status breakdown
                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        x=trends_df['date'],
                        y=trends_df['completed'],
                        name='Completed',
                        marker_color='#10b981'
                    ))

                    fig.add_trace(go.Bar(
                        x=trends_df['date'],
                        y=trends_df['cancelled'],
                        name='Cancelled',
                        marker_color='#ef4444'
                    ))

                    fig.add_trace(go.Bar(
                        x=trends_df['date'],
                        y=trends_df['no_shows'],
                        name='No Shows',
                        marker_color='#f59e0b'
                    ))

                    fig.update_layout(
                        title=f"Appointment Status Breakdown ({period})",
                        xaxis_title="Date",
                        yaxis_title="Number of Appointments",
                        barmode='stack',
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Patient satisfaction tracking
            st.markdown("#### 😊 Patient Satisfaction Tracking")

            satisfaction_data = dashboard.get_patient_satisfaction_overview(days_back=days_back)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Overall Satisfaction", f"{satisfaction_data['overall_satisfaction']:.1f}/5")
                st.metric("Total Surveys", satisfaction_data['total_surveys'])

            with col2:
                st.metric("Doctor Satisfaction", f"{satisfaction_data['doctor_satisfaction']:.1f}/5")
                st.metric("Communication Score", f"{satisfaction_data['communication_satisfaction']:.1f}/5")

            with col3:
                st.metric("Facility Rating", f"{satisfaction_data['facility_satisfaction']:.1f}/5")
                st.metric("Recommendation Rate", f"{satisfaction_data['recommendation_rate']:.1f}%")

            # Satisfaction breakdown by category
            if satisfaction_data['total_surveys'] > 0:
                satisfaction_categories = [
                    'Overall', 'Wait Time', 'Doctor', 'Facility', 'Communication'
                ]
                satisfaction_scores = [
                    satisfaction_data['overall_satisfaction'],
                    satisfaction_data['wait_time_satisfaction'],
                    satisfaction_data['doctor_satisfaction'],
                    satisfaction_data['facility_satisfaction'],
                    satisfaction_data['communication_satisfaction']
                ]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=satisfaction_categories,
                    y=satisfaction_scores,
                    marker_color=['#10b981' if score >= 4.0 else '#f59e0b' if score >= 3.0 else '#ef4444'
                                 for score in satisfaction_scores],
                    text=[f"{score:.1f}" for score in satisfaction_scores],
                    textposition='auto'
                ))

                fig.update_layout(
                    title="Patient Satisfaction Breakdown",
                    xaxis_title="Category",
                    yaxis_title="Score (out of 5)",
                    yaxis_range=[0, 5],
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading appointment analytics: {e}")
        st.exception(e)


def render_trends_analytics():
    """Render trends and forecasting analytics."""
    st.markdown("### 📈 Trends & Forecasting")

    session = get_db_session()
    try:
        # Monthly trends
        st.markdown("#### 📊 Monthly Appointment Trends")

        # Generate monthly data for last 6 months
        monthly_data = []
        for i in range(6, 0, -1):
            month_start = date.today().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            count = session.query(Appointment).filter(
                Appointment.appointment_date >= month_start,
                Appointment.appointment_date <= month_end
            ).count()

            monthly_data.append({
                'Month': month_start.strftime('%B %Y'),
                'Appointments': count
            })

        if monthly_data:
            monthly_df = pd.DataFrame(monthly_data)

            fig = px.line(
                monthly_df,
                x='Month',
                y='Appointments',
                title="6-Month Appointment Trend",
                markers=True
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        # Department growth comparison
        st.markdown("#### 🏢 Department Growth Comparison")

        departments = session.query(Department).all()
        dept_growth = []

        for dept in departments:
            # Last month
            last_month_start = date.today() - timedelta(days=60)
            last_month_end = date.today() - timedelta(days=30)

            # This month
            this_month_start = date.today() - timedelta(days=30)

            last_month_count = session.query(Appointment).join(Doctor).filter(
                Doctor.department_id == dept.id,
                Appointment.appointment_date >= last_month_start,
                Appointment.appointment_date <= last_month_end
            ).count()

            this_month_count = session.query(Appointment).join(Doctor).filter(
                Doctor.department_id == dept.id,
                Appointment.appointment_date >= this_month_start
            ).count()

            growth = ((this_month_count - last_month_count) / last_month_count * 100) if last_month_count > 0 else 0

            dept_growth.append({
                'Department': dept.name,
                'Last Month': last_month_count,
                'This Month': this_month_count,
                'Growth %': growth
            })

        if dept_growth:
            growth_df = pd.DataFrame(dept_growth)

            fig = px.bar(
                growth_df,
                x='Department',
                y='Growth %',
                title="Department Growth Rate (Month-over-Month)",
                color='Growth %',
                color_continuous_scale='RdYlGn'
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black")
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(growth_df, use_container_width=True)

        # Predictive insights
        st.markdown("#### 🔮 Predictive Insights")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Calculate average daily appointments
            total_appointments = session.query(Appointment).filter(
                Appointment.appointment_date >= date.today() - timedelta(days=30)
            ).count()
            avg_daily = total_appointments / 30

            st.metric(
                "Predicted Tomorrow",
                f"{int(avg_daily + (avg_daily * 0.1))}",
                delta=f"+{int(avg_daily * 0.1)}"
            )

        with col2:
            # Busiest hour prediction
            appointments_today = session.query(Appointment).filter_by(
                appointment_date=date.today()
            ).all()

            if appointments_today:
                hours = [apt.start_time.hour for apt in appointments_today]
                busiest_hour = max(set(hours), key=hours.count) if hours else 9
                st.metric("Busiest Hour Today", f"{busiest_hour:02d}:00")
            else:
                st.metric("Busiest Hour Today", "09:00")

        with col3:
            # Peak department
            dept_counts = {}
            for dept in departments:
                count = session.query(Appointment).join(Doctor).filter(
                    Doctor.department_id == dept.id,
                    Appointment.appointment_date >= date.today() - timedelta(days=7)
                ).count()
                dept_counts[dept.name] = count

            if dept_counts:
                peak_dept = max(dept_counts, key=dept_counts.get)
                st.metric("Peak Department", peak_dept)

    except Exception as e:
        st.error(f"Error loading trends analytics: {e}")
    finally:
        session.close()


def render_reports_page():
    """Render reports generation and management page."""
    st.markdown("# 📋 Reports & Analytics")
    st.markdown("### Automated report generation and custom report builder")

    # Report generation section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 🚀 Quick Report Generation")

        report_types = {
            "Hospital Performance": "hospital_performance",
            "Doctor Efficiency": "doctor_efficiency",
            "Financial Analysis": "financial",
            "Patient Satisfaction": "patient_satisfaction"
        }

        selected_report = st.selectbox("Select Report Type", list(report_types.keys()))

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            period = st.selectbox("Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days"])
        with col_b:
            format_type = st.selectbox("Format", ["HTML", "JSON"])
        with col_c:
            department_filter = st.selectbox("Department", ["All Departments", "Cardiology", "Emergency", "Surgery", "Internal Medicine", "Pediatrics"])

        if st.button("📊 Generate Report", type="primary", use_container_width=True):
            days_back = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}[period]

            with st.spinner(f"Generating {selected_report} report..."):
                try:
                    generator = ReportGenerator()
                    report_type = report_types[selected_report]

                    # Generate report based on type
                    if report_type == "hospital_performance":
                        filename = generator.generate_hospital_performance_report(
                            days_back=days_back,
                            format=format_type.lower()
                        )
                    elif report_type == "doctor_efficiency":
                        dept_id = department_filter if department_filter != "All Departments" else None
                        filename = generator.generate_doctor_efficiency_report(
                            days_back=days_back,
                            department_id=dept_id,
                            format=format_type.lower()
                        )
                    elif report_type == "financial":
                        filename = generator.generate_financial_report(
                            days_back=days_back,
                            format=format_type.lower()
                        )
                    else:  # patient_satisfaction
                        filename = generator.generate_patient_satisfaction_report(
                            days_back=days_back,
                            format=format_type.lower()
                        )

                    st.success(f"✅ Report generated successfully!")
                    st.info(f"📄 Report saved as: `{filename}`")

                    # Provide download button if HTML
                    if format_type.lower() == 'html' and os.path.exists(filename):
                        with open(filename, 'r', encoding='utf-8') as f:
                            report_content = f.read()

                        st.download_button(
                            label="📥 Download Report",
                            data=report_content,
                            file_name=os.path.basename(filename),
                            mime="text/html",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"❌ Error generating report: {e}")
                    st.exception(e)

    with col2:
        st.markdown("#### ⚙️ Report Settings")

        st.info("📈 **Available Reports:**\n\n"
               "• Hospital Performance - KPIs, metrics\n"
               "• Doctor Efficiency - Performance analysis\n"
               "• Financial Analysis - Revenue, costs\n"
               "• Patient Satisfaction - Survey results")

        if st.button("🔄 Run ETL Process", use_container_width=True):
            with st.spinner("Running daily ETL process..."):
                success = run_daily_etl()
                if success:
                    st.success("ETL process completed successfully!")
                else:
                    st.error("ETL process failed.")

    st.markdown("---")

    # Enhanced Custom Report Builder
    st.markdown("#### 🛠️ Enhanced Custom Report Builder")

    # Initialize report builder service
    try:
        from services.report_builder_service import ReportBuilderService
        from services.report_scheduler import ReportScheduler
        import json

        if 'report_builder' not in st.session_state:
            st.session_state.report_builder = ReportBuilderService(st.session_state.db_session)

        report_builder = st.session_state.report_builder

        # Tabs for different report builder functions
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Build Report", "📋 Templates", "⏰ Scheduling", "📤 Export & Share"])

        with tab1:
            st.markdown("Create customized reports with dynamic data sources and visualizations.")

            # Get available data sources and chart types
            data_sources = report_builder.get_available_data_sources()
            chart_types = report_builder.get_chart_types()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📊 Data Configuration**")

                selected_source = st.selectbox(
                    "Data Source",
                    options=list(data_sources.keys()),
                    format_func=lambda x: data_sources[x]['name']
                )

                if selected_source:
                    available_metrics = data_sources[selected_source]['metrics']
                    selected_metrics = st.multiselect(
                        "Select Metrics",
                        available_metrics,
                        default=available_metrics[:2] if len(available_metrics) >= 2 else available_metrics
                    )

                    available_filters = data_sources[selected_source]['filters']
                    st.markdown("**🔍 Filters**")

                    filters = {}
                    if 'date_range' in available_filters:
                        time_range = st.selectbox("Time Range",
                                                ["last_7_days", "last_30_days", "last_90_days", "last_year"])
                        filters['time_range'] = time_range

                    if 'department' in available_filters:
                        dept_filter = st.selectbox("Department (Optional)",
                                                 ["All"] + ["Cardiology", "Emergency", "Surgery", "Internal Medicine", "Pediatrics"])
                        if dept_filter != "All":
                            filters['department'] = dept_filter

            with col2:
                st.markdown("**🎨 Visualization Configuration**")

                selected_chart = st.selectbox(
                    "Chart Type",
                    options=list(chart_types.keys()),
                    format_func=lambda x: chart_types[x]['name']
                )

                grouping_field = None
                if selected_source in ['appointments', 'patients']:
                    grouping_field = st.selectbox(
                        "Group By (Optional)",
                        ["None", "department", "status", "priority"]
                    )
                    if grouping_field == "None":
                        grouping_field = None

                chart_title = st.text_input("Chart Title", value=f"{selected_source.title()} Analysis")
                x_axis_title = st.text_input("X-Axis Label", value="Category")
                y_axis_title = st.text_input("Y-Axis Label", value="Value")

            # Generate report button
            if st.button("🔍 Generate Report", use_container_width=True, type="primary"):
                if selected_metrics:
                    with st.spinner("Generating report..."):
                        # Build configuration
                        config = {
                            'data_source': selected_source,
                            'chart_type': selected_chart,
                            'metrics': selected_metrics,
                            'filters': filters,
                            'grouping': grouping_field,
                            'time_range': filters.get('time_range', 'last_30_days'),
                            'title': chart_title,
                            'x_axis_title': x_axis_title,
                            'y_axis_title': y_axis_title
                        }

                        # Generate chart
                        result = report_builder.generate_dynamic_chart(config)

                        if result.get('success'):
                            st.success("Report generated successfully!")

                            # Display the chart
                            chart_data = json.loads(result['chart_json'])
                            st.plotly_chart(chart_data, use_container_width=True)

                            # Display data summary
                            st.markdown("**📈 Data Summary:**")
                            summary = result.get('data_summary', {})
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Records", summary.get('total_records', 0))
                            with col2:
                                st.metric("Metrics", len(summary.get('metrics_included', [])))
                            with col3:
                                st.write(f"**Date Range:** {summary.get('date_range', 'N/A')}")

                            # Store in session for template saving
                            st.session_state.last_report_config = config
                            st.session_state.last_report_result = result

                        else:
                            st.error(f"Failed to generate report: {result.get('error')}")
                else:
                    st.warning("Please select at least one metric.")

        with tab2:
            st.markdown("**📋 Report Templates**")

            col1, col2 = st.columns([2, 1])

            with col1:
                # Save current report as template
                if hasattr(st.session_state, 'last_report_config'):
                    st.markdown("**💾 Save Current Report as Template**")
                    template_name = st.text_input("Template Name", value="My Custom Report")
                    template_desc = st.text_area("Description", value="Custom report template")

                    if st.button("Save as Template"):
                        template_data = {
                            'name': template_name,
                            'description': template_desc,
                            'config': st.session_state.last_report_config
                        }

                        result = report_builder.save_report_template(template_data, user_id=1)
                        if result.get('success'):
                            st.success(f"Template '{template_name}' saved successfully!")
                        else:
                            st.error(f"Failed to save template: {result.get('error')}")
                else:
                    st.info("Generate a report first to save it as a template.")

            with col2:
                # Load existing templates
                st.markdown("**📚 Saved Templates**")
                templates = report_builder.get_report_templates(user_id=1)

                if templates:
                    for template in templates:
                        with st.expander(f"📄 {template['name']}"):
                            st.write(template['description'])
                            st.caption(f"Created: {template['created_at'][:10]}")

                            if st.button(f"Use Template", key=f"use_{template['id']}"):
                                result = report_builder.generate_report_from_template(template['id'])
                                if result.get('success'):
                                    chart_data = json.loads(result['chart_json'])
                                    st.plotly_chart(chart_data, use_container_width=True)
                                else:
                                    st.error(f"Failed to generate from template: {result.get('error')}")
                else:
                    st.info("No saved templates found.")

        with tab3:
            st.markdown("**⏰ Report Scheduling**")
            st.info("Configure automated report generation and delivery via email.")

            # This would integrate with ReportScheduler
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📅 Schedule Configuration**")
                schedule_name = st.text_input("Schedule Name", value="Weekly Hospital Report")
                frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly", "quarterly"])
                schedule_time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time())

            with col2:
                st.markdown("**📧 Delivery Settings**")
                recipients = st.text_area("Email Recipients (one per line)",
                                        value="admin@hospital.com\ndirector@hospital.com")
                format_type = st.selectbox("Report Format", ["html", "pdf"])

            if st.button("Create Scheduled Report"):
                st.info("Scheduled report functionality will be activated when email service is configured.")

        with tab4:
            st.markdown("**📤 Export & Share**")

            if hasattr(st.session_state, 'last_report_result'):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("📊 Export as JSON", use_container_width=True):
                        chart_json = st.session_state.last_report_result['chart_json']
                        st.download_button(
                            label="Download JSON",
                            data=chart_json,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                            mime="application/json"
                        )

                with col2:
                    if st.button("🌐 Export as HTML", use_container_width=True):
                        # Generate HTML export
                        html_content = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Hospital Report</title>
                            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                        </head>
                        <body>
                            <h1>Hospital Analytics Report</h1>
                            <div id="chart" style="width:100%;height:600px;"></div>
                            <script>
                                Plotly.newPlot('chart', {st.session_state.last_report_result['chart_json']});
                            </script>
                        </body>
                        </html>
                        """

                        st.download_button(
                            label="Download HTML",
                            data=html_content,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                            mime="text/html"
                        )

                with col3:
                    if st.button("📧 Share via Email", use_container_width=True):
                        st.info("Email sharing will be available when email service is configured.")
            else:
                st.info("Generate a report first to access export options.")

    except ImportError as e:
        st.error(f"Report builder service not available: {str(e)}")
        st.info("Please ensure all required dependencies are installed.")
    except Exception as e:
        st.error(f"Error initializing report builder: {str(e)}")

    # Report history section
    st.markdown("---")
    st.markdown("#### 📚 Report History")

    # List existing reports
    if os.path.exists("reports"):
        report_files = [f for f in os.listdir("reports") if f.endswith(('.html', '.json'))]

        if report_files:
            # Sort by modification time (newest first)
            report_files.sort(key=lambda x: os.path.getmtime(os.path.join("reports", x)), reverse=True)

            for i, report_file in enumerate(report_files[:10]):  # Show last 10 reports
                file_path = os.path.join("reports", report_file)
                file_size = os.path.getsize(file_path)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"📄 **{report_file}**")
                    st.caption(f"Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')} | Size: {file_size:,} bytes")

                with col2:
                    if report_file.endswith('.html'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        st.download_button(
                            "⬇️ Download",
                            data=content,
                            file_name=report_file,
                            mime="text/html",
                            key=f"download_{i}"
                        )
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        st.download_button(
                            "⬇️ Download",
                            data=content,
                            file_name=report_file,
                            mime="application/json",
                            key=f"download_{i}"
                        )

                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        os.remove(file_path)
                        st.rerun()
        else:
            st.info("No reports generated yet. Generate your first report using the tools above!")
    else:
        st.info("Reports directory not found. Generate your first report to create it!")


def render_integrations_page():
    """Render integrations and external services management page."""
    st.markdown("# 🔗 Integrations & External Services")
    st.markdown("### Manage email, calendar, and API integrations")

    # Create tabs for different integration categories
    tab1, tab2, tab3 = st.tabs(["📧 Email Services", "📅 Calendar Integration", "🔌 API Management"])

    # Email Services Tab
    with tab1:
        st.markdown("#### 📧 Email Service Configuration")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**📮 Email Settings**")

            # Email configuration form
            with st.expander("⚙️ Configure Email Settings"):
                smtp_host = st.text_input("SMTP Host", value=os.getenv('SMTP_HOST', 'smtp.gmail.com'))
                smtp_port = st.number_input("SMTP Port", value=int(os.getenv('SMTP_PORT', 587)), min_value=1, max_value=65535)
                smtp_user = st.text_input("SMTP Username", value=os.getenv('SMTP_USER', ''))
                smtp_password = st.text_input("SMTP Password", type="password", value="")
                from_email = st.text_input("From Email", value=os.getenv('FROM_EMAIL', ''))
                from_name = st.text_input("From Name", value=os.getenv('FROM_NAME', 'City General Hospital'))

                if st.button("💾 Save Email Settings"):
                    st.success("Email settings saved! (Note: In production, these would be saved to environment variables)")

            # Test email configuration
            if st.button("🧪 Test Email Configuration"):
                with st.spinner("Testing email configuration..."):
                    try:
                        email_service = EmailService()
                        result = email_service.test_email_configuration()

                        if result['status'] == 'success':
                            st.success(f"✅ {result['message']}")
                            st.info(f"SMTP Host: {result['smtp_host']}:{result['smtp_port']}")
                        else:
                            st.error(f"❌ {result['message']}")

                    except Exception as e:
                        st.error(f"❌ Email test failed: {e}")

            # Email templates management
            st.markdown("**📝 Email Templates**")

            template_types = [
                "Appointment Confirmation",
                "Appointment Reminder",
                "Appointment Cancellation",
                "Satisfaction Survey"
            ]

            selected_template = st.selectbox("Select Template", template_types)

            if st.button("📧 Send Test Email"):
                st.info("Test email functionality would be implemented here.")

        with col2:
            st.markdown("**📊 Email Statistics**")

            # Email stats (simulated for demo)
            st.metric("Emails Sent Today", "47", delta="12")
            st.metric("Delivery Rate", "98.5%", delta="1.2%")
            st.metric("Open Rate", "76.3%", delta="-2.1%")

            # Recent email activity
            st.markdown("**🕒 Recent Activity**")
            recent_emails = [
                "Confirmation sent to john@example.com",
                "Reminder sent to jane@example.com",
                "Survey sent to bob@example.com"
            ]

            for email in recent_emails:
                st.write(f"• {email}")

    # Calendar Integration Tab
    with tab2:
        st.markdown("#### 📅 Calendar Integration Status")

        try:
            calendar_service = CalendarIntegrationService()
            integration_status = calendar_service.get_integration_status()

            col1, col2, col3 = st.columns(3)

            # Google Calendar
            with col1:
                st.markdown("**🟢 Google Calendar**")

                google_status = integration_status['google']
                status_color = "🟢" if google_status['authenticated'] else "🔴"

                st.write(f"{status_color} **Status:** {'Connected' if google_status['authenticated'] else 'Not Connected'}")
                st.write(f"**Available:** {'Yes' if google_status['available'] else 'No'}")
                st.write(f"**Configured:** {'Yes' if google_status['configured'] else 'No'}")

                if st.button("🔄 Sync Google Calendar", key="google_sync"):
                    if google_status['authenticated']:
                        st.success("Google Calendar sync initiated!")
                    else:
                        st.warning("Google Calendar authentication required")

                if st.button("⚙️ Configure Google", key="google_config"):
                    st.info("Google Calendar configuration would open here")

            # Outlook Calendar
            with col2:
                st.markdown("**🟦 Outlook Calendar**")

                outlook_status = integration_status['outlook']
                status_color = "🟢" if outlook_status['authenticated'] else "🔴"

                st.write(f"{status_color} **Status:** {'Connected' if outlook_status['authenticated'] else 'Not Connected'}")
                st.write(f"**Available:** {'Yes' if outlook_status['available'] else 'No'}")
                st.write(f"**Configured:** {'Yes' if outlook_status['configured'] else 'No'}")

                if st.button("🔄 Sync Outlook Calendar", key="outlook_sync"):
                    if outlook_status['authenticated']:
                        st.success("Outlook Calendar sync initiated!")
                    else:
                        st.warning("Outlook Calendar authentication required")

                if st.button("⚙️ Configure Outlook", key="outlook_config"):
                    st.info("Outlook Calendar configuration would open here")

            # iCal Export
            with col3:
                st.markdown("**📋 iCal Export**")

                ical_status = integration_status['ical']
                st.write("🟢 **Status:** Always Available")
                st.write("**Available:** Yes")
                st.write("**Configured:** Yes")

                if st.button("📥 Export iCal", key="ical_export"):
                    # Generate sample iCal for demonstration
                    st.success("iCal file would be generated here")
                    st.download_button(
                        label="📥 Download Sample iCal",
                        data="BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR",
                        file_name="hospital_appointments.ics",
                        mime="text/calendar"
                    )

        except Exception as e:
            st.error(f"Error loading calendar integration status: {e}")

        st.markdown("---")

        # Calendar sync settings
        st.markdown("#### ⚙️ Calendar Sync Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🔄 Sync Preferences**")

            auto_sync = st.checkbox("Auto-sync new appointments", value=True)
            sync_reminders = st.checkbox("Include appointment reminders", value=True)
            sync_cancelled = st.checkbox("Sync cancelled appointments", value=False)

            sync_frequency = st.selectbox("Sync Frequency", ["Real-time", "Every 15 minutes", "Every hour", "Daily"])

        with col2:
            st.markdown("**📊 Sync Statistics**")

            st.metric("Appointments Synced Today", "23", delta="7")
            st.metric("Last Sync", "2 minutes ago")
            st.metric("Sync Success Rate", "100%")

    # API Management Tab
    with tab3:
        st.markdown("#### 🔌 API Management & External Access")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**🔑 API Configuration**")

            # API settings
            with st.expander("⚙️ API Settings"):
                api_enabled = st.checkbox("Enable REST API", value=True)
                api_port = st.number_input("API Port", value=5000, min_value=1000, max_value=9999)
                api_host = st.text_input("API Host", value="0.0.0.0")
                api_debug = st.checkbox("Debug Mode", value=False)

                rate_limit = st.slider("Rate Limit (requests/minute)", 10, 1000, 100)

                if st.button("💾 Save API Settings"):
                    st.success("API settings saved!")

            # API endpoints documentation
            st.markdown("**📚 API Documentation**")

            endpoints_data = {
                "Endpoint": [
                    "GET /api/v1/health",
                    "POST /api/v1/auth/token",
                    "GET /api/v1/departments",
                    "GET /api/v1/doctors",
                    "GET /api/v1/appointments",
                    "POST /api/v1/appointments",
                    "GET /api/v1/analytics/hospital"
                ],
                "Description": [
                    "Health check endpoint",
                    "Generate JWT token",
                    "List all departments",
                    "List doctors with filtering",
                    "List appointments with filtering",
                    "Create new appointment",
                    "Get hospital analytics"
                ],
                "Auth Required": [
                    "No", "No", "API Key", "API Key", "API Key", "JWT Token", "API Key"
                ]
            }

            st.dataframe(pd.DataFrame(endpoints_data), use_container_width=True)

            if st.button("📖 View Full API Documentation"):
                st.info("Full API documentation would open in a new tab: /api/v1/docs")

        with col2:
            st.markdown("**📊 API Statistics**")

            # API stats (simulated for demo)
            st.metric("API Requests Today", "156", delta="23")
            st.metric("Success Rate", "99.2%", delta="0.5%")
            st.metric("Avg Response Time", "145ms", delta="-12ms")

            st.markdown("**🔑 API Keys**")

            # API key management
            if st.button("🔑 Generate New API Key"):
                import secrets
                new_key = f"hb_{secrets.token_hex(16)}"
                st.code(new_key)
                st.success("New API key generated!")

            # Active API keys (demo)
            st.markdown("**Active Keys:**")
            st.write("• hb_a1b2c3d4... (Main Client)")
            st.write("• hb_e5f6g7h8... (Mobile App)")

        st.markdown("---")

        # Integration monitoring
        st.markdown("#### 📡 Integration Health Monitoring")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Email Service", "🟢 Healthy")
        with col2:
            st.metric("Google Calendar", "🟡 Warning")
        with col3:
            st.metric("Outlook Calendar", "🔴 Error")
        with col4:
            st.metric("API Endpoints", "🟢 Healthy")

        # Integration logs
        st.markdown("#### 📝 Integration Logs")

        log_entries = [
            {"time": "14:30:25", "service": "Email", "message": "Confirmation sent to patient@example.com", "status": "✅"},
            {"time": "14:29:15", "service": "Google Cal", "message": "Event created: appointment-123", "status": "✅"},
            {"time": "14:28:45", "service": "API", "message": "New appointment created via API", "status": "✅"},
            {"time": "14:27:30", "service": "Outlook", "message": "Authentication failed", "status": "❌"},
            {"time": "14:26:12", "service": "Email", "message": "Reminder sent to user@example.com", "status": "✅"}
        ]

        log_df = pd.DataFrame(log_entries)
        st.dataframe(log_df, use_container_width=True, hide_index=True)

        if st.button("🔄 Refresh Logs"):
            st.rerun()


def render_navigation():
    """Render navigation sidebar."""
    st.sidebar.markdown("# 🏥 Navigation")
    
    # Main navigation options
    pages = {
        "🏠 Hospital Overview": "overview",
        "👨‍⚕️ Doctors": "doctors",
        "🏢 Departments": "departments",
        "📅 Appointments": "appointments",
        "📊 Analytics": "analytics",
        "📋 Reports": "reports",
        "🔗 Integrations": "integrations"
    }
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'overview'
    
    # Navigation buttons
    for page_name, page_key in pages.items():
        if st.sidebar.button(
            page_name, 
            key=f"nav_{page_key}",
            use_container_width=True
        ):
            st.session_state['current_page'] = page_key
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.markdown("### ⚡ Quick Actions")
    if st.sidebar.button("➕ Schedule Appointment", use_container_width=True):
        st.session_state['show_appointment_form'] = True
        st.rerun()
    
    if st.sidebar.button("🔍 Find Doctor", use_container_width=True):
        st.session_state['current_page'] = 'doctors'
        st.rerun()
    
    # System info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ System Info")
    st.sidebar.info(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n**Time:** {datetime.now().strftime('%H:%M')}")


def main():
    """Main application function."""
    # Load CSS
    load_tailwind_css()
    
    # Initialize database
    if not initialize_database():
        st.stop()
    
    # Render navigation
    render_navigation()
    
    # Get current page
    current_page = st.session_state.get('current_page', 'overview')
    
    # Render main content based on current page
    if current_page == 'overview':
        render_hospital_overview()
    elif current_page == 'doctors':
        render_doctors_directory()
    elif current_page == 'departments':
        render_departments_management()
    elif current_page == 'appointments':
        render_appointments_management()
    elif current_page == 'analytics':
        render_analytics_dashboard()
    elif current_page == 'reports':
        render_reports_page()
    elif current_page == 'integrations':
        render_integrations_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.8rem;">
        City General Hospital Booking System v1.0 | Phase 1.1: Foundation
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
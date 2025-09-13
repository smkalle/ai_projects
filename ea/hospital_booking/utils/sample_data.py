"""Sample data creation for Hospital Booking System."""

from datetime import datetime, date, time, timedelta
from database.connection import get_database_manager
from database.models import (
    Hospital, Department, Doctor, DoctorAvailability,
    Patient, Appointment, Room, Equipment
)


def create_sample_data():
    """Create sample data for testing."""
    db_manager = get_database_manager()
    session = db_manager.get_session()

    try:
        # Create hospital
        hospital = Hospital(
            name="City General Hospital",
            address="123 Medical Center Drive, Downtown",
            phone="(555) 123-4567",
            total_beds=500,
            current_occupancy=387
        )
        session.add(hospital)
        session.flush()

        # Create departments
        departments_data = [
            {"id": "cardiology", "name": "Cardiology", "location": "Wing A, Floor 3", "total_staff": 25, "active_staff": 22},
            {"id": "emergency", "name": "Emergency Department", "location": "Ground Floor", "total_staff": 40, "active_staff": 38},
            {"id": "surgery", "name": "Surgery", "location": "Wing B, Floor 2", "total_staff": 30, "active_staff": 27},
            {"id": "internal_medicine", "name": "Internal Medicine", "location": "Wing A, Floor 2", "total_staff": 20, "active_staff": 18},
            {"id": "pediatrics", "name": "Pediatrics", "location": "Wing C, Floor 1", "total_staff": 15, "active_staff": 14}
        ]

        departments = {}
        for dept_data in departments_data:
            dept = Department(
                id=dept_data["id"],
                name=dept_data["name"],
                location=dept_data["location"],
                total_staff=dept_data["total_staff"],
                active_staff=dept_data["active_staff"],
                hospital_id=hospital.id
            )
            session.add(dept)
            departments[dept_data["id"]] = dept

        # Create doctors
        doctors_data = [
            {"id": "DR001", "name": "Dr. Sarah Johnson", "title": "Chief of Cardiology", "dept": "cardiology", "email": "s.johnson@hospital.com"},
            {"id": "DR002", "name": "Dr. Michael Chen", "title": "Emergency Physician", "dept": "emergency", "email": "m.chen@hospital.com"},
            {"id": "DR003", "name": "Dr. Emily Rodriguez", "title": "Surgeon", "dept": "surgery", "email": "e.rodriguez@hospital.com"},
            {"id": "DR004", "name": "Dr. James Wilson", "title": "Internal Medicine", "dept": "internal_medicine", "email": "j.wilson@hospital.com"},
            {"id": "DR005", "name": "Dr. Lisa Thompson", "title": "Pediatrician", "dept": "pediatrics", "email": "l.thompson@hospital.com"},
            {"id": "DR006", "name": "Dr. David Park", "title": "Cardiologist", "dept": "cardiology", "email": "d.park@hospital.com"},
            {"id": "DR007", "name": "Dr. Maria Garcia", "title": "Emergency Physician", "dept": "emergency", "email": "m.garcia@hospital.com"},
            {"id": "DR008", "name": "Dr. Robert Kim", "title": "Surgeon", "dept": "surgery", "email": "r.kim@hospital.com"}
        ]

        doctors = {}
        for doc_data in doctors_data:
            doctor = Doctor(
                id=doc_data["id"],
                name=doc_data["name"],
                title=doc_data["title"],
                department_id=doc_data["dept"],
                email=doc_data["email"],
                license_number=f"LIC{doc_data['id'][-3:]}",
                specialization=doc_data["title"],
                phone=f"(555) {doc_data['id'][-3:]}-0000",
                years_experience=10,
                status="active",
                schedule_type="full_time",
                available_for_booking=True
            )
            session.add(doctor)
            doctors[doc_data["id"]] = doctor

            # Create availability (Mon-Fri 9-5)
            for day in range(5):
                availability = DoctorAvailability(
                    doctor_id=doc_data["id"],
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    appointment_duration=30
                )
                session.add(availability)

        # Set department heads
        departments["cardiology"].head_doctor_id = "DR001"
        departments["emergency"].head_doctor_id = "DR002"
        departments["surgery"].head_doctor_id = "DR003"
        departments["internal_medicine"].head_doctor_id = "DR004"
        departments["pediatrics"].head_doctor_id = "DR005"

        # Create sample patients
        patients_data = [
            {"first": "John", "last": "Smith", "email": "john.smith@email.com", "phone": "(555) 101-0001"},
            {"first": "Mary", "last": "Johnson", "email": "mary.johnson@email.com", "phone": "(555) 101-0002"},
            {"first": "David", "last": "Brown", "email": "david.brown@email.com", "phone": "(555) 101-0003"},
            {"first": "Sarah", "last": "Davis", "email": "sarah.davis@email.com", "phone": "(555) 101-0004"},
            {"first": "Michael", "last": "Wilson", "email": "michael.wilson@email.com", "phone": "(555) 101-0005"}
        ]

        patients = []
        for pat_data in patients_data:
            patient = Patient(
                first_name=pat_data["first"],
                last_name=pat_data["last"],
                email=pat_data["email"],
                phone=pat_data["phone"],
                date_of_birth=date(1985, 1, 15),
                emergency_contact="Emergency Contact"
            )
            session.add(patient)
            patients.append(patient)

        session.flush()  # Get patient IDs

        # Create sample appointments for today and next few days
        today = date.today()
        appointments_data = [
            {"patient_idx": 0, "doctor": "DR001", "date": today, "start": "09:00", "end": "09:30", "type": "patient_care", "reason": "Regular checkup"},
            {"patient_idx": 1, "doctor": "DR002", "date": today, "start": "10:30", "end": "11:00", "type": "emergency", "reason": "Chest pain evaluation"},
            {"patient_idx": 2, "doctor": "DR003", "date": today + timedelta(days=1), "start": "14:00", "end": "15:00", "type": "procedure", "reason": "Pre-surgical consultation"},
            {"patient_idx": 3, "doctor": "DR004", "date": today, "start": "11:00", "end": "11:30", "type": "patient_care", "reason": "Follow-up visit"},
            {"patient_idx": 4, "doctor": "DR005", "date": today + timedelta(days=2), "start": "15:30", "end": "16:00", "type": "patient_care", "reason": "Child wellness exam"}
        ]

        for apt_data in appointments_data:
            start_time_obj = datetime.strptime(apt_data["start"], "%H:%M").time()
            end_time_obj = datetime.strptime(apt_data["end"], "%H:%M").time()

            appointment = Appointment(
                patient_id=patients[apt_data["patient_idx"]].id,
                doctor_id=apt_data["doctor"],
                appointment_date=apt_data["date"],
                start_time=start_time_obj,
                end_time=end_time_obj,
                appointment_type=apt_data["type"],
                priority="routine" if apt_data["type"] != "emergency" else "urgent",
                status="scheduled",
                reason_for_visit=apt_data["reason"],
                location=f"Room {apt_data['doctor'][-3:]}"
            )
            session.add(appointment)

        # Add some rooms and equipment
        room_data = [
            {"dept": "cardiology", "rooms": ["Card-101", "Card-102", "Card-103"]},
            {"dept": "emergency", "rooms": ["ER-1", "ER-2", "ER-3", "ER-4", "Trauma-1"]},
            {"dept": "surgery", "rooms": ["OR-1", "OR-2", "OR-3", "Recovery-A"]},
            {"dept": "internal_medicine", "rooms": ["IM-201", "IM-202", "IM-203"]},
            {"dept": "pediatrics", "rooms": ["Peds-101", "Peds-102", "NICU-1"]}
        ]

        for room_info in room_data:
            for room_name in room_info["rooms"]:
                room = Room(
                    room_number=room_name,
                    department_id=room_info["dept"],
                    room_type="examination",
                    capacity=1,
                    status="available"
                )
                session.add(room)

        equipment_data = [
            {"dept": "cardiology", "equipment": ["ECG Machine", "Holter Monitor", "Echocardiogram"]},
            {"dept": "emergency", "equipment": ["Defibrillator", "Ventilator", "X-Ray Mobile Unit"]},
            {"dept": "surgery", "equipment": ["Surgical Robot", "Anesthesia Machine", "OR Lights"]},
            {"dept": "internal_medicine", "equipment": ["BP Monitor", "Thermometer", "Stethoscope"]},
            {"dept": "pediatrics", "equipment": ["Pediatric Scale", "Infant Warmer", "Pulse Oximeter"]}
        ]

        for eq_info in equipment_data:
            for eq_name in eq_info["equipment"]:
                equipment = Equipment(
                    name=eq_name,
                    department_id=eq_info["dept"],
                    equipment_type="medical_device",
                    status="operational"
                )
                session.add(equipment)

        session.commit()
        print("✅ Sample data created successfully!")
        return True

    except Exception as e:
        session.rollback()
        print(f"❌ Error creating sample data: {e}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    create_sample_data()
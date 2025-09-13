"""Data migration utility to convert JavaScript data to SQLite."""

import json
import re
from datetime import datetime, date, time
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path to import database models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseManager, Base
from database.models import (
    Hospital, Department, Doctor, DoctorAvailability, 
    Patient, Appointment, Room, Equipment, SystemConfiguration
)


class DataMigrator:
    """Handles migration of data from JavaScript to SQLite database."""
    
    def __init__(self, js_file_path: str):
        self.js_file_path = js_file_path
        self.db_manager = DatabaseManager()
        
    def parse_javascript_data(self) -> Dict[str, Any]:
        """Parse JavaScript file and extract appData object."""
        try:
            with open(self.js_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Find the appData object
            pattern = r'const appData\s*=\s*({.*?});'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                raise ValueError("Could not find appData object in JavaScript file")
            
            js_object_str = match.group(1)
            
            # Clean up JavaScript object to make it valid JSON
            js_object_str = self._clean_js_object(js_object_str)
            
            # Parse as JSON
            app_data = json.loads(js_object_str)
            return app_data
            
        except Exception as e:
            print(f"Error parsing JavaScript file: {e}")
            return {}
    
    def _clean_js_object(self, js_str: str) -> str:
        """Clean JavaScript object string to make it valid JSON."""
        # Remove JavaScript comments
        js_str = re.sub(r'//.*?\n', '\n', js_str)
        js_str = re.sub(r'/\*.*?\*/', '', js_str, flags=re.DOTALL)
        
        # Fix unquoted keys - find keys that aren't quoted
        js_str = re.sub(r'(\w+):', r'"\1":', js_str)
        
        # Fix already quoted keys that got double-quoted
        js_str = re.sub(r'""(\w+)"":', r'"\1":', js_str)
        
        # Handle trailing commas
        js_str = re.sub(r',(\s*[}\]])', r'\1', js_str)
        
        return js_str
    
    def create_database_schema(self):
        """Create all database tables."""
        self.db_manager.create_all_tables()
        print("✅ Database schema created successfully")
    
    def migrate_hospital_data(self, app_data: Dict[str, Any]):
        """Migrate hospital information."""
        session = self.db_manager.get_session()
        try:
            hospital_data = app_data.get('hospital', {})
            
            hospital = Hospital(
                name=hospital_data.get('name', 'City General Hospital'),
                address=hospital_data.get('address', ''),
                phone=hospital_data.get('phone', ''),
                total_beds=hospital_data.get('totalBeds', 0),
                current_occupancy=hospital_data.get('currentOccupancy', 0)
            )
            
            session.add(hospital)
            session.commit()
            
            print(f"✅ Migrated hospital: {hospital.name}")
            return hospital.id
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error migrating hospital data: {e}")
            return None
        finally:
            session.close()
    
    def migrate_departments(self, app_data: Dict[str, Any], hospital_id: int):
        """Migrate department information."""
        session = self.db_manager.get_session()
        try:
            departments_data = app_data.get('departments', {})
            
            for dept_id, dept_info in departments_data.items():
                department = Department(
                    id=dept_id,
                    name=dept_info.get('name', ''),
                    head_doctor_id=dept_info.get('head'),
                    location=dept_info.get('location', ''),
                    total_staff=dept_info.get('totalStaff', 0),
                    active_staff=dept_info.get('activeStaff', 0),
                    hospital_id=hospital_id
                )
                
                session.add(department)
                
                # Migrate rooms
                rooms_data = dept_info.get('rooms', [])
                for room_name in rooms_data:
                    room = Room(
                        room_number=room_name,
                        department_id=dept_id,
                        room_type=self._determine_room_type(room_name)
                    )
                    session.add(room)
                
                # Migrate equipment
                equipment_data = dept_info.get('equipment', [])
                for equipment_name in equipment_data:
                    equipment = Equipment(
                        name=equipment_name,
                        department_id=dept_id,
                        equipment_type=self._determine_equipment_type(equipment_name)
                    )
                    session.add(equipment)
            
            session.commit()
            print(f"✅ Migrated {len(departments_data)} departments")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error migrating departments: {e}")
        finally:
            session.close()
    
    def migrate_doctors(self, app_data: Dict[str, Any]):
        """Migrate doctor information."""
        session = self.db_manager.get_session()
        try:
            doctors_data = app_data.get('doctors', {})
            
            for doctor_id, doctor_info in doctors_data.items():
                doctor = Doctor(
                    id=doctor_id,
                    name=doctor_info.get('name', ''),
                    title=doctor_info.get('title', ''),
                    department_id=doctor_info.get('department'),
                    email=doctor_info.get('email', ''),
                    license_number=doctor_info.get('licenseNumber', ''),
                    specialization=doctor_info.get('specialization', ''),
                    phone=doctor_info.get('phone', ''),
                    years_experience=doctor_info.get('yearsExperience', 0),
                    status=doctor_info.get('status', 'active'),
                    schedule_type=doctor_info.get('schedule', 'full_time'),
                    available_for_booking=True
                )
                
                session.add(doctor)
                
                # Create default availability (9 AM - 5 PM, Mon-Fri)
                for day in range(5):  # Monday to Friday
                    availability = DoctorAvailability(
                        doctor_id=doctor_id,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        appointment_duration=30
                    )
                    session.add(availability)
            
            session.commit()
            print(f"✅ Migrated {len(doctors_data)} doctors")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error migrating doctors: {e}")
        finally:
            session.close()
    
    def migrate_appointments(self, app_data: Dict[str, Any]):
        """Migrate appointment information."""
        session = self.db_manager.get_session()
        try:
            appointments_data = app_data.get('appointments', [])
            patient_count = 0
            
            for apt_info in appointments_data:
                # Create patient if not exists (simplified for demo)
                patient_name = apt_info.get('patient', 'Unknown Patient')
                first_name, last_name = self._split_patient_name(patient_name)
                
                # Check if patient exists
                existing_patient = session.query(Patient).filter_by(
                    first_name=first_name, 
                    last_name=last_name
                ).first()
                
                if not existing_patient:
                    patient = Patient(
                        first_name=first_name,
                        last_name=last_name,
                        email=f"patient{patient_count}@example.com",
                        phone="(555) 000-0000"
                    )
                    session.add(patient)
                    session.flush()  # Get patient ID
                    patient_count += 1
                else:
                    patient = existing_patient
                
                # Create appointment
                apt_date = self._parse_date(apt_info.get('date', app_data.get('currentDate', '2025-09-11')))
                start_time_obj = self._parse_time(apt_info.get('startTime', '09:00'))
                end_time_obj = self._parse_time(apt_info.get('endTime', '09:30'))
                
                appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=apt_info.get('doctorId', 'DR001'),
                    appointment_date=apt_date,
                    start_time=start_time_obj,
                    end_time=end_time_obj,
                    appointment_type=apt_info.get('type', 'patient_care'),
                    priority=apt_info.get('priority', 'routine'),
                    status=apt_info.get('status', 'scheduled'),
                    reason_for_visit=apt_info.get('reason', ''),
                    location=apt_info.get('location', ''),
                    notes=apt_info.get('notes', '')
                )
                
                session.add(appointment)
            
            session.commit()
            print(f"✅ Migrated {len(appointments_data)} appointments")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error migrating appointments: {e}")
        finally:
            session.close()
    
    def _determine_room_type(self, room_name: str) -> str:
        """Determine room type based on room name."""
        room_name_lower = room_name.lower()
        if 'or' in room_name_lower or 'surgery' in room_name_lower:
            return 'surgery'
        elif 'er' in room_name_lower or 'emergency' in room_name_lower or 'trauma' in room_name_lower:
            return 'emergency'
        elif 'lab' in room_name_lower:
            return 'laboratory'
        elif 'icu' in room_name_lower or 'nicu' in room_name_lower:
            return 'intensive_care'
        else:
            return 'examination'
    
    def _determine_equipment_type(self, equipment_name: str) -> str:
        """Determine equipment type based on equipment name."""
        equipment_lower = equipment_name.lower()
        if 'surgical' in equipment_lower or 'robot' in equipment_lower:
            return 'surgical'
        elif 'monitor' in equipment_lower or 'ecg' in equipment_lower:
            return 'monitoring'
        elif 'machine' in equipment_lower or 'ventilator' in equipment_lower:
            return 'life_support'
        elif 'x-ray' in equipment_lower or 'imaging' in equipment_lower:
            return 'imaging'
        else:
            return 'medical_device'
    
    def _split_patient_name(self, full_name: str) -> tuple:
        """Split patient name into first and last name."""
        parts = full_name.strip().split(' ', 1)
        first_name = parts[0] if parts else 'Unknown'
        last_name = parts[1] if len(parts) > 1 else 'Patient'
        return first_name, last_name
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string to date object."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return date.today()
    
    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except:
            return time(9, 0)
    
    def run_full_migration(self):
        """Run complete data migration process."""
        print("🚀 Starting data migration from JavaScript to SQLite...")
        
        # Parse JavaScript data
        app_data = self.parse_javascript_data()
        if not app_data:
            print("❌ Failed to parse JavaScript data")
            return False
        
        print(f"✅ Parsed JavaScript data successfully")
        
        # Create database schema
        self.create_database_schema()
        
        # Migrate hospital data
        hospital_id = self.migrate_hospital_data(app_data)
        if not hospital_id:
            print("❌ Failed to migrate hospital data")
            return False
        
        # Migrate departments
        self.migrate_departments(app_data, hospital_id)
        
        # Migrate doctors
        self.migrate_doctors(app_data)
        
        # Migrate appointments
        self.migrate_appointments(app_data)
        
        print("🎉 Data migration completed successfully!")
        return True


def main():
    """Main migration function."""
    js_file_path = "../../app.js"  # Path to original app.js file
    
    if not os.path.exists(js_file_path):
        print(f"❌ JavaScript file not found: {js_file_path}")
        print("Please ensure app.js is in the correct location")
        return
    
    migrator = DataMigrator(js_file_path)
    success = migrator.run_full_migration()
    
    if success:
        print("\n✅ Migration completed! You can now run the Streamlit application.")
    else:
        print("\n❌ Migration failed. Please check the errors above.")


if __name__ == "__main__":
    main()
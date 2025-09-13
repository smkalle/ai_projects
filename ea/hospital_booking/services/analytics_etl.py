"""
Analytics ETL Service
Real-time data processing for hospital analytics
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from database.connection import get_db_session
from database.models import (
    Hospital, Department, Doctor, Appointment, Patient,
    AppointmentAnalytics, DoctorPerformanceAnalytics, DepartmentPerformanceAnalytics,
    HospitalPerformanceAnalytics, FinancialMetrics, PatientSatisfactionSurvey
)

logger = logging.getLogger(__name__)


class AnalyticsETL:
    """ETL service for processing analytics data."""

    def __init__(self):
        self.session = None

    def __enter__(self):
        self.session = get_db_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

    def process_daily_analytics(self, target_date: date = None) -> bool:
        """Process daily analytics for all entities."""
        if target_date is None:
            target_date = date.today()

        try:
            logger.info(f"Processing daily analytics for {target_date}")

            # Process appointment analytics
            self.process_appointment_analytics(target_date)

            # Process doctor performance analytics
            self.process_doctor_performance_analytics(target_date)

            # Process department performance analytics
            self.process_department_performance_analytics(target_date)

            # Process hospital performance analytics
            self.process_hospital_performance_analytics(target_date)

            # Process financial metrics
            self.process_financial_metrics(target_date)

            self.session.commit()
            logger.info(f"Successfully processed daily analytics for {target_date}")
            return True

        except Exception as e:
            logger.error(f"Error processing daily analytics for {target_date}: {e}")
            self.session.rollback()
            return False

    def process_appointment_analytics(self, target_date: date):
        """Process appointment analytics by department."""
        departments = self.session.query(Department).all()

        for department in departments:
            # Get appointment counts for the department
            dept_appointments = self.session.query(Appointment).join(Doctor).filter(
                Doctor.department_id == department.id,
                Appointment.appointment_date == target_date
            )

            total_appointments = dept_appointments.count()
            completed_appointments = dept_appointments.filter(Appointment.status == 'completed').count()
            cancelled_appointments = dept_appointments.filter(Appointment.status == 'cancelled').count()
            no_show_appointments = dept_appointments.filter(Appointment.status == 'no_show').count()

            # Calculate average wait time (simulated for now)
            avg_wait_time = self._calculate_average_wait_time(department.id, target_date)

            # Calculate patient satisfaction (simulated for now)
            patient_satisfaction = self._calculate_department_satisfaction(department.id, target_date)

            # Check if analytics record already exists
            existing_record = self.session.query(AppointmentAnalytics).filter(
                AppointmentAnalytics.department_id == department.id,
                AppointmentAnalytics.date == target_date
            ).first()

            if existing_record:
                # Update existing record
                existing_record.total_appointments = total_appointments
                existing_record.completed_appointments = completed_appointments
                existing_record.cancelled_appointments = cancelled_appointments
                existing_record.no_show_appointments = no_show_appointments
                existing_record.average_wait_time = avg_wait_time
                existing_record.patient_satisfaction = patient_satisfaction
            else:
                # Create new record
                analytics_record = AppointmentAnalytics(
                    date=target_date,
                    department_id=department.id,
                    total_appointments=total_appointments,
                    completed_appointments=completed_appointments,
                    cancelled_appointments=cancelled_appointments,
                    no_show_appointments=no_show_appointments,
                    average_wait_time=avg_wait_time,
                    patient_satisfaction=patient_satisfaction
                )
                self.session.add(analytics_record)

    def process_doctor_performance_analytics(self, target_date: date):
        """Process doctor performance analytics."""
        doctors = self.session.query(Doctor).filter(Doctor.status == 'active').all()

        for doctor in doctors:
            # Get appointment counts for the doctor
            doctor_appointments = self.session.query(Appointment).filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date == target_date
            )

            total_appointments = doctor_appointments.count()
            completed_appointments = doctor_appointments.filter(Appointment.status == 'completed').count()
            cancelled_appointments = doctor_appointments.filter(Appointment.status == 'cancelled').count()
            no_show_appointments = doctor_appointments.filter(Appointment.status == 'no_show').count()

            # Calculate average appointment duration
            avg_duration = self._calculate_average_appointment_duration(doctor.id, target_date)

            # Calculate patient satisfaction for this doctor
            patient_satisfaction = self._calculate_doctor_satisfaction(doctor.id, target_date)

            # Calculate utilization rate
            utilization_rate = self._calculate_doctor_utilization(doctor.id, target_date)

            # Calculate revenue (simulated for now)
            revenue = self._calculate_doctor_revenue(doctor.id, target_date)

            # Check if analytics record already exists
            existing_record = self.session.query(DoctorPerformanceAnalytics).filter(
                DoctorPerformanceAnalytics.doctor_id == doctor.id,
                DoctorPerformanceAnalytics.date == target_date
            ).first()

            if existing_record:
                # Update existing record
                existing_record.total_appointments = total_appointments
                existing_record.completed_appointments = completed_appointments
                existing_record.cancelled_appointments = cancelled_appointments
                existing_record.no_show_appointments = no_show_appointments
                existing_record.average_appointment_duration = avg_duration
                existing_record.patient_satisfaction_avg = patient_satisfaction
                existing_record.utilization_rate = utilization_rate
                existing_record.revenue_generated = revenue
            else:
                # Create new record
                analytics_record = DoctorPerformanceAnalytics(
                    doctor_id=doctor.id,
                    date=target_date,
                    total_appointments=total_appointments,
                    completed_appointments=completed_appointments,
                    cancelled_appointments=cancelled_appointments,
                    no_show_appointments=no_show_appointments,
                    average_appointment_duration=avg_duration,
                    patient_satisfaction_avg=patient_satisfaction,
                    utilization_rate=utilization_rate,
                    revenue_generated=revenue
                )
                self.session.add(analytics_record)

    def process_department_performance_analytics(self, target_date: date):
        """Process department performance analytics."""
        departments = self.session.query(Department).all()

        for department in departments:
            # Get department appointments through doctors
            dept_appointments = self.session.query(Appointment).join(Doctor).filter(
                Doctor.department_id == department.id,
                Appointment.appointment_date == target_date
            )

            total_appointments = dept_appointments.count()
            completed_appointments = dept_appointments.filter(Appointment.status == 'completed').count()
            cancelled_appointments = dept_appointments.filter(Appointment.status == 'cancelled').count()
            no_show_appointments = dept_appointments.filter(Appointment.status == 'no_show').count()

            # Calculate metrics
            avg_wait_time = self._calculate_average_wait_time(department.id, target_date)
            patient_satisfaction = self._calculate_department_satisfaction(department.id, target_date)
            staff_utilization = self._calculate_department_staff_utilization(department.id, target_date)
            equipment_utilization = self._calculate_department_equipment_utilization(department.id, target_date)
            revenue = self._calculate_department_revenue(department.id, target_date)
            operating_costs = self._calculate_department_costs(department.id, target_date)

            # Check if analytics record already exists
            existing_record = self.session.query(DepartmentPerformanceAnalytics).filter(
                DepartmentPerformanceAnalytics.department_id == department.id,
                DepartmentPerformanceAnalytics.date == target_date
            ).first()

            if existing_record:
                # Update existing record
                existing_record.total_appointments = total_appointments
                existing_record.completed_appointments = completed_appointments
                existing_record.cancelled_appointments = cancelled_appointments
                existing_record.no_show_appointments = no_show_appointments
                existing_record.average_wait_time = avg_wait_time
                existing_record.patient_satisfaction_avg = patient_satisfaction
                existing_record.staff_utilization_rate = staff_utilization
                existing_record.equipment_utilization_rate = equipment_utilization
                existing_record.revenue_generated = revenue
                existing_record.operating_costs = operating_costs
            else:
                # Create new record
                analytics_record = DepartmentPerformanceAnalytics(
                    department_id=department.id,
                    date=target_date,
                    total_appointments=total_appointments,
                    completed_appointments=completed_appointments,
                    cancelled_appointments=cancelled_appointments,
                    no_show_appointments=no_show_appointments,
                    average_wait_time=avg_wait_time,
                    patient_satisfaction_avg=patient_satisfaction,
                    staff_utilization_rate=staff_utilization,
                    equipment_utilization_rate=equipment_utilization,
                    revenue_generated=revenue,
                    operating_costs=operating_costs
                )
                self.session.add(analytics_record)

    def process_hospital_performance_analytics(self, target_date: date):
        """Process hospital-wide performance analytics."""
        hospital = self.session.query(Hospital).first()
        if not hospital:
            return

        # Get all appointments for the date
        all_appointments = self.session.query(Appointment).filter(
            Appointment.appointment_date == target_date
        )

        total_appointments = all_appointments.count()
        completed_appointments = all_appointments.filter(Appointment.status == 'completed').count()
        cancelled_appointments = all_appointments.filter(Appointment.status == 'cancelled').count()
        no_show_appointments = all_appointments.filter(Appointment.status == 'no_show').count()
        emergency_appointments = all_appointments.filter(Appointment.priority == 'urgent').count()

        # Calculate hospital-wide metrics
        avg_wait_time = self._calculate_hospital_average_wait_time(target_date)
        patient_satisfaction = self._calculate_hospital_satisfaction(target_date)
        bed_occupancy = self._calculate_bed_occupancy_rate(target_date)
        staff_utilization = self._calculate_hospital_staff_utilization(target_date)
        total_revenue = self._calculate_hospital_revenue(target_date)
        total_costs = self._calculate_hospital_costs(target_date)

        # Check if analytics record already exists
        existing_record = self.session.query(HospitalPerformanceAnalytics).filter(
            HospitalPerformanceAnalytics.hospital_id == hospital.id,
            HospitalPerformanceAnalytics.date == target_date
        ).first()

        if existing_record:
            # Update existing record
            existing_record.total_appointments = total_appointments
            existing_record.completed_appointments = completed_appointments
            existing_record.cancelled_appointments = cancelled_appointments
            existing_record.no_show_appointments = no_show_appointments
            existing_record.emergency_appointments = emergency_appointments
            existing_record.average_wait_time = avg_wait_time
            existing_record.patient_satisfaction_avg = patient_satisfaction
            existing_record.bed_occupancy_rate = bed_occupancy
            existing_record.staff_utilization_rate = staff_utilization
            existing_record.total_revenue = total_revenue
            existing_record.total_operating_costs = total_costs
        else:
            # Create new record
            analytics_record = HospitalPerformanceAnalytics(
                hospital_id=hospital.id,
                date=target_date,
                total_appointments=total_appointments,
                completed_appointments=completed_appointments,
                cancelled_appointments=cancelled_appointments,
                no_show_appointments=no_show_appointments,
                emergency_appointments=emergency_appointments,
                average_wait_time=avg_wait_time,
                patient_satisfaction_avg=patient_satisfaction,
                bed_occupancy_rate=bed_occupancy,
                staff_utilization_rate=staff_utilization,
                total_revenue=total_revenue,
                total_operating_costs=total_costs
            )
            self.session.add(analytics_record)

    def process_financial_metrics(self, target_date: date):
        """Process financial metrics by department and doctor."""
        departments = self.session.query(Department).all()

        for department in departments:
            # Calculate department financial metrics
            dept_revenue = self._calculate_department_revenue(department.id, target_date)
            dept_costs = self._calculate_department_costs(department.id, target_date)

            # Get doctors in department
            doctors = self.session.query(Doctor).filter(
                Doctor.department_id == department.id,
                Doctor.status == 'active'
            ).all()

            for doctor in doctors:
                doctor_revenue = self._calculate_doctor_revenue(doctor.id, target_date)

                # Check if financial record already exists
                existing_record = self.session.query(FinancialMetrics).filter(
                    FinancialMetrics.department_id == department.id,
                    FinancialMetrics.doctor_id == doctor.id,
                    FinancialMetrics.date == target_date
                ).first()

                if existing_record:
                    # Update existing record
                    existing_record.appointment_revenue = doctor_revenue
                    existing_record.staff_costs = int(dept_costs * 0.6)  # 60% of costs are staff
                    existing_record.equipment_costs = int(dept_costs * 0.25)  # 25% equipment
                    existing_record.facility_costs = int(dept_costs * 0.15)  # 15% facility
                else:
                    # Create new record
                    financial_record = FinancialMetrics(
                        date=target_date,
                        department_id=department.id,
                        doctor_id=doctor.id,
                        appointment_revenue=doctor_revenue,
                        procedure_revenue=0,  # To be implemented
                        emergency_revenue=0,  # To be implemented
                        insurance_claims=0,  # To be implemented
                        outstanding_payments=0,  # To be implemented
                        staff_costs=int(dept_costs * 0.6),
                        equipment_costs=int(dept_costs * 0.25),
                        facility_costs=int(dept_costs * 0.15)
                    )
                    self.session.add(financial_record)

    # Helper methods for calculations (simulated data for now)

    def _calculate_average_wait_time(self, department_id: str, target_date: date) -> int:
        """Calculate average wait time for a department."""
        # Simulated calculation - in real system, this would be based on actual wait time data
        base_wait_time = {
            'emergency': 15,
            'cardiology': 25,
            'surgery': 20,
            'internal_medicine': 30,
            'pediatrics': 20
        }
        return base_wait_time.get(department_id, 25)

    def _calculate_average_appointment_duration(self, doctor_id: str, target_date: date) -> int:
        """Calculate average appointment duration for a doctor."""
        # Simulated calculation
        return 30  # 30 minutes average

    def _calculate_doctor_satisfaction(self, doctor_id: str, target_date: date) -> int:
        """Calculate patient satisfaction for a doctor."""
        # Query actual satisfaction surveys if available
        avg_satisfaction = self.session.query(func.avg(PatientSatisfactionSurvey.doctor_satisfaction)).filter(
            PatientSatisfactionSurvey.doctor_id == doctor_id,
            func.date(PatientSatisfactionSurvey.submitted_at) == target_date
        ).scalar()

        return int(avg_satisfaction) if avg_satisfaction else 4  # Default to 4/5

    def _calculate_department_satisfaction(self, department_id: str, target_date: date) -> int:
        """Calculate patient satisfaction for a department."""
        # Simulated calculation - would use actual survey data
        return 4  # Default to 4/5

    def _calculate_doctor_utilization(self, doctor_id: str, target_date: date) -> int:
        """Calculate doctor utilization rate."""
        # Simulated calculation based on appointments vs available time
        appointments_count = self.session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date,
            Appointment.status == 'completed'
        ).count()

        # Assume 8 hour workday, 30 min appointments = max 16 appointments
        max_appointments = 16
        utilization = min(100, int((appointments_count / max_appointments) * 100))
        return utilization

    def _calculate_doctor_revenue(self, doctor_id: str, target_date: date) -> int:
        """Calculate revenue generated by a doctor."""
        # Simulated calculation - in cents
        appointments_count = self.session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date,
            Appointment.status == 'completed'
        ).count()

        # Assume $150 per appointment
        return appointments_count * 15000  # $150 in cents

    def _calculate_department_staff_utilization(self, department_id: str, target_date: date) -> int:
        """Calculate department staff utilization."""
        department = self.session.query(Department).filter(Department.id == department_id).first()
        if not department:
            return 0

        return int((department.active_staff / department.total_staff) * 100) if department.total_staff > 0 else 0

    def _calculate_department_equipment_utilization(self, department_id: str, target_date: date) -> int:
        """Calculate department equipment utilization."""
        # Simulated calculation
        return 75  # 75% utilization

    def _calculate_department_revenue(self, department_id: str, target_date: date) -> int:
        """Calculate revenue for a department."""
        # Sum revenue from all doctors in department
        doctors = self.session.query(Doctor).filter(Doctor.department_id == department_id).all()
        total_revenue = 0
        for doctor in doctors:
            total_revenue += self._calculate_doctor_revenue(doctor.id, target_date)
        return total_revenue

    def _calculate_department_costs(self, department_id: str, target_date: date) -> int:
        """Calculate operating costs for a department."""
        # Simulated calculation - in cents
        department = self.session.query(Department).filter(Department.id == department_id).first()
        if not department:
            return 0

        # Base cost calculation: $500 per active staff member per day
        base_cost = department.active_staff * 50000  # $500 in cents
        return base_cost

    def _calculate_hospital_average_wait_time(self, target_date: date) -> int:
        """Calculate hospital-wide average wait time."""
        # Simulated calculation
        return 25  # 25 minutes average

    def _calculate_hospital_satisfaction(self, target_date: date) -> int:
        """Calculate hospital-wide patient satisfaction."""
        avg_satisfaction = self.session.query(func.avg(PatientSatisfactionSurvey.overall_satisfaction)).filter(
            func.date(PatientSatisfactionSurvey.submitted_at) == target_date
        ).scalar()

        return int(avg_satisfaction) if avg_satisfaction else 4  # Default to 4/5

    def _calculate_bed_occupancy_rate(self, target_date: date) -> int:
        """Calculate bed occupancy rate."""
        hospital = self.session.query(Hospital).first()
        if not hospital:
            return 0

        # Simulated calculation
        return int((hospital.current_occupancy / hospital.total_beds) * 100) if hospital.total_beds > 0 else 0

    def _calculate_hospital_staff_utilization(self, target_date: date) -> int:
        """Calculate hospital-wide staff utilization."""
        # Average department staff utilization
        departments = self.session.query(Department).all()
        total_utilization = 0
        count = 0

        for dept in departments:
            utilization = self._calculate_department_staff_utilization(dept.id, target_date)
            total_utilization += utilization
            count += 1

        return int(total_utilization / count) if count > 0 else 0

    def _calculate_hospital_revenue(self, target_date: date) -> int:
        """Calculate hospital-wide revenue."""
        departments = self.session.query(Department).all()
        total_revenue = 0
        for dept in departments:
            total_revenue += self._calculate_department_revenue(dept.id, target_date)
        return total_revenue

    def _calculate_hospital_costs(self, target_date: date) -> int:
        """Calculate hospital-wide operating costs."""
        departments = self.session.query(Department).all()
        total_costs = 0
        for dept in departments:
            total_costs += self._calculate_department_costs(dept.id, target_date)
        return total_costs


def run_daily_etl(target_date: date = None) -> bool:
    """Run daily ETL process for analytics."""
    with AnalyticsETL() as etl:
        return etl.process_daily_analytics(target_date)


def backfill_analytics(start_date: date, end_date: date) -> bool:
    """Backfill analytics data for a date range."""
    current_date = start_date

    with AnalyticsETL() as etl:
        while current_date <= end_date:
            success = etl.process_daily_analytics(current_date)
            if not success:
                logger.error(f"Failed to process analytics for {current_date}")
                return False
            current_date += timedelta(days=1)

    logger.info(f"Successfully backfilled analytics from {start_date} to {end_date}")
    return True
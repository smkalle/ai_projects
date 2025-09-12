# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a Hospital Doctor Schedule Management web application built as a static single-page application featuring:

- **Frontend**: Pure HTML, CSS, and vanilla JavaScript with medical theme
- **Doctor Dashboard**: Calendar interface for Dr. Michael Rodriguez (Cardiologist) with appointment management
- **Medical Analytics**: Comprehensive healthcare analytics with Chart.js visualizations
- **Data Structure**: In-memory JavaScript objects containing doctor profile, patient appointments, and clinical metrics

The application displays:
- Daily schedule view with patient appointments (time, patient info, location, priority, diagnosis)
- Weekly medical analytics with appointment type breakdowns, patient metrics, and clinical outcomes
- Doctor profile information with license number and specialization
- Interactive navigation between daily schedule and analytics views

## Development Commands

### Running the Application
- **No build step required** - this is a static website
- **Local development**: Open `index.html` directly in a web browser
- **HTTP server**: `python -m http.server` then visit `http://localhost:8000`

### Dependencies
- **Chart.js**: Loaded via CDN (`https://cdn.jsdelivr.net/npm/chart.js`)
- **Python virtual environment**: Present in `venv/` directory (for potential server-side features)

## File Structure

- `index.html`: Main application HTML with doctor schedule interface
- `app.js`: JavaScript application logic with appointment data and medical analytics
- `style.css`: CSS styling for medical theme with priority indicators and appointment types
- `GEMINI.md`: Existing project documentation
- `venv/`: Python virtual environment (standard pip installation)

## Data Architecture

The application uses a centralized `appData` object containing:

### Doctor Profile
- Doctor information (name, title, department, email, license number, specialization)

### Appointments Array
- Detailed appointment objects with medical-specific fields:
  - Patient care appointments with patient IDs and diagnoses
  - Medical procedures with priority levels
  - Emergency consultations
  - Administrative meetings
  - Break periods

### Medical Analytics
- **Appointment Distribution**: Patient care, procedures, emergency, administrative, breaks
- **Time Allocation**: How doctor's time is spent across different activities
- **Patient Metrics**: New patients, follow-ups, procedures completed, emergency consults
- **Clinical Outcomes**: Patient satisfaction, readmission rates, procedure success rates
- **Efficiency Metrics**: On-time starts, average wait times, completion rates
- **Workload Distribution**: Breakdown of clinical activities

## Medical Theme Features

### Appointment Types
- `patient_care`: Regular patient consultations and check-ups
- `procedure`: Medical procedures and surgeries  
- `emergency`: Urgent patient cases
- `administrative`: Hospital meetings and paperwork
- `break`: Lunch and rest periods

### Priority Levels
- `urgent`: Critical cases with pulsing red badge animation
- `high`: Important cases with orange badge
- `routine`: Standard appointments

### Color Coding
- **Patient Care**: Green theme
- **Procedures**: Blue theme  
- **Emergency**: Red theme with special highlighting
- **Administrative**: Orange theme
- **Breaks**: Gray theme

## Key Functions

- `renderAppointments()`: Renders filtered appointment list
- `createAppointmentElement()`: Creates individual appointment blocks with priority badges
- `openAppointmentModal()`: Shows detailed appointment information including patient ID and diagnosis
- `setupAppointmentTypeChart()`: Creates medical analytics charts
- `detectConflicts()`: Prevents appointment scheduling conflicts
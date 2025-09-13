# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a Hospital Scheduling Management System - a comprehensive static web application for managing hospital operations. Built as a single-page application with multiple views and departments:

- **Frontend**: Pure HTML, CSS, and vanilla JavaScript (no framework dependencies)
- **Multi-View Interface**: Hospital overview, department view, and doctor view with dynamic switching
- **Department Management**: Cardiology, Emergency, Surgery, Internal Medicine, and Pediatrics
- **Analytics Dashboard**: Hospital-wide metrics with Chart.js visualizations
- **Data Structure**: Large in-memory JavaScript object (`appData`) containing hospital, staff, and scheduling data

## Development Commands

### Running the Application
- **No build step required** - this is a static website
- **Local development**: Open `index.html` directly in web browser
- **HTTP server**: `python -m http.server` then visit `http://localhost:8000` (recommended)
- **No package manager** - uses CDN for Chart.js dependency

### Dependencies
- **Chart.js**: Loaded via CDN (`https://cdn.jsdelivr.net/npm/chart.js`)
- **No build tools, bundlers, or package managers** - pure static files

## Core File Structure

- `index.html` (521 lines): Main application HTML with navigation, modals, and dashboard sections
- `app.js` (1505 lines): Complete application logic and comprehensive hospital data
- `style.css` (1928 lines): Extensive CSS with hospital theming, responsive layout, and animations
- `README.md`: User-facing documentation with setup instructions
- `ENHANCEMENT_SPEC.md`: Specification for patient-facing booking feature (future enhancement)

## Data Architecture

The `appData` object in `app.js` contains the complete hospital data model:

### Hospital Information
- Basic hospital details (name, address, bed capacity, occupancy)
- Current user context and permissions
- Date/time and view state management

### Departments Structure
- **5 departments**: cardiology, emergency, surgery, internal_medicine, pediatrics
- Each department includes: head doctor, location, staff counts, rooms, equipment
- Complete staffing and resource allocation data

### Doctor Profiles
- Comprehensive doctor records with licenses, specializations, contact info
- Department assignments and experience levels
- Status and scheduling information

### Appointments System
- Detailed appointment objects with patient information
- Multiple appointment types: patient_care, procedure, emergency, administrative, break
- Priority levels: urgent, high, routine with visual indicators
- Time slots, locations, and medical notes

### Analytics Data
- Hospital performance metrics and KPIs
- Department-specific analytics and comparisons
- Resource utilization and capacity planning data

## Key Application Views

### Hospital Overview
- Real-time hospital statistics and occupancy
- Department status summaries
- System-wide analytics and charts

### Department View  
- Department-specific scheduling and resources
- Staff assignments and availability
- Equipment and room management

### Doctor View
- Individual doctor schedules and appointments
- Patient care tracking and medical records
- Performance metrics and workload analysis

## Major JavaScript Functions

The application uses a modular approach with key functions:
- `initializeApp()`: Main initialization and setup
- `switchView()`: Handles view transitions between hospital/department/doctor
- `renderAppointments()`: Dynamic appointment rendering with filtering
- `setupEventListeners()`: Comprehensive event handling
- Chart setup functions for analytics visualization
- Modal management for appointment details and quick scheduling

## Development Notes

- **Static Architecture**: No server-side dependencies or build process
- **Single File Components**: All logic contained in three main files
- **In-Memory Data**: All data stored in JavaScript objects (no persistence)
- **Responsive Design**: Mobile-friendly interface with CSS Grid/Flexbox
- **Accessibility**: Semantic HTML structure with proper ARIA labels
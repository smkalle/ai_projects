# Hospital Doctor Schedule Management

<!-- Optional: Add a project logo here -->
<!-- ![Project Logo](path/to/logo.png) -->

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

> A modern, interactive dashboard for managing hospital doctor schedules, appointments, and resources.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

This is a static web application that provides a comprehensive solution for managing hospital doctor schedules. It features an interactive dashboard for viewing and managing appointments, along with powerful analytics to monitor hospital performance. The application is built with vanilla HTML, CSS, and JavaScript, making it lightweight and easy to run.

## Features

- **Calendar & Scheduling:**
  - Interactive daily schedule timeline.
  - Create, view, and manage appointments.
  - Drag-and-drop rescheduling (simulated).
  - Appointment conflict detection.
  - Smart suggestions for optimal booking times.
- **Dashboards & Analytics:**
  - Hospital-wide analytics dashboard.
  - Department and doctor performance metrics.
  - Visualizations for appointment distribution, resource utilization, and more, powered by Chart.js.
- **Resource Management:**
  - Real-time status of rooms and equipment.
  - Staff overview and utilization metrics.
- **Filtering & Views:**
  - Switch between hospital, department, and doctor views.
  - Filter appointments by type, department, and doctor.

## Getting Started

### Prerequisites

- A modern web browser (e.g., Chrome, Firefox, Safari).
- Python 3 (for running a simple HTTP server).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/hospital-schedule-management.git
    cd hospital-schedule-management
    ```
2.  **Run the application:**
    - **Option 1: Open `index.html` directly**
      - Open the `index.html` file in your web browser.
    - **Option 2: Use a local server (recommended)**
      - If you have Python installed, you can run a simple HTTP server:
        ```bash
        python -m http.server
        ```
      - Then, open `http://localhost:8000` in your browser.

## Usage

- **Switch Views:** Use the navigation on the left to switch between "Today's Schedule", "Hospital Analytics", "Resource Management", and "Department Overview".
- **Filter Appointments:** Use the filter buttons to narrow down the appointments shown on the schedule.
- **View Appointment Details:** Click on an appointment in the schedule to see more details in a modal window.
- **Analyze Data:** Explore the "Hospital Analytics" view to see charts and metrics on hospital performance.

## File Structure

- `index.html`: The main application HTML file.
- `style.css`: The CSS stylesheet for the application.
- `app.js`: The JavaScript file containing the application logic and data.
- `ENHANCEMENT_SPEC.md`: Specification for a new patient booking feature.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

This project is licensed under the MIT License.

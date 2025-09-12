# Product Specification: Patient-Facing Appointment Booking

## 1. Introduction & Vision

This document outlines the requirements for a new patient-facing appointment booking feature to be added to the existing Hospital Scheduling Management System. The goal is to create a seamless, user-friendly experience for patients to book appointments with doctors, similar to the functionality provided by services like Calendly. This will empower patients, reduce administrative overhead, and improve the overall efficiency of the appointment scheduling process.

## 2. Target Audience

*   **Primary:** New and existing patients of City General Hospital who want to book appointments online.
*   **Secondary:** Hospital administrative staff who will manage and oversee the booking process.

## 3. User Stories

### As a patient, I want to:

*   `PA-1`: View a list of available doctors and their specialties.
*   `PA-2`: Filter doctors by department/specialty.
*   `PA-3`: Select a doctor and view their available appointment slots.
*   `PA-4`: Choose a date and time for my appointment.
*   `PA-5`: Enter my personal details (name, contact information, reason for visit).
*   `PA-6`: Receive a confirmation of my booked appointment via email or SMS.
*   `PA-7`: Be able to cancel or reschedule my appointment through a link in the confirmation.

### As a hospital administrator, I want to:

*   `HA-1`: Have the patient-booked appointments automatically appear in the main scheduling system.
*   `HA-2`: Be able to define which doctors are available for online booking.
*   `HA-3`: Be able to configure the duration of different appointment types.
*   `HA-4`: Receive notifications for new patient bookings, cancellations, or rescheduling.

## 4. Design & UX

The patient-facing booking system should be a new, separate web page that is clean, simple, and mobile-friendly. It should be accessible from the main hospital website.

### 4.1. User Flow

1.  **Doctor Selection:**
    *   The user lands on a page displaying a grid of doctors available for online booking.
    *   Each doctor's card shows their photo, name, specialty, and a brief bio.
    *   A filtering mechanism allows users to narrow down the list by department.

2.  **Scheduling:**
    *   Upon selecting a doctor, the user is taken to a scheduling view.
    *   This view will display a calendar (e.g., a weekly view) showing the doctor's availability.
    *   The user can navigate between weeks.
    *   Available time slots for each day are clearly displayed.

3.  **Booking Form:**
    *   After selecting a time slot, a booking form appears.
    *   The form will require the patient's first name, last name, email address, phone number, and a brief reason for the visit.

4.  **Confirmation:**
    *   After submitting the form, a confirmation page is displayed with the appointment details.
    *   An email/SMS confirmation is sent to the patient with the appointment details and links to cancel or reschedule.

### 4.2. Mockups (Conceptual)

*   **Doctor Listing Page:** A grid of cards, each with a doctor's photo, name, and specialty. A sidebar with department filters.
*   **Scheduling Page:** A two-panel layout. The left panel shows a calendar for date selection. The right panel shows available time slots for the selected date.
*   **Booking Form:** A simple, clean form with clearly labeled fields.

## 5. Technical Requirements

### 5.1. Frontend

*   A new HTML file (`booking.html`) will be created for the patient-facing interface.
*   The existing `style.css` will be extended to style the new booking interface, ensuring a consistent look and feel.
*   A new JavaScript file (`booking.js`) will be created to handle the logic for the booking process, including:
    *   Fetching doctor and availability data.
    *   Dynamically rendering the doctor list and calendar.
    *   Handling user interactions (filtering, selecting dates/times).
    *   Submitting the booking form.

### 5.2. Backend (Simulated)

Since there is no real backend, the `app.js` file will be modified to simulate the backend functionality:

*   **Doctor Availability:** A new data structure will be added to `appData` to represent each doctor's availability for online booking (e.g., which days of the week and times they are available).
*   **Appointment Creation:** A new function will be added to `app.js` to handle the creation of new appointments from the patient booking form. This function will add the new appointment to the `appData.appointments` array.
*   **Data Persistence:** To simulate data persistence between sessions, the updated `appData` can be saved to the browser's `localStorage`.

### 5.3. Data Model Extensions

The following additions will be made to the `appData` object in `app.js`:

*   **In the `doctors` object:** A new property `availableForBooking: true/false` will be added to each doctor.
*   **A new object `doctorAvailability`:** This will store the weekly availability for each doctor who can be booked online.
    ```javascript
    "doctorAvailability": {
      "DR001": {
        "days": [1, 2, 3, 4, 5], // Monday to Friday
        "startTime": "09:00",
        "endTime": "17:00",
        "appointmentDuration": 30 // in minutes
      },
      // ... other doctors
    }
    ```

## 6. Success Metrics

*   **Number of appointments booked** through the new patient-facing system per week.
*   **Reduction in phone calls** for appointment booking.
*   **Patient satisfaction score** for the online booking experience (can be measured with a simple survey after booking).
*   **No-show rate** for appointments booked online compared to those booked through traditional channels.

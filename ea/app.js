// Hospital Management System Data
const appData = {
  "hospital": {
    "name": "City General Hospital",
    "address": "123 Medical Center Drive, City, ST 12345",
    "phone": "(555) 123-4567",
    "totalBeds": 450,
    "currentOccupancy": 387
  },
  "currentUser": {
    "id": "admin001",
    "name": "Hospital Administrator",
    "role": "admin",
    "department": "Administration",
    "permissions": ["view_all", "schedule_all", "analytics_all"]
  },
  "currentDate": "2025-09-11",
  "currentTime": "10:29",
  "currentView": "hospital",
  "selectedDepartment": "all",
  "selectedDoctor": "all",
  "departments": {
    "cardiology": {
      "id": "cardiology",
      "name": "Cardiology",
      "head": "DR001",
      "location": "Wing A, Floor 3",
      "totalStaff": 12,
      "activeStaff": 8,
      "rooms": ["304A", "304B", "305A", "305B", "Cath Lab 1", "Cath Lab 2"],
      "equipment": ["ECG Machine", "Echocardiogram", "Stress Test Equipment"]
    },
    "emergency": {
      "id": "emergency",
      "name": "Emergency Department",
      "head": "DR005",
      "location": "Ground Floor, East Wing",
      "totalStaff": 15,
      "activeStaff": 12,
      "rooms": ["ER1", "ER2", "ER3", "ER4", "Trauma 1", "Trauma 2"],
      "equipment": ["Defibrillator", "Ventilator", "X-Ray Portable"]
    },
    "surgery": {
      "id": "surgery",
      "name": "Surgery",
      "head": "DR003",
      "location": "Wing B, Floor 4",
      "totalStaff": 20,
      "activeStaff": 16,
      "rooms": ["OR1", "OR2", "OR3", "OR4", "OR5", "Pre-Op 1", "Pre-Op 2"],
      "equipment": ["Surgical Robot", "Anesthesia Machine", "Surgical Lights"]
    },
    "internal_medicine": {
      "id": "internal_medicine",
      "name": "Internal Medicine",
      "head": "DR007",
      "location": "Wing C, Floor 2",
      "totalStaff": 10,
      "activeStaff": 8,
      "rooms": ["201A", "201B", "202A", "202B", "203A", "203B"],
      "equipment": ["Examination Tables", "Blood Pressure Monitors"]
    },
    "pediatrics": {
      "id": "pediatrics",
      "name": "Pediatrics",
      "head": "DR008",
      "location": "Wing D, Floor 2",
      "totalStaff": 8,
      "activeStaff": 6,
      "rooms": ["PED1", "PED2", "PED3", "PED4", "NICU"],
      "equipment": ["Pediatric Monitors", "Incubators"]
    }
  },
  "doctors": {
    "DR001": {
      "id": "DR001",
      "name": "Dr. Michael Rodriguez",
      "title": "Chief of Cardiology",
      "department": "cardiology",
      "email": "m.rodriguez@cityhospital.com",
      "licenseNumber": "MD-2019-8847",
      "specialization": "Interventional Cardiology",
      "phone": "(555) 123-4501",
      "yearsExperience": 12,
      "status": "active",
      "schedule": "full_time"
    },
    "DR002": {
      "id": "DR002",
      "name": "Dr. Sarah Chen",
      "title": "Cardiologist",
      "department": "cardiology",
      "email": "s.chen@cityhospital.com",
      "licenseNumber": "MD-2020-9234",
      "specialization": "Electrophysiology",
      "phone": "(555) 123-4502",
      "yearsExperience": 8,
      "status": "active",
      "schedule": "full_time"
    },
    "DR003": {
      "id": "DR003",
      "name": "Dr. James Wilson",
      "title": "Chief of Surgery",
      "department": "surgery",
      "email": "j.wilson@cityhospital.com",
      "licenseNumber": "MD-2015-7643",
      "specialization": "General Surgery",
      "phone": "(555) 123-4503",
      "yearsExperience": 15,
      "status": "active",
      "schedule": "full_time"
    },
    "DR004": {
      "id": "DR004",
      "name": "Dr. Emily Davis",
      "title": "Surgeon",
      "department": "surgery",
      "email": "e.davis@cityhospital.com",
      "licenseNumber": "MD-2018-5432",
      "specialization": "Orthopedic Surgery",
      "phone": "(555) 123-4504",
      "yearsExperience": 10,
      "status": "active",
      "schedule": "full_time"
    },
    "DR005": {
      "id": "DR005",
      "name": "Dr. Robert Kim",
      "title": "Emergency Medicine Director",
      "department": "emergency",
      "email": "r.kim@cityhospital.com",
      "licenseNumber": "MD-2017-8765",
      "specialization": "Emergency Medicine",
      "phone": "(555) 123-4505",
      "yearsExperience": 11,
      "status": "active",
      "schedule": "full_time"
    },
    "DR006": {
      "id": "DR006",
      "name": "Dr. Lisa Thompson",
      "title": "Emergency Physician",
      "department": "emergency",
      "email": "l.thompson@cityhospital.com",
      "licenseNumber": "MD-2019-3456",
      "specialization": "Emergency Medicine",
      "phone": "(555) 123-4506",
      "yearsExperience": 7,
      "status": "active",
      "schedule": "full_time"
    },
    "DR007": {
      "id": "DR007",
      "name": "Dr. David Park",
      "title": "Internal Medicine Chief",
      "department": "internal_medicine",
      "email": "d.park@cityhospital.com",
      "licenseNumber": "MD-2016-7890",
      "specialization": "Internal Medicine",
      "phone": "(555) 123-4507",
      "yearsExperience": 13,
      "status": "active",
      "schedule": "full_time"
    },
    "DR008": {
      "id": "DR008",
      "name": "Dr. Amanda Martinez",
      "title": "Pediatrics Chief",
      "department": "pediatrics",
      "email": "a.martinez@cityhospital.com",
      "licenseNumber": "MD-2018-4567",
      "specialization": "Pediatric Medicine",
      "phone": "(555) 123-4508",
      "yearsExperience": 9,
      "status": "active",
      "schedule": "full_time"
    }
  },
  "resources": {
    "rooms": {
      "304A": { "id": "304A", "department": "cardiology", "type": "examination", "capacity": 4, "equipment": ["ECG"], "status": "available" },
      "304B": { "id": "304B", "department": "cardiology", "type": "examination", "capacity": 4, "equipment": ["ECG"], "status": "occupied" },
      "Cath Lab 1": { "id": "Cath Lab 1", "department": "cardiology", "type": "procedure", "capacity": 8, "equipment": ["Catheterization"], "status": "available" },
      "Cath Lab 2": { "id": "Cath Lab 2", "department": "cardiology", "type": "procedure", "capacity": 8, "equipment": ["Catheterization"], "status": "maintenance" },
      "OR1": { "id": "OR1", "department": "surgery", "type": "surgery", "capacity": 12, "equipment": ["Surgical Robot"], "status": "occupied" },
      "OR2": { "id": "OR2", "department": "surgery", "type": "surgery", "capacity": 12, "equipment": ["Standard Surgical"], "status": "available" },
      "ER1": { "id": "ER1", "department": "emergency", "type": "emergency", "capacity": 6, "equipment": ["Monitor"], "status": "occupied" },
      "ER2": { "id": "ER2", "department": "emergency", "type": "emergency", "capacity": 6, "equipment": ["Monitor"], "status": "available" }
    },
    "equipment": {
      "ECG_001": { "id": "ECG_001", "name": "ECG Machine", "department": "cardiology", "status": "available", "location": "304A" },
      "ECHO_001": { "id": "ECHO_001", "name": "Echocardiogram", "department": "cardiology", "status": "in_use", "location": "304B" },
      "ROBOT_001": { "id": "ROBOT_001", "name": "Da Vinci Surgical Robot", "department": "surgery", "status": "in_use", "location": "OR1" }
    }
  },
  "appointments": [
    {
      "id": 1,
      "title": "Patient Consultation - John Martinez",
      "date": "2025-09-11",
      "startTime": "09:00",
      "endTime": "09:30",
      "type": "patient_care",
      "doctorId": "DR001",
      "patientId": "P-2025-0234",
      "attendees": ["John Martinez", "Nurse Sarah Kim"],
      "location": "304A",
      "department": "cardiology",
      "status": "confirmed",
      "priority": "routine",
      "recurring": false,
      "diagnosis": "Chest pain evaluation",
      "visitType": "follow-up",
      "resources": ["ECG_001"]
    },
    {
      "id": 2,
      "title": "Cardiac Catheterization - Maria Garcia",
      "date": "2025-09-11",
      "startTime": "11:00",
      "endTime": "12:30",
      "type": "procedure",
      "doctorId": "DR001",
      "patientId": "P-2025-0189",
      "attendees": ["Maria Garcia", "Cath Lab Team", "Anesthesiologist Dr. Wong"],
      "location": "Cath Lab 2",
      "department": "cardiology",
      "status": "confirmed",
      "priority": "high",
      "recurring": false,
      "diagnosis": "Coronary artery disease",
      "visitType": "procedure",
      "resources": []
    },
    {
      "id": 3,
      "title": "Lunch Break",
      "date": "2025-09-11",
      "startTime": "13:00",
      "endTime": "14:00",
      "type": "break",
      "doctorId": "DR001",
      "attendees": [],
      "location": "Hospital Cafeteria",
      "department": "personal",
      "status": "confirmed",
      "priority": "routine",
      "recurring": true,
      "diagnosis": "",
      "visitType": "break",
      "resources": []
    },
    {
      "id": 4,
      "title": "Cardiology Department Meeting",
      "date": "2025-09-11",
      "startTime": "14:30",
      "endTime": "15:30",
      "type": "administrative",
      "doctorId": "DR001",
      "attendees": ["Dr. Jennifer Park", "Dr. Robert Kim", "Nurse Manager Lisa Chen"],
      "location": "Conference Room B",
      "department": "cardiology",
      "status": "confirmed",
      "priority": "routine",
      "recurring": true,
      "diagnosis": "",
      "visitType": "meeting",
      "resources": []
    },
    {
      "id": 5,
      "title": "Emergency Consult - David Thompson",
      "date": "2025-09-11",
      "startTime": "16:00",
      "endTime": "16:45",
      "type": "emergency",
      "doctorId": "DR001",
      "patientId": "P-2025-0298",
      "attendees": ["David Thompson", "ER Team"],
      "location": "ER1",
      "department": "emergency",
      "status": "confirmed",
      "priority": "urgent",
      "recurring": false,
      "diagnosis": "Acute chest pain",
      "visitType": "emergency",
      "resources": []
    },
    {
      "id": 6,
      "title": "Appendectomy - Sarah Johnson",
      "date": "2025-09-11",
      "startTime": "08:00",
      "endTime": "10:00",
      "type": "procedure",
      "doctorId": "DR003",
      "patientId": "P-2025-0301",
      "attendees": ["Sarah Johnson", "OR Team", "Anesthesiologist Dr. Brown"],
      "location": "OR1",
      "department": "surgery",
      "status": "in_progress",
      "priority": "high",
      "recurring": false,
      "diagnosis": "Acute appendicitis",
      "visitType": "surgery",
      "resources": ["ROBOT_001"]
    },
    {
      "id": 7,
      "title": "Pediatric Checkup - Tommy Wilson",
      "date": "2025-09-11",
      "startTime": "10:00",
      "endTime": "10:30",
      "type": "patient_care",
      "doctorId": "DR008",
      "patientId": "P-2025-0302",
      "attendees": ["Tommy Wilson", "Mrs. Wilson", "Pediatric Nurse"],
      "location": "PED1",
      "department": "pediatrics",
      "status": "confirmed",
      "priority": "routine",
      "recurring": false,
      "diagnosis": "Annual checkup",
      "visitType": "checkup",
      "resources": []
    },
    {
      "id": 8,
      "title": "Trauma Case - John Doe",
      "date": "2025-09-11",
      "startTime": "14:15",
      "endTime": "15:45",
      "type": "emergency",
      "doctorId": "DR005",
      "patientId": "P-2025-0303",
      "attendees": ["John Doe", "Trauma Team"],
      "location": "ER1",
      "department": "emergency",
      "status": "confirmed",
      "priority": "critical",
      "recurring": false,
      "diagnosis": "Motor vehicle accident",
      "visitType": "trauma",
      "resources": []
    }
  ],
  "hospitalAnalytics": {
    "overview": {
      "totalAppointments": 247,
      "todayAppointments": 32,
      "activeDoctors": 8,
      "occupancyRate": 86,
      "avgWaitTime": 12,
      "patientSatisfaction": 4.6
    },
    "departmentMetrics": {
      "cardiology": {
        "appointments": 47,
        "utilization": 85,
        "avgWaitTime": 8,
        "patientSatisfaction": 4.7
      },
      "emergency": {
        "appointments": 89,
        "utilization": 92,
        "avgWaitTime": 5,
        "patientSatisfaction": 4.4
      },
      "surgery": {
        "appointments": 34,
        "utilization": 78,
        "avgWaitTime": 15,
        "patientSatisfaction": 4.8
      },
      "internal_medicine": {
        "appointments": 56,
        "utilization": 88,
        "avgWaitTime": 10,
        "patientSatisfaction": 4.5
      },
      "pediatrics": {
        "appointments": 21,
        "utilization": 72,
        "avgWaitTime": 7,
        "patientSatisfaction": 4.9
      }
    },
    "appointmentsByType": {
      "patient_care": 156,
      "procedure": 42,
      "emergency": 28,
      "administrative": 15,
      "break": 6
    },
    "resourceUtilization": {
      "rooms": {
        "total": 25,
        "occupied": 18,
        "utilization": 72
      },
      "equipment": {
        "total": 45,
        "in_use": 32,
        "utilization": 71
      }
    },
    "staffMetrics": {
      "totalStaff": 65,
      "activeStaff": 50,
      "utilizationRate": 77,
      "overtimeHours": 45
    },
    "financialMetrics": {
      "dailyRevenue": 125000,
      "weeklyRevenue": 875000,
      "avgCostPerPatient": 3200
    },
    "qualityMetrics": {
      "patient_satisfaction": 4.6,
      "readmission_rate": 2.3,
      "procedure_success_rate": 96.8,
      "infection_rate": 1.2,
      "mortality_rate": 0.8
    },
    "trends": {
      "appointments": "+12%",
      "patient_satisfaction": "+0.2",
      "wait_times": "-8%",
      "revenue": "+15%"
    }
  },
  "upcomingAppointments": [
    {
      "title": "Cardiac Surgery - Jennifer Liu",
      "date": "2025-09-12",
      "time": "08:00",
      "type": "procedure",
      "priority": "high"
    },
    {
      "title": "Medical Conference - Heart Disease Prevention",
      "date": "2025-09-13",
      "time": "14:00",
      "type": "education"
    },
    {
      "title": "Clinic Hours - Outpatient Cardiology",
      "date": "2025-09-15",
      "time": "09:00",
      "type": "patient_care"
    }
  ]
};

// Global variables
let currentFilter = 'all';
let currentDepartmentFilter = 'all';
let currentDoctorFilter = 'all';
let currentView = 'hospital';
let charts = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

function initializeApp() {
  setupEventListeners();
  renderAppointments();
  setupCharts();
  updateCurrentTime();
  showCurrentTimeLine();
  populatePriorityAlerts();
  populateResourceManagement();
  populateDepartmentOverview();
  updateHospitalStats();
  
  // Update time every minute
  setInterval(() => {
    updateCurrentTime();
    showCurrentTimeLine();
    updateHospitalStats();
  }, 60000);
}

function setupEventListeners() {
  // View switching
  document.querySelectorAll('[data-view]').forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const view = e.target.getAttribute('data-view');
      switchView(view);
    });
  });
  
  // Department filters
  document.querySelectorAll('[data-department]').forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const department = e.target.getAttribute('data-department');
      setDepartmentFilter(department);
    });
  });
  
  // Doctor selector
  const doctorSelector = document.getElementById('doctorSelector');
  if (doctorSelector) {
    doctorSelector.addEventListener('change', (e) => {
      currentDoctorFilter = e.target.value;
      renderAppointments();
    });
  }
  
  // Department selector in header
  const departmentSelector = document.getElementById('departmentSelector');
  if (departmentSelector) {
    departmentSelector.addEventListener('change', (e) => {
      setDepartmentFilter(e.target.value);
    });
  }
  
  // View selector in header
  const viewSelector = document.getElementById('viewSelector');
  if (viewSelector) {
    viewSelector.addEventListener('change', (e) => {
      currentView = e.target.value;
      updateScheduleView();
    });
  }
  
  // Filter buttons
  document.querySelectorAll('[data-filter]').forEach(button => {
    button.addEventListener('click', (e) => {
      e.preventDefault();
      const filter = e.target.getAttribute('data-filter');
      setFilter(filter);
    });
  });
  
  // Quick Add Modal
  const quickAddBtn = document.getElementById('quickAddBtn');
  if (quickAddBtn) {
    quickAddBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openQuickAddModal();
    });
  }
  
  // Quick Add Modal Close buttons
  const quickAddClose = document.getElementById('quickAddClose');
  if (quickAddClose) {
    quickAddClose.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal('quickAddModal');
    });
  }
  
  const quickAddCancel = document.getElementById('quickAddCancel');
  if (quickAddCancel) {
    quickAddCancel.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal('quickAddModal');
    });
  }
  
  const quickAddSave = document.getElementById('quickAddSave');
  if (quickAddSave) {
    quickAddSave.addEventListener('click', (e) => {
      e.preventDefault();
      handleQuickAdd();
    });
  }
  
  // Appointment Modal Close buttons
  const modalClose = document.getElementById('modalClose');
  if (modalClose) {
    modalClose.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal('appointmentModal');
    });
  }
  
  const modalClose2 = document.getElementById('modalClose2');
  if (modalClose2) {
    modalClose2.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal('appointmentModal');
    });
  }
  
  // Modal backdrop clicks
  document.querySelectorAll('.modal__backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      const modal = e.target.closest('.modal');
      if (modal) {
        modal.classList.add('hidden');
      }
    });
  });
}

function switchView(viewName) {
  console.log('Switching to view:', viewName);
  
  // Update navigation
  document.querySelectorAll('[data-view]').forEach(button => {
    const navItem = button.closest('.nav__item');
    if (navItem) {
      navItem.classList.remove('nav__item--active');
      if (button.getAttribute('data-view') === viewName) {
        navItem.classList.add('nav__item--active');
      }
    }
  });
  
  // Switch views
  document.querySelectorAll('.view').forEach(view => {
    view.classList.remove('view--active');
  });
  
  const viewMap = {
    'daily': 'dailyView',
    'analytics': 'analyticsView',
    'resources': 'resourcesView',
    'departments': 'departmentsView'
  };
  
  const targetView = viewMap[viewName] || 'dailyView';
  const targetElement = document.getElementById(targetView);
  if (targetElement) {
    targetElement.classList.add('view--active');
  }
  
  // Initialize view-specific content
  if (viewName === 'analytics') {
    setTimeout(() => {
      setupCharts();
    }, 100);
  } else if (viewName === 'resources') {
    populateResourceManagement();
  } else if (viewName === 'departments') {
    populateDepartmentOverview();
  }
}

function setFilter(filter) {
  console.log('Setting filter:', filter);
  currentFilter = filter;
  
  // Update filter buttons
  document.querySelectorAll('[data-filter]').forEach(button => {
    button.classList.remove('filter-btn--active');
    if (button.getAttribute('data-filter') === filter) {
      button.classList.add('filter-btn--active');
    }
  });
  
  // Re-render appointments with filter
  renderAppointments();
}

function setDepartmentFilter(department) {
  console.log('Setting department filter:', department);
  currentDepartmentFilter = department;
  
  // Update department filter buttons
  document.querySelectorAll('[data-department]').forEach(button => {
    button.classList.remove('filter-btn--active');
    if (button.getAttribute('data-department') === department) {
      button.classList.add('filter-btn--active');
    }
  });
  
  // Update header selector
  const departmentSelector = document.getElementById('departmentSelector');
  if (departmentSelector) {
    departmentSelector.value = department;
  }
  
  // Re-render appointments with filter
  renderAppointments();
}

function renderAppointments() {
  console.log('Rendering appointments with filters:', {currentFilter, currentDepartmentFilter, currentDoctorFilter});
  const container = document.getElementById('meetingsContainer');
  if (!container) {
    console.error('Meetings container not found');
    return;
  }
  
  container.innerHTML = '';
  
  // Filter appointments
  const filteredAppointments = appData.appointments.filter(appointment => {
    const typeMatch = currentFilter === 'all' || appointment.type === currentFilter;
    const departmentMatch = currentDepartmentFilter === 'all' || appointment.department === currentDepartmentFilter;
    const doctorMatch = currentDoctorFilter === 'all' || appointment.doctorId === currentDoctorFilter;
    
    return typeMatch && departmentMatch && doctorMatch;
  });
  
  console.log('Filtered appointments:', filteredAppointments.length);
  
  filteredAppointments.forEach(appointment => {
    const appointmentElement = createAppointmentElement(appointment);
    container.appendChild(appointmentElement);
  });
}

function createAppointmentElement(appointment) {
  const element = document.createElement('div');
  element.className = `appointment appointment--${appointment.type}`;
  element.dataset.appointmentId = appointment.id;
  
  // Calculate position and height
  const position = calculateAppointmentPosition(appointment);
  element.style.top = `${position.top}%`;
  element.style.height = `${position.height}%`;
  
  const priorityBadge = appointment.priority === 'urgent' ? '<span class="priority-badge priority-urgent">URGENT</span>' : 
                       appointment.priority === 'critical' ? '<span class="priority-badge priority-urgent">CRITICAL</span>' : 
                       appointment.priority === 'high' ? '<span class="priority-badge priority-high">HIGH</span>' : '';
  
  // Get doctor name
  const doctor = appData.doctors[appointment.doctorId];
  const doctorName = doctor ? doctor.name : 'Unknown Doctor';
  
  element.innerHTML = `
    <div class="appointment__title">${appointment.title} ${priorityBadge}</div>
    <div class="appointment__time">${formatTime(appointment.startTime)} - ${formatTime(appointment.endTime)}</div>
    <div class="appointment__location">${appointment.location}</div>
    <div class="appointment__doctor">${doctorName}</div>
  `;
  
  // Add click handler
  element.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    console.log('Appointment clicked:', appointment.title);
    openAppointmentModal(appointment);
  });
  
  // Make draggable
  element.draggable = true;
  
  return element;
}

function calculateAppointmentPosition(appointment) {
  const startHour = parseTime(appointment.startTime);
  const endHour = parseTime(appointment.endTime);
  const dayStart = 8; // 8 AM
  const dayEnd = 18; // 6 PM
  const totalHours = dayEnd - dayStart;
  
  const top = ((startHour - dayStart) / totalHours) * 100;
  const height = ((endHour - startHour) / totalHours) * 100;
  
  return { top: Math.max(0, top), height: Math.max(5, height) };
}

function parseTime(timeString) {
  const [hours, minutes] = timeString.split(':').map(Number);
  return hours + minutes / 60;
}

function formatTime(timeString) {
  const [hours, minutes] = timeString.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours > 12 ? hours - 12 : hours === 0 ? 12 : hours;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
}

function openAppointmentModal(appointment) {
  console.log('Opening appointment modal for:', appointment.title);
  const modal = document.getElementById('appointmentModal');
  if (!modal) {
    console.error('Appointment modal not found');
    return;
  }
  
  // Get doctor name
  const doctor = appData.doctors[appointment.doctorId];
  const doctorName = doctor ? doctor.name : 'Unknown Doctor';
  
  // Update modal content
  const titleElement = document.getElementById('modalTitle');
  const timeElement = document.getElementById('modalTime');
  const locationElement = document.getElementById('modalLocation');
  const attendeesElement = document.getElementById('modalAttendees');
  const typeElement = document.getElementById('modalType');
  const departmentElement = document.getElementById('modalDepartment');
  const doctorElement = document.getElementById('modalDoctor');
  const patientIdElement = document.getElementById('modalPatientId');
  const diagnosisElement = document.getElementById('modalDiagnosis');
  const priorityElement = document.getElementById('modalPriority');
  const resourcesElement = document.getElementById('modalResources');
  
  if (titleElement) titleElement.textContent = appointment.title;
  if (timeElement) timeElement.textContent = `${formatTime(appointment.startTime)} - ${formatTime(appointment.endTime)}`;
  if (locationElement) locationElement.textContent = appointment.location;
  if (attendeesElement) attendeesElement.textContent = appointment.attendees.join(', ');
  if (typeElement) typeElement.textContent = appointment.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  if (departmentElement) departmentElement.textContent = appData.departments[appointment.department]?.name || appointment.department;
  if (doctorElement) doctorElement.textContent = doctorName;
  if (patientIdElement && appointment.patientId) patientIdElement.textContent = appointment.patientId;
  if (diagnosisElement && appointment.diagnosis) diagnosisElement.textContent = appointment.diagnosis;
  if (priorityElement && appointment.priority) priorityElement.textContent = appointment.priority.toUpperCase();
  if (resourcesElement) resourcesElement.textContent = appointment.resources?.join(', ') || 'None';
  
  modal.classList.remove('hidden');
}

function openQuickAddModal() {
  console.log('Opening quick add modal');
  const modal = document.getElementById('quickAddModal');
  if (modal) {
    modal.classList.remove('hidden');
  } else {
    console.error('Quick add modal not found');
  }
}

function closeModal(modalId) {
  console.log('Closing modal:', modalId);
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('hidden');
  }
}

function handleQuickAdd() {
  // Get form values
  const form = document.querySelector('.quick-add-form');
  if (form) {
    const formData = new FormData(form);
    console.log('Adding new appointment with form data');
    // In a real app, this would save the appointment
    alert('Appointment would be added in a real application');
  }
  closeModal('quickAddModal');
}

function updateCurrentTime() {
  const now = new Date();
  const timeString = now.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
  
  const timeElement = document.getElementById('currentTime');
  if (timeElement) {
    timeElement.textContent = timeString;
  }
}

function showCurrentTimeLine() {
  const now = new Date();
  const currentHour = now.getHours() + now.getMinutes() / 60;
  const dayStart = 8;
  const dayEnd = 18;
  
  // Only show line during business hours
  if (currentHour >= dayStart && currentHour <= dayEnd) {
    const totalHours = dayEnd - dayStart;
    const position = ((currentHour - dayStart) / totalHours) * 100;
    
    // Remove existing line
    const existingLine = document.querySelector('.current-time-line');
    if (existingLine) {
      existingLine.remove();
    }
    
    // Add new line
    const line = document.createElement('div');
    line.className = 'current-time-line';
    line.style.top = `${position}%`;
    
    const timelineContent = document.querySelector('.timeline__content');
    if (timelineContent) {
      timelineContent.appendChild(line);
    }
  }
}

function setupCharts() {
  // Wait for the elements to be visible
  setTimeout(() => {
    setupAppointmentTypeChart();
    setupDepartmentChart();
    setupResourceChart();
  }, 50);
}

function setupAppointmentTypeChart() {
  const ctx = document.getElementById('appointmentTypeChart');
  if (!ctx) {
    console.log('Appointment type chart canvas not found');
    return;
  }
  
  // Destroy existing chart if it exists
  if (charts.appointmentType) {
    charts.appointmentType.destroy();
  }
  
  const data = appData.hospitalAnalytics.appointmentsByType;
  
  try {
    charts.appointmentType = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Patient Care', 'Procedures', 'Emergency', 'Administrative', 'Break'],
        datasets: [{
          data: [data.patient_care, data.procedure, data.emergency, data.administrative, data.break],
          backgroundColor: ['#4CAF50', '#2196F3', '#F44336', '#FF9800', '#9E9E9E'],
          borderWidth: 0,
          cutout: '60%'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 15,
              font: {
                size: 11
              }
            }
          }
        }
      }
    });
    console.log('Appointment type chart created successfully');
  } catch (error) {
    console.error('Error creating appointment type chart:', error);
  }
}

function setupDepartmentChart() {
  const ctx = document.getElementById('departmentChart');
  if (!ctx) {
    console.log('Department chart canvas not found');
    return;
  }
  
  // Destroy existing chart if it exists
  if (charts.department) {
    charts.department.destroy();
  }
  
  const data = appData.hospitalAnalytics.departmentMetrics;
  
  try {
    charts.department = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Cardiology', 'Emergency', 'Surgery', 'Internal Med', 'Pediatrics'],
        datasets: [{
          label: 'Appointments',
          data: [data.cardiology.appointments, data.emergency.appointments, data.surgery.appointments, data.internal_medicine.appointments, data.pediatrics.appointments],
          backgroundColor: ['#4CAF50', '#F44336', '#2196F3', '#FF9800', '#9C27B0'],
          borderWidth: 0,
          borderRadius: 4,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.1)'
            }
          },
          x: {
            grid: {
              display: false
            },
            ticks: {
              maxRotation: 45,
              font: {
                size: 10
              }
            }
          }
        }
      }
    });
    console.log('Department chart created successfully');
  } catch (error) {
    console.error('Error creating department chart:', error);
  }
}

function setupResourceChart() {
  const ctx = document.getElementById('resourceChart');
  if (!ctx) {
    console.log('Resource chart canvas not found');
    return;
  }
  
  // Destroy existing chart if it exists
  if (charts.resource) {
    charts.resource.destroy();
  }
  
  const roomUtilization = appData.hospitalAnalytics.resourceUtilization.rooms.utilization;
  const equipUtilization = appData.hospitalAnalytics.resourceUtilization.equipment.utilization;
  const staffUtilization = appData.hospitalAnalytics.staffMetrics.utilizationRate;
  
  try {
    charts.resource = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Rooms', 'Equipment', 'Staff'],
        datasets: [{
          data: [roomUtilization, equipUtilization, staffUtilization],
          backgroundColor: ['#4CAF50', '#2196F3', '#FF9800'],
          borderWidth: 0,
          cutout: '60%'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 15,
              font: {
                size: 11
              },
              generateLabels: function(chart) {
                const data = chart.data;
                return data.labels.map((label, i) => {
                  return {
                    text: `${label} (${data.datasets[0].data[i]}%)`,
                    fillStyle: data.datasets[0].backgroundColor[i],
                    pointStyle: 'circle'
                  };
                });
              }
            }
          }
        }
      }
    });
    console.log('Resource chart created successfully');
  } catch (error) {
    console.error('Error creating resource chart:', error);
  }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
  // Escape key closes modals
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal:not(.hidden)').forEach(modal => {
      modal.classList.add('hidden');
    });
  }
  
  // Ctrl/Cmd + A for quick add
  if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
    e.preventDefault();
    openQuickAddModal();
  }
  
  // Number keys for view switching
  if (e.key === '1') {
    switchView('daily');
  } else if (e.key === '2') {
    switchView('weekly');
  }
});

// Drag and drop functionality (simplified)
let draggedElement = null;

document.addEventListener('dragstart', function(e) {
  if (e.target.classList.contains('appointment')) {
    draggedElement = e.target;
    e.target.style.opacity = '0.5';
  }
});

document.addEventListener('dragend', function(e) {
  if (e.target.classList.contains('appointment')) {
    e.target.style.opacity = '';
    draggedElement = null;
  }
});

document.addEventListener('dragover', function(e) {
  e.preventDefault();
});

document.addEventListener('drop', function(e) {
  e.preventDefault();
  if (draggedElement && e.target.closest('.timeline__content')) {
    // In a real app, this would update the appointment time
    console.log('Appointment would be rescheduled');
  }
});

// Search functionality (placeholder)
function searchAppointments(query) {
  // In a real app, this would filter appointments by search query
  console.log('Searching for:', query);
}

// Export functionality (placeholder)
function exportCalendar() {
  // In a real app, this would export the calendar
  alert('Calendar would be exported in a real application');
}

// Notification system (placeholder)
function showNotification(message, type = 'info') {
  // In a real app, this would show a toast notification
  console.log(`${type.toUpperCase()}: ${message}`);
}

// Conflict detection
function detectConflicts(newAppointment) {
  const conflicts = [];
  const newStart = parseTime(newAppointment.startTime);
  const newEnd = parseTime(newAppointment.endTime);
  
  appData.appointments.forEach(appointment => {
    if (appointment.id === newAppointment.id) return;
    
    const existingStart = parseTime(appointment.startTime);
    const existingEnd = parseTime(appointment.endTime);
    
    if ((newStart >= existingStart && newStart < existingEnd) ||
        (newEnd > existingStart && newEnd <= existingEnd) ||
        (newStart <= existingStart && newEnd >= existingEnd)) {
      conflicts.push(appointment);
    }
  });
  
  return conflicts;
}

// Smart scheduling suggestions
function suggestBestTime(duration = 60) {
  const suggestions = [];
  const dayStart = 8;
  const dayEnd = 18;
  
  for (let hour = dayStart; hour < dayEnd; hour += 0.5) {
    const endHour = hour + (duration / 60);
    if (endHour > dayEnd) break;
    
    const hasConflict = appData.appointments.some(appointment => {
      const appointmentStart = parseTime(appointment.startTime);
      const appointmentEnd = parseTime(appointment.endTime);
      return (hour >= appointmentStart && hour < appointmentEnd) ||
             (endHour > appointmentStart && endHour <= appointmentEnd);
    });
    
    if (!hasConflict) {
      const timeString = formatTimeFromHour(hour);
      suggestions.push({
        time: timeString,
        duration: duration,
        quality: calculateTimeQuality(hour)
      });
    }
  }
  
  return suggestions.sort((a, b) => b.quality - a.quality).slice(0, 3);
}

function formatTimeFromHour(hour) {
  const hours = Math.floor(hour);
  const minutes = (hour - hours) * 60;
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
}

function calculateTimeQuality(hour) {
  // Prefer mid-morning and mid-afternoon slots
  if (hour >= 9 && hour <= 11) return 10; // High quality
  if (hour >= 14 && hour <= 16) return 8; // Good quality
  if (hour >= 8 && hour <= 9) return 6; // Okay quality
  if (hour >= 16 && hour <= 17) return 5; // Lower quality
  return 3; // Lowest quality
}

// Hospital Management Functions

function updateHospitalStats() {
  const stats = appData.hospitalAnalytics.overview;
  const hospitalStats = document.getElementById('hospitalStats');
  if (hospitalStats) {
    hospitalStats.textContent = `${appData.hospital.totalBeds} Beds • ${appData.hospital.currentOccupancy} Occupied • ${stats.occupancyRate}% Capacity`;
  }
}

function updateScheduleView() {
  const scheduleTitle = document.getElementById('scheduleTitle');
  if (!scheduleTitle) return;
  
  switch(currentView) {
    case 'hospital':
      scheduleTitle.textContent = "Today's Hospital Schedule";
      break;
    case 'department':
      const departmentName = appData.departments[currentDepartmentFilter]?.name || 'Department';
      scheduleTitle.textContent = `${departmentName} Schedule`;
      break;
    case 'doctor':
      const doctorName = appData.doctors[currentDoctorFilter]?.name || 'Doctor';
      scheduleTitle.textContent = `${doctorName}'s Schedule`;
      break;
  }
}

function populatePriorityAlerts() {
  const alertsContainer = document.getElementById('priorityAlerts');
  if (!alertsContainer) return;

  const urgentAppointments = appData.appointments.filter(apt => 
    apt.priority === 'urgent' || apt.priority === 'critical'
  );

  alertsContainer.innerHTML = '';
  
  urgentAppointments.forEach(appointment => {
    const doctor = appData.doctors[appointment.doctorId];
    const eventElement = document.createElement('div');
    eventElement.className = 'event';
    eventElement.innerHTML = `
      <div class="event__date">${formatTime(appointment.startTime)} - ${appointment.location}</div>
      <div class="event__title">${appointment.title}</div>
      <div class="event__type event__type--${appointment.type}">${appointment.type.replace('_', ' ')}</div>
      <div class="event__priority event__priority--${appointment.priority}">${appointment.priority.toUpperCase()}</div>
      <div class="event__doctor">${doctor?.name || 'Unknown'}</div>
    `;
    alertsContainer.appendChild(eventElement);
  });

  if (urgentAppointments.length === 0) {
    alertsContainer.innerHTML = '<div class="event"><div class="event__title">No urgent alerts</div></div>';
  }
}

function populateResourceManagement() {
  populateRoomsList();
  populateEquipmentList();
  populateStaffOverview();
}

function populateRoomsList() {
  const roomsList = document.getElementById('roomsList');
  if (!roomsList) return;

  roomsList.innerHTML = '';
  
  Object.values(appData.resources.rooms).forEach(room => {
    const roomElement = document.createElement('div');
    roomElement.className = 'resource-item';
    
    const statusClass = room.status === 'available' ? 'status--success' : 
                       room.status === 'occupied' ? 'status--warning' : 'status--error';
    
    roomElement.innerHTML = `
      <div class="resource-item__header">
        <span class="resource-item__name">${room.id}</span>
        <span class="status ${statusClass}">${room.status}</span>
      </div>
      <div class="resource-item__details">
        <div>Department: ${appData.departments[room.department]?.name || room.department}</div>
        <div>Type: ${room.type}</div>
        <div>Capacity: ${room.capacity} people</div>
        <div>Equipment: ${room.equipment.join(', ')}</div>
      </div>
    `;
    roomsList.appendChild(roomElement);
  });
}

function populateEquipmentList() {
  const equipmentList = document.getElementById('equipmentList');
  if (!equipmentList) return;

  equipmentList.innerHTML = '';
  
  Object.values(appData.resources.equipment).forEach(equipment => {
    const equipmentElement = document.createElement('div');
    equipmentElement.className = 'resource-item';
    
    const statusClass = equipment.status === 'available' ? 'status--success' : 
                       equipment.status === 'in_use' ? 'status--warning' : 'status--error';
    
    equipmentElement.innerHTML = `
      <div class="resource-item__header">
        <span class="resource-item__name">${equipment.name}</span>
        <span class="status ${statusClass}">${equipment.status.replace('_', ' ')}</span>
      </div>
      <div class="resource-item__details">
        <div>Department: ${appData.departments[equipment.department]?.name || equipment.department}</div>
        <div>Location: ${equipment.location}</div>
        <div>ID: ${equipment.id}</div>
      </div>
    `;
    equipmentList.appendChild(equipmentElement);
  });
}

function populateStaffOverview() {
  const staffOverview = document.getElementById('staffOverview');
  if (!staffOverview) return;

  const staffMetrics = appData.hospitalAnalytics.staffMetrics;
  
  staffOverview.innerHTML = `
    <div class="staff-metrics">
      <div class="metric">
        <span class="metric__value">${staffMetrics.totalStaff}</span>
        <span class="metric__label">Total Staff</span>
      </div>
      <div class="metric">
        <span class="metric__value">${staffMetrics.activeStaff}</span>
        <span class="metric__label">Active Today</span>
      </div>
      <div class="metric">
        <span class="metric__value">${staffMetrics.utilizationRate}%</span>
        <span class="metric__label">Utilization</span>
      </div>
      <div class="metric">
        <span class="metric__value">${staffMetrics.overtimeHours}h</span>
        <span class="metric__label">Overtime</span>
      </div>
    </div>
    <div class="departments-breakdown">
      <h4>Department Breakdown</h4>
      ${Object.values(appData.departments).map(dept => `
        <div class="dept-staff">
          <span class="dept-name">${dept.name}</span>
          <span class="dept-count">${dept.activeStaff}/${dept.totalStaff}</span>
        </div>
      `).join('')}
    </div>
  `;
}

function populateDepartmentOverview() {
  const departmentGrid = document.getElementById('departmentGrid');
  if (!departmentGrid) return;

  departmentGrid.innerHTML = '';
  
  Object.values(appData.departments).forEach(department => {
    const metrics = appData.hospitalAnalytics.departmentMetrics[department.id];
    const departmentElement = document.createElement('div');
    departmentElement.className = 'department-card';
    
    departmentElement.innerHTML = `
      <div class="department-card__header">
        <h3>${department.name}</h3>
        <span class="department-card__location">${department.location}</span>
      </div>
      <div class="department-card__metrics">
        <div class="metric">
          <span class="metric__value">${metrics.appointments}</span>
          <span class="metric__label">Appointments</span>
        </div>
        <div class="metric">
          <span class="metric__value">${metrics.utilization}%</span>
          <span class="metric__label">Utilization</span>
        </div>
        <div class="metric">
          <span class="metric__value">${metrics.avgWaitTime}min</span>
          <span class="metric__label">Avg Wait</span>
        </div>
        <div class="metric">
          <span class="metric__value">${metrics.patientSatisfaction}</span>
          <span class="metric__label">Satisfaction</span>
        </div>
      </div>
      <div class="department-card__details">
        <div class="detail-row">
          <span>Head:</span>
          <span>${appData.doctors[department.head]?.name || 'Unknown'}</span>
        </div>
        <div class="detail-row">
          <span>Staff:</span>
          <span>${department.activeStaff}/${department.totalStaff}</span>
        </div>
        <div class="detail-row">
          <span>Rooms:</span>
          <span>${department.rooms.length}</span>
        </div>
      </div>
      <div class="department-card__actions">
        <button class="btn btn--sm btn--outline" onclick="viewDepartmentSchedule('${department.id}')">View Schedule</button>
        <button class="btn btn--sm btn--secondary" onclick="manageDepartmentResources('${department.id}')">Manage Resources</button>
      </div>
    `;
    departmentGrid.appendChild(departmentElement);
  });
}

function viewDepartmentSchedule(departmentId) {
  setDepartmentFilter(departmentId);
  switchView('daily');
}

function manageDepartmentResources(departmentId) {
  // This would open a resource management modal for the specific department
  console.log('Managing resources for department:', departmentId);
  // Implementation would go here
}

// Enhanced appointment scheduling with department/doctor integration
function handleQuickAdd() {
  const form = document.querySelector('.quick-add-form');
  if (!form) return;

  const formData = new FormData(form);
  const departmentId = document.getElementById('appointmentDepartment').value;
  const doctorId = document.getElementById('appointmentDoctor').value;
  
  // Validate that doctor belongs to selected department
  const selectedDoctor = appData.doctors[doctorId];
  if (selectedDoctor && selectedDoctor.department !== departmentId) {
    alert('Selected doctor does not belong to the selected department');
    return;
  }

  // Check for conflicts
  const newAppointment = {
    startTime: formData.get('time'),
    endTime: calculateEndTime(formData.get('time'), parseInt(formData.get('duration'))),
    doctorId: doctorId,
    department: departmentId
  };

  const conflicts = detectConflicts(newAppointment);
  if (conflicts.length > 0) {
    const conflictMessages = conflicts.map(c => `${c.title} (${formatTime(c.startTime)} - ${formatTime(c.endTime)})`);
    alert(`Scheduling conflict detected with:\n${conflictMessages.join('\n')}`);
    return;
  }

  console.log('Adding new appointment:', newAppointment);
  alert('Appointment would be scheduled in a real application');
  closeModal('quickAddModal');
}

function calculateEndTime(startTime, durationMinutes) {
  const [hours, minutes] = startTime.split(':').map(Number);
  const totalMinutes = hours * 60 + minutes + durationMinutes;
  const endHours = Math.floor(totalMinutes / 60);
  const endMins = totalMinutes % 60;
  return `${endHours.toString().padStart(2, '0')}:${endMins.toString().padStart(2, '0')}`;
}

// Department-based doctor filtering for appointment form
document.addEventListener('DOMContentLoaded', function() {
  const departmentSelect = document.getElementById('appointmentDepartment');
  const doctorSelect = document.getElementById('appointmentDoctor');
  
  if (departmentSelect && doctorSelect) {
    departmentSelect.addEventListener('change', function() {
      const selectedDepartment = this.value;
      const departmentDoctors = Object.values(appData.doctors).filter(
        doctor => doctor.department === selectedDepartment
      );
      
      doctorSelect.innerHTML = '';
      departmentDoctors.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor.id;
        option.textContent = doctor.name;
        doctorSelect.appendChild(option);
      });
    });
    
    // Trigger initial population
    departmentSelect.dispatchEvent(new Event('change'));
  }
});
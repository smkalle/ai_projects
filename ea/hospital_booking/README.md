# 🏥 Hospital Booking & Management System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.29+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0+-green.svg" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

> A comprehensive, modern hospital management system built with Streamlit, featuring appointment scheduling, doctor management, analytics dashboards, and automated reporting with beautiful calendar views.

## 🚀 Features

### 📅 **Appointment Management**
- **Beautiful Calendar Views**: Timeline and week grid layouts inspired by modern scheduling apps
- **Quick Booking**: One-click appointment scheduling from calendar view
- **Smart Scheduling**: Conflict detection and optimal time suggestions
- **Multi-View Support**: Day, week, and list views with filtering
- **Status Management**: Complete appointment lifecycle tracking

### 👨‍⚕️ **Doctor & Department Management**
- **Comprehensive Profiles**: Doctor specializations, experience, availability
- **Department Organization**: Cardiology, Emergency, Surgery, Internal Medicine, Pediatrics
- **Performance Tracking**: Efficiency metrics and patient satisfaction scores
- **Resource Management**: Room assignments and equipment tracking

### 📊 **Advanced Analytics & Reporting**
- **Real-time Dashboards**: Hospital KPIs, department performance, doctor efficiency
- **Custom Report Builder**: Dynamic chart generation with multiple data sources
- **Automated Reporting**: Scheduled report generation and email delivery
- **Interactive Visualizations**: Plotly-powered charts and metrics

### 🔧 **Integration & Automation**
- **Email Services**: Appointment confirmations, reminders, and notifications
- **Calendar Integration**: Google Calendar, Outlook, and iCal support
- **REST API**: Full CRUD operations with JWT authentication
- **Report Scheduling**: Automated daily, weekly, monthly, and quarterly reports

### 🎨 **Modern UI/UX**
- **Professional Interface**: Medical-grade design with intuitive navigation
- **Responsive Layout**: Mobile-friendly design that works on all devices
- **Color-coded System**: Visual indicators for appointment types and priorities
- **Interactive Components**: Expandable cards, filterable lists, and search functionality

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python-based web framework)
- **Backend**: SQLAlchemy ORM with SQLite database
- **Visualizations**: Plotly, Chart.js integration
- **Authentication**: JWT-based security
- **Email**: SMTP with Jinja2 templating
- **Calendar APIs**: Google Calendar API, Microsoft Graph API
- **Scheduling**: Python-schedule for automated tasks
- **Export Formats**: HTML, PDF, JSON, CSV, PNG, SVG

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser
- (Optional) SMTP server for email notifications
- (Optional) Google/Microsoft accounts for calendar integration

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hospital-booking-system.git
cd hospital-booking-system
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Initialize Database
```bash
python -c "from database.models import init_db; init_db()"
```

### 6. Run the Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🏗️ Project Structure

```
hospital-booking-system/
├── 📁 api/                     # REST API endpoints
│   ├── __init__.py
│   └── endpoints.py           # API routes and handlers
├── 📁 database/               # Database models and configuration
│   ├── __init__.py
│   ├── models.py             # SQLAlchemy models
│   └── seed_data.py          # Sample data for testing
├── 📁 services/              # Business logic and external services
│   ├── analytics_etl.py      # Data processing pipeline
│   ├── calendar_service.py   # Calendar integrations
│   ├── dashboard_service.py  # Analytics and KPIs
│   ├── email_service.py      # Email notifications
│   ├── report_builder_service.py  # Dynamic reporting
│   ├── report_generator.py   # Report templates
│   ├── report_scheduler.py   # Automated scheduling
│   └── report_sharing.py     # Export and sharing
├── 📁 templates/             # Jinja2 templates
│   └── email/               # Email templates
├── 📁 tests/                # Unit and integration tests
├── 📁 utils/                # Utility functions
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=sqlite:///hospital_booking.db

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# API Keys (Optional)
GOOGLE_CALENDAR_CLIENT_ID=your-google-client-id
GOOGLE_CALENDAR_CLIENT_SECRET=your-google-client-secret
MICROSOFT_GRAPH_CLIENT_ID=your-microsoft-client-id
MICROSOFT_GRAPH_CLIENT_SECRET=your-microsoft-client-secret

# JWT Secret
JWT_SECRET_KEY=your-secret-key-here
```

## 📖 Usage Guide

### 🏥 **Dashboard Overview**
Navigate through different sections using the sidebar:
- **🏠 Home**: Hospital overview and key metrics
- **👨‍⚕️ Doctors**: Doctor profiles and management
- **🏢 Departments**: Department information and statistics
- **📅 Appointments**: Full appointment management system
- **📊 Analytics**: Advanced reporting and visualizations
- **🔗 Integrations**: External service connections
- **📄 Reports**: Custom and scheduled reports

### 📅 **Appointment Management**
1. **Calendar View**: Switch between Day/Week views
2. **Quick Add**: Click ➕ on any day to schedule appointments
3. **Filtering**: Filter by department, doctor, or appointment type
4. **Status Tracking**: Monitor scheduled, completed, cancelled appointments

### 📊 **Analytics & Reporting**
1. **Custom Reports**: Build dynamic reports with multiple data sources
2. **Templates**: Save and reuse report configurations
3. **Scheduling**: Automate report generation and delivery
4. **Export Options**: Download in various formats (PDF, Excel, JSON)

### 🔗 **Integrations**
1. **Email Setup**: Configure SMTP for notifications
2. **Calendar Sync**: Connect Google Calendar or Outlook
3. **API Access**: Use REST endpoints for external integrations

## 🎨 Customization

### Adding New Departments
```python
# In database/models.py
new_department = Department(
    name="Neurology",
    description="Nervous system disorders",
    head_doctor_id=doctor_id
)
```

### Custom Report Types
```python
# In services/report_builder_service.py
def create_custom_metric(self, data_source, calculation):
    # Add your custom metric logic
    pass
```

### Email Templates
Add new templates in `templates/email/` directory using Jinja2 syntax.

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_appointments.py

# Run with coverage
python -m pytest --cov=. tests/
```

## 📚 API Documentation

The system provides a REST API for external integrations:

### Authentication
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "doctor@hospital.com",
  "password": "password"
}
```

### Appointments
```bash
# Get appointments
GET /api/appointments?date=2024-01-15&department=cardiology

# Create appointment
POST /api/appointments
Content-Type: application/json

{
  "patient_id": 1,
  "doctor_id": 2,
  "appointment_date": "2024-01-15",
  "start_time": "14:00",
  "end_time": "15:00",
  "appointment_type": "patient_care"
}
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 1. Fork the Repository
Click the "Fork" button on GitHub

### 2. Create a Feature Branch
```bash
git checkout -b feature/amazing-feature
```

### 3. Make Your Changes
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation as needed

### 4. Run Tests
```bash
python -m pytest tests/
```

### 5. Commit Your Changes
```bash
git commit -m "Add amazing feature"
```

### 6. Push to Your Fork
```bash
git push origin feature/amazing-feature
```

### 7. Create a Pull Request
Submit a pull request with a clear description of your changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** - For the amazing web framework
- **Plotly** - For beautiful, interactive visualizations
- **SQLAlchemy** - For robust database operations
- **The Open Source Community** - For inspiration and support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/hospital-booking-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hospital-booking-system/discussions)
- **Email**: support@yourdomain.com

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Heroku Deployment
1. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

---

<p align="center">
  Made with ❤️ for better healthcare management
</p>
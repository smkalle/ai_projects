# Medical AI Assistant MVP V2.0 - Deployment Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.sample .env
   # Edit .env with your configuration
   ```

3. **Run Application**
   ```bash
   python -m src.main
   ```

4. **Run Tests**
   ```bash
   python api_test_suite.py
   ```

## Production Deployment

### Environment Setup
- Set `ENVIRONMENT=production`
- Set `DEBUG=False`
- Configure your OpenAI API key
- Set up proper database (SQLite for MVP, PostgreSQL for production)

### Security Considerations
- Never commit `.env` files to version control
- Use secure secrets management in production
- Configure proper CORS settings
- Set up HTTPS/SSL certificates
- Implement rate limiting

### Database
- The application will automatically create required tables on first run
- For production, consider migrating to PostgreSQL
- Regular backups are recommended

## API Endpoints

### Patient Management
- `POST /api/v2/patients/register` - Register new patient
- `GET /api/v2/patients/search` - Search patients
- `GET /api/v2/patients/{patient_id}` - Get patient details
- `GET /api/v2/patients/{patient_id}/history` - Get patient history
- `GET /api/v2/patients/{patient_id}/alerts` - Check visit alerts
- `POST /api/v2/patients/{patient_id}/cases` - Create case
- `POST /api/v2/patients/{patient_id}/assess` - AI assessment

### Case Management
- `GET /api/cases` - List cases (with filtering)
- `GET /api/cases/{case_id}` - Get case details
- `PUT /api/cases/{case_id}/status` - Update case status

### Filtering Options
- Status: `?status=new|reviewed|closed`
- Patient Name: `?patient_name=John`
- Combined: `?status=new&patient_name=John`

## Features

✅ Patient Registration & Search
✅ AI-Powered Medical Assessment
✅ Case Management with Status Updates
✅ Visit Pattern Analysis & Alerts
✅ Advanced Filtering & Search
✅ QR Code Generation
✅ Photo Upload Support
✅ Real-time Status Updates
✅ Comprehensive API Test Suite

## Support

For issues and questions, please check the main README.md file.

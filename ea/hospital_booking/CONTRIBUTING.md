# Contributing to Hospital Booking System

🎉 Thank you for your interest in contributing to the Hospital Booking System! We welcome contributions from developers of all skill levels.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## 🤝 Code of Conduct

This project adheres to a code of conduct that ensures a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Streamlit and SQLAlchemy
- Familiarity with healthcare management systems (helpful but not required)

### Areas for Contribution

We welcome contributions in these areas:

- 🐛 **Bug Fixes**: Help us identify and fix issues
- ✨ **New Features**: Implement new functionality
- 📚 **Documentation**: Improve or add documentation
- 🧪 **Testing**: Add or improve test coverage
- 🎨 **UI/UX**: Enhance the user interface and experience
- 🔧 **Performance**: Optimize code and database queries
- 🌐 **Localization**: Add support for different languages

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/hospital-booking-system.git
cd hospital-booking-system

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/hospital-booking-system.git
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 3. Initialize Database

```bash
# Create and seed the database
python -c "from database.models import init_db; init_db()"
python database/seed_data.py
```

### 4. Run the Application

```bash
streamlit run app.py
```

## 🔄 Contribution Workflow

### 1. Create an Issue

Before starting work, please:

- Check if an issue already exists
- Create a new issue describing the bug or feature
- Wait for maintainer feedback before implementing large changes

### 2. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number
```

### 3. Make Changes

- Write clear, concise code
- Follow our coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run tests
python -m pytest tests/

# Check code coverage
python -m pytest --cov=. tests/

# Run linting
flake8 .
black .
isort .
```

### 5. Commit and Push

```bash
# Stage and commit changes
git add .
git commit -m "feat: add patient search functionality"

# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Go to GitHub and create a pull request
- Use the pull request template
- Link to related issues
- Provide a clear description of changes

## 📏 Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Use Black formatter (line length: 88)
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .
```

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Files**: `snake_case.py`
- **Database models**: `PascalCase`

### Documentation

```python
def create_appointment(patient_id: int, doctor_id: int, date: str) -> dict:
    """
    Create a new appointment.

    Args:
        patient_id (int): The patient's unique identifier
        doctor_id (int): The doctor's unique identifier
        date (str): Appointment date in YYYY-MM-DD format

    Returns:
        dict: Created appointment data with id and status

    Raises:
        ValidationError: If date format is invalid
        DatabaseError: If database operation fails
    """
    # Implementation here
    pass
```

### Database Changes

For database schema changes:

1. Create migration scripts in `database/migrations/`
2. Update model definitions in `database/models.py`
3. Update seed data if necessary
4. Test both forward and backward migrations

## 🧪 Testing

### Test Structure

```
tests/
├── unit/              # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/       # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── e2e/              # End-to-end tests
    └── test_workflows.py
```

### Writing Tests

```python
import pytest
from database.models import Appointment, Doctor, Patient

def test_create_appointment():
    """Test appointment creation with valid data."""
    # Arrange
    patient = Patient(first_name="John", last_name="Doe")
    doctor = Doctor(name="Dr. Smith", specialization="Cardiology")

    # Act
    appointment = create_appointment(patient.id, doctor.id, "2024-01-15")

    # Assert
    assert appointment.id is not None
    assert appointment.status == "scheduled"
```

### Test Requirements

- All new features must have tests
- Bug fixes should include regression tests
- Aim for >80% code coverage
- Use meaningful test names and descriptions

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use type hints consistently
- Keep inline comments minimal and meaningful

### User Documentation

- Update README.md for new features
- Add usage examples
- Update API documentation for endpoint changes
- Include screenshots for UI changes

### Technical Documentation

For major features, add documentation in `docs/`:

- Architecture decisions
- Database schema changes
- API specifications
- Deployment guides

## 🛠️ Development Tools

### Recommended Tools

- **IDE**: VS Code, PyCharm, or similar
- **Database**: DB Browser for SQLite
- **API Testing**: Postman or curl
- **Git GUI**: GitKraken, SourceTree, or built-in IDE tools

### VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json"
  ]
}
```

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, browser
- **Steps to reproduce**: Detailed steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Screenshots**: If applicable
- **Console errors**: Any error messages

### Bug Report Template

```markdown
**Environment:**
- OS: [e.g., Windows 10, macOS 12.1, Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Browser: [e.g., Chrome 96.0.4664.110]

**Steps to Reproduce:**
1. Navigate to appointments page
2. Click on "Add Appointment"
3. Fill in patient details
4. Click "Save"

**Expected Behavior:**
Appointment should be created and appear in the calendar

**Actual Behavior:**
Error message appears: "Database connection failed"

**Additional Context:**
This happens only when trying to create appointments after 5 PM
```

## ✨ Feature Requests

For new features, please provide:

- **Problem statement**: What issue does this solve?
- **Proposed solution**: How would you like it to work?
- **Alternatives considered**: Other ways to solve this
- **Additional context**: Use cases, examples, mockups

## 🚀 Release Process

### Version Numbering

We use Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Example: `1.2.3` → `1.3.0` (new feature) → `2.0.0` (breaking change)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] CHANGELOG.md updated
- [ ] Migration scripts tested
- [ ] Performance regression tested

## 🏆 Recognition

Contributors are recognized in several ways:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- GitHub contributor statistics
- Special recognition for major contributions

## ❓ Getting Help

### Where to Ask Questions

- **General questions**: GitHub Discussions
- **Bug reports**: GitHub Issues
- **Security issues**: Email maintainers directly
- **Real-time chat**: Discord/Slack (if available)

### Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Plotly Documentation](https://plotly.com/python/)
- [Healthcare Data Standards](https://www.hl7.org/fhir/)

## 🎯 Beginner-Friendly Issues

Look for issues labeled:

- `good first issue`: Perfect for newcomers
- `help wanted`: We need community help
- `documentation`: Improve docs
- `tests`: Add or improve testing

## 📞 Contact

- **Project Maintainers**: Listed in CODEOWNERS file
- **Security Issues**: security@yourdomain.com
- **General Questions**: discussions@yourdomain.com

---

Thank you for contributing to better healthcare management software! 🏥❤️
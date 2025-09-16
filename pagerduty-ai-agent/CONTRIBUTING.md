# Contributing to PagerDuty AI Agent

Thank you for your interest in contributing to the PagerDuty AI Agent project!

## Development Setup

### Prerequisites
- Python 3.9 or higher
- Git
- OpenAI API key

### Setup Instructions

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/pagerduty-ai-agent.git
   cd pagerduty-ai-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   python scripts/init_database.py
   ```

6. **Run Tests**
   ```bash
   python -m pytest tests/ -v
   ```

## Code Style

### Python Standards
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and returns
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable and function names

### Documentation
- All functions must have docstrings following Google style
- Include parameter descriptions and return value explanations
- Add inline comments for complex logic
- Update API documentation for new features

## Testing Guidelines

### Test Structure
- All new features must include tests
- Aim for >80% code coverage
- Use pytest for test framework
- Follow AAA pattern (Arrange, Act, Assert)

## Pull Request Process

### Before Submitting
1. Ensure all tests pass locally
2. Run code formatting: `black . && isort .`
3. Update documentation if needed
4. Add/update tests for new functionality

### PR Requirements
- Clear, descriptive title
- Detailed description of changes
- Link to related issues
- Screenshots for UI changes
- Test coverage maintained or improved

## Getting Help

### Resources
- [Project Documentation](docs/API.md)
- [GitHub Issues](https://github.com/your-repo/issues)
- [LangChain Documentation](https://docs.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

Thank you for contributing to making incident management more intelligent and accessible!
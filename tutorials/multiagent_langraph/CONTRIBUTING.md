# Contributing to GreenGuard

Thank you for your interest in contributing to GreenGuard! We welcome contributions from the community and are pleased to have you join us.

## 🚀 Quick Start for Contributors

### Setting up your development environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/greenguard.git
   cd greenguard
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

6. **Copy environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use the [issue tracker](https://github.com/yourusername/greenguard/issues)
- Search existing issues before creating new ones
- Include steps to reproduce, expected behavior, and actual behavior
- Add relevant system information (OS, Python version, etc.)

### 💡 Feature Requests
- Check existing issues and discussions first
- Clearly describe the problem you're trying to solve
- Provide examples of how the feature would be used
- Consider submitting a design document for large features

### 🔧 Code Contributions

#### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/your-feature-name`: Feature development
- `fix/issue-description`: Bug fixes

#### Development Process
1. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-improvement
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   # Run tests
   python -m pytest
   
   # Check code formatting
   black greenguard/
   flake8 greenguard/
   
   # Type checking
   mypy greenguard/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing improvement
   
   - Detailed description of changes
   - Reference any relevant issues (#123)
   "
   ```

5. **Push and create a Pull Request**:
   ```bash
   git push origin feature/amazing-improvement
   ```

## 📝 Coding Standards

### Code Style
We follow Python best practices and use automated tools:

- **Black** for code formatting
- **Flake8** for linting
- **isort** for import sorting
- **mypy** for type checking

### Code Guidelines
```python
# Type hints are required
def process_location(location: str, demo_mode: bool = False) -> Dict[str, Any]:
    """Process a location for environmental analysis.
    
    Args:
        location: Geographic location to analyze
        demo_mode: Whether to use demo data
        
    Returns:
        Dictionary containing analysis results
        
    Raises:
        ValueError: If location is invalid
    """
    pass

# Use descriptive variable names
environmental_data = collect_hazard_data(location)
risk_assessment = analyze_health_risks(environmental_data)

# Add docstrings to all public functions and classes
class DataScoutAgent:
    """Agent responsible for collecting environmental hazard data.
    
    This agent uses various data sources to gather information about
    environmental conditions in a specified location.
    """
    pass
```

### Commit Message Format
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(agents): add retry logic to DataScout agent

- Implement exponential backoff for API failures
- Add configurable max retry attempts
- Include retry metrics in agent logs

Closes #123
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=greenguard

# Run specific test file
python -m pytest greenguard/tests/test_agents.py

# Run with verbose output
python -m pytest -v
```

### Test Structure
```
greenguard/
├── tests/
│   ├── unit/           # Unit tests for individual components
│   ├── integration/    # Integration tests for agent workflows
│   ├── fixtures/       # Test data and fixtures
│   └── conftest.py     # Pytest configuration
```

### Writing Tests
```python
import pytest
from greenguard.agents import DataScoutAgent

class TestDataScoutAgent:
    """Test cases for DataScout agent."""
    
    @pytest.fixture
    def agent(self):
        return DataScoutAgent(api_key="test_key")
    
    def test_search_environmental_data(self, agent):
        """Test environmental data search functionality."""
        result = agent.search("San Francisco, CA")
        assert result is not None
        assert "hazards" in result
        assert len(result["hazards"]) > 0
    
    def test_invalid_location_handling(self, agent):
        """Test handling of invalid locations."""
        with pytest.raises(ValueError):
            agent.search("")
```

## 📖 Documentation

### Code Documentation
- All public functions and classes must have docstrings
- Use Google-style docstrings
- Include type hints for all parameters and return values
- Add examples for complex functions

### README Updates
- Update README.md if your changes affect user-facing functionality
- Update installation instructions if dependencies change
- Add new features to the features list

## 🔍 Code Review Process

### Pull Request Guidelines
- **Title**: Clear, descriptive title
- **Description**: Explain what changes you made and why
- **Testing**: Describe how you tested your changes
- **Breaking Changes**: Highlight any breaking changes
- **Screenshots**: Include screenshots for UI changes

### Review Criteria
Reviewers will check for:
- ✅ Code follows style guidelines
- ✅ Tests are included and passing
- ✅ Documentation is updated
- ✅ No breaking changes (or properly documented)
- ✅ Performance impact is considered
- ✅ Security implications are addressed

## 🏗️ Architecture Contributions

### Adding New Agents
When contributing new agents:

1. **Follow the agent interface**:
   ```python
   async def your_agent(state: GreenGuardState) -> GreenGuardState:
       """Your agent implementation."""
       pass
   ```

2. **Update the supervisor routing**
3. **Add comprehensive tests**
4. **Update documentation**
5. **Consider backward compatibility**

### UI/UX Contributions
- Follow the existing design system
- Ensure mobile responsiveness
- Test accessibility features
- Include dark/light theme support

## 🎉 Recognition

Contributors will be:
- Added to the Contributors section in README
- Mentioned in release notes for significant contributions
- Invited to join the core team for consistent contributors

## 📞 Getting Help

- **Discord**: [Join our community](https://discord.gg/greenguard)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/greenguard/discussions)
- **Issues**: [Report bugs or request features](https://github.com/yourusername/greenguard/issues)

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

---

Thank you for contributing to GreenGuard! Together, we're making the world safer through technology. 🌿
# Contributing to MediPulse

Thank you for considering contributing to MediPulse! This document provides guidelines for contributing to the project.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or request features
- Before creating an issue, please search to see if a similar issue already exists
- Provide as much detail as possible, including steps to reproduce bugs

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/medipulse.git
   cd medipulse
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   make test
   make lint
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style

- Follow PEP 8 Python style guidelines
- Use `black` for code formatting: `make format`
- Use `flake8` for linting: `make lint`
- Keep lines under 88 characters when possible

### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PRs
- Aim for good test coverage
- Use pytest for testing

### Documentation

- Update README.md if your changes affect usage
- Update API documentation in docs/api.md
- Add docstrings to new functions and classes
- Include examples for new features

## Types of Contributions

### Bug Fixes
- Fix issues reported in the issue tracker
- Add regression tests for fixed bugs

### New Features
- Implement new medical document types (discharge summaries, pathology reports, etc.)
- Add new extraction capabilities for medical fields
- Improve accuracy of existing medical data extraction
- Enhance review workflow and annotation systems
- Add FHIR compliance features

### Documentation
- Improve existing documentation
- Add medical workflow examples and tutorials
- Document clinical use cases
- Fix typos and unclear medical explanations

### Performance Improvements
- Optimize medical document processing speed
- Reduce memory usage for large medical datasets
- Improve error handling for malformed medical documents
- Enhance batch processing capabilities

## Medical AI Guidelines

### Healthcare Data Handling
- **Never commit real patient data** or PHI (Protected Health Information)
- **Use synthetic/demo data** for all examples and tests
- **Follow HIPAA guidelines** when applicable
- **Implement proper data anonymization** in examples

### Medical Domain Expertise
- **Validate medical terminology** and ensure accuracy
- **Consult healthcare professionals** for clinical workflows
- **Include proper medical disclaimers** in documentation
- **Test with realistic medical scenarios**

### Clinical Accuracy
- Ensure extracted data maintains medical context
- Validate against standard medical references
- Include confidence scoring for medical extractions
- Handle medical abbreviations and terminology correctly

## Security Considerations

When contributing to MediPulse, keep in mind:

- **Never commit real medical data or PHI**
- **Use synthetic/fake data for testing**
- **Consider HIPAA compliance** in new features
- **Report security issues privately**
- **Follow medical data security best practices**
- **Implement audit trails for medical operations**

## Pull Request Process

1. **Update documentation** if your changes affect the public API
2. **Add tests** that prove your fix is effective or your feature works
3. **Ensure all tests pass** and linting is clean
4. **Update the version number** if appropriate
5. **Write a clear PR description** explaining what you changed and why

## Questions?

If you have questions about contributing:
- Open an issue for discussion
- Check existing issues and PRs
- Review the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to MediPulse! 🏥

# MediPulse Makefile

.PHONY: install test clean lint format demo

# Install dependencies
install:
	pip install -r requirements.txt

# Install in development mode
install-dev:
	pip install -e .
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Run demo
demo:
	python examples/demo.py

# Clean up Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Lint code
lint:
	flake8 src/ tests/ examples/

# Format code
format:
	black src/ tests/ examples/

# Create distribution package
build:
	python setup.py sdist bdist_wheel

# Help
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  install-dev - Install in development mode"
	@echo "  test        - Run tests"
	@echo "  demo        - Run demo application"
	@echo "  clean       - Clean up Python cache files"
	@echo "  lint        - Lint code with flake8"
	@echo "  format      - Format code with black"
	@echo "  build       - Create distribution package"

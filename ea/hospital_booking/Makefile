# Hospital Booking System Makefile

.PHONY: help install dev-install test lint format clean build docker run docs

# Variables
PYTHON = python3
PIP = pip
VENV = venv
STREAMLIT = streamlit

# Default target
help:
	@echo "Hospital Booking System - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install production dependencies"
	@echo "  dev-install      Install development dependencies"
	@echo "  setup           Complete project setup (recommended for new installs)"
	@echo ""
	@echo "Development Commands:"
	@echo "  run             Run the Streamlit application"
	@echo "  test            Run all tests"
	@echo "  test-cov        Run tests with coverage report"
	@echo "  lint            Run code linting"
	@echo "  format          Format code with black and isort"
	@echo "  typecheck       Run type checking with mypy"
	@echo ""
	@echo "Database Commands:"
	@echo "  db-init         Initialize the database"
	@echo "  db-seed         Seed database with sample data"
	@echo "  db-reset        Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run application in Docker"
	@echo "  docker-compose  Run full stack with docker-compose"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean           Clean up generated files"
	@echo "  docs            Generate documentation"
	@echo "  security        Run security checks"

# Installation
install:
	$(PIP) install -r requirements.txt

dev-install: install
	$(PIP) install -r requirements-dev.txt
	pre-commit install

setup: dev-install db-init db-seed
	@echo "✅ Setup complete! Run 'make run' to start the application."

# Development
run:
	$(STREAMLIT) run app.py

test:
	$(PYTHON) -m pytest tests/ -v

test-cov:
	$(PYTHON) -m pytest tests/ --cov=. --cov-report=html --cov-report=term

lint:
	flake8 .
	mypy .
	bandit -r . -f json -o bandit-report.json

format:
	black .
	isort .

typecheck:
	mypy .

# Database
db-init:
	$(PYTHON) -c "from database.models import init_db; init_db()"

db-seed:
	$(PYTHON) database/seed_data.py

db-reset:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f hospital_booking.db; \
		$(MAKE) db-init db-seed; \
		echo "✅ Database reset complete"; \
	fi

# Docker
docker-build:
	docker build -t hospital-booking-system .

docker-run: docker-build
	docker run -p 8501:8501 hospital-booking-system

docker-compose:
	docker-compose up -d

# Documentation
docs:
	@echo "📚 Generating documentation..."
	$(PYTHON) -c "import os; os.makedirs('docs', exist_ok=True)"
	@echo "✅ Documentation setup complete"

# Security
security:
	bandit -r . -f json -o bandit-report.json
	safety check

# Maintenance
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -f bandit-report.json

# CI/CD helpers
ci-install:
	$(PIP) install -r requirements.txt -r requirements-dev.txt

ci-test: ci-install test lint security

# Virtual environment management
venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Activate with:"
	@echo "source $(VENV)/bin/activate  # Linux/Mac"
	@echo "$(VENV)\\Scripts\\activate     # Windows"

# Production deployment helpers
deploy-check:
	@echo "🔍 Running pre-deployment checks..."
	$(MAKE) test
	$(MAKE) lint
	$(MAKE) security
	@echo "✅ All checks passed!"

# Quick development setup
quick-start: venv
	source $(VENV)/bin/activate && $(MAKE) setup run

# Help for common issues
troubleshoot:
	@echo "🔧 Common troubleshooting steps:"
	@echo ""
	@echo "1. Permission issues:"
	@echo "   chmod +x setup.sh"
	@echo ""
	@echo "2. Python version issues:"
	@echo "   Make sure you have Python 3.8+ installed"
	@echo "   python3 --version"
	@echo ""
	@echo "3. Database issues:"
	@echo "   make db-reset"
	@echo ""
	@echo "4. Dependency issues:"
	@echo "   make clean && make dev-install"
	@echo ""
	@echo "5. Port already in use:"
	@echo "   lsof -ti:8501 | xargs kill"
# Energy Document AI Makefile

.PHONY: install test lint format run-ui run-api run-both docker-build docker-run clean help

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest black flake8 mypy

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=app --cov-report=html

# Code quality
lint:
	flake8 app/ tests/
	mypy app/

format:
	black app/ tests/
	isort app/ tests/

# Running the application
run-ui:
	python app/main.py --mode ui

run-api:
	python app/main.py --mode api

run-both:
	python app/main.py --mode both

# Docker
docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-stop:
	docker-compose down

# Qdrant
start-qdrant:
	docker run -d -p 6333:6333 -v ./qdrant_data:/qdrant/storage qdrant/qdrant

stop-qdrant:
	docker stop $$(docker ps -q --filter ancestor=qdrant/qdrant)

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

clean-data:
	rm -rf data/processed/*
	rm -rf qdrant_data/

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  install-dev  - Install dev dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  run-ui       - Run Streamlit UI"
	@echo "  run-api      - Run FastAPI server"
	@echo "  run-both     - Run both UI and API"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  start-qdrant - Start Qdrant container"
	@echo "  clean        - Clean Python cache files"
	@echo "  help         - Show this help"

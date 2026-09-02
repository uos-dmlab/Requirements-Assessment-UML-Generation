.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate db-upgrade db-downgrade

# Default target
help:
	@echo "UMLReq Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install all dependencies"
	@echo "  make dev              - Install dev dependencies and setup environment"
	@echo ""
	@echo "Development:"
	@echo "  make run              - Run development server"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code with black and isort"
	@echo "  make clean            - Clean temporary files"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          - Create new migration"
	@echo "  make db-upgrade       - Apply pending migrations"
	@echo "  make db-downgrade     - Rollback last migration"
	@echo "  make db-reset         - Reset database (WARNING: deletes data)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docker-shell     - Open shell in app container"
	@echo ""

# Installation
install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

dev:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm
	@echo "Creating .env file from .env.example if it doesn't exist..."
	@test -f .env || cp .env.example .env
	@echo "Development environment ready!"
	@echo "IMPORTANT: Update .env with your API keys before running the app"

# Development server
run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	pytest -v --cov=app --cov-report=html --cov-report=term

test-watch:
	pytest-watch

# Code quality
lint:
	@echo "Running flake8..."
	flake8 app tests
	@echo "Running mypy..."
	mypy app --ignore-missing-imports || true

format:
	@echo "Running isort..."
	isort app tests
	@echo "Running black..."
	black app tests

check-format:
	@echo "Checking code formatting..."
	black --check app tests
	isort --check app tests

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

# Database migrations
migrate:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		alembic downgrade base && alembic upgrade head; \
	fi

db-shell:
	@echo "Connecting to database..."
	psql postgresql://$(DB_USER):$(DB_PASS)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

docker-shell:
	docker-compose exec app /bin/bash

docker-test:
	docker-compose exec app pytest

docker-restart:
	docker-compose restart app

# Production deployment
docker-prod:
	docker-compose --profile production up -d

# Database backup
db-backup:
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	pg_dump postgresql://$(DB_USER):$(DB_PASS)@$(DB_HOST):$(DB_PORT)/$(DB_NAME) > backups/backup_$$timestamp.sql
	@echo "Backup created: backups/backup_$$timestamp.sql"

db-restore:
	@read -p "Enter backup file path: " file; \
	psql postgresql://$(DB_USER):$(DB_PASS)@$(DB_HOST):$(DB_PORT)/$(DB_NAME) < $$file

# Security checks
security-check:
	@echo "Checking for security vulnerabilities..."
	pip-audit || echo "Install pip-audit: pip install pip-audit"

# Generate secret key
generate-secret:
	@python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Show project info
info:
	@echo "Project: UMLReq"
	@echo "Python version: $$(python --version)"
	@echo "Database URL: postgresql://$(DB_USER):***@$(DB_HOST):$(DB_PORT)/$(DB_NAME)"
	@echo "Environment files: $$(test -f .env && echo '.env exists' || echo '.env missing')"

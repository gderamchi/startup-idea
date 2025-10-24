# =============================================================================
# Freelancer Feedback Assistant - Makefile
# =============================================================================
# Quick commands for development, testing, and deployment
# Usage: make <target>
# =============================================================================

.PHONY: help install setup dev test clean docker-up docker-down migrate seed lint format check deploy

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "$(BLUE)Freelancer Feedback Assistant - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make install    # Install all dependencies"
	@echo "  make dev        # Start development servers"
	@echo "  make test       # Run all tests"
	@echo "  make docker-up  # Start with Docker"

# =============================================================================
# Installation & Setup
# =============================================================================

install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@$(MAKE) install-backend
	@$(MAKE) install-frontend
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

install-backend: ## Install Python backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && python -m venv venv
	cd backend && . venv/bin/activate && pip install --upgrade pip
	cd backend && . venv/bin/activate && pip install -r requirements.txt
	cd backend && . venv/bin/activate && pip install -r requirements-dev.txt
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend: ## Install Node.js frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

setup: ## Complete project setup (install + env + db)
	@echo "$(BLUE)Setting up project...$(NC)"
	@$(MAKE) install
	@$(MAKE) setup-env
	@$(MAKE) setup-db
	@echo "$(GREEN)✓ Project setup complete$(NC)"

setup-env: ## Create environment files from examples
	@echo "$(BLUE)Creating environment files...$(NC)"
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env"; fi
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "Created backend/.env"; fi
	@if [ ! -f frontend/.env ]; then cp frontend/.env.example frontend/.env; echo "Created frontend/.env"; fi
	@echo "$(YELLOW)⚠ Remember to update .env files with your actual values$(NC)"

setup-db: ## Set up database (create + migrate + seed)
	@echo "$(BLUE)Setting up database...$(NC)"
	@$(MAKE) db-create
	@$(MAKE) migrate
	@$(MAKE) seed
	@echo "$(GREEN)✓ Database setup complete$(NC)"

# =============================================================================
# Development
# =============================================================================

dev: ## Start all development servers (backend + frontend + celery)
	@echo "$(BLUE)Starting development servers...$(NC)"
	@trap 'kill 0' EXIT; \
	$(MAKE) dev-backend & \
	$(MAKE) dev-frontend & \
	$(MAKE) dev-celery & \
	wait

dev-backend: ## Start backend development server only
	@echo "$(BLUE)Starting backend server...$(NC)"
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server only
	@echo "$(BLUE)Starting frontend server...$(NC)"
	cd frontend && npm run dev

dev-celery: ## Start Celery worker for background tasks
	@echo "$(BLUE)Starting Celery worker...$(NC)"
	cd backend && . venv/bin/activate && celery -A app.tasks.celery_app worker --loglevel=info

dev-flower: ## Start Flower for Celery monitoring
	@echo "$(BLUE)Starting Flower...$(NC)"
	cd backend && . venv/bin/activate && celery -A app.tasks.celery_app flower --port=5555

# =============================================================================
# Database
# =============================================================================

db-create: ## Create database
	@echo "$(BLUE)Creating database...$(NC)"
	createdb freelancer_feedback_db || echo "Database already exists"
	@echo "$(GREEN)✓ Database created$(NC)"

db-drop: ## Drop database (WARNING: destroys all data)
	@echo "$(RED)Dropping database...$(NC)"
	@read -p "Are you sure? This will delete all data. [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		dropdb freelancer_feedback_db; \
		echo "$(GREEN)✓ Database dropped$(NC)"; \
	fi

db-reset: ## Reset database (drop + create + migrate + seed)
	@echo "$(BLUE)Resetting database...$(NC)"
	@$(MAKE) db-drop
	@$(MAKE) db-create
	@$(MAKE) migrate
	@$(MAKE) seed
	@echo "$(GREEN)✓ Database reset complete$(NC)"

migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	cd backend && . venv/bin/activate && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	@echo "$(BLUE)Creating migration...$(NC)"
	cd backend && . venv/bin/activate && alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)✓ Migration created$(NC)"

migrate-rollback: ## Rollback last migration
	@echo "$(BLUE)Rolling back migration...$(NC)"
	cd backend && . venv/bin/activate && alembic downgrade -1
	@echo "$(GREEN)✓ Rollback complete$(NC)"

seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd backend && . venv/bin/activate && python -m app.db.init_db
	@echo "$(GREEN)✓ Database seeded$(NC)"

# =============================================================================
# Testing
# =============================================================================

test: ## Run all tests (backend + frontend)
	@echo "$(BLUE)Running all tests...$(NC)"
	@$(MAKE) test-backend
	@$(MAKE) test-frontend
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-backend: ## Run backend tests with coverage
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && . venv/bin/activate && pytest --cov=app --cov-report=html --cov-report=term -v
	@echo "$(GREEN)✓ Backend tests complete$(NC)"
	@echo "Coverage report: backend/htmlcov/index.html"

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm run test
	@echo "$(GREEN)✓ Frontend tests complete$(NC)"

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd frontend && npm run test:e2e
	@echo "$(GREEN)✓ E2E tests complete$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd backend && . venv/bin/activate && pytest-watch

coverage: ## Generate and open coverage report
	@$(MAKE) test-backend
	@echo "$(BLUE)Opening coverage report...$(NC)"
	open backend/htmlcov/index.html || xdg-open backend/htmlcov/index.html

# =============================================================================
# Code Quality
# =============================================================================

lint: ## Run linters (backend + frontend)
	@echo "$(BLUE)Running linters...$(NC)"
	@$(MAKE) lint-backend
	@$(MAKE) lint-frontend
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-backend: ## Run Python linters
	@echo "$(BLUE)Linting backend...$(NC)"
	cd backend && . venv/bin/activate && ruff check .
	cd backend && . venv/bin/activate && mypy app

lint-frontend: ## Run JavaScript/TypeScript linters
	@echo "$(BLUE)Linting frontend...$(NC)"
	cd frontend && npm run lint

format: ## Format code (backend + frontend)
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(MAKE) format-backend
	@$(MAKE) format-frontend
	@echo "$(GREEN)✓ Formatting complete$(NC)"

format-backend: ## Format Python code
	@echo "$(BLUE)Formatting backend...$(NC)"
	cd backend && . venv/bin/activate && black .
	cd backend && . venv/bin/activate && ruff check --fix .

format-frontend: ## Format JavaScript/TypeScript code
	@echo "$(BLUE)Formatting frontend...$(NC)"
	cd frontend && npm run format

check: ## Run all checks (lint + test + type-check)
	@echo "$(BLUE)Running all checks...$(NC)"
	@$(MAKE) lint
	@$(MAKE) test
	@echo "$(GREEN)✓ All checks passed$(NC)"

# =============================================================================
# Docker
# =============================================================================

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start all services with Docker
	@echo "$(BLUE)Starting Docker services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

docker-down: ## Stop all Docker services
	@echo "$(BLUE)Stopping Docker services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-ps: ## List running Docker containers
	docker-compose ps

docker-shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

docker-shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend /bin/sh

docker-clean: ## Remove all Docker containers, volumes, and images
	@echo "$(RED)Cleaning Docker resources...$(NC)"
	docker-compose down -v --rmi all
	@echo "$(GREEN)✓ Docker cleaned$(NC)"

# =============================================================================
# Deployment
# =============================================================================

deploy: ## Deploy to production (Fly.io)
	@echo "$(BLUE)Deploying to production...$(NC)"
	@$(MAKE) deploy-backend
	@$(MAKE) deploy-frontend
	@echo "$(GREEN)✓ Deployment complete$(NC)"

deploy-backend: ## Deploy backend to Fly.io
	@echo "$(BLUE)Deploying backend...$(NC)"
	cd backend && fly deploy
	@echo "$(GREEN)✓ Backend deployed$(NC)"

deploy-frontend: ## Deploy frontend to Fly.io
	@echo "$(BLUE)Deploying frontend...$(NC)"
	cd frontend && fly deploy
	@echo "$(GREEN)✓ Frontend deployed$(NC)"

deploy-db-migrate: ## Run migrations on production database
	@echo "$(BLUE)Running production migrations...$(NC)"
	fly ssh console -a freelancer-feedback-api -C "alembic upgrade head"
	@echo "$(GREEN)✓ Production migrations complete$(NC)"

# =============================================================================
# Utilities
# =============================================================================

clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

logs: ## View application logs
	@echo "$(BLUE)Viewing logs...$(NC)"
	tail -f backend/logs/app.log

shell-backend: ## Open Python shell with app context
	@echo "$(BLUE)Opening backend shell...$(NC)"
	cd backend && . venv/bin/activate && python -m app.shell

docs: ## Generate and serve documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	cd docs && make html
	@echo "$(GREEN)✓ Documentation generated$(NC)"
	open docs/_build/html/index.html || xdg-open docs/_build/html/index.html

api-docs: ## Open API documentation in browser
	@echo "$(BLUE)Opening API docs...$(NC)"
	open http://localhost:8000/docs || xdg-open http://localhost:8000/docs

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -f http://localhost:8000/health && echo "$(GREEN)✓ Backend healthy$(NC)" || echo "$(RED)✗ Backend unhealthy$(NC)"
	@curl -f http://localhost:3000 && echo "$(GREEN)✓ Frontend healthy$(NC)" || echo "$(RED)✗ Frontend unhealthy$(NC)"

version: ## Show version information
	@echo "$(BLUE)Version Information:$(NC)"
	@echo "Python: $$(python --version)"
	@echo "Node: $$(node --version)"
	@echo "npm: $$(npm --version)"
	@echo "Docker: $$(docker --version)"
	@echo "PostgreSQL: $$(psql --version)"
	@echo "Redis: $$(redis-cli --version)"

# =============================================================================
# CI/CD
# =============================================================================

ci: ## Run CI pipeline locally
	@echo "$(BLUE)Running CI pipeline...$(NC)"
	@$(MAKE) install
	@$(MAKE) lint
	@$(MAKE) test
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

pre-commit: ## Run pre-commit checks
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test-backend
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

# =============================================================================
# Security
# =============================================================================

security-check: ## Run security vulnerability checks
	@echo "$(BLUE)Running security checks...$(NC)"
	cd backend && . venv/bin/activate && pip-audit
	cd frontend && npm audit
	@echo "$(GREEN)✓ Security checks complete$(NC)"

security-fix: ## Fix security vulnerabilities
	@echo "$(BLUE)Fixing security vulnerabilities...$(NC)"
	cd backend && . venv/bin/activate && pip-audit --fix
	cd frontend && npm audit fix
	@echo "$(GREEN)✓ Security fixes applied$(NC)"

# =============================================================================
# Backup & Restore
# =============================================================================

backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	pg_dump freelancer_feedback_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup complete$(NC)"

restore: ## Restore database from backup (usage: make restore FILE=backup.sql)
	@echo "$(BLUE)Restoring database...$(NC)"
	psql freelancer_feedback_db < $(FILE)
	@echo "$(GREEN)✓ Restore complete$(NC)"

# =============================================================================
# Monitoring
# =============================================================================

monitor: ## Start monitoring stack (Prometheus + Grafana)
	@echo "$(BLUE)Starting monitoring stack...$(NC)"
	docker-compose --profile monitoring up -d
	@echo "$(GREEN)✓ Monitoring started$(NC)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001 (admin/admin)"

monitor-down: ## Stop monitoring stack
	@echo "$(BLUE)Stopping monitoring stack...$(NC)"
	docker-compose --profile monitoring down
	@echo "$(GREEN)✓ Monitoring stopped$(NC)"

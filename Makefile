.PHONY: help up down clean fresh migrate logs restart ps build check-env logs-backend logs-db shell-backend test check-db view-db dev-start dev-stop dev-logs health lint format format-check build-frontend

# Use bash shell explicitly
SHELL := /bin/bash

# Check and create .env if needed
check-env:
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "✓ .env file created"; \
	else \
		echo "✓ .env file already exists"; \
	fi

# Build frontend (IMPORTANT: must be run before docker compose)
build-frontend:
	@echo "Building frontend..."
	@if [ ! -d "frontend" ]; then \
		echo "❌ Error: frontend directory not found"; \
		exit 1; \
	fi
	@if ! command -v bun &> /dev/null; then \
		echo "❌ Error: bun is not installed. Install from https://bun.sh"; \
		exit 1; \
	fi
	@echo "Installing dependencies..."
	cd frontend && bun install
	@echo "Building frontend..."
	cd frontend && bun run build
	@echo "✓ Frontend built successfully to backend/app/frontend"

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "  make build-frontend  - Build frontend (REQUIRED before docker compose)"
	@echo "  make up              - Start containers with visible logs (no -d flag)"
	@echo "  make down            - Stop running containers"
	@echo "  make clean           - Remove stopped containers and volumes (WARNING: deletes data)"
	@echo "  make fresh           - Clean + build + start (for first run or complete reset)"
	@echo "  make restart         - Restart all containers"
	@echo "  make migrate         - Run database migrations manually"
	@echo "  make logs            - Show logs from all containers"
	@echo "  make logs-backend    - Show logs from backend only"
	@echo "  make logs-db         - Show logs from database only"
	@echo "  make ps              - Show running containers"
	@echo "  make build           - Build images"
	@echo "  make shell-backend   - Open shell in backend container"
	@echo "  make test            - Run tests"
	@echo ""

# Start containers with visible logs (no daemon mode)
up: check-env
	@echo "Starting containers with visible logs..."
	docker compose up

# Stop containers
down:
	@echo "Stopping containers..."
	docker compose down

# Remove containers and volumes (careful - deletes data!)
clean: check-env
	@echo "WARNING: This will delete all containers and volumes (database data will be lost)"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		echo "Cleanup complete"; \
	else \
		echo "Cleanup cancelled"; \
	fi

# Complete fresh setup (for first run or full reset)
fresh: check-env
	@echo ""
	@echo "🚀 Starting fresh setup..."
	@echo ""
	@echo "Step 1: Building frontend..."
	@if [ ! -d "frontend" ]; then \
		echo "❌ Error: frontend directory not found"; \
		exit 1; \
	fi
	@if ! command -v bun &> /dev/null; then \
		echo "❌ Error: bun is not installed. Install from https://bun.sh"; \
		exit 1; \
	fi
	cd frontend && bun install && bun run build && cd ..
	@echo "✓ Frontend built successfully"
	@echo ""
	@echo "Step 2: Cleaning up old containers and volumes..."
	docker compose down -v
	@echo "✓ Cleanup complete"
	@echo ""
	@echo "Step 3: Building Docker images..."
	docker compose build
	@echo "✓ Docker images built"
	@echo ""
	@echo "Step 4: Starting services..."
	docker compose up -d
	@echo "⏳ Waiting for services to start..."
	@sleep 15
	@echo ""
	@echo "Step 5: Running database migrations..."
	@docker compose exec -T backend bash -c "cd /app/backend && alembic upgrade head"
	@echo "✓ Migrations complete"
	@echo ""
	@echo "Step 6: Creating initial data..."
	@docker compose exec -T backend bash -c "cd /app/backend && python app/initial_data.py"
	@echo "✓ Initial data created"
	@echo ""
	@echo "✅ Setup complete!"
	@echo "✓ Frontend is built and served by backend"
	@echo "✓ Volume mounts configured for development"
	@echo "✓ You can now edit backend files locally and changes will appear in the container"
	@echo ""
	@echo "Starting containers with logs..."
	@echo ""
	docker compose up

# Build images
build: check-env
	@echo "Building Docker images..."
	docker compose build

# Run migrations manually
migrate: check-env
	@echo "Running database migrations..."
	docker compose exec backend alembic upgrade head
	@echo "Running initial data setup..."
	docker compose exec backend python app/initial_data.py

# Restart containers
restart: check-env
	@echo "Restarting containers..."
	docker compose restart
	@echo "Containers restarted. Use 'make logs' to see logs"

# Show logs from all containers
logs: check-env
	@echo "Showing logs from all containers (Ctrl+C to stop)..."
	docker compose logs -f

# Show logs from backend only
logs-backend: check-env
	@echo "Showing backend logs (Ctrl+C to stop)..."
	docker compose logs -f backend

# Show logs from database only
logs-db: check-env
	@echo "Showing database logs (Ctrl+C to stop)..."
	docker compose logs -f db

# Show running containers
ps: check-env
	docker compose ps

# Open shell in backend container
shell-backend: check-env
	@echo "Opening shell in backend container..."
	docker compose exec backend bash

# Run tests
test: check-env
	@echo "Running tests..."
	docker compose exec backend pytest

# Check database connection
check-db: check-env
	@echo "Checking database connection..."
	docker compose exec db psql -U postgres -d app -c "SELECT NOW();"

# View database in adminer
view-db:
	@echo ""
	@echo "Opening Adminer (database web UI) at http://localhost:8080"
	@echo "Use these credentials:"
	@echo "  Server: db"
	@echo "  Username: postgres"
	@echo "  Password: (check .env file)"
	@echo ""

# Quick development workflow
dev-start: check-env build-frontend build up

dev-stop: down

dev-logs: logs-backend

# Health check
health: check-env
	@echo "Checking health status..."
	curl -s http://localhost:8000/api/v1/utils/health-check/ || echo "Backend not responding"

# Code quality and formatting
lint: check-env
	@echo "Running linters (ruff, mypy)..."
	docker compose exec backend ruff check app tests
	docker compose exec backend mypy app

format: check-env
	@echo "Formatting code with black and isort..."
	docker compose exec backend black app tests
	docker compose exec backend isort app tests

format-check: check-env
	@echo "Checking code formatting..."
	docker compose exec backend black --check app tests
	docker compose exec backend isort --check-only app tests

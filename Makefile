.PHONY: help up down clean fresh migrate logs restart ps build

# Use bash shell explicitly
SHELL := /bin/bash

# Default target
help:
	@echo "Available commands:"
	@echo ""
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
up:
	@echo "Starting containers with visible logs..."
	docker compose up

# Stop containers
down:
	@echo "Stopping containers..."
	docker compose down

# Remove containers and volumes (careful - deletes data!)
clean:
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
fresh: clean build
	@echo ""
	@echo "Starting fresh setup (first run)..."
	@echo "Containers will start and migrations will run automatically"
	@echo ""
	docker compose up -d
	@echo "Waiting 15 seconds for services to start..."
	@sleep 15
	@echo "Running database migrations..."
	@docker compose exec -T backend bash -c "cd /app/backend && alembic upgrade head"
	@echo "Creating initial data..."
	@docker compose exec -T backend bash -c "cd /app/backend && python app/initial_data.py"
	@echo ""
	@echo "✓ Setup complete! Starting containers with logs..."
	@echo ""
	docker compose up

# Build images
build:
	@echo "Building Docker images..."
	docker compose build

# Run migrations manually
migrate:
	@echo "Running database migrations..."
	docker compose exec backend alembic upgrade head
	@echo "Running initial data setup..."
	docker compose exec backend python app/initial_data.py

# Restart containers
restart:
	@echo "Restarting containers..."
	docker compose restart
	@echo "Containers restarted. Use 'make logs' to see logs"

# Show logs from all containers
logs:
	@echo "Showing logs from all containers (Ctrl+C to stop)..."
	docker compose logs -f

# Show logs from backend only
logs-backend:
	@echo "Showing backend logs (Ctrl+C to stop)..."
	docker compose logs -f backend

# Show logs from database only
logs-db:
	@echo "Showing database logs (Ctrl+C to stop)..."
	docker compose logs -f db

# Show running containers
ps:
	docker compose ps

# Open shell in backend container
shell-backend:
	@echo "Opening shell in backend container..."
	docker compose exec backend bash

# Run tests
test:
	@echo "Running tests..."
	docker compose exec backend pytest

# Check database connection
check-db:
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
dev-start: build up

dev-stop: down

dev-logs: logs-backend

# Health check
health:
	@echo "Checking health status..."
	curl -s http://localhost:8000/api/v1/utils/health-check/ || echo "Backend not responding"

# Code quality and formatting
lint:
	@echo "Running linters (ruff, mypy)..."
	docker compose exec backend ruff check app tests
	docker compose exec backend mypy app
format:
	@echo "Formatting code with black and isort..."
	docker compose exec backend black app tests
	docker compose exec backend isort app tests
format-check:
	@echo "Checking code formatting..."
	docker compose exec backend black --check app tests
	docker compose exec backend isort --check-only app tests

# Quick Start Guide - Makefile

## TL;DR - Just Run These Commands

### 🚀 First Time (Clean Start)
```bash
make fresh
```

This command:
1. Stops and removes all containers and volumes
2. Rebuilds Docker images
3. Starts all services (db, backend, adminer, etc.)
4. Waits 15 seconds for services to be ready
5. **Runs database migrations** (alembic upgrade head)
6. **Creates initial data** (admin user, etc.)
7. Shows all logs in foreground (press Ctrl+C to stop)

Opens http://localhost:8000 when ready

### 📅 Daily Start (Project Already Set Up)
```bash
make up
```
Shows all logs in terminal. Press `Ctrl+C` to stop.

### 📊 View Logs While Working (in Another Terminal)
```bash
make logs-backend
```

### 🔄 Restart After Code Changes
```bash
make restart
```

---

## Complete Workflow Example

### Scenario 1: Fresh Project Setup
```bash
# First time setup - deletes everything and starts fresh
make fresh

# Waits for services to start...
# Output:
#   Building backend...
#   Starting containers...
#   Waiting fresh setup (first run)...
#   
#   ✓ Containers started with visible logs

# Logs will display. You'll see:
# - Database migrations running
# - Initial data being created
# - Backend server starting up
# Press Ctrl+C when you see "Application startup complete"
```

Then open **http://localhost:8000** in browser

### Scenario 2: Stop and Restart
```bash
# Press Ctrl+C in the terminal running 'make up'

# Restart containers
make restart

# View just backend logs
make logs-backend
```

### Scenario 3: Clean Database and Start Over
```bash
# Ctrl+C in running terminal first

# Full cleanup (asks for confirmation)
make clean

# Then fresh setup
make fresh
```

---

## All Available Commands

| Command | What It Does | Logs |
|---------|------------|------|
| `make help` | Show this help text | ✓ |
| `make up` | Start containers | ✓ (all) |
| `make down` | Stop gracefully | ✗ |
| `make restart` | Restart running | ✓ (on restart) |
| `make clean` | Delete all + ask | ✗ |
| `make fresh` | clean + build + up | ✓ (all) |
| `make build` | Rebuild images | ✓ |
| `make logs` | Show all logs | ✓ (all) |
| `make logs-backend` | Show backend only | ✓ (backend) |
| `make logs-db` | Show database only | ✓ (db) |
| `make ps` | List containers | ✗ |
| `make migrate` | Run migrations manually | ✓ |
| `make check-db` | Test DB connection | ✓ |
| `make shell-backend` | SSH into backend | ✓ |
| `make test` | Run pytest | ✓ |
| `make health` | Check API health | ✗ |

---

## Common Issues & Fixes

### "Port 8000 already in use"
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>

# Then retry
make fresh
```

### "Too many open files"
✓ Fixed in compose.override.yml with proper ulimits and uvicorn (no watchfiles)

### "Tables don't exist"
```bash
# Migrations should run automatically, but if not:
make migrate
```

### "Frontend not updating"
```bash
make restart
```

### "Database connection error"
```bash
make check-db
make logs-db
```

---

## Services Available After Startup

Once containers are running, access:

- **Frontend**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Database UI (Adminer)**: http://localhost:8080
- **Email Inbox (Mailpit)**: http://localhost:8025
- **Traefik Dashboard**: http://localhost:8090

---

## Development Workflow

1. **Start work**
   ```bash
   make up
   ```

2. **Edit code** - backend changes are auto-synced

3. **View logs in another terminal**
   ```bash
   make logs-backend
   ```

4. **Stop** - Press `Ctrl+C` in the make up terminal

5. **Restart** if needed
   ```bash
   make restart
   ```

6. **Full reset** when needed
   ```bash
   make clean    # ask for confirmation
   make fresh
   ```

---

## Notes

- **No `-d` flags**: By default, commands show logs so you can see what's happening
- **File sync**: Backend code changes automatically sync via Docker compose
- **No watchfiles issues**: Using uvicorn directly instead of `fastapi dev`
- **Migrations**: Run automatically on first startup via `scripts/prestart.sh`
- **Confirmations**: Destructive commands (like `clean`) ask before doing anything

---

## Environment Variables

Edit `.env` to customize:
- `PROJECT_NAME` - Application name
- `SECRET_KEY` - Flask/FastAPI secret
- `POSTGRES_PASSWORD` - Database password
- `FIRST_SUPERUSER` - Admin username
- `FIRST_SUPERUSER_PASSWORD` - Admin password

See `.env` file for all options.



# Development Setup Guide

## Quick Start Issues & Solutions

### Issue 1: `pip: command not found` (asdf version manager)

**Problem:** asdf doesn't have a Python version set for this project.

**Solution A:** Set Python version with asdf

```bash
# Install Python 3.11 if not already installed
asdf plugin add python
asdf install python 3.11.4

# Set local version for this project
cd backend
asdf local python 3.11.4
cd ..

# Now retry
make be-install
```

**Solution B:** Use system Python

```bash
# If you have system Python 3.11+
which python3
python3 --version

# Install deps directly
cd backend
python3 -m pip install -r requirements-dev.txt
cd ..
```

**Solution C:** Run everything in Docker (recommended for consistency)

```bash
# Run tests in container
docker exec sysdesign_backend pytest -v

# Run guardrails in container
docker exec sysdesign_backend black --check src/
docker exec sysdesign_backend ruff check src/
docker exec sysdesign_backend mypy
```

---

### Issue 2: Backend not responding to curl

**Diagnosis:**

```bash
# Check container status
docker ps | grep sysdesign

# Check backend logs
docker logs sysdesign_backend

# Check if uvicorn is running
docker exec sysdesign_backend ps aux | grep uvicorn
```

**Common causes:**

1. **App failed to start** - syntax error or import error
2. **Still starting up** - wait 5-10 seconds after `make up`
3. **Wrong port** - verify port 8000 is exposed

**Fix:**

```bash
# Restart with fresh logs
make down
make up

# Wait for healthy status
sleep 5

# Test health endpoint
curl http://localhost:8000/api/health

# If still fails, check detailed logs
docker logs sysdesign_backend --follow
```

---

### Issue 3: Makefile assumes host Python environment

The current Makefile assumes you have Python installed on the host. For Docker-first development:

**Option 1: Install deps on host (for IDE autocomplete, linting)**

```bash
# After fixing asdf Python version
make be-install
```

**Option 2: Use Docker for everything**

```bash
# Add these to Makefile or run directly:

# Run tests in container
docker exec sysdesign_backend pytest -v

# Format code in container
docker exec sysdesign_backend black src/

# Lint in container
docker exec sysdesign_backend ruff check src/

# Type check in container
docker exec sysdesign_backend mypy
```

---

## Recommended Development Workflow

### 1. Docker-First (Simplest, most consistent)

```bash
# Start services
make up

# Watch logs
make logs

# Run tests (add to Makefile)
docker exec sysdesign_backend pytest -v

# Access backend shell
docker exec -it sysdesign_backend bash
```

**Pros:** No host Python dependencies, consistent environment  
**Cons:** Slower feedback loop, less IDE integration

### 2. Hybrid (Best for development)

```bash
# Fix asdf Python version ONCE
cd backend
asdf local python 3.11.4

# Install deps on host ONCE
make be-install

# Start Docker services (DB only, run backend on host)
docker-compose up -d postgres

# Run backend on host for hot reload
cd backend
PYTHONPATH=src DATABASE_URL=postgresql+psycopg://lab:lab@localhost:5432/lab \
  uvicorn app.api.main:app --reload

# In another terminal: run tests/guardrails locally
make be-test
make guardrails
```

**Pros:** Fast feedback, full IDE support, hot reload  
**Cons:** Requires host Python setup

---

## Current Status Check

Run this to verify system state:

```bash
echo "=== Python ===" && python3 --version 2>&1 || echo "Python not found"
echo -e "\n=== Docker ===" && docker --version
echo -e "\n=== Containers ===" && docker ps --filter "name=sysdesign"
echo -e "\n=== Backend Health ===" && curl -s http://localhost:8000/api/health || echo "Backend not responding"
```

---

## Next Steps for Frontend Branch

Once backend is validated:

```bash
# 1. Verify backend works
curl http://localhost:8000/api/health
curl http://localhost:8000/api/sim/scenarios

# 2. Initialize frontend
cd frontend  # (doesn't exist yet)
npm create vite@latest . -- --template react-ts
npm install

# 3. Add dependencies
npm install @tanstack/react-query axios
npm install -D @playwright/test prettier eslint

# 4. Start development
npm run dev
```

---

## Troubleshooting Commands

```bash
# Nuclear option: reset everything
make down
docker system prune -f
make up

# Check backend startup errors
docker logs sysdesign_backend 2>&1 | grep -i error

# Enter backend container for debugging
docker exec -it sysdesign_backend bash

# Inside container, test imports
cd /app
python3 -c "from app.api.main import app; print('✓ Imports work')"

# Test DB connection from container
docker exec sysdesign_backend python3 -c "import psycopg; psycopg.connect('postgresql://lab:lab@postgres:5432/lab')"
```

---

## Known Issues

1. **asdf Python version not set** → Set with `asdf local python 3.11.4`
2. **Backend logs show import errors** → Check PYTHONPATH and file structure
3. **Port 8000 already in use** → Kill process or change port in docker-compose.yml
4. **Postgres connection refused** → Wait for health check, check docker-compose logs

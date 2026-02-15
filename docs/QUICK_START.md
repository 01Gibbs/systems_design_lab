# Quick Reference - Frontend Branch Setup

## ⚠️ Current Issues Detected

Based on your command output:

1. ✅ **Docker services started successfully** (postgres + backend containers running)
2. ❌ **Host Python not configured** (`pip` command not found - asdf issue)
3. ❌ **Backend not responding** (curl failures - need to investigate)

---

## 🔧 Immediate Actions Required

### Step 1: Check Backend Container Logs

```bash
# View backend logs to see startup errors
docker logs sysdesign_backend

# Look for:
# - Import errors (ModuleNotFoundError)
# - Syntax errors
# - Port binding issues
# - Database connection failures
```

### Step 2: Choose Your Development Approach

#### Option A: Docker-Only Workflow (Recommended for Now)

**Pros:** No host Python setup needed, consistent environment
**Cons:** Slightly slower feedback loop

```bash
# Run all tests in container
./scripts/dev-container.sh test

# Run all guardrails checks
./scripts/dev-container.sh all

# Test backend health manually
docker exec sysdesign_backend curl -v http://localhost:8000/api/health

# View scenarios endpoint
docker exec sysdesign_backend curl http://localhost:8000/api/sim/scenarios | jq

# Open shell for debugging
make be-docker-shell
```

#### Option B: Fix Host Python + Hybrid Workflow

**Pros:** Fast feedback, IDE integration, hot reload
**Cons:** Requires one-time setup

```bash
# 1. Install Python 3.11 with asdf
asdf plugin add python
asdf install python 3.11.4
cd backend
asdf local python 3.11.4
cd ..

# 2. Install dependencies on host
make be-install

# 3. Run only Postgres in Docker, backend on host
docker-compose up -d postgres
docker-compose stop backend

# 4. Run backend locally with hot reload
cd backend
PYTHONPATH=src DATABASE_URL=postgresql+psycopg://lab:lab@localhost:5432/lab \
  uvicorn app.api.main:app --reload --port 8000

# 5. In another terminal: run tests/guardrails locally
make be-test
make guardrails
```

---

## 🎯 Frontend Development Next Steps

Once backend is validated:

### 1. Create Frontend Directory Structure

```bash
# Create frontend directory
mkdir -p frontend

# Initialize Vite project with React + TypeScript
cd frontend
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install

# Install key packages
npm install @tanstack/react-query axios zod
npm install -D @playwright/test prettier eslint @types/node

# Create directory structure
mkdir -p src/{api,components,pages,hooks,types}
```

### 2. Key Files to Create

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          # Axios instance with interceptors
│   │   └── simulator.ts       # Typed simulator API calls
│   ├── components/
│   │   ├── ScenarioCard.tsx       # Individual scenario display
│   │   ├── ScenarioList.tsx       # List of available scenarios
│   │   ├── ActiveIndicator.tsx    # Banner showing active scenarios
│   │   └── ErrorBoundary.tsx      # Error handling
│   ├── pages/
│   │   └── SimulatorControlPanel.tsx  # Main page
│   ├── hooks/
│   │   └── useSimulator.ts    # React Query hooks
│   └── types/
│       └── simulator.ts       # TypeScript types from OpenAPI
├── e2e/
│   └── simulator.spec.ts      # Playwright tests
├── .prettierrc.json
├── .eslintrc.json
└── playwright.config.ts
```

### 3. Generate Types from OpenAPI

```bash
# Option 1: Use openapi-typescript
npm install -D openapi-typescript
npx openapi-typescript ../openapi.json -o src/types/api.d.ts

# Option 2: Use openapi-generator-cli
npm install -D @openapitools/openapi-generator-cli
npx openapi-generator-cli generate \
  -i ../openapi.json \
  -g typescript-axios \
  -o src/api/generated
```

### 4. Update docker-compose.yml

```yaml
services:
  # ... existing services ...

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sysdesign_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host 0.0.0.0
```

---

## 🧪 Testing Strategy for Frontend

### Unit Tests (Vitest)

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm run test:unit
```

### E2E Tests (Playwright)

```typescript
// e2e/simulator.spec.ts
test("enable fixed-latency scenario", async ({ page }) => {
  // Enable scenario via API
  await request.post("http://localhost:8000/api/sim/enable", {
    data: { scenario: "fixed-latency", parameters: { ms: 500 } },
  });

  // Verify UI shows active scenario
  await page.goto("http://localhost:5173");
  await expect(page.locator('[data-testid="active-banner"]')).toContainText(
    "fixed-latency",
  );

  // Verify API calls are delayed
  const startTime = Date.now();
  await page.click('[data-testid="refresh-scenarios"]');
  const endTime = Date.now();
  expect(endTime - startTime).toBeGreaterThan(500);
});
```

---

## 📋 Acceptance Criteria Checklist

Before merging `feature/frontend-simulator-ui`:

- [ ] Backend is healthy and responding
- [ ] Frontend Vite project initialized
- [ ] Typed API client generated from OpenAPI
- [ ] SimulatorControlPanel component complete
  - [ ] Lists all 16 scenarios with descriptions
  - [ ] Can enable scenarios with parameters
  - [ ] Shows active scenarios with expiry times
  - [ ] Can disable individual scenarios
  - [ ] Can reset all scenarios
- [ ] ActiveIndicator banner shows when scenarios active
- [ ] Error boundaries handle backend failures gracefully
- [ ] Loading states for all async operations
- [ ] Playwright E2E tests pass
  - [ ] Test: Enable fixed-latency, verify delay
  - [ ] Test: Enable error-burst, verify resilience
  - [ ] Test: UI remains functional under chaos
- [ ] docker-compose.yml includes frontend service
- [ ] Makefile frontend commands work
- [ ] README updated with frontend instructions
- [ ] `make guardrails` passes (backend)
- [ ] `make fe-lint && make fe-typecheck && make fe-test-e2e` passes

---

## 🐛 Current Debugging Commands

```bash
# Check what's wrong with backend
docker logs sysdesign_backend 2>&1 | tail -50

# Check if Python imports work in container
docker exec sysdesign_backend python3 -c "from app.api.main import app; print('OK')"

# Check if container can reach health endpoint internally
docker exec sysdesign_backend curl http://localhost:8000/api/health

# Check container network
docker exec sysdesign_backend netstat -tlnp

# Restart backend with fresh state
docker restart sysdesign_backend
sleep 5
curl http://localhost:8000/api/health
```

---

## 📞 Next Steps RIGHT NOW

1. **Run:** `docker logs sysdesign_backend` → Check for startup errors
2. **Fix:** Whatever error is preventing backend from starting
3. **Validate:** `./scripts/dev-container.sh test` → Ensure tests pass
4. **Proceed:** Initialize frontend with Vite once backend is healthy

---

**Quick Reference Commands:**

```bash
make status                    # Check system health
make be-docker-test           # Run tests in container
make be-docker-all           # Run all checks in container
./scripts/dev-container.sh shell  # Debug in container
docker logs sysdesign_backend      # View backend logs
```

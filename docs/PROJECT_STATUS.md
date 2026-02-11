# Project Status

**Last Updated:** February 10, 2026

## 🎯 Project Goal

Production-grade local systems design lab for simulating 50+ real-world system issues with strict Clean Architecture and contract-first API design.

---

## ✅ Phase 1: Foundation & Backend (COMPLETE)

### Backend Architecture

- ✅ Clean Architecture with Ports & Adapters pattern
- ✅ Dependency injection via composition root ([api/main.py](backend/src/app/api/main.py))
- ✅ Port interfaces: [Clock](backend/src/app/application/ports/clock.py), [SimulatorStore](backend/src/app/application/ports/simulator_store.py)
- ✅ Infrastructure adapters: SystemClock, InMemorySimulatorStore
- ✅ FastAPI application with middleware (RequestId, SimulatorInjection, CORS)
- ✅ Routers: `/api/health`, `/api/sim/*`

### Simulator Framework

- ✅ Effect-based scenario pattern (scenarios return dicts, middleware applies)
- ✅ Registry pattern for dynamic scenario management
- ✅ 5 starter scenarios implemented:
  - `fixed-latency` - Add HTTP latency
  - `error-burst` - Probabilistic 5xx errors
  - `slow-db-query` - Slow DB operations
  - `lock-contention` - Concurrent update conflicts
  - `algorithmic-degradation` - O(n) vs O(n²) performance

### Infrastructure

- ✅ Docker Compose with Postgres 16 + Backend
- ✅ Health checks and service dependencies
- ✅ Volume management for data persistence

### Guardrails

- ✅ Architecture boundary checker ([arch_check.py](backend/src/app/guardrails/arch_check.py))
- ✅ Contract drift checker ([contracts_check.py](backend/src/app/guardrails/contracts_check.py))
- ✅ Contract acceptance tool ([contracts_accept.py](backend/src/app/guardrails/contracts_accept.py))
- ✅ Makefile with all enforcement commands

### Testing

- ✅ Unit tests for simulator registry
- ✅ Unit tests for infrastructure adapters
- ✅ Pytest + pytest-cov setup
- ✅ Test structure: `backend/tests/unit/`

### Documentation

- ✅ [README.md](README.md) with quick start and architecture
- ✅ [.github/copilot-instructions.md](.github/copilot-instructions.md) for AI agents
- ✅ [Makefile](Makefile) with comprehensive commands (host + Docker)
- ✅ [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) for environment setup
- ✅ [QUICK_START.md](QUICK_START.md) for immediate troubleshooting
- ✅ [docs/FRONTEND_IMPLEMENTATION.md](docs/FRONTEND_IMPLEMENTATION.md) for frontend work
- ✅ Helper scripts: `scripts/dev-container.sh`, `scripts/status.sh`, `scripts/diagnose.sh`
- ✅ All docs updated to reflect actual structure (backend/src/app/)

---

## 🚧 Phase 2: Frontend (NEXT - Branch: `feature/frontend-simulator-ui`)

### Goals

- [ ] Vite + TypeScript + React project setup
- [ ] Typed API client generated from OpenAPI contracts
- [ ] SimulatorControlPanel component
  - [ ] List available scenarios
  - [ ] Enable/disable scenarios with parameters
  - [ ] View active scenarios
  - [ ] Reset all scenarios
- [ ] Active scenario indicator (banner/header)
- [ ] Error boundaries and loading states
- [ ] Playwright E2E tests
  - [ ] Enable scenario via API
  - [ ] Validate UI behavior under failure
- [ ] CI/CD integration for frontend checks

### Acceptance Criteria

- Frontend can list all 5 scenarios from backend
- Can enable `fixed-latency` and observe delayed responses
- Can enable `error-burst` and observe intermittent failures
- UI remains functional when backend is slow/failing
- E2E tests validate resilience to simulator scenarios
- `make fe-install`, `make fe-format`, `make fe-lint`, `make fe-typecheck`, `make fe-test-e2e` all work

---

## ⏳ Phase 3: Scenario Expansion (PENDING)

### Goals

- [ ] Implement 45 additional scenarios (total 50)
- [ ] Categories:
  - [ ] Latency & Timeouts (10 scenarios)
  - [ ] HTTP Failures (10 scenarios)
  - [ ] Database Issues (10 scenarios)
  - [ ] Caching Failures (5 scenarios)
  - [ ] Concurrency Issues (5 scenarios)
  - [ ] Resource Exhaustion (5 scenarios)
  - [ ] Network Partitions (5 scenarios)

### Scenario Catalogue Target

See [copilot-instructions.md](.github/copilot-instructions.md) for full scenario list.

---

## ⏳ Phase 4: Integration Testing (PENDING)

### Goals

- [ ] Testcontainers setup for real Postgres
- [ ] Integration tests for DB adapters
- [ ] Integration tests for simulator store (Redis adapter)
- [ ] Contract tests for OpenAPI validation
- [ ] Coverage enforcement (85%+ threshold)

### Structure

```
backend/tests/
├── unit/              ✅ Complete
├── integration/       ⏳ Pending
└── contract/          ⏳ Pending
```

---

## ⏳ Phase 5: Observability (FUTURE)

### Goals

- [ ] Prometheus metrics export
- [ ] Grafana dashboards
- [ ] Loki for log aggregation
- [ ] OpenTelemetry instrumentation
- [ ] Distributed tracing

### Current State

- ✅ Request correlation ready (request_id/trace_id)
- ✅ Structured logging in place
- ✅ Code structured for future instrumentation

---

## 📊 Progress Metrics

| Category             | Progress | Status         |
| -------------------- | -------- | -------------- |
| Backend Architecture | 5/5      | ✅ Complete    |
| Simulator Scenarios  | 5/50     | 🔄 10%         |
| Frontend             | 0/1      | ⏳ Not Started |
| Unit Tests           | 2/∞      | 🔄 Baseline    |
| Integration Tests    | 0/∞      | ⏳ Not Started |
| E2E Tests            | 0/∞      | ⏳ Not Started |
| Observability        | 0/4      | ⏳ Not Started |

---

## 🔧 Technical Debt

1. **OpenAPI Snapshot**: `openapi.json` exists but may not be current - needs validation
2. **Template Scenario**: No template file exists - use existing scenarios as reference
3. **Redis Adapter**: InMemorySimulatorStore works but Redis adapter pending for production
4. **Coverage**: Only 2 basic unit tests - need comprehensive test coverage

---

## 🚀 Recommended Next Steps

1. **Create branch**: `git checkout -b feature/frontend-simulator-ui`
2. **Initialize frontend**: Vite + TypeScript + React
3. **Generate API client**: From `openapi.json`
4. **Build SimulatorControlPanel**: Core UI component
5. **Add E2E tests**: Validate scenarios work end-to-end
6. **Merge & validate**: Ensure `make guardrails` passes

---

## 🎓 Learning Opportunities

This lab enables hands-on practice with:

- Clean Architecture & Ports/Adapters pattern
- Contract-first API design with OpenAPI
- Effect-based dependency injection
- Resilient frontend patterns
- Systems design failure modes
- Test pyramid (unit → integration → E2E)
- Observability patterns (future)

---

## 📝 Notes

- All guardrails are enforced via `make guardrails`
- Domain layer is pure - no framework imports
- Simulator scenarios are effect-based - no side effects in scenario code
- Frontend will validate entire stack works end-to-end

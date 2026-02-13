# Project Status

**Last Updated:** February 12, 2026

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
- ✅ 15 scenarios implemented:
  - `fixed-latency` - Add HTTP latency
  - `error-burst` - Probabilistic 5xx errors
  - `slow-db-query` - Slow DB operations
  - `lock-contention` - Concurrent update conflicts
  - `algorithmic-degradation` - O(n) vs O(n²) performance
  - `circuit-breaker` - Circuit breaker pattern simulation
  - `retry-storm` - Retry amplification failures
  - `connection-pool-exhaustion` - Connection pool depletion
  - `cache-stampede` - Thundering herd on cache miss
  - `cpu-spike` - CPU usage spikes
  - `memory-leak` - Memory leak simulation
  - `disk-full` - Disk space exhaustion
  - `network-partition` - Network split-brain scenarios
  - `clock-skew` - Time synchronization issues
  - `resource-starvation` - Resource contention simulation

### Infrastructure

- ✅ Docker Compose with Postgres 16 + Backend
- ✅ Health checks and service dependencies
- ✅ Volume management for data persistence

### Guardrails & Automation

- ✅ Architecture boundary checker ([arch_check.py](backend/src/app/guardrails/arch_check.py))
- ✅ Contract drift checker ([contracts_check.py](backend/src/app/guardrails/contracts_check.py))
- ✅ Contract acceptance tool ([contracts_accept.py](backend/src/app/guardrails/contracts_accept.py))
- ✅ Contract snapshot at project root (`openapi.json`)
- ✅ Makefile with all enforcement commands
- ✅ GitHub Actions CI workflow enforcing guardrails + coverage
- ✅ Pre-commit hooks for local enforcement
- ✅ Automated workspace cleanup (`make autoclean`)
- ✅ See [CI_AND_PRECOMMIT.md](docs/CI_AND_PRECOMMIT.md) for full CI/CD setup

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

## ✅ Phase 2: Frontend (COMPLETE)

### Frontend Implementation

- ✅ Vite + TypeScript + React project setup
- ✅ Typed API client ([api/client.ts](frontend/src/api/client.ts), [api/types.ts](frontend/src/api/types.ts))
- ✅ SimulatorControlPanel component ([pages/SimulatorControlPanel.tsx](frontend/src/pages/SimulatorControlPanel.tsx))
  - ✅ List available scenarios with descriptions
  - ✅ Enable/disable scenarios with parameter validation
  - ✅ View active scenarios with expiry times
  - ✅ Reset all scenarios
- ✅ Active scenario indicator ([components/GlobalBanner.tsx](frontend/src/components/GlobalBanner.tsx))
- ✅ Component library: ScenarioCard, ActiveScenarios
- ✅ Form validation with Zod schemas
- ✅ Error boundaries and loading states
- ✅ Tailwind CSS styling
- ✅ Vitest for unit/integration tests
- ✅ Playwright E2E tests ([tests/e2e/](frontend/tests/e2e/))
  - ✅ Enable scenario via API
  - ✅ Validate UI behavior under failure
  - ✅ Error handling and resilience tests
- ✅ Frontend Makefile commands: `fe-install`, `fe-format`, `fe-lint`, `fe-typecheck`, `fe-test-e2e`
- ✅ See [FRONTEND_IMPLEMENTATION.md](docs/FRONTEND_IMPLEMENTATION.md) for architecture details

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

## ✅ Phase 5: Observability (COMPLETE)

### Implementation

- ✅ Prometheus metrics collection with auto-instrumented HTTP metrics
- ✅ Grafana dashboards (System Metrics + Simulator Scenarios)
- ✅ Loki log aggregation with structured JSON logs
- ✅ Tempo distributed tracing with OpenTelemetry
- ✅ Promtail log shipping from Docker containers
- ✅ Clean Architecture compliant (MetricsPort interface + PrometheusMetrics adapter)
- ✅ Simulator metrics integration (active scenarios, injection tracking)
- ✅ Request correlation (request_id + trace_id + span_id)
- ✅ Makefile commands: `grafana`, `prometheus`, `logs-obs`, `metrics`
- ✅ Complete documentation in [OBSERVABILITY.md](OBSERVABILITY.md)

### Stack

- **Prometheus** - Metrics scraping from `/api/metrics` endpoint
- **Grafana** - Pre-provisioned dashboards + datasources
- **Loki** - Log aggregation with 7-day retention
- **Tempo** - Trace storage with 48-hour retention
- **Promtail** - Docker log shipping

### Metrics Available

- `http_requests_total` - HTTP request counter by method/endpoint/status
- `http_request_duration_seconds` - Request latency histogram
- `simulator_scenarios_enabled` - Active scenarios (gauge)
- `simulator_scenarios_active_total` - Scenario activation counter
- `simulator_injections_total` - Effect injection counter by scenario/type
- `simulator_effect_duration_seconds` - Effect application time

### Dashboards

1. **System Metrics** - HTTP metrics, error rates, application logs
2. **Simulator Scenarios** - Active scenarios, injection rates, effect durations

---

## ⏳ Phase 6: Scenario Expansion (PENDING)

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
| Simulator Scenarios  | 15/50    | 🔄 30%         |
| Frontend             | 1/1      | ✅ Complete    |
| CI/CD Enforcement    | 1/1      | ✅ Complete    |
| Backend Unit Tests   | 41+      | ✅ 92%+ cov    |
| Frontend Tests       | 14       | ✅ Passing     |
| E2E Tests            | 3        | ✅ Passing     |
| Integration Tests    | 0/∞      | ⏳ Not Started |
| Observability        | 4/4      | ✅ Complete    |

---

## 🔧 Technical Debt

1. **Scenario Expansion**: Only 15/50 scenarios implemented - 35 more to add
2. **Template Scenario**: No template file - use existing scenarios as reference
3. **Redis Adapter**: InMemorySimulatorStore works but Redis adapter pending for production
4. **Integration Tests**: Need testcontainers + real Postgres integration tests
5. **Observability Alerting**: No alerting rules configured yet (Grafana supports this)

---

## 🚀 Recommended Next Steps

1. **Scenario Expansion** (High Impact): Add 10-15 new scenarios
   - Circuit breakers, cascading failures
   - Retry storms, rate limiting
   - Connection pool exhaustion, deadlocks
   - Cache stampede, stale data
   - **Now easier to debug with observability dashboards!**

2. **Integration Testing** (Infrastructure):
   - Add testcontainers setup
   - Real Postgres integration tests
   - Increase test coverage for edge cases

3. **Observability Enhancements** (Polish):
   - Grafana alert rules (e.g., p95 > 1s for 5 min)
   - Custom dashboards for specific scenarios
   - Trace sampling for high-volume scenarios

---

## 🎓 Learning Opportunities

This lab enables hands-on practice with:

- Clean Architecture & Ports/Adapters pattern
- Contract-first API design with OpenAPI
- Effect-based dependency injection
- Resilient frontend patterns
- Systems design failure modes
- Test pyramid (unit → integration → E2E)
- Production observability patterns (metrics, logs, traces)

---

## 📝 Notes

- All guardrails are enforced via `make guardrails`
- Domain layer is pure - no framework imports
- Simulator scenarios are effect-based - no side effects in scenario code
- Frontend validates entire stack works end-to-end
- Observability stack respects Clean Architecture (MetricsPort interface)
- Grafana dashboards auto-reload on file change

# Systems Design Lab - AI Agent Instructions

## Core Purpose & Philosophy

This is a **production-grade local systems design lab** — NOT a demo app or one-off tutorial. It exists to:

- Provide a stable, maintainable baseline application with strict guardrails
- Enable deliberate, repeatable simulation of **100+ real-world system issues**
- Support deep hands-on learning: systems design, CQRS, event sourcing, caching, observability, DSA, performance, resilience
- Offer guided tutorials teaching distributed systems concepts
- Demonstrate production patterns with observable failure modes

**Vision**: The most comprehensive systems design learning platform (see [ROADMAP.md](../docs/ROADMAP.md))

**Critical constraints:**

- Clean Architecture is MANDATORY and automatically enforced
- Contract-first API design is MANDATORY and automatically enforced
- Maintainability is first-class; guardrails prevent drift
- Developer UX matters: Makefile provides single entry point
- All failure modes must be observable (metrics/logs/traces)

## Project Roadmap & Current Phase

**Current Phase**: Phase 4E - New Scenario Implementation (32% complete - 16/50 scenarios)

### Completed Phases

- ✅ **Phase 1**: Foundation & Backend
- ✅ **Phase 2**: Frontend & E2E
- ✅ **Phase 3**: Observability Stack (Prometheus + Grafana + Loki + Tempo)
- ✅ **Phase 4A**: Metrics Framework - MetricSpec and dynamic registration
- ✅ **Phase 4B**: Retrofit Existing Scenarios - All 16 scenarios have domain-specific metrics

### Active Phase

- 🔄 **Phase 4E**: New Scenarios (16 implemented, 34 remaining)
  - Priority: Caching & Data Consistency, Database Patterns, API & Network, Concurrency

### Upcoming Phases

- ⏳ **Phase 5**: Guided Tutorials (6 series, 24+ tutorials)
- ⏳ **Phase 6**: CQRS/Event Sourcing Module
- ⏳ **Phase 7**: Production Readiness (Redis, Multi-tenancy, K8s)
- ⏳ **Phase 8**: Interactive Documentation (Docusaurus site)
- ⏳ **Phase 9**: Advanced Scenarios (100+ total)

**Full Roadmap**: [docs/ROADMAP.md](../docs/ROADMAP.md)
**Scenario Tracker**: [docs/SCENARIO_TRACKER.md](../docs/SCENARIO_TRACKER.md)
**Project Status**: [docs/PROJECT_STATUS.md](../docs/PROJECT_STATUS.md)

## Technology Stack (NON-NEGOTIABLE)

**Frontend:** Vite + TypeScript + Playwright
**Backend:** Python + FastAPI + Uvicorn
**Database:** PostgreSQL (local, Docker)
**Infrastructure:** Docker Compose (local only)

**Forbidden:** cloud services, serverless, magic generators that bypass contracts

## Project Structure

```
/
├── backend/
│   ├── src/app/          # Namespaced application code
│   │   ├── api/          # Routers only, no business logic
│   │   ├── application/  # Use-cases, command/query handlers
│   │   │   ├── ports/    # Port interfaces (Clock, SimulatorStore, etc.)
│   │   │   └── simulator/
│   │   │       └── scenarios/  # Effect-based simulator scenarios
│   │   ├── contracts/    # Request/response models (Pydantic)
│   │   ├── domain/       # Entities, value objects (NO framework imports)
│   │   ├── guardrails/   # Boundary + contract enforcement
│   │   └── infrastructure/  # Adapters (DB, cache, time, simulator store)
│   ├── tests/
│   │   ├── unit/         # Fast tests, no external dependencies
│   │   └── integration/  # Real DB tests (testcontainers)
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/             # (Not yet implemented)
│   ├── src/
│   │   ├── api/          # Typed API client (contract-derived)
│   │   ├── components/
│   │   └── pages/
│   │       └── SimulatorControlPanel.tsx
│   └── e2e/              # Playwright tests
├── docker-compose.yml
├── Makefile              # Single developer entry point
└── openapi.json          # Checked-in OpenAPI snapshot
```

## Clean Architecture Rules (STRICT)

**Layer boundaries:**

- `domain/` imports NOTHING (no FastAPI, SQLAlchemy, HTTP, etc.)
- `application/` imports domain only
- `api/` imports application + contracts only
- `infrastructure/` imports application + domain, but domain/application import ONLY interfaces

**Enforcement:** `make arch-check` fails on violations (see guardrails/)

## Contract-First Development (STRICT)

**All external communication is contract-first:**

1. Define explicit request/response models (Pydantic in `contracts/`)
2. Generate OpenAPI from models
3. Check in `openapi.json` as snapshot
4. `make contracts-check` fails if OpenAPI drifts without explicit acceptance
5. Frontend uses typed API client derived from contract

**Breaking a contract is a failure. Silent schema drift is forbidden.**

Commands:

- `make contracts-check` — fail on drift
- `make contracts-accept` — regenerate snapshot intentionally

## Issue Simulator Framework (FIRST-CLASS)

The simulator is a first-class, extensible subsystem for injecting 50+ real-world failure modes.

**Architecture:**

- Each scenario is a separate class implementing `Scenario` interface
- Registry pattern: add new scenarios without modifying core
- Each scenario declares: name, description, parameter schema, targets, injection points, safety limits
- Scenarios are runtime-configurable (enable/disable, probability, duration)

**API endpoints:**

- `GET /api/sim/scenarios` — list available scenarios + schemas
- `GET /api/sim/status` — active scenarios + params + expiry
- `POST /api/sim/enable` — enable scenario with params
- `POST /api/sim/disable` — disable scenario
- `POST /api/sim/reset` — disable all

**Injection mechanism:**

- FastAPI middleware/dependency hooks for request/response behaviours
- Adapter wrapping for DB/cache behaviours
- NO simulator logic in domain layer

**Implemented scenarios (16/50 core, see [SCENARIO_TRACKER.md](../docs/SCENARIO_TRACKER.md)):**

1. Fixed latency injection (per route)
2. Error burst (probabilistic 5xx)
3. Slow DB query path
4. Lock contention (concurrent updates same row)
5. Algorithmic degradation (O(n) vs O(n²))
6. Circuit breaker pattern simulation
7. Retry storm (retry amplification)
8. Connection pool exhaustion
9. Cache stampede (thundering herd)
10. CPU spike simulation
11. Memory leak simulation
12. Disk full simulation
13. Network partition (split-brain)
14. Clock skew (time sync issues)
15. Resource starvation
16. Stale read (serve stale cache data)

**Target:** 50 core scenarios + 50+ advanced scenarios (100+ total)

**Priority categories for Phase 4:**

- Caching & Data Consistency (4 scenarios) - `cache-warming-failure`, `cache-invalidation-race`, etc.
- Database Patterns (5 scenarios) - `n-plus-one-query`, `missing-index`, `deadlock`, etc.
- API & Network (5 scenarios) - `rate-limit`, `timeout-cascade`, etc.
- Concurrency & Race Conditions (5 scenarios) - `double-write`, `optimistic-locking-collision`, etc.
- Plus 15 additional scenarios across latency, HTTP failures, resources

**See [SCENARIO_TRACKER.md](../docs/SCENARIO_TRACKER.md) for complete list and implementation status.**

## Guardrails & Enforcement (Packwerk-Style)

**`guardrails/` package enforces:**

1. **Contract drift checker:** Fail if OpenAPI changes vs snapshot
2. **Architecture boundary checker:** Fail on layer violations (domain importing FastAPI, etc.)
3. **Forbidden import checker:** Prevent framework leakage into domain
4. **CI-friendly output:** Clear errors pointing to offending files

Commands:

- `make guardrails` — run all checks
- `make arch-check` — architecture boundaries only
- `make contracts-check` — contract drift only
- `make contracts-accept` — accept contract changes

## Testing Strategy (Production-Grade)

**Backend:**

- `pytest` + `pytest-cov` with coverage gate
- `hypothesis` for property tests where valuable
- Integration tests use real Postgres (`testcontainers` preferred)
- Test pyramid: fast unit tests (domain/application), integration tests (DB), contract tests (OpenAPI), minimal API tests (wiring)
- **Forbidden:** mock-heavy tests, mixing concerns, flaky sleeps

**Frontend:**

- **Vitest** for unit and integration tests (fast, native ESM, Vite-compatible)
- **Playwright** for E2E tests (UI, resilience, failure modes)
- E2E tests must enable simulator scenarios via backend API
- Validate UI behaviour under those scenarios
- Avoid brittle timing-based tests

## Python Tooling (NON-NEGOTIABLE)

- **black** (formatting)
- **ruff** (linting; do NOT use ruff-format)
- **mypy** (type checking)
- **pytest** + **pytest-cov** (testing + coverage)
- **hypothesis** (property testing)
- **testcontainers** or docker-compose (integration tests)

## TypeScript Tooling

- **prettier** (formatting)
- **eslint** (linting)
- **tsc --noEmit** (type checking)
- **vitest** (unit/integration testing)
- **playwright** (E2E testing)

## Makefile Commands (Required Interface)

**Dev lifecycle:**

```bash
make up              # Start docker compose + services
make down            # Stop services
make reset           # Stop + remove volumes
make logs            # Tail logs
```

**Backend:**

```bash
make be-install      # Install dependencies
make be-format       # Format with black
make be-lint         # Lint with ruff
make be-typecheck    # Type check with mypy
make be-test         # Run all tests
make be-test-unit    # Unit tests only
make be-test-integration  # Integration tests only
make be-coverage     # Enforce coverage threshold
```

**Frontend:**

```bash
make fe-install      # Install dependencies
make fe-format       # Format with prettier
make fe-lint         # Lint with eslint
make fe-typecheck    # Type check with tsc
make fe-test         # Run all Vitest unit/integration tests
make fe-test-e2e     # Playwright E2E tests
```

**Guardrails:**

```bash
make guardrails      # Run all: format check, lint, typecheck, tests, arch-check, contracts-check
make contracts-check # Fail on contract drift
make contracts-accept # Accept contract changes
make arch-check      # Fail on boundary violations
```

## Frontend Requirements

**Must include:**

- Simulator Control Panel page (enable/disable scenarios)
- Active scenario indicator (banner/header)
- Resilient to slow/failing/inconsistent APIs
- Centralized, typed API access (no scattered fetch)

**Playwright tests must:**

- Enable simulator scenarios via backend API
- Validate UI behaviour under those scenarios

## Observability Stack (COMPLETE - Phase 3)

**Implemented:**

- ✅ Prometheus metrics collection with auto-instrumented HTTP metrics
- ✅ Grafana dashboards (System Metrics + Simulator Scenarios)
- ✅ Loki log aggregation with structured JSON logs
- ✅ Tempo distributed tracing with OpenTelemetry
- ✅ Request correlation (request_id + trace_id + span_id)
- ✅ Clean Architecture compliant (MetricsPort interface + PrometheusMetrics adapter)

**Makefile commands:**

```bash
make grafana      # Open Grafana dashboards (http://localhost:3000)
make prometheus   # Open Prometheus UI (http://localhost:9090)
make metrics      # Fetch backend metrics endpoint
make logs-obs     # Tail observability stack logs
```

**Documentation:** See [docs/OBSERVABILITY.md](../docs/OBSERVABILITY.md) for complete guide.

**Key Principle:** Observability respects Clean Architecture - never inject Prometheus directly into domain/application layers.

## Output Rules for AI Agents

## Branch Naming & Traceability (MANDATORY)

- All new branches must follow the convention in [docs/BRANCH_NAMING_STANDARDS.md](../docs/BRANCH_NAMING_STANDARDS.md):
  - `feature/{roadmap-id}-{short-description}`
  - `fix/{roadmap-id}-{short-description}`
  - `docs/{roadmap-id}-{short-description}`
  - `chore/{roadmap-id}-{short-description}`
- `{roadmap-id}` must match an entry in ROADMAP.md or SCENARIO_TRACKER.md
- PRs and commit messages must reference the roadmap/scenario ID
- All work must be traceable to a roadmap item

---

When implementing features, ALWAYS provide:

1. **File/folder plan** — what files will be added/changed
2. **Code/config** — with minimal, clear comments
3. **How to run** — exact commands
4. **Which guardrails enforce it** — reference Makefile targets

**Workflow Requirements:**

- Always open a new branch from `main` when starting a new feature or fix (use a descriptive branch name)
- Commit changes at appropriate intervals (atomic, logical commits)
- Before pushing, review your changes and ensure you are satisfied with them
- All commits and pushes are blocked unless both `make guardrails` and `make be-coverage` pass (enforced by pre-commit and CI)
- CI (GitHub Actions) will also enforce these checks on PRs and pushes

**A feature is only considered complete if:**

- All checks in `make guardrails` pass
- Test coverage threshold is met (`make be-coverage` must pass)

**Do NOT:**

- Invent additional tools
- Over-abstract
- Skip guardrails
- Place simulator logic in domain layer
- Allow domain to import frameworks

**Prefer:** Explicitness, clarity, production-grade discipline

## Critical Invariants (Always Check)

Before completing any task, verify:

- [ ] Domain layer has no framework imports
- [ ] Contracts are explicit and checked in
- [ ] Simulator logic is isolated from business logic
- [ ] Tests are deterministic and properly layered
- [ ] Makefile targets work end-to-end
- [ ] Guardrails pass (`make guardrails`)
- [ ] Test coverage threshold is met (`make be-coverage`)
- [ ] All commits and pushes are blocked unless these checks pass (pre-commit/CI)

## Adding New Simulator Scenarios

1. Create new class in `backend/src/app/application/simulator/scenarios/`
2. Implement effect-based scenario interface (meta, is_applicable, apply)
3. **CRITICAL:** Use only valid target categories: `["http", "db", "cpu", "algorithm"]` (type-checked by `TargetCategory` literal)
4. Register in scenario registry (`backend/src/app/application/simulator/registry.py`)
5. Add tests validating injection + safety limits in `backend/tests/unit/`
6. Document in scenario catalogue
7. Update frontend control panel if new parameter types needed

**Template:** See existing scenarios like `fixed_latency.py` or `TEMPLATE.py` for reference
**Pattern:** Scenarios return effect dicts, middleware applies them (no side effects in scenario code)
**Type Safety:** `ScenarioMeta.targets` is typed as `list[TargetCategory]` - mypy will catch invalid values at type-check time

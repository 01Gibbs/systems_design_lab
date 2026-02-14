# Systems Design Lab

Production-grade local systems design lab for learning and simulating real-world system issues.

## Overview

This project provides a **disciplined, maintainable baseline application** with strict architectural guardrails, designed to support deliberate simulation of **100+ common real-world system problems** including:

- **Core Failures**: Latency, timeouts, retries, HTTP failures, partial outages
- **Database Issues**: N+1 queries, missing indexes, deadlocks, connection leaks
- **Caching Patterns**: Cache stampede, stale reads, invalidation races
- **Concurrency**: Race conditions, optimistic locking, event ordering
- **CQRS/Event Sourcing**: Event replay, projections, sagas
- **Advanced Topics**: Performance benchmarking, security, cost optimization, AI/ML workloads

**This is NOT a demo app.** It's a production-grade learning platform with:

- ✅ Automated enforcement of Clean Architecture and contract-first API design
- ✅ Observable failure modes through Prometheus + Grafana + Loki + Tempo
- ✅ Guided tutorials teaching systems design concepts
- ✅ 50 core scenarios + 50+ advanced scenarios (roadmap)

## Vision & Roadmap

🎯 **Goal**: The most comprehensive, production-grade systems design learning platform

📋 **Quick Overview**: [EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md) - Visual roadmap and progress

📋 **Full Roadmap**: [ROADMAP.md](docs/ROADMAP.md) - Complete vision including:

- Phase 4: Complete 50 Core Scenarios (15/50 done)
- Phase 5: Guided Tutorials (24+ tutorials across 6 series)
- Phase 6: CQRS/Event Sourcing Module
- Phase 7: Production Readiness (Redis, Multi-tenancy, K8s)
- Phase 8: Interactive Documentation (Docusaurus + live demos)
- Phase 9: Advanced Scenarios (Performance, Security, Cost, Mobile, AI/ML)

## Stack

- **Frontend**: Vite + TypeScript + Playwright
- **Backend**: Python + FastAPI + Uvicorn
- **Database**: PostgreSQL (local, Docker)
- **Infrastructure**: Docker Compose
- **Observability**: Prometheus + Grafana + Loki + Tempo (local)

## Quick Start

### Prerequisites

- Docker & Docker Compose (required)
- Python 3.11+ (optional, for host-based development)
- Make (required)
- Node.js 18+ (for frontend, when added)

### Setup Option A: Docker-Only (Recommended)

```bash
# Start services (PostgreSQL + Backend)
make up

# Wait a few seconds, then check health
sleep 5
curl http://localhost:8000/api/health

# Run all tests in Docker
make be-docker-test

# Run all guardrails checks in Docker
make be-docker-all
```

### Setup Option B: Hybrid (Host Python + Docker DB)

```bash
# Fix Python version (if using asdf)
cd backend && asdf local python 3.11.4 && cd ..

# Install dependencies on host
make be-install

# Start services
make up

# Check health
curl http://localhost:8000/api/health

# Run guardrails on host
make guardrails
```

### Troubleshooting

See [QUICK_START.md](QUICK_START.md) and [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) for detailed setup instructions and troubleshooting.

**Common issues:**

- Backend not responding: `docker logs sysdesign_backend`
- Python not found: Use Docker workflow (`make be-docker-test`)
- Frontend can't reach backend: Check CORS and proxy settings

### Frontend Development

```bash
# Install frontend dependencies
make fe-install

# Start frontend dev server (http://localhost:5173)
cd frontend && npm run dev

# Run E2E tests
make fe-test-e2e

# Or use Docker
docker-compose up frontend
```

## License

MIT

## Makefile Commands

The Makefile is your single entry point for all development tasks:

### Development Lifecycle

- `make up` - Start all services
- `make down` - Stop services
- `make reset` - Stop and remove volumes
- `make logs` - Tail service logs
- `make status` - Check system health

### Observability

- `make grafana` - Open Grafana dashboards (http://localhost:3000)
- `make prometheus` - Open Prometheus UI (http://localhost:9090)
- `make logs-obs` - Tail observability stack logs
- `make metrics` - Check backend metrics endpoint

See [OBSERVABILITY.md](docs/OBSERVABILITY.md) for complete observability documentation.

### Backend Development (Host-based)

- `make be-install` - Install dependencies
- `make be-format` - Format code with black
- `make be-lint` - Lint with ruff
- `make be-typecheck` - Type check with mypy
- `make be-test` - Run all tests
- `make be-test-unit` - Unit tests only
- `make be-test-integration` - Integration tests only
- `make be-coverage` - Enforce coverage threshold

### Backend Development (Docker-based)

- `make be-docker-test` - Run tests in container
- `make be-docker-format` - Format code in container
- `make be-docker-lint` - Lint in container
- `make be-docker-typecheck` - Type check in container
- `make be-docker-all` - Run all checks in container
- `make be-docker-shell` - Open shell in container

### Guardrails & Enforcement

- `make guardrails` - Run ALL checks (required before commit)
- `make arch-check` - Check Clean Architecture boundaries
- `make contracts-check` - Check for OpenAPI contract drift
- `make contracts-accept` - Accept contract changes

### Quick Shortcuts

- `make format` - Format all code
- `make lint` - Lint all code
- `make test` - Run all tests
- `make check` - Run all guardrails

## Architecture

### Clean Architecture (Strict)

```
backend/src/app/
├── domain/           # Pure business logic (NO framework imports)
├── application/      # Use cases, command/query handlers
│   ├── ports/        # Port interfaces (Clock, SimulatorStore)
│   └── simulator/    # Simulator service + scenarios
├── api/              # FastAPI routers (no business logic)
├── infrastructure/   # Adapters (DB, cache, time, simulator store)
├── contracts/        # Request/response models (Pydantic)
├── guardrails/       # Boundary + contract enforcement
└── simulator/        # Issue simulator framework
```

**Layer Rules (Automatically Enforced):**

- `domain/` imports NOTHING from frameworks
- `application/` imports domain only
- `api/` imports application + contracts
- `infrastructure/` imports application + domain (via interfaces)

Violations are caught by `make arch-check`.

### Contract-First API

All API contracts are:

1. Defined explicitly as Pydantic models in `contracts/`
2. Generated into OpenAPI and checked in as snapshot
3. Validated against snapshot with `make contracts-check`
4. Updated deliberately with `make contracts-accept`

**Silent schema drift is prevented.**

## Issue Simulator Framework

The simulator is a first-class, extensible system for injecting 50+ real-world failure modes.

### Architecture

- Scenarios are separate classes implementing `Scenario` interface
- Registry pattern for dynamic scenario management
- Runtime configuration (enable/disable, parameters, duration)
- Safety limits prevent dangerous configurations

### API Endpoints

- `GET /api/sim/scenarios` - List available scenarios
- `GET /api/sim/status` - Active scenarios
- `POST /api/sim/enable` - Enable a scenario
- `POST /api/sim/disable` - Disable a scenario
- `POST /api/sim/reset` - Disable all

### Adding New Scenarios

1. Create new scenario class in `backend/src/app/application/simulator/scenarios/`
2. Implement effect-based interface: `meta`, `is_applicable()`, `apply()`
3. Register in `backend/src/app/application/simulator/registry.py`
4. Add tests in `backend/tests/unit/`
5. Document in scenario catalogue

**Pattern:** Scenarios return effect dicts (e.g., `{"http_delay_ms": 100}`), middleware applies them.

See existing scenarios like `fixed_latency.py` for reference.

## Testing Strategy

**Test Pyramid:**

- Unit tests: Domain + application (fast, no external dependencies)
- Integration tests: Real PostgreSQL via testcontainers
- Contract tests: OpenAPI schema validation
- E2E tests: Playwright (frontend, when added)

**Coverage threshold: 85%** (enforced by `make be-coverage`)

## CI/CD & Quality Gates

**All commits are protected by:**

- **Pre-commit hooks**: Run `make guardrails` and `make be-coverage` locally before commit
- **GitHub Actions CI**: Enforces guardrails + coverage on all PRs and pushes
- **Contract drift detection**: Fails if OpenAPI schema changes without explicit acceptance
- **Architecture boundaries**: Automated checks prevent layer violations

**Setup pre-commit hooks:**

```bash
pip install pre-commit
pre-commit install
```

See [CI_AND_PRECOMMIT.md](docs/CI_AND_PRECOMMIT.md) for full details.

## Tooling

**Python:**

- black (formatting)
- ruff (linting)
- mypy (type checking)
- pytest + pytest-cov (testing)
- hypothesis (property testing)

**Guardrails enforce:**

- Architecture boundaries
- Contract stability
- Code quality standards
- Test coverage

## Development Workflow

1. Make changes to code
2. Run `make format` to format
3. Run `make guardrails` to validate (runs automatically on commit via pre-commit)
4. Commit only if guardrails pass
5. CI validates all checks on push/PR

**All CI checks are runnable locally.**

## Observability Readiness

Code is structured for future observability:

- Request correlation (request_id/trace_id)
- Layered logging without leaking internals
- Ready for OpenTelemetry instrumentation

Future additions: Prometheus, Grafana, Loki.

## Contributing Guidelines

1. **Domain layer purity**: No framework imports in `domain/`
2. **Contract-first**: Update contracts explicitly, check in OpenAPI
3. **Test everything**: Unit + integration tests required
4. **Guardrails must pass**: `make guardrails` before commit
5. **Simulator isolation**: Keep simulator logic out of business logic

## Project Status & Next Steps

**Current Phase**: Core Scenario Expansion (Phase 4 - 30% complete)

### ✅ Complete

- Backend foundation (Clean Architecture + Ports & Adapters)
- Frontend (Vite + React + TypeScript + Simulator Control Panel)
- Observability Stack (Prometheus + Grafana + Loki + Tempo)
- CI/CD enforcement (GitHub Actions + pre-commit hooks)
- 15 simulator scenarios implemented
- 41 backend unit tests (92%+ coverage)
- 14 frontend tests + 3 E2E Playwright tests

### 🔄 In Progress (Q2 2026)

- **Scenario-Specific Observability Enhancement** 🎯
  - Add domain-specific metrics to all scenarios (e.g., `cache_miss_total`, `db_queries_per_request`, `db_lock_wait_seconds`)
  - Dynamic Grafana panels showing metric impact per active scenario
  - Makes failure modes directly observable and measurable
- Complete 50 core scenarios (35 remaining)
  - Caching & Data Consistency (5)
  - Database Patterns (5)
  - API & Network (5)
  - Concurrency & Race Conditions (5)
  - Plus 15 additional scenarios

### ⏳ Planned

- **Phase 5**: Guided Tutorials (6 series, 24+ tutorials)
- **Phase 6**: CQRS/Event Sourcing Module
- **Phase 7**: Production Readiness (Redis, Multi-tenancy, K8s)
- **Phase 8**: Interactive Documentation (Docusaurus site)
- **Phase 9**: Advanced Scenarios (100+ total)

**Full roadmap**: [ROADMAP.md](docs/ROADMAP.md)
**Detailed status**: [PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
**Scenario tracking**: [SCENARIO_TRACKER.md](docs/SCENARIO_TRACKER.md)

## Project Documentation

See:

- [ROADMAP.md](docs/ROADMAP.md) for vision and planned features
- [SCENARIO_TRACKER.md](docs/SCENARIO_TRACKER.md) for scenario implementation status
- [EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md) for quick overview

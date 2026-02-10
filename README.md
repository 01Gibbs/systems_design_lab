# Systems Design Lab

Production-grade local systems design lab for learning and simulating real-world system issues.

## Overview

This project provides a **disciplined, maintainable baseline application** with strict architectural guardrails, designed to support deliberate simulation of 50+ common real-world system problems including:

- Latency, timeouts, and retries
- HTTP failures and partial outages
- Database performance issues
- Caching strategies and failures
- Concurrency and race conditions
- Resource exhaustion
- CQRS patterns and read model projections

**This is NOT a demo app.** It's a production-grade lab with automated enforcement of Clean Architecture and contract-first API design.

## Stack

- **Frontend**: Vite + TypeScript + Playwright
- **Backend**: Python + FastAPI + Uvicorn
- **Database**: PostgreSQL (local, Docker)
- **Infrastructure**: Docker Compose

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Make
- Node.js 18+ (for frontend, when added)

### Setup

```bash
# Install Python dependencies
make be-install

# Start services (PostgreSQL + Backend)
make up

# In another terminal, check health
curl http://localhost:8000/api/health

# List available simulator scenarios
curl http://localhost:8000/api/sim/scenarios

# Run all guardrails (formatting, linting, type checking, tests, architecture checks)
make guardrails
```

## Makefile Commands

The Makefile is your single entry point for all development tasks:

### Development Lifecycle

- `make up` - Start all services
- `make down` - Stop services
- `make reset` - Stop and remove volumes
- `make logs` - Tail service logs

### Backend Development

- `make be-install` - Install dependencies
- `make be-format` - Format code with black
- `make be-lint` - Lint with ruff
- `make be-typecheck` - Type check with mypy
- `make be-test` - Run all tests
- `make be-test-unit` - Unit tests only
- `make be-test-integration` - Integration tests only
- `make be-coverage` - Enforce coverage threshold

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
backend/
├── domain/           # Pure business logic (NO framework imports)
├── application/      # Use cases, command/query handlers
├── api/              # FastAPI routers (no business logic)
├── infrastructure/   # DB, cache, external adapters
├── contracts/        # Request/response models (Pydantic)
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

1. Copy `backend/simulator/scenarios/template_scenario.py`
2. Implement all abstract methods
3. Register scenario at app startup
4. Add tests validating behavior
5. Document in scenario catalogue

See [template_scenario.py](backend/simulator/scenarios/template_scenario.py) for details.

## Testing Strategy

**Test Pyramid:**

- Unit tests: Domain + application (fast, no external dependencies)
- Integration tests: Real PostgreSQL via testcontainers
- Contract tests: OpenAPI schema validation
- E2E tests: Playwright (frontend, when added)

**Coverage threshold: 80%** (enforced by `make be-coverage`)

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
3. Run `make guardrails` to validate
4. Commit only if guardrails pass

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

## Project Status

**Current Phase**: Foundation and framework setup

**Next Steps**:

1. Implement 5 starter scenarios (latency, errors, slow DB, contention, algorithmic)
2. Add frontend with simulator control panel
3. Expand to 50 scenarios across all categories

## License

MIT

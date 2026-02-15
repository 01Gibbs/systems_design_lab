# CI and Pre-commit Enforcement

## CI (GitHub Actions)

The CI pipeline runs in two sequential jobs:

### Job 1: Guardrails and Coverage (Fast, ~2-3 minutes)

- `make guardrails` (format, lint, typecheck, tests, arch-check, contracts-check)
- `make be-coverage` (backend test coverage)
- `make be-test-integration` (integration tests using FastAPI TestClient)
- If any check fails, the build fails immediately without running E2E tests

### Job 2: E2E Tests (Slower, ~3-5 minutes)

- Only runs if Job 1 passes
- Starts Docker services (backend + PostgreSQL)
- Runs Playwright browser-based tests (`make fe-test-e2e`)

**Key Optimization:** Integration tests now use FastAPI `TestClient` instead of running a real server, so they run in Job 1 without Docker (~30-60s faster). Only actual E2E browser tests need Docker.

See `.github/workflows/ci.yml` for full pipeline definition.

## Pre-commit Hook

- Uses [pre-commit](https://pre-commit.com/) framework.
- On every commit, runs:
  - `make guardrails`
  - `make be-coverage`
- If either fails, commit is blocked.
- See `.pre-commit-config.yaml`.

## Setup

1. Install pre-commit: `pip install pre-commit`
2. Run `pre-commit install` in project root
3. On commit, checks will run automatically

## Rationale

- Ensures all features meet project quality bar before merge or commit
- Prevents contract/arch/test drift
- Enforces coverage threshold

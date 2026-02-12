# CI and Pre-commit Enforcement

## CI (GitHub Actions)

- On every push or PR, CI runs:
  - `make guardrails` (format, lint, typecheck, tests, arch-check, contracts-check)
  - `make be-coverage` (backend test coverage)
- If either fails, the build fails.
- See `.github/workflows/ci.yml`.

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

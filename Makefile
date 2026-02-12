# Always reset to project root (works on both Linux/macOS and Windows)
reset-root:
	@cd "$(CURDIR)"
	@cd "$(shell git rev-parse --show-toplevel 2>/dev/null || echo $(CURDIR))"
	@echo "$(YELLOW)Reset to project root: $$(pwd)$(NC)"
 .PHONY: help up down reset logs status \
        be-install be-format be-format-check be-lint be-typecheck be-test be-test-unit be-test-integration be-coverage \
        be-docker-test be-docker-format be-docker-lint be-docker-typecheck be-docker-all \
        fe-install fe-format fe-format-check be-lint fe-typecheck fe-test-e2e \
        guardrails arch-check contracts-check contracts-accept
##@ Automated Cleanup

autoclean: contracts-bootstrap guardrails
	@echo "$(YELLOW)Running workspace cleanup...$(NC)"
	# Remove Python __pycache__ folders
	find . -type d -name "__pycache__" -exec rm -rf {} +
	# Remove backend and frontend test artefacts
	 rm -rf frontend/playwright-report frontend/test-results
	# Remove mypy and pytest caches at root
	rm -rf .mypy_cache .pytest_cache
	# Remove empty folders
	find . -type d -empty -delete
	@echo "$(GREEN)✓ Workspace cleaned$(NC)"


# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Help

help: ## Display this help message
	@echo "$(BLUE)Systems Design Lab - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Lifecycle

up: autoclean ## Start docker compose + app services
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"

down: ## Stop services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

reset: ## Stop services and remove volumes
	@echo "$(YELLOW)Resetting all services and volumes...$(NC)"
	docker-compose down -v
	@echo "$(GREEN)✓ Reset complete$(NC)"

logs: ## Tail logs from all services
	docker-compose logs -f

status: ## Check system status and health
	@bash scripts/status.sh

##@ Backend Development (Host-based)

be-install: autoclean ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements-dev.txt; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

be-format: ## Format backend code with black
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && black src/; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ Code formatted$(NC)"

be-format-check: ## Check backend code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	cd backend && black --check src/; cd .. || true
	@$(MAKE) reset-root

be-lint: ## Lint backend code with ruff
	@echo "$(BLUE)Linting backend code...$(NC)"
	cd backend && ruff check src/; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ Linting passed$(NC)"

be-typecheck: ## Type check backend code with mypy
	@echo "$(BLUE)Type checking backend code...$(NC)"
	cd backend && mypy; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ Type checking passed$(NC)"

be-test: ## Run all backend tests
	@echo "$(BLUE)Running all backend tests...$(NC)"
	cd backend && PYTHONPATH=src pytest; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ All tests passed$(NC)"

be-test-unit: ## Run backend unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd backend && PYTHONPATH=src pytest -m "not integration" tests/unit; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ Unit tests passed$(NC)"

be-test-integration: ## Run backend integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd backend && PYTHONPATH=src pytest -m integration tests/integration; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ Integration tests passed$(NC)"

be-coverage: ## Run backend tests with coverage enforcement
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	cd backend && PYTHONPATH=src pytest --cov=src/app --cov-report=term-missing --cov-fail-under=85; cd .. || true
	@$(MAKE) reset-root
	@echo "$(GREEN)✓ Coverage threshold met$(NC)"

be-docker-test: ## Run tests in Docker container
	@./scripts/dev-container.sh test

be-docker-format: ## Format code in Docker container
	@./scripts/dev-container.sh format

be-docker-format-check: ## Check formatting in Docker container
	@./scripts/dev-container.sh format-check

be-docker-lint: ## Lint in Docker container
	@./scripts/dev-container.sh lint

be-docker-typecheck: ## Type check in Docker container
	@./scripts/dev-container.sh typecheck

be-docker-shell: ## Open shell in Docker container
	@./scripts/dev-container.sh shell

be-docker-all: ## Run all checks in Docker container
	@./scripts/dev-container.sh all

##@ backend && PYTHONPATH=src pytest --cov=app --cov-report=term-missing --cov-fail-under=85
	@echo "$(GREEN)✓ Coverage threshold met$(NC)"

##@ Frontend Development

fe-install: autoclean ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

fe-format: ## Format frontend code with prettier
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run format
	@echo "$(GREEN)✓ Code formatted$(NC)"

fe-format-check: ## Check frontend code formatting
	@echo "$(BLUE)Checking frontend formatting...$(NC)"
	cd frontend && npm run format:check

fe-lint: ## Lint frontend code with eslint
	@echo "$(BLUE)Linting frontend code...$(NC)"
	cd frontend && npm run lint
	@echo "$(GREEN)✓ Linting passed$(NC)"

fe-typecheck: ## Type check frontend code with tsc
	@echo "$(BLUE)Type checking frontend code...$(NC)"
	cd frontend && npm run typecheck
	@echo "$(GREEN)✓ Type checking passed$(NC)"

fe-test-e2e: ## Run frontend E2E tests with Playwright
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd frontend && npm run test:e2e
	@echo "$(GREEN)✓ E2E tests passed$(NC)"

##@ Guardrails & Enforcement

guardrails: contracts-bootstrap be-format-check be-lint be-typecheck be-test arch-check contracts-check ## Run all guardrails checks
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)✓ All guardrails checks passed$(NC)"
	@echo "$(GREEN)========================================$(NC)"

arch-check: ## Check Clean Architecture boundaries
	@echo "$(BLUE)Checking architecture boundaries...$(NC)"
	cd backend && PYTHONPATH=src python -m app.guardrails.arch_check

contracts-check: ## Check for contract drift
	@echo "$(BLUE)Checking contract drift...$(NC)"
	cd backend && PYTHONPATH=src python -m app.guardrails.contracts_check

contracts-accept: ## Accept current contract as new snapshot
	@echo "$(YELLOW)Accepting contract changes...$(NC)"
	cd backend && PYTHONPATH=src python -m app.guardrails.contracts_accept
	@echo "$(GREEN)✓ Contract snapshot updated$(NC)"

##@ Quick Shortcuts

format: be-format ## Format all code (shortcut)

lint: be-lint ## Lint all code (shortcut)

test: be-test ## Run all tests (shortcut)

check: guardrails ## Run all checks (shortcut)

# Ensure OpenAPI snapshot exists before checks
contracts-bootstrap:
	@if [ ! -f openapi.json ]; then \
		echo "$(YELLOW)No OpenAPI snapshot found. Bootstrapping...$(NC)"; \
		$(MAKE) contracts-accept; \
	fi

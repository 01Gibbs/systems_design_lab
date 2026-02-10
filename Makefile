.PHONY: help up down reset logs \
        be-install be-format be-format-check be-lint be-typecheck be-test be-test-unit be-test-integration be-coverage \
        fe-install fe-format fe-format-check fe-lint fe-typecheck fe-test-e2e \
        guardrails arch-check contracts-check contracts-accept

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

up: ## Start docker compose + app services
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

##@ Backend Development

be-install: ## Install backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

be-format: ## Format backend code with black
	@echo "$(BLUE)Formatting backend code...$(NC)"
	black backend/ guardrails/
	@echo "$(GREEN)✓ Code formatted$(NC)"

be-format-check: ## Check backend code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	black --check backend/ guardrails/

be-lint: ## Lint backend code with ruff
	@echo "$(BLUE)Linting backend code...$(NC)"
	ruff check backend/ guardrails/
	@echo "$(GREEN)✓ Linting passed$(NC)"

be-typecheck: ## Type check backend code with mypy
	@echo "$(BLUE)Type checking backend code...$(NC)"
	mypy backend/ guardrails/
	@echo "$(GREEN)✓ Type checking passed$(NC)"

be-test: ## Run all backend tests
	@echo "$(BLUE)Running all backend tests...$(NC)"
	pytest backend/tests/
	@echo "$(GREEN)✓ All tests passed$(NC)"

be-test-unit: ## Run backend unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest backend/tests/unit/ -m unit
	@echo "$(GREEN)✓ Unit tests passed$(NC)"

be-test-integration: ## Run backend integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest backend/tests/integration/ -m integration
	@echo "$(GREEN)✓ Integration tests passed$(NC)"

be-coverage: ## Run backend tests with coverage enforcement
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest backend/tests/ --cov=backend --cov-report=term-missing --cov-fail-under=80
	@echo "$(GREEN)✓ Coverage threshold met$(NC)"

##@ Frontend Development

fe-install: ## Install frontend dependencies
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

guardrails: be-format-check be-lint be-typecheck be-test arch-check contracts-check ## Run all guardrails checks
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)✓ All guardrails checks passed$(NC)"
	@echo "$(GREEN)========================================$(NC)"

arch-check: ## Check Clean Architecture boundaries
	@echo "$(BLUE)Checking architecture boundaries...$(NC)"
	python -m guardrails.runner arch-check

contracts-check: ## Check for contract drift
	@echo "$(BLUE)Checking contract drift...$(NC)"
	python -m guardrails.runner contracts-check

contracts-accept: ## Accept current contract as new snapshot
	@echo "$(YELLOW)Accepting contract changes...$(NC)"
	python -m guardrails.runner contracts-accept
	@echo "$(GREEN)✓ Contract snapshot updated$(NC)"

##@ Quick Shortcuts

format: be-format ## Format all code (shortcut)

lint: be-lint ## Lint all code (shortcut)

test: be-test ## Run all tests (shortcut)

check: guardrails ## Run all checks (shortcut)

#!/bin/bash
# Container-based development commands
# Use these when host Python environment isn't set up

set -e

BACKEND_CONTAINER="sysdesign_backend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${BACKEND_CONTAINER}$"; then
        echo -e "${RED}Error: Backend container not running${NC}"
        echo "Run: make up"
        exit 1
    fi
}

case "$1" in
    test)
        echo -e "${BLUE}Running tests in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER pytest -v
        ;;
    test-unit)
        echo -e "${BLUE}Running unit tests in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER pytest -v tests/unit
        ;;
    format)
        echo -e "${BLUE}Formatting code in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER black src/
        echo -e "${GREEN}✓ Code formatted${NC}"
        ;;
    format-check)
        echo -e "${BLUE}Checking code format in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER black --check src/
        ;;
    lint)
        echo -e "${BLUE}Linting in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER ruff check src/
        echo -e "${GREEN}✓ Linting passed${NC}"
        ;;
    typecheck)
        echo -e "${BLUE}Type checking in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER mypy
        echo -e "${GREEN}✓ Type checking passed${NC}"
        ;;
    arch-check)
        echo -e "${BLUE}Checking architecture boundaries in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER python -m app.guardrails.arch_check
        echo -e "${GREEN}✓ Architecture boundaries OK${NC}"
        ;;
    contracts-check)
        echo -e "${BLUE}Checking contracts in container...${NC}"
        check_container
        docker exec $BACKEND_CONTAINER python -m app.guardrails.contracts_check
        echo -e "${GREEN}✓ Contracts OK${NC}"
        ;;
    all)
        echo -e "${BLUE}Running all checks in container...${NC}"
        check_container
        echo -e "${YELLOW}1/5: Format check${NC}"
        docker exec $BACKEND_CONTAINER black --check src/
        echo -e "${YELLOW}2/5: Linting${NC}"
        docker exec $BACKEND_CONTAINER ruff check src/
        echo -e "${YELLOW}3/5: Type checking${NC}"
        docker exec $BACKEND_CONTAINER mypy
        echo -e "${YELLOW}4/5: Tests${NC}"
        docker exec $BACKEND_CONTAINER pytest -v
        echo -e "${YELLOW}5/5: Architecture check${NC}"
        docker exec $BACKEND_CONTAINER python -m app.guardrails.arch_check
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}✓ All checks passed${NC}"
        echo -e "${GREEN}========================================${NC}"
        ;;
    shell)
        echo -e "${BLUE}Opening shell in container...${NC}"
        check_container
        docker exec -it $BACKEND_CONTAINER bash
        ;;
    logs)
        echo -e "${BLUE}Backend logs:${NC}"
        docker logs $BACKEND_CONTAINER --tail 50 --follow
        ;;
    *)
        echo "Container-based development commands"
        echo ""
        echo "Usage: ./scripts/dev-container.sh <command>"
        echo ""
        echo "Commands:"
        echo "  test          - Run all tests"
        echo "  test-unit     - Run unit tests only"
        echo "  format        - Format code with black"
        echo "  format-check  - Check code formatting"
        echo "  lint          - Lint with ruff"
        echo "  typecheck     - Type check with mypy"
        echo "  arch-check    - Check architecture boundaries"
        echo "  contracts-check - Check contract drift"
        echo "  all           - Run all checks (guardrails)"
        echo "  shell         - Open bash shell in container"
        echo "  logs          - Follow container logs"
        echo ""
        echo "Example: ./scripts/dev-container.sh test"
        exit 1
        ;;
esac

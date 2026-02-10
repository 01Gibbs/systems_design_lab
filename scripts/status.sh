#!/bin/bash
# Simple status check script

echo "Checking system status..."
echo ""

# Check Docker
echo "Docker: $(docker --version 2>&1 | head -1 || echo 'Not installed')"
echo ""

# Check containers
echo "Containers:"
docker ps --format "  {{.Names}}: {{.Status}}" --filter "name=sysdesign" 2>&1 || echo "  None running"
echo ""

# Check backend health (with short timeout)
echo -n "Backend health: "
if timeout 3 curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✓ Healthy"
else
    echo "✗ Not responding"
    echo "  Run: docker logs sysdesign_backend"
fi
echo ""

# Check Python (host)
echo -n "Host Python: "
if command -v python3 &> /dev/null; then
    python3 --version
else
    echo "Not found (OK if using Docker-only workflow)"
fi
echo ""

# Check if deps installed
echo -n "Host dependencies: "
if command -v pytest &> /dev/null || [ -f "backend/.venv/bin/pytest" ]; then
    echo "✓ Installed"
else
    echo "✗ Not installed (run: make be-install)"
fi
echo ""

echo "Quick commands:"
echo "  make up              - Start services"
echo "  ./scripts/dev-container.sh test - Run tests in container"
echo "  ./scripts/dev-container.sh all  - Run all checks"
echo "  docker logs sysdesign_backend   - View backend logs"

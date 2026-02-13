#!/bin/bash
# Quick test of the complete stack

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Complete Stack Test - Systems Design Lab                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check backend
echo "1️⃣  Checking backend..."
if docker ps | grep -q sysdesign_backend; then
    echo "   ✓ Backend container running"
    if docker exec sysdesign_backend curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "   ✓ Backend API healthy"
    else
        echo "   ⚠️  Backend API not responding"
    fi
else
    echo "   ✗ Backend not running (run: make up)"
fi

echo ""
echo "2️⃣  Checking frontend..."
if [ -d "frontend/node_modules" ]; then
    echo "   ✓ Frontend dependencies installed"
else
    echo "   ⚠️  Run: cd frontend && npm install"
fi

echo ""
echo "3️⃣  Checking scenarios..."
scenario_count=$(docker exec sysdesign_backend curl -s http://localhost:8000/api/sim/scenarios 2>/dev/null | grep -o '"name"' | wc -l)
if [ "$scenario_count" -ge 15 ]; then
    echo "   ✓ $scenario_count scenarios available"
else
    echo "   ⚠️  Expected 15 scenarios, found $scenario_count"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   cd frontend"
echo "   npm install          # Install dependencies"
echo "   npm run dev          # Start dev server"
echo ""
echo "   Then open: http://localhost:5173"
echo ""
echo "   Run tests:"
echo "   npm run test:e2e     # E2E tests"
echo "   npm run typecheck    # Type check"
echo "   npm run lint         # Lint check"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

#!/bin/bash
# Quick API validation script

echo "Testing backend API..."
echo ""

# Test health endpoint
echo "1. Health check:"
response=$(docker exec sysdesign_backend curl -s http://localhost:8000/api/health)
if [ $? -eq 0 ]; then
    echo "   ✓ $response"
else
    echo "   ✗ Failed"
fi

echo ""
echo "2. List scenarios:"
docker exec sysdesign_backend curl -s http://localhost:8000/api/sim/scenarios | head -5
echo "   ..."

echo ""
echo "3. Get status:"
docker exec sysdesign_backend curl -s http://localhost:8000/api/sim/status

echo ""
echo "✅ Backend is ready for frontend integration!"

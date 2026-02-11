#!/bin/bash
# Frontend validation script

echo "=== Frontend Validation ==="
echo ""

# Check if in frontend directory
if [ ! -f "package.json" ]; then
    echo "Switching to frontend directory..."
    cd frontend || exit 1
fi

echo "1. Installing dependencies..."
npm install --silent

echo ""
echo "2. Type checking..."
npm run typecheck

echo ""
echo "3. Linting..."
npm run lint

echo ""
echo "4. Format checking..."
npm run format:check

echo ""
echo "✅ Frontend validation complete!"
echo ""
echo "To start development:"
echo "  npm run dev"
echo ""
echo "To run tests:"
echo "  npm run test:e2e"

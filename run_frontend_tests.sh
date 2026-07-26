#!/bin/bash
echo "🧪 RUNNING FRONTEND TESTS"
echo "========================="

cd ~/nemesis_madina/frontend

# Check if node_modules exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Run tests
echo ""
echo "📦 Running tests..."
npm run test:run 2>&1 | grep -E "(PASS|FAIL|✓|✗|✅|❌|Test Files|Tests)"

echo ""
echo "✅ Frontend tests completed!"
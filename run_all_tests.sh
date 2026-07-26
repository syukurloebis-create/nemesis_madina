#!/bin/bash
echo "🧪 RUNNING ALL TESTS"
echo "===================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run backend tests
run_backend_tests() {
    echo -e "${YELLOW}📦 Backend Tests:${NC}"
    cd ~/nemesis_madina
    
    # Setup Python path
    export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/backend"
    
    # Run tests
    cd backend
    if python -m pytest tests/ -v --tb=short 2>&1 | grep -q "ERROR"; then
        echo -e "${RED}❌ Backend tests failed${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Backend tests passed${NC}"
        return 0
    fi
    cd ..
}

# Function to run frontend tests
run_frontend_tests() {
    echo -e "${YELLOW}📦 Frontend Tests:${NC}"
    cd ~/nemesis_madina/frontend
    
    # Check dependencies
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install --silent
    fi
    
    # Run tests
    if npm run test:run -- --silent 2>&1 | grep -q "FAIL"; then
        echo -e "${RED}❌ Frontend tests failed${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Frontend tests passed${NC}"
        return 0
    fi
}

# Run tests
echo ""
run_backend_tests
BACKEND_RESULT=$?

echo ""
run_frontend_tests
FRONTEND_RESULT=$?

echo ""
echo "📊 Test Summary:"
if [ $BACKEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Backend: PASSED${NC}"
else
    echo -e "${RED}❌ Backend: FAILED${NC}"
fi

if [ $FRONTEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend: PASSED${NC}"
else
    echo -e "${RED}❌ Frontend: FAILED${NC}"
fi

echo ""
echo "✅ Tests completed!"
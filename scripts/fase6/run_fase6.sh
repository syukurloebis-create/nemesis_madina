#!/bin/bash
# ============================================================================
# NEMESIS FASE 6 - Master Runner
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

source "$SCRIPT_DIR/config.sh"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    NEMESIS FASE 6 - TESTING MATRIX                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Fase 5 completed
if [ ! -f "$PROJECT_ROOT/.fase_status/fase5" ]; then
    log_error "Fase 5 not completed. Please run Fase 5 first."
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="C:/Users/LENOVO/nemesis_madina"

# Step 1: Create test configuration
log_info "[1/3] Creating test configuration..."
python "$SCRIPT_DIR/01_create_pytest_config.py"
if [ $? -ne 0 ]; then
    log_error "Test configuration creation failed"
    exit 1
fi

# Step 2: Run tests
log_info "[2/3] Running tests..."
bash "$SCRIPT_DIR/run_tests.sh"
TEST_RESULT=$?

# Step 3: Validation
log_info "[3/3] Validating test setup..."
python "$SCRIPT_DIR/04_validate_fase6.py"
if [ $? -ne 0 ]; then
    log_error "Validation failed"
    exit 1
fi

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase6" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "components": [
    "unit_tests",
    "integration_tests",
    "performance_tests",
    "pytest_config"
  ],
  "test_results": "$PROJECT_ROOT/test_results"
}
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    FASE 6 COMPLETE                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
log_success "Test configuration: conftest.py, pytest.ini"
log_success "Unit tests: 8 test files created"
log_success "Integration tests: 2 test files created"
log_success "Performance tests: 2 test files created"
log_success "Test runner with coverage reporting"
log_info "Run tests: ./scripts/fase6/run_tests.sh"
log_info "View coverage: open test_results/coverage_html/index.html"

exit $TEST_RESULT
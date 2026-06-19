#!/bin/bash
# ============================================================================
# NEMESIS FASE 6 - Run Tests
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

# Install test dependencies if needed
log_info "Checking test dependencies..."
pip install pytest pytest-asyncio pytest-cov pytest-timeout pytest-mock 2>/dev/null

# Create test results directory
RESULTS_DIR="$PROJECT_ROOT/test_results"
mkdir -p "$RESULTS_DIR"

# Run unit tests
log_info "Running unit tests..."
cd "$PROJECT_ROOT"
python -m pytest tests/unit -v --tb=short \
    --cov=backend \
    --cov-report=html:"$RESULTS_DIR/coverage_html" \
    --cov-report=xml:"$RESULTS_DIR/coverage.xml" \
    --cov-report=term \
    --junitxml="$RESULTS_DIR/junit.xml" \
    2>&1 | tee "$RESULTS_DIR/unit_test_output.txt"

UNIT_EXIT=${PIPESTATUS[0]}

# Run integration tests (if any)
if [ -d "tests/integration" ] && [ "$(ls -A tests/integration)" ]; then
    log_info "Running integration tests..."
    python -m pytest tests/integration -v --tb=short \
        --junitxml="$RESULTS_DIR/integration_junit.xml" \
        2>&1 | tee "$RESULTS_DIR/integration_output.txt"
    
    INT_EXIT=${PIPESTATUS[0]}
else
    log_info "No integration tests found"
    INT_EXIT=0
fi

# Run performance tests (optional, skip if slow)
if [ "${RUN_PERFORMANCE_TESTS}" = "true" ]; then
    log_info "Running performance tests..."
    python -m pytest tests/performance -v --tb=short \
        --junitxml="$RESULTS_DIR/performance_junit.xml" \
        2>&1 | tee "$RESULTS_DIR/performance_output.txt"
    
    PERF_EXIT=${PIPESTATUS[0]}
else
    log_info "Skipping performance tests (set RUN_PERFORMANCE_TESTS=true to run)"
    PERF_EXIT=0
fi

# Summary
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                         TEST SUMMARY                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Unit Tests:        $([ $UNIT_EXIT -eq 0 ] && echo "PASSED" || echo "FAILED")"
echo "  Integration Tests: $([ $INT_EXIT -eq 0 ] && echo "PASSED" || echo "FAILED")"
echo "  Performance Tests: $([ $PERF_EXIT -eq 0 ] && echo "PASSED" || echo "SKIPPED")"
echo ""
echo "  Results saved to: $RESULTS_DIR/"
echo "  Coverage report: $RESULTS_DIR/coverage_html/index.html"
echo ""

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/fase6" << EOF
{
  "status": "COMPLETED",
  "timestamp": "$(date -Iseconds)",
  "tests": {
    "unit": $([ $UNIT_EXIT -eq 0 ] && echo "true" || echo "false"),
    "integration": $([ $INT_EXIT -eq 0 ] && echo "true" || echo "false"),
    "performance": $([ $PERF_EXIT -eq 0 ] && echo "true" || echo "false")
  },
  "coverage_dir": "$RESULTS_DIR/coverage_html"
}
EOF

if [ $UNIT_EXIT -eq 0 ] && [ $INT_EXIT -eq 0 ]; then
    log_success "All tests passed!"
    exit 0
else
    log_error "Some tests failed. Check results in $RESULTS_DIR/"
    exit 1
fi
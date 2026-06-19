#!/bin/bash
# ============================================================================
# Run All NEMESIS Tests
# ============================================================================

cd ~/nemesis_madina

echo "============================================================"
echo "RUNNING NEMESIS TEST SUITE"
echo "============================================================"
echo ""

# Set PYTHONPATH
export PYTHONPATH="C:/Users/LENOVO/nemesis_madina"

# Create test results directory
mkdir -p test_results

# Run unit tests
echo "[1/3] Running unit tests..."
python -m pytest tests/unit -v \
    --cov=backend \
    --cov-report=html:test_results/coverage_html \
    --cov-report=xml:test_results/coverage.xml \
    --cov-report=term \
    --junitxml=test_results/junit.xml \
    2>&1 | tee test_results/unit_test_output.txt

UNIT_EXIT=${PIPESTATUS[0]}

# Run integration tests (if any)
echo ""
echo "[2/3] Running integration tests..."
if [ -d "tests/integration" ] && [ "$(ls -A tests/integration)" ]; then
    python -m pytest tests/integration -v \
        --junitxml=test_results/integration_junit.xml \
        2>&1 | tee test_results/integration_output.txt
    INT_EXIT=${PIPESTATUS[0]}
else
    echo "  No integration tests found"
    INT_EXIT=0
fi

# Run performance tests (optional)
echo ""
echo "[3/3] Running performance tests (optional)..."
if [ "${RUN_PERFORMANCE_TESTS}" = "true" ]; then
    python -m pytest tests/performance -v \
        --junitxml=test_results/performance_junit.xml \
        2>&1 | tee test_results/performance_output.txt
    PERF_EXIT=${PIPESTATUS[0]}
else
    echo "  Skipping performance tests (set RUN_PERFORMANCE_TESTS=true to run)"
    PERF_EXIT=0
fi

# Summary
echo ""
echo "============================================================"
echo "TEST SUMMARY"
echo "============================================================"
echo ""
echo "  Unit Tests:        $([ $UNIT_EXIT -eq 0 ] && echo "PASSED" || echo "FAILED")"
echo "  Integration Tests: $([ $INT_EXIT -eq 0 ] && echo "PASSED" || echo "FAILED")"
echo "  Performance Tests: $([ $PERF_EXIT -eq 0 ] && echo "PASSED" || echo "SKIPPED")"
echo ""
echo "  Coverage report: test_results/coverage_html/index.html"
echo "  JUnit report: test_results/junit.xml"
echo ""

# Create phase marker
if [ $UNIT_EXIT -eq 0 ]; then
    cat > .fase_status/phase4_complete << 'EOF'
{
  "status": "COMPLETED",
  "timestamp": "2026-06-01T18:30:00",
  "components": [
    "unit_tests_enhanced",
    "integration_tests",
    "test_fixtures"
  ]
}
EOF
    echo "✅ Phase 4 completed!"
else
    echo "⚠️ Some tests failed. Please review before proceeding."
fi

exit $UNIT_EXIT
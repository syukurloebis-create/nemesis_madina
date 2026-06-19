#!/bin/bash
# Run all debug tests before making changes

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     NEMESIS MADINA - PRE-FIX DEBUG TEST SUITE               ║"
echo "║     Timestamp: $(date)                                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Create results directory
mkdir -p test_results

# Function to run test and save output
run_test() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶ Running: $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python3 "$1" 2>&1 | tee "test_results/$(basename $1 .py).log"
    echo ""
}

# Check if Python dependencies are installed
echo "📦 Checking test dependencies..."
pip3 install requests sqlalchemy psycopg2-binary 2>/dev/null

# Run all tests
run_test "tests/debug/test_healthcheck.py"
run_test "tests/debug/test_dns_resolution.py"
run_test "tests/debug/test_database_integrity.py"
run_test "tests/performance/test_load_balancing.py"
run_test "tests/debug/test_error_scenarios.py"

# Generate summary report
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY REPORT                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📊 Test results saved to: ./test_results/"
echo ""
echo "🔍 Quick analysis:"
echo ""

# Check for common issues
if grep -q "❌" test_results/*.log 2>/dev/null; then
    echo "⚠️  WARNING: Some tests failed. Review logs above."
    echo ""
    echo "Common issues found:"
    grep -h "❌" test_results/*.log 2>/dev/null | sort -u
else
    echo "✅ All tests passed! System is healthy."
fi

echo ""
echo "💡 Recommendation:"
echo "   - If all tests pass, system is ready for blueprint implementation"
echo "   - If some tests fail, run individual test for detailed debug"
echo ""
echo "📁 To view full logs: cat test_results/*.log"
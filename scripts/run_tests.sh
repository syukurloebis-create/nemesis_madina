#!/bin/bash
# scripts/run_tests.sh

echo "========================================="
echo "NEMESIS TEST RUNNER"
echo "========================================="

case "$1" in
    unit)
        echo "📁 Running unit tests..."
        pytest tests/ -m unit -v --ignore=tests/performance --ignore=tests/e2e
        ;;
    integration)
        echo "📁 Running integration tests..."
        pytest tests/integration/ -m integration -v
        ;;
    event-store)
        echo "📁 Running Event Store tests..."
        pytest tests/ -m event_store -v --ignore=tests/performance --ignore=tests/e2e
        ;;
    all)
        echo "📁 Running all tests (except performance)..."
        pytest tests/ -v --ignore=tests/performance --ignore=tests/e2e
        ;;
    *)
        echo "Usage: $0 {unit|integration|event-store|all}"
        echo ""
        echo "Commands:"
        echo "  unit        - Run only unit tests"
        echo "  integration - Run only integration tests"
        echo "  event-store - Run only Event Store tests"
        echo "  all         - Run all tests except performance/e2e"
        exit 1
        ;;
esac
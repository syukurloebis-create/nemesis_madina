#!/bin/bash
# NEMESIS Benchmark Script

set -e

echo "=== NEMESIS Benchmark ==="
echo "Running 1,000,000 events benchmark..."

# Run benchmark
python benchmarks/event_store_benchmark.py \
    --events 1000000 \
    --concurrent 10 \
    --output reports/benchmark_results.json

# Check results
if [ $? -eq 0 ]; then
    echo "✓ Benchmark passed"
    
    # Extract metrics
    P95=$(jq '.results.append_p95' reports/benchmark_results.json)
    REBUILD=$(jq '.results.rebuild_time_minutes' reports/benchmark_results.json)
    
    echo "  Append P95: ${P95}ms"
    echo "  Rebuild Time: ${REBUILD} minutes"
    
    # Validate against targets
    if (( $(echo "$P95 <= 50" | bc -l) )); then
        echo "  ✓ G1: append_p95 target met"
    else
        echo "  ✗ G1: append_p95 target NOT met"
        exit 1
    fi
    
    if (( $(echo "$REBUILD <= 10" | bc -l) )); then
        echo "  ✓ G2: rebuild target met"
    else
        echo "  ✗ G2: rebuild target NOT met"
        exit 1
    fi
else
    echo "✗ Benchmark failed"
    exit 1
fi

echo "=== Gate B: ALL PASS ==="
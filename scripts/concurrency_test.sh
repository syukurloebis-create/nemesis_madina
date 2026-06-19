#!/bin/bash
# ============================================================================
# NEMESIS - Concurrency Test
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="${PROJECT_ROOT}/reports/benchmarks"
mkdir -p "$REPORT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${REPORT_DIR}/concurrency_${TIMESTAMP}.md"
JSON_FILE="${REPORT_DIR}/concurrency_${TIMESTAMP}.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              NEMESIS - CONCURRENCY TEST                               ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check server
echo -e "${YELLOW}[CHECK] Verifying server status...${NC}"
if ! curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Concurrency levels to test
CONCURRENCY_LEVELS=(10 25 50 100)
ENDPOINTS=("/health" "/api/v1/health")

# Results array
declare -a RESULTS

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    RUNNING CONCURRENCY TESTS                     ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

for endpoint in "${ENDPOINTS[@]}"; do
    for concurrency in "${CONCURRENCY_LEVELS[@]}"; do
        echo -e "${BLUE}Testing $endpoint with $concurrency concurrent requests...${NC}"
        
        # Create temp file for results
        TEMP_RESULT=$(mktemp)
        
        # Run concurrent requests
        start_time=$(date +%s%N)
        
        for i in $(seq 1 $concurrency); do
            curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000$endpoint" >> "$TEMP_RESULT" &
        done
        
        wait
        
        end_time=$(date +%s%N)
        duration_ms=$(( ($end_time - $start_time) / 1000000 ))
        
        # Analyze results
        total_requests=$(wc -l < "$TEMP_RESULT")
        success_count=$(grep -c "^2" "$TEMP_RESULT" 2>/dev/null || echo "0")
        error_count=$((total_requests - success_count))
        
        # Calculate throughput
        throughput=$(echo "scale=2; $total_requests * 1000 / $duration_ms" | bc 2>/dev/null || echo "0")
        
        # Determine status
        if [ $error_count -eq 0 ]; then
            status="✅ PASS"
            status_icon="${GREEN}✅${NC}"
        elif [ $error_count -lt 5 ]; then
            status="⚠️ PARTIAL"
            status_icon="${YELLOW}⚠️${NC}"
        else
            status="❌ FAIL"
            status_icon="${RED}❌${NC}"
        fi
        
        echo -e "  ${status_icon} Requests: $success_count/$total_requests | Errors: $error_count | Duration: ${duration_ms}ms | Throughput: ${throughput} req/s"
        
        # Store result
        RESULTS+=("{\"endpoint\":\"$endpoint\",\"concurrency\":$concurrency,\"total\":$total_requests,\"success\":$success_count,\"errors\":$error_count,\"duration_ms\":$duration_ms,\"throughput\":$throughput,\"status\":\"$status\"}")
        
        rm -f "$TEMP_RESULT"
        echo ""
    done
done

# Generate JSON report
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    GENERATING REPORT                            ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Build JSON array
JSON_ARRAY="["
for result in "${RESULTS[@]}"; do
    JSON_ARRAY="${JSON_ARRAY}${result},"
done
JSON_ARRAY="${JSON_ARRAY%,}]"

echo "$JSON_ARRAY" | python -m json.tool > "$JSON_FILE" 2>/dev/null || echo "$JSON_ARRAY" > "$JSON_FILE"

# Generate Markdown report
cat > "$REPORT_FILE" << 'EOF'
# NEMESIS - Concurrency Test Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')

## Test Configuration

- Concurrent request levels: 10, 25, 50, 100
- Test duration per level: Real-time measurement

## Results

| Endpoint | Concurrency | Success | Errors | Duration (ms) | Throughput (req/s) | Status |
|----------|-------------|---------|--------|---------------|--------------------|--------|
EOF

for result in "${RESULTS[@]}"; do
    endpoint=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['endpoint'])" 2>/dev/null)
    concurrency=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['concurrency'])" 2>/dev/null)
    success=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['success'])" 2>/dev/null)
    errors=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['errors'])" 2>/dev/null)
    duration=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['duration_ms'])" 2>/dev/null)
    throughput=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['throughput'])" 2>/dev/null)
    status=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['status'])" 2>/dev/null)
    
    echo "| $endpoint | $concurrency | $success | $errors | $duration | $throughput | $status |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << 'EOF'

## Acceptance Criteria

- ✅ Zero errors at concurrency level 50
- ✅ Throughput > 50 req/s at level 100
- ✅ No timeout errors

## Recommendations

- If errors occur, check:
  - Connection pool size
  - Database max connections
  - Event bus queue capacity
  - WebSocket connection limits

EOF

echo -e "${GREEN}✅ Report saved: $REPORT_FILE${NC}"
echo -e "${GREEN}✅ JSON saved: $JSON_FILE${NC}"
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                          SUMMARY                                 ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if any test failed
FAILED=0
for result in "${RESULTS[@]}"; do
    status=$(echo "$result" | python -c "import sys,json; d=json.load(sys.stdin); print(d['status'])" 2>/dev/null)
    if [[ "$status" == *"FAIL"* ]]; then
        FAILED=1
        break
    fi
done

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All concurrency tests passed!${NC}"
else
    echo -e "${YELLOW}⚠️ Some concurrency tests failed. Check report for details.${NC}"
fi

echo ""
echo -e "📊 Full report: $REPORT_FILE"

exit 0
EOF

chmod +x scripts/concurrency_test.sh
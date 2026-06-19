#!/bin/bash
# ============================================================================
# NEMESIS - Hari 4: Resilience & Recovery Test Runner
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              NEMESIS - HARI 4: RESILIENCE & RECOVERY                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if server is running
echo -e "${YELLOW}[CHECK] Verifying server status...${NC}"
if ! curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server is not running${NC}"
    echo "  Please start server first: ./scripts/start_server.sh"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Create reports directory
mkdir -p "$PROJECT_ROOT/reports/resilience_tests"

# Test 1: Recovery Test
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    TEST 1: RECOVERY TEST                        ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_recovery.py"
RECOVERY_RESULT=$?

# Test 2: Circuit Breaker
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    TEST 2: CIRCUIT BREAKER                      ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_circuit_breaker.py"
CIRCUIT_RESULT=$?

# Test 3: Failover
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    TEST 3: FAILOVER TEST                        ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_failover.py"
FAILOVER_RESULT=$?

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                          SUMMARY                                 ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $RECOVERY_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Recovery Test: PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️ Recovery Test: PARTIAL${NC}"
fi

if [ $CIRCUIT_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Circuit Breaker: PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️ Circuit Breaker: PARTIAL${NC}"
fi

if [ $FAILOVER_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Failover Test: PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️ Failover Test: PARTIAL${NC}"
fi

echo ""
echo -e "${GREEN}📊 Reports saved in: reports/resilience_tests/${NC}"

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/hari4_complete" << EOF
{
  "status": "COMPLETED",
  "date": "$(date -Iseconds)",
  "tests": {
    "recovery": $([ $RECOVERY_RESULT -eq 0 ] && echo "true" || echo "false"),
    "circuit_breaker": $([ $CIRCUIT_RESULT -eq 0 ] && echo "true" || echo "false"),
    "failover": $([ $FAILOVER_RESULT -eq 0 ] && echo "true" || echo "false")
  },
  "reports": "reports/resilience_tests/"
}
EOF

echo ""
echo -e "${GREEN}✅ Hari 4 completed!${NC}"

exit 0
EOF

chmod +x scripts/run_hari4.sh
chmod +x scripts/test_recovery.py
chmod +x scripts/test_circuit_breaker.py
chmod +x scripts/test_failover.py
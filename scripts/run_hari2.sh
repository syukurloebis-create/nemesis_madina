#!/bin/bash
# ============================================================================
# NEMESIS - Hari 2: Event & Graph Scale Test Runner
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
echo "║              NEMESIS - HARI 2: SCALE TEST                             ║"
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

# Install required packages if needed
echo -e "${YELLOW}[SETUP] Checking dependencies...${NC}"
pip install psutil -q 2>/dev/null || echo "  ⚠️ psutil already installed"
echo -e "${GREEN}✅ Dependencies ready${NC}"
echo ""

# Create reports directory
mkdir -p "$PROJECT_ROOT/reports/scale_tests"

# Test 1: Event Burst Test
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                         TEST 1: EVENT BURST                      ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_event_burst.py"
EVENT_RESULT=$?

# Test 2: Graph Scale Test
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                         TEST 2: GRAPH SCALE                     ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_graph_scale.py"
GRAPH_RESULT=$?

# Test 3: Memory Monitoring (optional background)
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                      TEST 3: MEMORY MONITOR                      ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/monitor_memory.py" --duration 30
MEMORY_RESULT=$?

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                          SUMMARY                                 ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $EVENT_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Event Burst Test: PASSED${NC}"
else
    echo -e "  ${RED}❌ Event Burst Test: FAILED${NC}"
fi

if [ $GRAPH_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Graph Scale Test: PASSED${NC}"
else
    echo -e "  ${RED}❌ Graph Scale Test: FAILED${NC}"
fi

echo -e "  ${GREEN}✅ Memory Monitor: Completed${NC}"

echo ""
echo -e "${GREEN}📊 Reports saved in: reports/scale_tests/${NC}"

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/hari2_complete" << EOF
{
  "status": "COMPLETED",
  "date": "$(date -Iseconds)",
  "tests": {
    "event_burst": $([ $EVENT_RESULT -eq 0 ] && echo "true" || echo "false"),
    "graph_scale": $([ $GRAPH_RESULT -eq 0 ] && echo "true" || echo "false")
  },
  "reports": "reports/scale_tests/"
}
EOF

exit 0
EOF

chmod +x scripts/run_hari2.sh
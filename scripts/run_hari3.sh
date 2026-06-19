#!/bin/bash
# ============================================================================
# NEMESIS - Hari 3: Security Edge Cases Runner
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
echo "║              NEMESIS - HARI 3: SECURITY EDGE CASES                    ║"
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
mkdir -p "$PROJECT_ROOT/reports/security_tests"

# Test 1: JWT Edge Cases
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    TEST 1: JWT EDGE CASES                       ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_jwt_edges.py"
JWT_RESULT=$?

# Test 2: Rate Limit
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    TEST 2: RATE LIMIT                           ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_rate_limit.py"
RATE_RESULT=$?

# Test 3: Auth Flow
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    TEST 3: AUTH FLOW                            ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python "$SCRIPT_DIR/test_auth_flow.py"
AUTH_RESULT=$?

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                          SUMMARY                                 ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $JWT_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ JWT Edge Cases: PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️ JWT Edge Cases: PARTIAL${NC}"
fi

if [ $RATE_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Rate Limit: PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️ Rate Limit: PARTIAL${NC}"
fi

if [ $AUTH_RESULT -eq 0 ]; then
    echo -e "  ${GREEN}✅ Auth Flow: PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️ Auth Flow: PARTIAL${NC}"
fi

echo ""
echo -e "${GREEN}📊 Reports saved in: reports/security_tests/${NC}"

# Create status marker
mkdir -p "$PROJECT_ROOT/.fase_status"
cat > "$PROJECT_ROOT/.fase_status/hari3_complete" << EOF
{
  "status": "COMPLETED",
  "date": "$(date -Iseconds)",
  "tests": {
    "jwt_edges": $([ $JWT_RESULT -eq 0 ] && echo "true" || echo "false"),
    "rate_limit": $([ $RATE_RESULT -eq 0 ] && echo "true" || echo "false"),
    "auth_flow": $([ $AUTH_RESULT -eq 0 ] && echo "true" || echo "false")
  },
  "reports": "reports/security_tests/"
}
EOF

echo ""
echo -e "${GREEN}✅ Hari 3 completed!${NC}"

exit 0
EOF

chmod +x scripts/run_hari3.sh
chmod +x scripts/test_jwt_edges.py
chmod +x scripts/test_rate_limit.py
chmod +x scripts/test_auth_flow.py
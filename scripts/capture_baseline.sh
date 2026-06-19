#!/bin/bash
# ============================================================================
# NEMESIS - Baseline Metrics Capture
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="${PROJECT_ROOT}/reports/benchmarks"
mkdir -p "$REPORT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASELINE_FILE="${REPORT_DIR}/baseline_${TIMESTAMP}.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              NEMESIS - BASELINE METRICS CAPTURE                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Capture system info
echo -e "${BLUE}[1/5] Capturing system information...${NC}"
SYSTEM_INFO=$(cat << EOF
{
  "timestamp": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "os": "$(uname -a)",
  "python_version": "$(python --version 2>&1)",
  "cpu_count": $(nproc 2>/dev/null || echo 1),
  "memory_total_gb": $(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "N/A")
}
EOF
)

# Capture API metrics
echo -e "${BLUE}[2/5] Capturing API metrics...${NC}"
API_METRICS=$(curl -s http://localhost:8000/metrics 2>/dev/null || echo '{"error":"not available"}')

# Capture health status
echo -e "${BLUE}[3/5] Capturing health status...${NC}"
HEALTH_STATUS=$(curl -s http://localhost:8000/health 2>/dev/null || echo '{"status":"unavailable"}')

# Capture detailed health
echo -e "${BLUE}[4/5] Capturing detailed health...${NC}"
DETAILED_HEALTH=$(curl -s http://localhost:8000/health/detailed 2>/dev/null || echo '{"status":"unavailable"}')

# Capture version info
echo -e "${BLUE}[5/5] Capturing version information...${NC}"
VERSION_INFO=$(cat << EOF
{
  "nemesis_version": "2.0.0",
  "api_version": "v1",
  "build_date": "$(date -Iseconds)"
}
EOF
)

# Combine all into single JSON
cat > "$BASELINE_FILE" << EOF
{
  "system": $SYSTEM_INFO,
  "health": $HEALTH_STATUS,
  "detailed_health": $DETAILED_HEALTH,
  "api_metrics": $API_METRICS,
  "version": $VERSION_INFO,
  "capture_timestamp": "$(date -Iseconds)"
}
EOF

echo ""
echo -e "${GREEN}✅ Baseline captured: $BASELINE_FILE${NC}"
echo ""

# Display summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                          SUMMARY                                 ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

HEALTH_STATUS=$(echo "$HEALTH_STATUS" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null)
echo "  Health Status: $HEALTH_STATUS"
echo "  Capture Time: $(date)"
echo "  Report: $BASELINE_FILE"

exit 0
EOF

chmod +x scripts/capture_baseline.sh
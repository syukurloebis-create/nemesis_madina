#!/bin/bash
# ============================================================================
# NEMESIS Monitor Script
# ============================================================================

API_URL="http://localhost:8000"

echo "============================================================"
echo "NEMESIS MONITOR"
echo "============================================================"
echo ""

# Check server status
echo "[1] Server Status:"
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    echo "    [OK] Server is running"
else
    echo "    [FAIL] Server is not responding"
    exit 1
fi

# Health check
echo ""
echo "[2] Health Check:"
curl -s "$API_URL/health" | python -m json.tool 2>/dev/null

# Metrics
echo ""
echo "[3] Metrics:"
curl -s "$API_URL/metrics" | python -m json.tool 2>/dev/null

# System info
echo ""
echo "[4] System Info:"
echo "    Time: $(date)"
echo "    Uptime: $(uptime 2>/dev/null || echo "N/A")"

echo ""
echo "============================================================"

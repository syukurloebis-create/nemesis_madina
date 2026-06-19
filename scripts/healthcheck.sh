#!/bin/bash
# ============================================================================
# NEMESIS Health Check Script
# ============================================================================

API_URL=${API_URL:-http://localhost:8000}
WS_URL=${WS_URL:-ws://localhost:8001}

echo "Running health checks..."

# API Health
echo -n "API Health: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/health)
if [ "$HTTP_CODE" = "200" ]; then
    echo "OK"
else
    echo "FAILED (HTTP $HTTP_CODE)"
    exit 1
fi

# API Readiness
echo -n "API Readiness: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/health/ready)
if [ "$HTTP_CODE" = "200" ]; then
    echo "OK"
else
    echo "FAILED (HTTP $HTTP_CODE)"
    exit 1
fi

# Metrics endpoint
echo -n "Metrics endpoint: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/metrics)
if [ "$HTTP_CODE" = "200" ]; then
    echo "OK"
else
    echo "FAILED (HTTP $HTTP_CODE)"
    exit 1
fi

# WebSocket (simple check)
echo -n "WebSocket: "
if command -v wscat &> /dev/null; then
    echo "WebSocket check requires wscat"
else
    echo "Skipped (install wscat for WebSocket tests)"
fi

echo "All health checks passed!"

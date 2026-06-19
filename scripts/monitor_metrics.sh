#!/bin/bash
# Metrics monitor - run every 30 seconds

echo "=== WEBSOCKET METRICS MONITOR ==="
echo "Monitoring every 30 seconds. Press Ctrl+C to stop."
echo ""

COUNT=0
while true; do
    COUNT=$((COUNT + 1))
    echo "[$COUNT] $(date '+%H:%M:%S')"
    curl -s http://localhost:8000/websocket/metrics | python -m json.tool 2>/dev/null
    echo ""
    sleep 30
done

#!/bin/bash
# NEMESIS Performance Monitor

echo "=== NEMESIS Performance Monitor ==="
echo "Time: $(date)"
echo ""

# CPU Usage
echo "CPU Usage:"
top -bn1 | head -3 | tail -1

# Memory Usage
echo -e "\nMemory Usage:"
free -h

# API Response Times
echo -e "\nAPI Response Times:"
for endpoint in "/health" "/api/v1/cases/stats" "/api/v1/alerts/stats"; do
    START=$(date +%s%N)
    curl -s http://localhost:8000${endpoint} > /dev/null
    END=$(date +%s%N)
    TIME=$((($END - $START)/1000000))
    echo "  ${endpoint}: ${TIME}ms"
done

# Active Connections
echo -e "\nActive Connections:"
netstat -an | grep 8000 | wc -l

# Frontend Build Size
echo -e "\nFrontend Build Size:"
if [ -d "frontend/dist" ]; then
    du -sh frontend/dist/
else
    echo "  Build not found"
fi

echo ""
echo "=== Monitoring Complete ==="

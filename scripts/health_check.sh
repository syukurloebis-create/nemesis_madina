#!/bin/bash
# NEMESIS Health Check Script

echo "=== NEMESIS V8+ Health Check ==="

# Check API
echo -n "API Health: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health

# Check Database
echo -n "Database: "
docker exec nemesis_madina-postgres-1 pg_isready -U nemesis -d nemesis_db

# Check Events Count
echo -n "Total Events: "
docker exec nemesis_madina-postgres-1 psql -U nemesis -d nemesis_db -t -c "SELECT COUNT(*) FROM events;" | tr -d ' '

# Check Integrity
echo -n "Integrity Status: "
curl -s http://localhost:8000/integrity/verify-all | python -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['passed_cases']}/{d['total_cases']} cases passed\")" 2>/dev/null || echo "N/A"

echo "=== Health Check Complete ==="

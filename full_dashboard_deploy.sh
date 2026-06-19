#!/bin/bash
set -e

echo "========================================="
echo "🚀 FULL DASHBOARD DEPLOYMENT"
echo "========================================="

# 1. Update files (already done via cat commands above)
echo "1️⃣ Files updated: metrics.py, main.py"

# 2. Rebuild
echo ""
echo "2️⃣ Rebuilding containers..."
docker-compose -f docker-compose.lb.yml down
docker-compose -f docker-compose.lb.yml build --no-cache
docker-compose -f docker-compose.lb.yml up -d

# 3. Wait
echo ""
echo "3️⃣ Waiting for containers (60s)..."
for i in {1..60}; do echo -n "."; sleep 1; done
echo ""

# 4. Generate test traffic
echo "4️⃣ Generating test traffic..."
for i in {1..30}; do
    curl -s http://localhost/health > /dev/null 2>&1
    curl -s http://localhost/cases/ > /dev/null 2>&1
    curl -s http://localhost/api/dashboard/summary > /dev/null 2>&1
done
echo "   Done"

# 5. Wait for Prometheus
echo "5️⃣ Waiting for Prometheus scrape (30s)..."
sleep 30

# 6. Import dashboard
echo "6️⃣ Importing dashboard..."
curl -s -X POST "http://admin:admin@localhost:3000/api/dashboards/db" \
  -H "Content-Type: application/json" \
  -d @nemesis_dashboard_fixed.json | jq '.status, .uid'

echo ""
echo "========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================="
echo "🔗 Dashboard: http://localhost:3000/d/nemesis-production-v2"
echo "   Login: admin / admin"
echo "   Hard refresh: Ctrl+Shift+R"
echo ""
echo "📊 All panels should now show data:"
echo "   - API Health Status: 3"
echo "   - System Uptime: >0"
echo "   - Total Cases: 21"
echo "   - API Response Time: >0 (p95 latency)"
echo "   - Cases by Priority: pie chart"
echo "========================================="

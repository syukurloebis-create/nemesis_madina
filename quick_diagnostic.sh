#!/bin/bash
# Quick diagnostic untuk pre-fix assessment

echo "═══════════════════════════════════════════════════════════════"
echo "                 NEMESIS MADINA - QUICK DIAGNOSTIC"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 1. Container Status
echo "📦 CONTAINER STATUS:"
echo "───────────────────────────────────────────────────────────────"
docker-compose -f docker-compose.lb.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
echo ""

# 2. API Health via Load Balancer
echo "🔍 API HEALTH (via Load Balancer):"
echo "───────────────────────────────────────────────────────────────"
HEALTH_RESPONSE=$(curl -s http://localhost/health)
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# 3. Database Connection Test
echo "🗄️ DATABASE CONNECTION:"
echo "───────────────────────────────────────────────────────────────"
DB_CHECK=$(docker exec nemesis_madina-postgres-1 pg_isready -U nemesis 2>&1)
echo "$DB_CHECK"
echo ""

# 4. DNS Resolution Test
echo "🌐 DNS RESOLUTION (API → PostgreSQL):"
echo "───────────────────────────────────────────────────────────────"
for api in api1 api2 api3; do
    RESULT=$(docker exec nemesis_madina-${api}-1 python -c "import socket; print(socket.gethostbyname('postgres'))" 2>/dev/null)
    if [ "$RESULT" != "" ]; then
        echo "✅ $api: postgres = $RESULT"
    else
        echo "❌ $api: Cannot resolve postgres"
    fi
done
echo ""

# 5. Recent Error Logs
echo "📋 RECENT ERRORS (last 5 per container):"
echo "───────────────────────────────────────────────────────────────"
for api in api1 api2 api3; do
    echo ""
    echo "[$api]"
    docker logs nemesis_madina-${api}-1 --tail=10 2>&1 | grep -i "error\|fail\|exception" || echo "  No recent errors"
done
echo ""

# 6. Summary
echo "═══════════════════════════════════════════════════════════════"
echo "SUMMARY & RECOMMENDATIONS:"
echo "═══════════════════════════════════════════════════════════════"

# Check health endpoint
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ API is healthy and responding"
else
    echo "❌ API is not healthy - check logs"
fi

# Check database
if echo "$DB_CHECK" | grep -q "accepting connections"; then
    echo "✅ Database is accepting connections"
else
    echo "❌ Database is not responding"
fi

# Check DNS
if [ "$(docker exec nemesis_madina-api1-1 python -c 'import socket; print(socket.gethostbyname("postgres"))' 2>/dev/null)" != "" ]; then
    echo "✅ DNS resolution working correctly"
else
    echo "⚠️ DNS resolution issue detected (but system may still work via IP)"
fi

echo ""
echo "💡 READINESS FOR BLUEPRINT:"
if echo "$HEALTH_RESPONSE" | grep -q "healthy" && echo "$DB_CHECK" | grep -q "accepting"; then
    echo "   ✅ SYSTEM IS READY for Fase B-I implementation"
    echo "   📝 Next: Run full debug tests with run_debug_tests.sh"
else
    echo "   ❌ System has issues that need fixing before blueprint"
    echo "   🔧 Run: python3 tests/debug/test_healthcheck.py"
fi
echo ""
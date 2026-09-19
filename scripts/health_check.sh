#!/usr/bin/env bash
# NEMESIS — Health Check
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8000}"
CASE_ID="b4897392-87ab-4e7a-84b6-90228f3d1eb9"

echo "═══════════════════════════════════════════════════════════════"
echo " NEMESIS CP2.5.1 — HEALTH CHECK"
echo "═══════════════════════════════════════════════════════════════"

echo
echo "───── Containers ─────"
docker compose ps | head -10

echo
echo "───── Health Endpoints ─────"
for ep in /health /health/live /health/ready; do
  printf "  %-20s → " "$ep"
  status=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$ep" || echo "000")
  if [ "$status" = "200" ]; then
    echo "HTTP $status ✅"
  else
    echo "HTTP $status ⚠️"
  fi
done

echo
echo "───── /health/ready detail ─────"
curl -s "$API_URL/health/ready" | jq . 2>/dev/null || echo "  (no JSON)"

echo
echo "───── Baseline ─────"
FRESH_TOKEN=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}' | jq -r '.access_token // empty')

if [ -z "$FRESH_TOKEN" ]; then
  echo "  ❌ Auth failed"
  exit 1
fi

echo "  Auth: ✅"
echo -n "  Risk:  "
curl -s "$API_URL/api/v1/risk/explanations/$CASE_ID" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq -c '{score, risk_level}'

echo -n "  Graph: "
curl -s "$API_URL/api/v1/graph/cases/$CASE_ID/summary" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq -c '{total_entities, total_relationships}'

echo
echo "═══════════════════════════════════════════════════════════════"

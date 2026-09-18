#!/usr/bin/env bash
# scripts/F3.6_regression.sh
# F3.6 — Regression Verification
# Baseline: 47.58 MEDIUM (FROZEN)
# Case: b4897392-87ab-4e7a-84b6-90228f3d1eb9

set -euo pipefail

API="http://127.0.0.1:8000"
CASE="b4897392-87ab-4e7a-84b6-90228f3d1eb9"
PG="nemesis_madina_cp25_audit-postgres-1"

echo "═══════════════════════════════════════════════════════════"
echo " F3.6 Regression Verification"
echo " Case: $CASE"
echo "═══════════════════════════════════════════════════════════"
echo

# ─── Login ────────────────────────────────────────────────────────
TOKEN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}' | jq -r '.access_token')

[ -n "$TOKEN" ] && [ "$TOKEN" != "null" ] || { echo "✗ Login FAILED"; exit 1; }
AUTH="Authorization: Bearer $TOKEN"

# ─── [1] Risk baseline anchor ────────────────────────────────────
echo "▶ [1/5] Risk baseline anchor"
RISK=$(curl -s "$API/api/v1/risk/explanations/$CASE" -H "$AUTH")
SCORE=$(echo "$RISK" | jq -r '.score')
LEVEL=$(echo "$RISK" | jq -r '.risk_level')

[ "$SCORE" = "47.58" ] || { echo "  ✗ score: $SCORE (expected 47.58)"; exit 1; }
[ "$LEVEL" = "MEDIUM" ] || { echo "  ✗ level: $LEVEL (expected MEDIUM)"; exit 1; }
echo "  ✓ score=$SCORE level=$LEVEL"
echo

# ─── [2] DB state ─────────────────────────────────────────────────
echo "▶ [2/5] DB state"
ENT=$(docker exec "$PG" psql -U nemesis -d nemesis_db -tAc \
  "SELECT COUNT(*) FROM graph_entities WHERE case_id = '$CASE';")
REL=$(docker exec "$PG" psql -U nemesis -d nemesis_db -tAc \
  "SELECT COUNT(*) FROM graph_relationships WHERE case_id = '$CASE';")
DET=$(docker exec "$PG" psql -U nemesis -d nemesis_db -tAc \
  "SELECT COUNT(*) FROM collusion_detections WHERE case_id = '$CASE';")

[ "$ENT" = "4177" ] || { echo "  ✗ entities: $ENT (expected 4177)"; exit 1; }
[ "$REL" = "2424" ] || { echo "  ✗ relationships: $REL (expected 2424)"; exit 1; }
[ "$DET" = "0" ]    || { echo "  ✗ detections: $DET (expected 0)"; exit 1; }
echo "  ✓ entities=$ENT relationships=$REL detections=$DET"
echo

# ─── [3] Canonical Graph API 7/7 ─────────────────────────────────
echo "▶ [3/5] Canonical Graph API"
for ep in "" "/summary" "/metrics" "/entities" "/relationships" "/key-actors" "/collusion"; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    "$API/api/v1/graph/cases/$CASE$ep" -H "$AUTH")
  [ "$CODE" = "200" ] || { echo "  ✗ /cases/\$CASE$ep → $CODE"; exit 1; }
  echo "  ✓ /cases/\$CASE$ep → $CODE"
done
echo

# ─── [4] Risk Engine isolation ───────────────────────────────────
echo "▶ [4/5] Risk Engine isolation (no side-effect from Graph reads)"
BEFORE=$(curl -s "$API/api/v1/risk/explanations/$CASE" -H "$AUTH" | jq -r '.score')

for _ in 1 2 3; do
  curl -s "$API/api/v1/graph/cases/$CASE/summary" -H "$AUTH" > /dev/null
  curl -s "$API/api/v1/graph/cases/$CASE/key-actors" -H "$AUTH" > /dev/null
done

AFTER=$(curl -s "$API/api/v1/risk/explanations/$CASE" -H "$AUTH" | jq -r '.score')

[ "$BEFORE" = "$AFTER" ] || { echo "  ✗ baseline drifted: $BEFORE → $AFTER"; exit 1; }
[ "$AFTER" = "47.58" ]   || { echo "  ✗ unexpected baseline: $AFTER"; exit 1; }
echo "  ✓ isolated: $BEFORE → $AFTER"
echo

# ─── [5] Legacy behaviour sanity ─────────────────────────────────
echo "▶ [5/5] Legacy behaviour sanity"
C1=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/graph" -H "$AUTH")
[ "$C1" = "410" ] || { echo "  ✗ /api/v1/graph → $C1 (expected 410)"; exit 1; }
echo "  ✓ /api/v1/graph → 410"

C2=$(curl -s -o /dev/null -w "%{http_code}" \
  "$API/api/v1/graph/stats?case_id=$CASE" -H "$AUTH")
[ "$C2" = "301" ] || { echo "  ✗ /api/v1/graph/stats → $C2 (expected 301)"; exit 1; }
echo "  ✓ /api/v1/graph/stats → 301"
echo

echo "═══════════════════════════════════════════════════════════"
echo " F3.6 REGRESSION — ✅ ALL PASS"
echo "═══════════════════════════════════════════════════════════"
#!/usr/bin/env bash
# scripts/F3.5_verify.sh
# F3.5 — Runtime Verification for Graph Intelligence
# Baseline case: b4897392-87ab-4e7a-84b6-90228f3d1eb9
# Expected: 4177 entities, 2424 relationships, risk 47.58 MEDIUM

set -euo pipefail

API="http://127.0.0.1:8000"
CASE="b4897392-87ab-4e7a-84b6-90228f3d1eb9"

echo "═══════════════════════════════════════════════════════════"
echo " F3.5 Runtime Verification — Graph Intelligence (Hybrid)"
echo " Case: $CASE"
echo "═══════════════════════════════════════════════════════════"
echo

# ─── 1. Health ────────────────────────────────────────────────────
echo "▶ [1/7] Health check"
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$API/health")
echo "  HTTP $HEALTH"
[ "$HEALTH" = "200" ] || { echo "  ✗ FAIL"; exit 1; }
echo "  ✓ OK"
echo

# ─── 2. Login ─────────────────────────────────────────────────────
echo "▶ [2/7] Login"
TOKEN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}' | jq -r '.access_token')

[ -n "$TOKEN" ] && [ "$TOKEN" != "null" ] || { echo "  ✗ FAIL"; exit 1; }
echo "  ✓ Token acquired"
echo

AUTH="Authorization: Bearer $TOKEN"

# ─── 3. Canonical: summary ────────────────────────────────────────
echo "▶ [3/7] GET /api/v1/graph/cases/$CASE/summary"
SUMMARY=$(curl -s "$API/api/v1/graph/cases/$CASE/summary" -H "$AUTH")
echo "$SUMMARY" | jq .

ENT=$(echo "$SUMMARY" | jq -r '.total_entities')
REL=$(echo "$SUMMARY" | jq -r '.total_relationships')

[ "$ENT" = "4177" ] || { echo "  ✗ FAIL: expected 4177 entities, got $ENT"; exit 1; }
[ "$REL" = "2424" ] || { echo "  ✗ FAIL: expected 2424 relationships, got $REL"; exit 1; }
echo "  ✓ Nodes: $ENT | Edges: $REL"
echo

# ─── 4. Canonical: metrics (density) ──────────────────────────────
echo "▶ [4/7] GET /api/v1/graph/cases/$CASE/metrics"
curl -s "$API/api/v1/graph/cases/$CASE/metrics" -H "$AUTH" | jq '{total_entities, total_relationships, density}'
echo

# ─── 5. Canonical: key-actors (no risk_score, no confidence) ──────
echo "▶ [5/7] GET /api/v1/graph/cases/$CASE/key-actors"
ACTORS=$(curl -s "$API/api/v1/graph/cases/$CASE/key-actors?limit=5" -H "$AUTH")
echo "$ACTORS" | jq .

# Assert no risk_score / confidence
if echo "$ACTORS" | jq -e '.actors[0] | has("risk_score")' > /dev/null 2>&1; then
  echo "  ✗ FAIL: risk_score must NOT exist in actors"
  exit 1
fi
if echo "$ACTORS" | jq -e '.actors[0] | has("confidence")' > /dev/null 2>&1; then
  echo "  ✗ FAIL: confidence must NOT exist in actors"
  exit 1
fi
echo "  ✓ OK: no risk_score/confidence (domain-honest)"
echo

# ─── 6. Legacy behaviour ──────────────────────────────────────────
echo "▶ [6/7] Legacy endpoints"

# 6a. /api/v1/graph (no case_id) → 410 Gone
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/graph" -H "$AUTH")
echo "  /api/v1/graph                    → $CODE (expected 410)"
[ "$CODE" = "410" ] || { echo "  ✗ FAIL"; exit 1; }

# 6b. /api/v1/graph/collusion/{case_id} → 410 Gone
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/graph/collusion/$CASE" -H "$AUTH")
echo "  /api/v1/graph/collusion/{case}   → $CODE (expected 410)"
[ "$CODE" = "410" ] || { echo "  ✗ FAIL"; exit 1; }

# 6c. /api/v1/graph/metrics?case_id=... → 301
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/graph/metrics?case_id=$CASE" -H "$AUTH")
echo "  /api/v1/graph/metrics?case_id=   → $CODE (expected 301)"
[ "$CODE" = "301" ] || { echo "  ✗ FAIL"; exit 1; }

# 6d. /api/v1/graph/stats?case_id=... → 301
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/graph/stats?case_id=$CASE" -H "$AUTH")
echo "  /api/v1/graph/stats?case_id=     → $CODE (expected 301)"
[ "$CODE" = "301" ] || { echo "  ✗ FAIL"; exit 1; }

echo "  ✓ OK"
echo

# ─── 7. Risk baseline anchor ──────────────────────────────────────
echo "▶ [7/7] Risk baseline anchor (MUST NOT change)"
RISK=$(curl -s "$API/api/v1/risk/explanations/$CASE" -H "$AUTH")
SCORE=$(echo "$RISK" | jq -r '.score')
LEVEL=$(echo "$RISK" | jq -r '.risk_level')

echo "  Score: $SCORE | Level: $LEVEL"
[ "$SCORE" = "47.58" ] || { echo "  ✗ FAIL: baseline score changed!"; exit 1; }
[ "$LEVEL" = "MEDIUM" ] || { echo "  ✗ FAIL: baseline level changed!"; exit 1; }
echo "  ✓ OK: baseline FROZEN"
echo

echo "═══════════════════════════════════════════════════════════"
echo " F3.5 RUNTIME VERIFICATION — ✅ ALL PASS"
echo "═══════════════════════════════════════════════════════════"
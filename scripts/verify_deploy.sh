#!/bin/bash
# NEMESIS — Verify deploy sync
# Purpose: Ensure dist/ is up to date with source

set -euo pipefail

: "${NEMESIS_TEST_USERNAME:?NEMESIS_TEST_USERNAME is required}"
: "${NEMESIS_TEST_PASSWORD:?NEMESIS_TEST_PASSWORD is required}"

cd "$(dirname "$0")/.."

echo "═══════════════════════════════════════════════════════════════"
echo " VERIFY DEPLOY SYNC"
echo "═══════════════════════════════════════════════════════════════"

echo
echo "===== [1] Source latest timestamp ====="
SRC_TIME=$(find frontend/src -type f \( -name '*.ts' -o -name '*.tsx' \) -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1)
echo "$SRC_TIME"

echo
echo "===== [2] Dist timestamp ====="
ls -la frontend/dist/index.html

echo
echo "===== [3] Bundle hash ====="
curl -sS http://localhost/ | grep -oE 'assets/index-[^"]+\.js'

echo
echo "===== [4] Baseline ====="
FRESH_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$NEMESIS_TEST_USERNAME\",\"password\":\"$NEMESIS_TEST_PASSWORD\"}" | jq -r '.access_token')
CASE=b4897392-87ab-4e7a-84b6-90228f3d1eb9

echo -n "Risk:  "
curl -s "http://127.0.0.1:8000/api/v1/risk/explanations/$CASE" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq -c '{score, risk_level}'

echo -n "Graph: "
curl -s "http://127.0.0.1:8000/api/v1/graph/cases/$CASE/summary" \
  -H "Authorization: Bearer $FRESH_TOKEN" | jq -c '{total_entities, total_relationships}'

echo
echo "═══════════════════════════════════════════════════════════════"
echo " ✅ Deploy verify complete"
echo "═══════════════════════════════════════════════════════════════"

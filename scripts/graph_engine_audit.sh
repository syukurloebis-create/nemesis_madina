#!/bin/bash

# =========================================================
# GRAPH ENGINE AUDIT PIPELINE (NEMESIS MADINA)
# =========================================================
# Tujuan:
# 1. Extract entity & transaction
# 2. Build graph
# 3. Validate graph structure
# 4. Run collusion detection
# =========================================================

CASE_ID="d48a0980-102b-451d-90dd-0b72ad381038"

echo "================================================="
echo "🧠 GRAPH ENGINE AUDIT START"
echo "CASE ID: $CASE_ID"
echo "================================================="


# =========================================================
# STEP 1 — ENTITY EXTRACTION
# =========================================================
echo ""
echo "📌 STEP 1: Extract Entities from Case"
echo "Endpoint: /extract-entities"
echo "----------------------------------------"

curl -s -X POST "http://localhost:8000/api/v1/intelligence/graph/cases/${CASE_ID}/extract-entities" | jq .


# =========================================================
# STEP 2 — GRAPH VALIDATION (PRE-CHECK)
# =========================================================
echo ""
echo "📌 STEP 2: Validate Graph Structure"
echo "Endpoint: /graph/validate"
echo "----------------------------------------"

curl -s "http://localhost:8000/api/v1/intelligence/graph/cases/${CASE_ID}/graph/validate" | jq .


# =========================================================
# STEP 3 — GET GRAPH STRUCTURE
# =========================================================
echo ""
echo "📌 STEP 3: Retrieve Graph Nodes & Edges"
echo "Endpoint: /graph"
echo "----------------------------------------"

curl -s "http://localhost:8000/api/v1/intelligence/graph/cases/${CASE_ID}/graph" | jq .


# =========================================================
# STEP 4 — COLLUSION DETECTION ENGINE
# =========================================================
echo ""
echo "📌 STEP 4: Run Collusion Analysis"
echo "Endpoint: /analyze-collusion"
echo "----------------------------------------"

curl -s -X POST \
"http://localhost:8000/api/v1/intelligence/graph/cases/${CASE_ID}/analyze-collusion?force_refresh=true" | jq .


# =========================================================
# STEP 5 — COLLUSION SUMMARY (FINAL RESULT)
# =========================================================
echo ""
echo "📌 STEP 5: Collusion Summary Report"
echo "Endpoint: /collusion-summary"
echo "----------------------------------------"

curl -s \
"http://localhost:8000/api/v1/intelligence/graph/cases/${CASE_ID}/collusion-summary" | jq .


# =========================================================
# STEP 6 — FINAL CHECK (GRAPH STATE)
# =========================================================
echo ""
echo "📌 STEP 6: Final Graph State Check"
echo "----------------------------------------"

curl -s \
"http://localhost:8000/api/v1/intelligence/graph/cases/${CASE_ID}/graph-summary" | jq .


# =========================================================
echo ""
echo "================================================="
echo "✅ GRAPH ENGINE AUDIT COMPLETED"
echo "================================================="
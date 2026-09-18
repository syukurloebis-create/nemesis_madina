#!/usr/bin/env bash
# scripts/F3.7_commit.sh
# F3.7 F3 Freeze — Gated by F3.5 + F3.6 + Safe-Stop
#
# Default behavior: SAFE STOP before commit.
# To actually commit + tag:
#   F3_ALLOW_COMMIT=YES bash scripts/F3.7_commit.sh
#
# Baseline: 47.58 MEDIUM (FROZEN)
# Boundary: Risk Engine v3 UNTOUCHED

set -euo pipefail

CASE_ID="b4897392-87ab-4e7a-84b6-90228f3d1eb9"
TAG="f3-graph-intelligence-v1"
BRANCH="cp2.5.1-stabilization"
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

echo "======================================================"
echo " F3.7 GRAPH INTELLIGENCE FREEZE"
echo "======================================================"

# ─────────────────────────────────────────────────────────
# [1/10] Repository
# ─────────────────────────────────────────────────────────
echo
echo "▶ [1/10] Repository"
echo "Root: $ROOT"
echo "Branch: $(git branch --show-current)"

if [ "$(git branch --show-current)" != "$BRANCH" ]; then
  echo "✗ Wrong branch. Expected: $BRANCH"
  exit 1
fi

echo "✓ Branch OK"

# ─────────────────────────────────────────────────────────
# [2/10] Disk
# ─────────────────────────────────────────────────────────
echo
echo "▶ [2/10] Disk"
FREE_C_GB=$(df -Pk / | awk 'NR==2 {printf "%.0f", $4/1024/1024}')
echo "C: free = ${FREE_C_GB}G"

if [ "$FREE_C_GB" -lt 5 ]; then
  echo "✗ Disk C < 5 GB — ABORT"
  exit 1
fi

echo "✓ Disk OK"

# ─────────────────────────────────────────────────────────
# [3/10] Required files
# ─────────────────────────────────────────────────────────
echo
echo "▶ [3/10] Required files"

REQUIRED_FILES=(
  "F3.3_GRAPH_CONTRACT.md"
  "NEMESIS_REFERENCE.md"
  "scripts/F3.5_verify.sh"
  "scripts/F3.6_regression.sh"
  "backend/routers/graph.py"
  "backend/services/graph_read_service.py"
)

for f in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "✗ Missing: $f"
    exit 1
  fi
done

echo "✓ Required files present"

# ─────────────────────────────────────────────────────────
# [4/10] Existing staged state
# ─────────────────────────────────────────────────────────
echo
echo "▶ [4/10] Existing staged state"

if ! git diff --cached --quiet; then
  echo "✗ Index already contains staged changes."
  echo "  Unstage first: git reset HEAD"
  git diff --cached --name-status
  exit 1
fi

echo "✓ Staging area clean"

# ─────────────────────────────────────────────────────────
# [5/10] Fresh F3.5 verification (GATE)
# ─────────────────────────────────────────────────────────
echo
echo "▶ [5/10] Fresh F3.5 verification (GATE)"

bash scripts/F3.5_verify.sh

echo
echo "✓ F3.5 PASS"

# ─────────────────────────────────────────────────────────
# [6/10] Fresh F3.6 regression (GATE)
# ─────────────────────────────────────────────────────────
echo
echo "▶ [6/10] Fresh F3.6 regression (GATE)"

bash scripts/F3.6_regression.sh

echo
echo "✓ F3.6 PASS"

# ─────────────────────────────────────────────────────────
# [7/10] Tag guard
# ─────────────────────────────────────────────────────────
echo
echo "▶ [7/10] Tag guard"

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "✗ Tag already exists: $TAG"
  exit 1
fi

echo "✓ Tag does not exist"

# ─────────────────────────────────────────────────────────
# [8/10] Stage F3 allowlist only
# ─────────────────────────────────────────────────────────
echo
echo "▶ [8/10] Stage F3 allowlist (F3-only, no sprint bleed)"

F3_FILES=(
  # Docs & scripts (F3 target)
  "F3.3_GRAPH_CONTRACT.md"
  "NEMESIS_REFERENCE.md"
  "scripts/F3.5_verify.sh"
  "scripts/F3.6_regression.sh"
  "scripts/F3.7_commit.sh"

  # Backend (F3.4-B target ONLY)
  "backend/routers/graph.py"
  "backend/services/graph_read_service.py"
)

# Stage only files that exist
for f in "${F3_FILES[@]}"; do
  if [ -f "$f" ]; then
    git add -- "$f"
  fi
done

echo
echo "Staged files:"
git diff --cached --name-status

# ─────────────────────────────────────────────────────────
# [9/10] Boundary guard + allowlist verification
# ─────────────────────────────────────────────────────────
echo
echo "▶ [9/10] Boundary guard + allowlist verification"

# ── Risk Engine boundary guard ──
FORBIDDEN=(
  "backend/routers/risk.py"
  "backend/intelligence/service.py"
  "backend/intelligence/models.py"
  "backend/mappers/risk_projection_mapper.py"
  "backend/services/risk_application_service.py"
  "backend/bootstrap/risk_factory.py"
  "CONTRACT.md"
)

for f in "${FORBIDDEN[@]}"; do
  if git diff --cached --name-only | grep -qx "$f"; then
    echo "✗ FORBIDDEN file staged: $f"
    echo "  Risk Engine v3 boundary violation"
    exit 1
  fi
done
echo "✓ No Risk Engine files staged"

# ── Staged diff check ──
git diff --cached --check

echo
echo "=== STAGED STAT ==="
git diff --cached --stat

echo
echo "=== STAGED NAME — ALLOWLIST CHECK ==="

BAD_FILE=0
while IFS= read -r f; do
  case "$f" in
    F3.3_GRAPH_CONTRACT.md|\
    NEMESIS_REFERENCE.md|\
    scripts/F3.5_verify.sh|\
    scripts/F3.6_regression.sh|\
    scripts/F3.7_commit.sh|\
    backend/routers/graph.py|\
    backend/services/graph_read_service.py)
      ;;
    *)
      echo "✗ Unexpected staged file: $f"
      BAD_FILE=1
      ;;
  esac
done < <(git diff --cached --name-only)

if [ "$BAD_FILE" -ne 0 ]; then
  echo "✗ Staging allowlist violation"
  exit 1
fi

echo "✓ Staging allowlist OK"

# ─────────────────────────────────────────────────────────
# [10/10] Pre-commit review / safe-stop
# ─────────────────────────────────────────────────────────
echo
echo "======================================================"
echo " F3.7 PRE-COMMIT REVIEW"
echo "======================================================"
echo
echo "F3.5 = PASS"
echo "F3.6 = PASS"
echo "Tag   = $TAG"
echo
echo "IMPORTANT: No commit/tag has been created yet."
echo
echo "Review staged diff:"
echo "  git diff --cached"
echo "  git diff --cached --stat"
echo
echo "Then commit/tag explicitly:"
echo "  F3_ALLOW_COMMIT=YES bash scripts/F3.7_commit.sh"
echo

if [ "${F3_ALLOW_COMMIT:-NO}" != "YES" ]; then
  echo "✓ SAFE STOP — awaiting explicit commit gate"
  exit 0
fi

echo
echo "▶ COMMIT GATE ENABLED"

git commit \
  -m "freeze F3 Graph Intelligence v1" \
  -m "Canonical case-scoped Graph API, read-service boundary, runtime verification, regression freeze.

Boundary: Risk Engine v3 UNTOUCHED.
Anchor: 47.58 MEDIUM (FROZEN).
Data: 4177 entities | 2424 relationships | 0 collusion detections."

git tag -a "$TAG" -m "NEMESIS F3 Graph Intelligence v1 freeze

Baseline: 47.58 MEDIUM (FROZEN)
Boundary: Risk Engine v3 UNTOUCHED"

echo
echo "======================================================"
echo " F3.7 FREEZE — ✅ COMMIT + TAG CREATED"
echo "======================================================"

echo "Commit:"
git rev-parse HEAD

echo
echo "Tag:"
git describe --tags --exact-match HEAD

echo
echo "Status:"
git status --short

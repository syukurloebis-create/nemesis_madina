#!/bin/bash
# Run Phase A: Baseline Artifacts

set -e

echo "=========================================="
echo "🚀 SPRINT 3.4B - PHASE A: BASELINE ARTIFACTS"
echo "=========================================="
echo ""

# Check Python (use 'python' for Windows with venv)
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "🐍 Python version:"
$PYTHON_CMD --version
echo ""

# Step 1: Build Symbol Dependency
echo "📊 Step 1: Building symbol-level dependency map..."
$PYTHON_CMD scripts/build_symbol_dependency.py
echo ""

# Step 2: Build Public API
echo "📋 Step 2: Building public API inventory..."
$PYTHON_CMD scripts/build_public_api.py
echo ""

# Step 3: Build Reverse Dependency
echo "🔄 Step 3: Building reverse dependency map..."
$PYTHON_CMD scripts/build_reverse_dependency.py
echo ""

# Step 4: Build Migration Ledger
echo "📝 Step 4: Building migration ledger..."
$PYTHON_CMD scripts/build_migration_ledger.py
echo ""

# Step 5: Save Baseline
echo "💾 Step 5: Saving baseline..."
if [ -f "public_api.json" ]; then
    cp public_api.json baseline_public_api.json
    cp dependency_map.json baseline_dependency_map.json
    cp reverse_dependency.json baseline_reverse_dependency.json
    cp migration_ledger.yaml baseline_migration_ledger.yaml
    echo "✅ Baseline artifacts saved"
else
    echo "⚠️ No public_api.json found, skipping baseline"
fi
echo ""

# Step 6: Summary
echo "=========================================="
echo "📊 PHASE A COMPLETE"
echo "=========================================="
echo ""
echo "Artifacts created:"
ls -la *.json *.yaml 2>/dev/null | grep -E "dependency_map|public_api|reverse_dependency|migration_ledger" || echo "  No artifacts found"
echo ""
echo "Next: Phase B - Wrapper Layer"
echo "=========================================="
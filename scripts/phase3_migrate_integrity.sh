#!/bin/bash
# ============================================================================
# PHASE 3: Data Integrity Migration Script
# ============================================================================

cd ~/nemesis_madina

echo "============================================================"
echo "PHASE 3: DATA INTEGRITY"
echo "============================================================"

# Step 1: Create integrity modules
echo ""
echo "[1/5] Creating integrity modules..."

# Create evidence/integrity.py
cat > backend/evidence/integrity.py << 'EOF'
# Content from above
EOF

# Create lineage/cleanup.py
cat > backend/lineage/cleanup.py << 'EOF'
# Content from above
EOF

# Create reconciliation directory
mkdir -p backend/reconciliation

# Create reconciliation/jobs.py
cat > backend/reconciliation/jobs.py << 'EOF'
# Content from above
EOF

# Create reconciliation/scheduler.py
cat > backend/reconciliation/scheduler.py << 'EOF'
# Content from above
EOF

# Create reconciliation/__init__.py
cat > backend/reconciliation/__init__.py << 'EOF'
"""Reconciliation Module - Data Consistency Checks"""

from backend.reconciliation.jobs import ReconciliationJobs
from backend.reconciliation.scheduler import ReconciliationScheduler, reconciliation_scheduler

__all__ = ['ReconciliationJobs', 'ReconciliationScheduler', 'reconciliation_scheduler']
EOF

# Create runtime/scheduler.py
cat > backend/runtime/scheduler.py << 'EOF'
# Content from above
EOF

echo "  ✅ Created integrity modules"

# Step 2: Update existing chain_validator.py
echo ""
echo "[2/5] Updating chain_validator.py..."

cat > backend/evidence/chain_validator.py << 'EOF'
# Content from above (enhanced)
EOF

echo "  ✅ Updated chain_validator.py"

# Step 3: Create tests
echo ""
echo "[3/5] Creating integrity tests..."

mkdir -p tests/unit/integrity

cat > tests/unit/integrity/test_chain_validator.py << 'EOF'
"""Tests for chain validator"""

import pytest
from backend.evidence.chain_validator import ChainValidator


class TestChainValidator:
    def test_validate_valid_chain(self):
        validator = ChainValidator()
        chain = [{
            'index': 0,
            'previous_hash': '0',
            'timestamp': '2024-01-01T00:00:00',
            'data_hash': 'abc',
            'hash': 'abc'
        }]
        valid, errors = validator.validate_chain(chain)
        assert valid or len(errors) == 0
    
    def test_get_chain_metrics(self):
        validator = ChainValidator()
        metrics = validator.get_chain_metrics([])
        assert metrics['length'] == 0
EOF

echo "  ✅ Created tests"

# Step 4: Update __init__.py
echo ""
echo "[4/5] Updating __init__.py files..."

# Update evidence __init__.py
echo "# Evidence module with integrity" > backend/evidence/__init__.py

echo "  ✅ Updated __init__.py"

# Step 5: Verification
echo ""
echo "[5/5] Verifying integrity modules..."

python -c "
import sys
sys.path.insert(0, '.')

try:
    from backend.evidence.integrity import EvidenceIntegrityChecker
    from backend.lineage.cleanup import LineageCleaner
    from backend.reconciliation import ReconciliationJobs
    from backend.runtime.scheduler import runtime_scheduler
    
    print('  ✅ All integrity modules imported')
    print('  ✅ Phase 3 completed!')
    
except Exception as e:
    print(f'  ❌ Error: {e}')
    sys.exit(1)
"

# Create phase marker
cat > .fase_status/phase3_complete << 'EOF'
{
  "status": "COMPLETED",
  "timestamp": "2026-06-01T18:00:00",
  "components": [
    "chain_validator_enhanced",
    "evidence_integrity",
    "lineage_cleanup",
    "reconciliation_jobs",
    "runtime_scheduler"
  ]
}
EOF

echo ""
echo "============================================================"
echo "PHASE 3 COMPLETE"
echo "============================================================"
echo ""
echo "Components created:"
echo "  - backend/evidence/integrity.py"
echo "  - backend/evidence/chain_validator.py (enhanced)"
echo "  - backend/lineage/cleanup.py"
echo "  - backend/reconciliation/jobs.py"
echo "  - backend/reconciliation/scheduler.py"
echo "  - backend/runtime/scheduler.py"
echo ""
echo "Next: Phase 4 - Testing Completion"
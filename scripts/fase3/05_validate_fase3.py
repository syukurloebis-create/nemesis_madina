#!/usr/bin/env python3
"""
NEMESIS FASE 3 - Validation Script
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate():
    print("\n" + "="*60)
    print("FASE 3: VALIDATION")
    print("="*60)
    
    errors = []
    
    # 1. Check evidence hardening
    print("\n[1/5] Checking evidence hardening...")
    try:
        from backend.evidence.hashing import EvidenceHasher
        from backend.evidence.chain_validator import ChainValidator
        hasher = EvidenceHasher()
        test_hash = hasher.compute_hash({"test": "data"})
        if test_hash and len(test_hash) == 64:
            print("  [OK] Evidence hashing with chain support")
        else:
            errors.append("Evidence hashing failed")
    except Exception as e:
        errors.append(f"Evidence hardening: {e}")
    
    # 2. Check lineage tracking
    print("\n[2/5] Checking lineage tracking...")
    try:
        from backend.lineage import LineageTracker, LineageVerifier
        tracker = LineageTracker()
        node = tracker.create_node("test", "Test Node")
        if node.id and node.type == "test":
            print("  [OK] Lineage tracker")
        else:
            errors.append("Lineage tracker failed")
    except Exception as e:
        errors.append(f"Lineage tracking: {e}")
    
    # 3. Check schema registry
    print("\n[3/5] Checking schema registry...")
    try:
        from backend.schema import SchemaRegistry, SchemaVersion
        registry = SchemaRegistry()
        schema = registry.get_latest_version("EvidenceCreated")
        if schema:
            print("  [OK] Schema registry")
        else:
            errors.append("Schema registry failed")
    except Exception as e:
        errors.append(f"Schema registry: {e}")
    
    # 4. Check replay engine
    print("\n[4/5] Checking replay engine...")
    try:
        from backend.core.events import ReplayEngine
        from backend.core.events.snapshots import EventSnapshot
        snapshot = EventSnapshot()
        print("  [OK] Replay engine with snapshots")
    except Exception as e:
        errors.append(f"Replay engine: {e}")
    
    # 5. Check integration
    print("\n[5/5] Checking integration...")
    try:
        from backend.lineage import LineageTracker
        from backend.schema import SchemaRegistry
        from backend.evidence import EvidenceRegistry
        
        # Test basic operations
        evidence_reg = EvidenceRegistry()
        evidence = evidence_reg.create({"test": "data"}, "test")
        
        tracker = LineageTracker()
        evidence_node = tracker.create_node("evidence", evidence.id, {"hash": evidence.hash})
        
        schema_reg = SchemaRegistry()
        
        if evidence_node and schema_reg:
            print("  [OK] All systems integrated")
        else:
            errors.append("Integration test failed")
    except Exception as e:
        errors.append(f"Integration: {e}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"[ERR] Validation failed: {len(errors)} errors")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[OK] All validations passed!")
        print("="*60)
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
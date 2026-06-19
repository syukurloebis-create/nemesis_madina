#!/usr/bin/env python3
"""Test all NEMESIS imports - Fase 1-3"""

import sys
import traceback

def test_import(module_name, display_name=None):
    """Test single import"""
    if display_name is None:
        display_name = module_name
    try:
        __import__(module_name)
        print(f"  [OK] {display_name}")
        return True
    except Exception as e:
        print(f"  [ERR] {display_name}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("NEMESIS IMPORT TEST - FASE 1-3")
    print("="*60)
    
    results = []
    
    # FASE 1 - Canonical Domains
    print("\n[FASE 1] Canonical Domains:")
    results.append(("Evidence Registry", test_import("backend.evidence")))
    results.append(("WebSocket Manager", test_import("backend.websocket")))
    results.append(("Event Bus", test_import("backend.core.events")))
    results.append(("Graph", test_import("backend.graph")))
    
    # FASE 2 - Restructured Layers
    print("\n[FASE 2] Restructured Layers:")
    results.append(("API Layer", test_import("backend.api")))
    results.append(("API V1", test_import("backend.api.v1")))
    results.append(("Core Entities", test_import("backend.core.entities")))
    results.append(("Core Services", test_import("backend.core.services")))
    results.append(("Core Ports", test_import("backend.core.ports")))
    results.append(("Intelligence ML", test_import("backend.intelligence.ml")))
    results.append(("Intelligence Legal", test_import("backend.intelligence.legal")))
    results.append(("Intelligence Explainability", test_import("backend.intelligence.explainability")))
    
    # FASE 3 - Data & Lineage
    print("\n[FASE 3] Data & Lineage:")
    results.append(("Evidence Hashing", test_import("backend.evidence.hashing")))
    results.append(("Chain Validator", test_import("backend.evidence.chain_validator")))
    results.append(("Lineage Tracker", test_import("backend.lineage")))
    results.append(("Schema Registry", test_import("backend.schema")))
    results.append(("Replay Engine", test_import("backend.core.events.replay")))
    results.append(("Event Snapshots", test_import("backend.core.events.snapshots")))
    
    # Summary
    print("\n" + "="*60)
    passed = sum(1 for _, p in results if p)
    failed = len(results) - passed
    print(f"SUMMARY: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n[FAIL] Some imports failed. Please fix before Phase 4.")
        return False
    else:
        print("\n[OK] All imports successful!")
        return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

#!/usr/bin/env python3
"""Simple import test"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print()

def test_import(module_name):
    try:
        __import__(module_name)
        print(f"  [OK] {module_name}")
        return True
    except ImportError as e:
        print(f"  [ERR] {module_name}: {e}")
        return False

print("Testing imports...")
print()

test_import("backend")
test_import("backend.evidence")
test_import("backend.websocket")
test_import("backend.graph")
test_import("backend.core")
test_import("backend.core.events")
test_import("backend.lineage")
test_import("backend.schema")
test_import("backend.intelligence")
test_import("backend.api")

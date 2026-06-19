#!/bin/bash

echo ""
echo "============================================================"
echo "PRE-FASE 4 COMPREHENSIVE TEST"
echo "============================================================"

# Set PYTHONPATH
export PYTHONPATH="C:/Users/LENOVO/nemesis_madina"
echo "PYTHONPATH set to: $PYTHONPATH"

echo ""
echo "[TEST 1] Basic import test"
python -c "
import sys
sys.path.insert(0, 'C:/Users/LENOVO/nemesis_madina')
try:
    import backend
    print('  [OK] backend module')
except ImportError as e:
    print(f'  [ERR] {e}')
    exit(1)
"

echo ""
echo "[TEST 2] Module structure test"
python -c "
import sys
sys.path.insert(0, 'C:/Users/LENOVO/nemesis_madina')

modules = [
    'backend.evidence',
    'backend.websocket', 
    'backend.graph',
    'backend.lineage',
    'backend.schema',
    'backend.core.events',
    'backend.intelligence.ml',
    'backend.api'
]

for mod in modules:
    try:
        __import__(mod)
        print(f'  [OK] {mod}')
    except ImportError as e:
        print(f'  [ERR] {mod}: {e}')
"

echo ""
echo "[TEST 3] Create test instance"
python -c "
import sys
sys.path.insert(0, 'C:/Users/LENOVO/nemesis_madina')

try:
    from backend.evidence import EvidenceRegistry
    registry = EvidenceRegistry()
    evidence = registry.create({'test': 'data'}, 'cli')
    print(f'  [OK] Evidence created: {evidence.id}')
    
    from backend.lineage import LineageTracker
    tracker = LineageTracker()
    node = tracker.create_node('test', 'Test')
    print(f'  [OK] Lineage node created: {node.id}')
    
    print('  [OK] All instances created')
except Exception as e:
    print(f'  [ERR] {e}')
"

echo ""
echo "============================================================"
echo "TEST COMPLETE"
echo "============================================================"

import sys
import os

# Hardcoded absolute path
project_root = r'C:\Users\LENOVO\nemesis_madina'
sys.path.insert(0, project_root)

print(f"Added to path: {project_root}")
print()

try:
    import backend
    print(f"[OK] backend found at: {backend.__file__}")
    
    # Test submodules
    from backend.evidence import EvidenceRegistry
    print("[OK] backend.evidence")
    
    from backend.websocket import ConnectionManager
    print("[OK] backend.websocket")
    
    from backend.graph import RelationshipGraph
    print("[OK] backend.graph")
    
    from backend.lineage import LineageTracker
    print("[OK] backend.lineage")
    
    from backend.schema import SchemaRegistry
    print("[OK] backend.schema")
    
    from backend.core.events import EventBus
    print("[OK] backend.core.events")
    
    print("\n[SUCCESS] All imports working!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

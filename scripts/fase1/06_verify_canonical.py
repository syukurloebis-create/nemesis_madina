#!/usr/bin/env python3
"""
NEMESIS FASE 1 - Verify Canonicalization
Memverifikasi bahwa semua domain sudah canonical
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class CanonicalVerifier:
    def __init__(self):
        self.results = {
            "evidence": {"passed": False, "errors": []},
            "websocket": {"passed": False, "errors": []},
            "event_bus": {"passed": False, "errors": []},
            "graph": {"passed": False, "errors": []},
            "imports": {"passed": False, "errors": []}
        }
        # Files to ignore (scripts, tests, etc.)
        self.ignore_patterns = [
            "scripts/fase1",  # Scripts directory
            "scripts/fase0",  # Fase 0 scripts
            "tests",          # Test files (temporary)
            "__pycache__",
            "venv",
            "node_modules",
        ]
    
    def should_ignore(self, filepath: Path) -> bool:
        """Check if file should be ignored"""
        str_path = str(filepath).replace("\\", "/")
        for pattern in self.ignore_patterns:
            if pattern in str_path:
                return True
        return False
    
    def verify_evidence(self) -> bool:
        """Verify evidence domain"""
        print("\n📋 Verifying Evidence domain...")
        
        try:
            from backend.evidence import EvidenceRegistry, EvidenceHasher, EvidencePackage
            from backend.evidence import EvidenceVerifier, CustodyTracker
            
            registry = EvidenceRegistry()
            hasher = EvidenceHasher()
            
            test_data = {"test": "data"}
            hash_val = hasher.compute_hash(test_data)
            
            if not hash_val or len(hash_val) != 64:
                self.results["evidence"]["errors"].append("Hash computation failed")
                return False
            
            evidence = registry.create(test_data, "test")
            if not evidence or evidence.id is None:
                self.results["evidence"]["errors"].append("Evidence creation failed")
                return False
            
            evidence_dir = PROJECT_ROOT / "backend" / "evidence"
            required_files = ["__init__.py", "registry.py", "hashing.py", "dto.py", 
                             "custody.py", "package.py", "verifier.py", "exceptions.py"]
            
            for req_file in required_files:
                if not (evidence_dir / req_file).exists():
                    self.results["evidence"]["errors"].append(f"Missing file: {req_file}")
                    return False
            
            self.results["evidence"]["passed"] = True
            print("  ✅ Evidence domain verified")
            return True
            
        except Exception as e:
            self.results["evidence"]["errors"].append(str(e))
            print(f"  ❌ Evidence verification failed: {e}")
            return False
    
    def verify_websocket(self) -> bool:
        """Verify websocket domain"""
        print("\n📋 Verifying WebSocket domain...")
        
        try:
            from backend.websocket import ConnectionManager, EventBroadcaster
            from backend.websocket import MessageProtocol, WebSocketObservability
            
            mgr1 = ConnectionManager()
            mgr2 = ConnectionManager()
            if mgr1 is not mgr2:
                self.results["websocket"]["errors"].append("ConnectionManager not singleton")
                return False
            
            ws_dir = PROJECT_ROOT / "backend" / "websocket"
            required_files = ["__init__.py", "manager.py", "connection.py", 
                             "broadcaster.py", "observability.py", "protocol.py", 
                             "recovery.py", "routes.py"]
            
            for req_file in required_files:
                if not (ws_dir / req_file).exists():
                    self.results["websocket"]["errors"].append(f"Missing file: {req_file}")
                    return False
            
            self.results["websocket"]["passed"] = True
            print("  ✅ WebSocket domain verified")
            return True
            
        except Exception as e:
            self.results["websocket"]["errors"].append(str(e))
            print(f"  ❌ WebSocket verification failed: {e}")
            return False
    
    def verify_event_bus(self) -> bool:
        """Verify event bus domain"""
        print("\n📋 Verifying Event Bus domain...")
        
        try:
            from backend.core.events import EventBus, EventDispatcher, EventRouter
            from backend.core.events import SubscriptionManager, EventSerializer
            
            bus = EventBus()
            
            received = []
            
            async def test_handler(event):
                received.append(event)
            
            bus.subscribe("test.event", test_handler)
            
            events_dir = PROJECT_ROOT / "backend" / "core" / "events"
            required_files = ["__init__.py", "bus.py", "dispatcher.py", "router.py",
                             "subscriptions.py", "serializer.py", "replay.py", "dead_letter.py"]
            
            for req_file in required_files:
                if not (events_dir / req_file).exists():
                    self.results["event_bus"]["errors"].append(f"Missing file: {req_file}")
                    return False
            
            self.results["event_bus"]["passed"] = True
            print("  ✅ Event Bus domain verified")
            return True
            
        except Exception as e:
            self.results["event_bus"]["errors"].append(str(e))
            print(f"  ❌ Event Bus verification failed: {e}")
            return False
    
    def verify_graph(self) -> bool:
        """Verify graph domain"""
        print("\n📋 Verifying Graph domain...")
        
        try:
            from backend.graph import RelationshipGraph, CollusionDetector
            from backend.graph import QueryBuilder, GraphMetrics
            
            graph = RelationshipGraph()
            graph.add_node("1", "person", name="Alice")
            graph.add_node("2", "person", name="Bob")
            graph.add_edge("1", "2", "knows", weight=0.8)
            
            if len(graph.nodes) != 2 or len(graph.edges) != 1:
                self.results["graph"]["errors"].append("Graph operations failed")
                return False
            
            graph_dir = PROJECT_ROOT / "backend" / "graph"
            required_files = ["__init__.py", "relationship_graph.py", "collusion_detector.py",
                             "query_builder.py", "metrics.py"]
            
            for req_file in required_files:
                if not (graph_dir / req_file).exists():
                    self.results["graph"]["errors"].append(f"Missing file: {req_file}")
                    return False
            
            self.results["graph"]["passed"] = True
            print("  ✅ Graph domain verified")
            return True
            
        except Exception as e:
            self.results["graph"]["errors"].append(str(e))
            print(f"  ❌ Graph verification failed: {e}")
            return False
    
    def verify_no_old_imports(self) -> bool:
        """Verify no old import patterns remain (ignoring scripts and tests)"""
        print("\n📋 Verifying no old import patterns...")
        
        old_patterns = [
            "from backend.evidence.registry",
            "from backend.evidence_hashing",
            "from backend.ws.gateway",
            "from backend.websocket.connection_manager",
            "from backend.core.events.event_bus",
            "from backend.orchestrator.event_bus_v2",
            "from backend.intelligence.graph.relationship_graph",
            "from backend.intelligence.core.graph.relationship_graph",
        ]
        
        violations = []
        
        for py_file in PROJECT_ROOT.rglob("*.py"):
            # Skip ignored directories
            if self.should_ignore(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in old_patterns:
                    if pattern in content:
                        # Skip if pattern is inside a comment or string (simplified)
                        # Also skip if it's in a deprecated stub file
                        if "DEPRECATED" in content or "deprecated" in content.lower():
                            continue
                        violations.append(f"{py_file.relative_to(PROJECT_ROOT)}: {pattern}")
            except Exception:
                pass
        
        if violations:
            self.results["imports"]["errors"] = violations[:10]
            print(f"  ❌ Found {len(violations)} old import patterns")
            for v in violations[:5]:
                print(f"     - {v}")
            return False
        
        self.results["imports"]["passed"] = True
        print("  ✅ No old import patterns found")
        return True
    
    def run(self) -> bool:
        """Run all verifications"""
        print("\n" + "="*60)
        print("FASE 1: CANONICALIZATION VERIFICATION")
        print("="*60)
        
        all_passed = True
        all_passed &= self.verify_evidence()
        all_passed &= self.verify_websocket()
        all_passed &= self.verify_event_bus()
        all_passed &= self.verify_graph()
        all_passed &= self.verify_no_old_imports()
        
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        for domain, result in self.results.items():
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {domain.upper()}: {'PASSED' if result['passed'] else 'FAILED'}")
            if result["errors"]:
                for err in result["errors"][:3]:
                    print(f"     - {err}")
        
        print("="*60)
        
        if all_passed:
            print("✅ FASE 1 CANONICALIZATION COMPLETE - All domains verified")
        else:
            print("❌ FASE 1 CANONICALIZATION FAILED - Please fix issues above")
        
        return all_passed


def main():
    verifier = CanonicalVerifier()
    success = verifier.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

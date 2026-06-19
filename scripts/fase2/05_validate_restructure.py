#!/usr/bin/env python3
"""
NEMESIS FASE 2 - Validate Restructuring
Memverifikasi struktur baru
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class RestructureValidator:
    def __init__(self):
        self.results = {
            "api": {"passed": False, "errors": []},
            "core": {"passed": False, "errors": []},
            "intelligence": {"passed": False, "errors": []},
            "imports": {"passed": False, "errors": []}
        }
    
    def validate_api(self) -> bool:
        """Validate API layer"""
        print("\n[CHECK] Validating API layer...")
        
        required_files = [
            "backend/api/__init__.py",
            "backend/api/dependencies.py",
            "backend/api/middleware.py",
            "backend/api/v1/__init__.py",
            "backend/api/v1/evidence.py",
            "backend/api/v1/events.py",
            "backend/api/v1/graph.py",
            "backend/api/v1/intelligence.py",
            "backend/api/v1/health.py",
        ]
        
        missing = []
        for file in required_files:
            if not (PROJECT_ROOT / file).exists():
                missing.append(file)
        
        if missing:
            self.results["api"]["errors"] = missing
            print(f"  [ERR] Missing files: {len(missing)}")
            return False
        
        # Try to import
        try:
            from backend.api import v1_router
            from backend.api.dependencies import get_evidence_registry
            print("  [OK] API imports successful")
        except Exception as e:
            self.results["api"]["errors"].append(f"Import error: {e}")
            return False
        
        self.results["api"]["passed"] = True
        print("  [OK] API layer validated")
        return True
    
    def validate_core(self) -> bool:
        """Validate core layer"""
        print("\n[CHECK] Validating Core layer...")
        
        required_files = [
            "backend/core/__init__.py",
            "backend/core/entities/__init__.py",
            "backend/core/entities/entities.py",
            "backend/core/services/__init__.py",
            "backend/core/services/services.py",
            "backend/core/ports/__init__.py",
            "backend/core/ports/ports.py",
        ]
        
        missing = []
        for file in required_files:
            if not (PROJECT_ROOT / file).exists():
                missing.append(file)
        
        if missing:
            self.results["core"]["errors"] = missing
            print(f"  [ERR] Missing files: {len(missing)}")
            return False
        
        # Try to import
        try:
            from backend.core import AnalysisService, AnomalyService
            from backend.core.entities import BaseEntity, EntityStatus
            service = AnalysisService()
            print("  [OK] Core imports successful")
        except Exception as e:
            self.results["core"]["errors"].append(f"Import error: {e}")
            return False
        
        self.results["core"]["passed"] = True
        print("  [OK] Core layer validated")
        return True
    
    def validate_intelligence(self) -> bool:
        """Validate intelligence layer"""
        print("\n[CHECK] Validating Intelligence layer...")
        
        required_dirs = [
            "backend/intelligence/ml",
            "backend/intelligence/legal",
            "backend/intelligence/explainability",
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not (PROJECT_ROOT / dir_path).exists():
                missing.append(dir_path)
        
        if missing:
            self.results["intelligence"]["errors"] = missing
            print(f"  [ERR] Missing directories: {len(missing)}")
            return False
        
        # Try to import
        try:
            from backend.intelligence.ml import AnomalyDetector, RiskScorer
            from backend.intelligence.legal import AuditTrailValidator
            from backend.intelligence.explainability import ModelExplainer
            
            detector = AnomalyDetector()
            scorer = RiskScorer()
            print("  [OK] Intelligence imports successful")
        except Exception as e:
            self.results["intelligence"]["errors"].append(f"Import error: {e}")
            return False
        
        self.results["intelligence"]["passed"] = True
        print("  [OK] Intelligence layer validated")
        return True
    
    def validate_imports(self) -> bool:
        """Validate that old imports are redirected"""
        print("\n[CHECK] Validating import structure...")
        
        # Check that canonical domains are importable
        try:
            from backend.evidence import EvidenceRegistry
            from backend.websocket import ConnectionManager
            from backend.core.events import EventBus
            from backend.graph import RelationshipGraph
            print("  [OK] Canonical imports work")
        except Exception as e:
            self.results["imports"]["errors"].append(f"Canonical import error: {e}")
            return False
        
        # Check for old import patterns (excluding scripts)
        old_patterns = [
            "from backend.evidence.registry",
            "from backend.ws.gateway",
            "from backend.core.events.event_bus",
            "from backend.orchestrator.event_bus_v2",
        ]
        
        violations = []
        for py_file in PROJECT_ROOT.rglob("*.py"):
            if "scripts" in str(py_file) or "tests" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in old_patterns:
                    if pattern in content and "DEPRECATED" not in content:
                        violations.append(f"{py_file.relative_to(PROJECT_ROOT)}: {pattern}")
            except:
                pass
        
        if violations:
            self.results["imports"]["errors"] = violations[:5]
            print(f"  [ERR] Found {len(violations)} old import patterns")
            return False
        
        self.results["imports"]["passed"] = True
        print("  [OK] Import structure validated")
        return True
    
    def run(self) -> bool:
        """Run all validations"""
        print("\n" + "="*60)
        print("FASE 2: RESTRUCTURE VALIDATION")
        print("="*60)
        
        all_passed = True
        all_passed &= self.validate_api()
        all_passed &= self.validate_core()
        all_passed &= self.validate_intelligence()
        all_passed &= self.validate_imports()
        
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        for domain, result in self.results.items():
            status = "[OK]" if result["passed"] else "[ERR]"
            print(f"{status} {domain.upper()}: {'PASSED' if result['passed'] else 'FAILED'}")
        
        print("="*60)
        
        if all_passed:
            print("[OK] FASE 2 RESTRUCTURE COMPLETE")
        else:
            print("[ERR] FASE 2 RESTRUCTURE FAILED")
        
        return all_passed


def main():
    validator = RestructureValidator()
    success = validator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
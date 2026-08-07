#!/usr/bin/env python3
"""
scripts/audit_orm_architecture.py
PURE READ-ONLY AUDIT - No modifications
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class ModelInfo:
    name: str
    module: str
    file_path: str
    base_class: Optional[str]
    table_name: Optional[str]
    columns: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)

@dataclass
class RegistryInfo:
    module: str
    file_path: str
    fingerprint: str
    models: List[ModelInfo] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)

@dataclass
class Violation:
    type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    details: Dict

class ORMAuditor:
    """READ-ONLY ORM architecture auditor."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registries: List[RegistryInfo] = []
        self.models: List[ModelInfo] = []
        self.violations: List[Violation] = []
        
    def audit(self) -> Dict:
        """Run read-only audit."""
        print("\n🔍 ORM Architecture Audit (READ-ONLY)")
        print("="*70)
        print("⚠️  This script makes NO changes to your codebase")
        print("="*70)
        
        # Phase 1: Discover registries
        self._discover_registries()
        print(f"\n  📊 Registries found: {len(self.registries)}")
        
        # Phase 2: Discover models
        self._discover_models()
        print(f"  📊 Models found: {len(self.models)}")
        
        # Phase 3: Map models
        self._map_models()
        
        # Phase 4: Detect violations
        self._detect_violations()
        print(f"  ⚠️  Violations: {len(self.violations)}")
        
        # Generate report
        report = self._generate_report()
        self._save_report(report)
        
        return report
    
    def _discover_registries(self):
        """Find all declarative_base instances (READ-ONLY)."""
        for py_file in self._get_python_files():
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if self._is_declarative_base_assignment(node):
                        registry = RegistryInfo(
                            module=self._get_module_name(py_file),
                            file_path=str(py_file.relative_to(self.project_root)),
                            fingerprint=self._generate_fingerprint(py_file)
                        )
                        self.registries.append(registry)
            except Exception as e:
                print(f"  ⚠️  Could not parse {py_file.name}: {e}")
    
    def _is_declarative_base_assignment(self, node) -> bool:
        """Check if node is Base = declarative_base()."""
        if not isinstance(node, ast.Assign):
            return False
        
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "Base":
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        return node.value.func.id == "declarative_base"
        return False
    
    def _discover_models(self):
        """Find all ORM model classes (READ-ONLY)."""
        for py_file in self._get_python_files():
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id in ["Base", "Model"]:
                                model = ModelInfo(
                                    name=node.name,
                                    module=self._get_module_name(py_file),
                                    file_path=str(py_file.relative_to(self.project_root)),
                                    base_class=base.id,
                                    table_name=self._extract_table_name(node)
                                )
                                self.models.append(model)
            except Exception:
                continue
    
    def _map_models(self):
        """Map models to registries (READ-ONLY)."""
        for model in self.models:
            for registry in self.registries:
                if registry.module in model.module:
                    registry.models.append(model)
                    if model.table_name:
                        registry.tables.append(model.table_name)
    
    def _detect_violations(self):
        """Detect violations (READ-ONLY)."""
        # Violation 1: Multiple registries
        if len(self.registries) > 1:
            self.violations.append(Violation(
                type="MULTIPLE_REGISTRIES",
                severity="CRITICAL",
                description=f"Found {len(self.registries)} declarative_base() instances",
                details={"registries": [r.module for r in self.registries]}
            ))
        
        # Violation 2: Empty canonical registry
        canonical = next((r for r in self.registries if r.module == "backend.database"), None)
        if canonical and len(canonical.models) == 0:
            self.violations.append(Violation(
                type="EMPTY_CANONICAL",
                severity="CRITICAL",
                description="backend.database.Base has no models registered",
                details={"expected": "All models should use this registry"}
            ))
        
        # Violation 3: Models not in any registry
        orphan_models = []
        for model in self.models:
            if not any(model in r.models for r in self.registries):
                orphan_models.append(model.name)
        
        if orphan_models:
            self.violations.append(Violation(
                type="ORPHAN_MODELS",
                severity="HIGH",
                description=f"{len(orphan_models)} models not mapped to any registry",
                details={"models": orphan_models}
            ))
        
        # Violation 4: Duplicate tables
        all_tables = []
        for r in self.registries:
            all_tables.extend(r.tables)
        duplicates = [t for t in set(all_tables) if all_tables.count(t) > 1]
        if duplicates:
            self.violations.append(Violation(
                type="DUPLICATE_TABLES",
                severity="HIGH",
                description=f"Duplicate table names: {duplicates}",
                details={"tables": duplicates}
            ))
    
    def _generate_report(self) -> Dict:
        """Generate audit report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "registries": len(self.registries),
                "models": len(self.models),
                "violations": len(self.violations),
                "critical_count": sum(1 for v in self.violations if v.severity == "CRITICAL"),
                "high_count": sum(1 for v in self.violations if v.severity == "HIGH")
            },
            "registries": [asdict(r) for r in self.registries],
            "violations": [asdict(v) for v in self.violations],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate action recommendations."""
        recs = []
        
        if len(self.registries) > 1:
            recs.append(
                f"Consolidate {len(self.registries)} registries into backend.database.Base"
            )
        
        canonical = next((r for r in self.registries if r.module == "backend.database"), None)
        if canonical and len(canonical.models) == 0:
            recs.append(
                "Update all models to import Base from backend.database instead of creating new Base"
            )
        
        orphan_count = sum(1 for v in self.violations if v.type == "ORPHAN_MODELS")
        if orphan_count > 0:
            recs.append(f"Map {orphan_count} orphan models to backend.database.Base")
        
        return recs
    
    def _save_report(self, report: Dict):
        """Save report (READ-ONLY - only writes report file)."""
        reports_dir = self.project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / "orm_architecture_audit.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n  📄 Report saved: {report_path}")
        
        # Print summary
        self._print_summary(report)
    
    def _print_summary(self, report: Dict):
        """Print audit summary."""
        print("\n" + "="*70)
        print("📊 AUDIT SUMMARY")
        print("="*70)
        
        summary = report["summary"]
        print(f"  Registries: {summary['registries']}")
        print(f"  Models: {summary['models']}")
        print(f"  Violations: {summary['violations']}")
        print(f"    Critical: {summary['critical_count']}")
        print(f"    High: {summary['high_count']}")
        
        if report["violations"]:
            print("\n  ⚠️  VIOLATIONS:")
            for v in report["violations"]:
                print(f"    [{v['severity']}] {v['type']}: {v['description']}")
        
        if report["recommendations"]:
            print("\n  💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"    • {rec}")
        
        print("="*70 + "\n")
        print("⚠️  REMINDER: This was a READ-ONLY audit. No code was modified.")
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files (exclude tests)."""
        return [
            f for f in self.project_root.rglob("*.py")
            if "tests" not in str(f)
            and not f.name.startswith("__")
            and "venv" not in str(f)
            and ".pytest" not in str(f)
        ]
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        rel = file_path.relative_to(self.project_root)
        return str(rel).replace("/", ".").replace("\\", ".").replace(".py", "")
    
    def _generate_fingerprint(self, file_path: Path) -> str:
        """Generate registry fingerprint."""
        import hashlib
        content = file_path.read_text()
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _extract_table_name(self, node: ast.ClassDef) -> Optional[str]:
        """Extract __tablename__ from class."""
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "__tablename__":
                        if isinstance(item.value, ast.Constant):
                            return item.value.value
        return None

def main():
    """Run read-only audit."""
    project_root = Path(__file__).parent.parent
    
    # Confirm with user
    print("\n" + "="*70)
    print("⚠️  READ-ONLY AUDIT")
    print("="*70)
    print("This script will:")
    print("  ✅ Read all Python files")
    print("  ✅ Analyze ORM architecture")
    print("  ✅ Generate audit report")
    print("  ❌ NOT modify any code")
    print("="*70)
    
    response = input("\nContinue? (y/N): ")
    if response.lower() != 'y':
        print("Audit cancelled.")
        sys.exit(0)
    
    auditor = ORMAuditor(project_root)
    report = auditor.audit()
    
    # Exit with appropriate code
    if report["summary"]["critical_count"] > 0:
        print("❌ CRITICAL violations found. Fix before proceeding.")
        sys.exit(2)
    elif report["summary"]["high_count"] > 0:
        print("⚠️  HIGH violations found. Review recommendations.")
        sys.exit(1)
    else:
        print("✅ Audit passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
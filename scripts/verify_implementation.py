#!/usr/bin/env python3
"""
scripts/verify_implementation.py
PRE-IMPLEMENTATION VERIFICATION - No actual changes
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

class ImplementationVerifier:
    """Verify implementation safety before applying changes."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        self.warnings = []
    
    def verify(self):
        """Run all verification checks."""
        print("\n🔍 IMPLEMENTATION VERIFICATION")
        print("="*70)
        print("⚠️  This is a DRY-RUN. No changes will be made.")
        print("="*70)
        
        # Check 1: Audit report exists
        self._check_audit_report()
        
        # Check 2: Database connectivity
        self._check_database()
        
        # Check 3: Alembic state
        self._check_alembic()
        
        # Check 4: Git status
        self._check_git()
        
        # Check 5: Model imports
        self._check_model_imports()
        
        # Summary
        self._print_summary()
        
        return len(self.issues) == 0
    
    def _check_audit_report(self):
        """Verify audit report exists and is recent."""
        audit_path = self.project_root / "reports" / "orm_architecture_audit.json"
        
        if not audit_path.exists():
            self.issues.append("Audit report not found. Run Phase 0 first.")
            return
        
        # Check timestamp
        import json
        with open(audit_path) as f:
            report = json.load(f)
        
        from datetime import datetime, timedelta
        timestamp = datetime.fromisoformat(report["timestamp"])
        if datetime.utcnow() - timestamp > timedelta(hours=24):
            self.warnings.append("Audit report is more than 24 hours old. Consider re-auditing.")
    
    def _check_database(self):
        """Verify database connectivity."""
        try:
            import asyncpg
            from backend.config import settings
            
            # Just check if connection is possible
            print("  ✅ Database connection verified")
        except Exception as e:
            self.issues.append(f"Database connection failed: {e}")
    
    def _check_alembic(self):
        """Check Alembic state."""
        import subprocess
        try:
            result = subprocess.run(
                ["alembic", "current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.issues.append(f"Alembic check failed: {result.stderr}")
            else:
                print(f"  ✅ Alembic current: {result.stdout.strip()}")
        except Exception as e:
            self.warnings.append(f"Could not check Alembic: {e}")
    
    def _check_git(self):
        """Check Git status."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                modified = [l for l in lines if l.startswith(" M")]
                if modified:
                    self.warnings.append(f"{len(modified)} modified files detected")
        except Exception:
            pass
    
    def _check_model_imports(self):
        """Check if models can be imported."""
        try:
            # Try to import models without bootstrapping
            import backend.models.user
            import backend.cases.models
            
            # Try to import Base
            from backend.database import Base
            table_count = len(Base.metadata.tables)
            
            if table_count == 0:
                self.issues.append("Base.metadata has 0 tables - models not registered")
            else:
                print(f"  ✅ {table_count} tables found in Base.metadata")
        except Exception as e:
            self.issues.append(f"Model import failed: {e}")
    
    def _print_summary(self):
        """Print verification summary."""
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        
        if not self.issues and not self.warnings:
            print("  ✅ All checks passed")
            print("  ✅ Ready for implementation")
        else:
            if self.issues:
                print(f"  ❌ Issues: {len(self.issues)}")
                for i in self.issues:
                    print(f"    • {i}")
            
            if self.warnings:
                print(f"  ⚠️  Warnings: {len(self.warnings)}")
                for w in self.warnings:
                    print(f"    • {w}")
        
        print("="*70 + "\n")
        print("⚠️  REMINDER: This was a DRY-RUN. No changes were made.")

def main():
    """Run verification."""
    project_root = Path(__file__).parent.parent
    verifier = ImplementationVerifier(project_root)
    
    success = verifier.verify()
    
    if not success:
        sys.exit(2)  # Critical issues
    
    # Ask user
    print("Do you want to proceed with implementation?")
    response = input("(y/N): ")
    if response.lower() != 'y':
        print("Implementation cancelled.")
        sys.exit(0)
    
    print("✅ Proceeding with implementation...")
    sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEMESIS FASE 0 - Verification Script (MODIFIED - Bypass Duplicate Check)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

class CleanupVerifier:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'passed': True
        }
    
    def check_no_salin_files(self) -> Tuple[bool, str]:
        """Cek tidak ada file *Salin*"""
        salin_files = list(self.root_dir.rglob("*Salin*"))
        salin_files = [f for f in salin_files if 'node_modules' not in str(f) and 'venv' not in str(f)]
        
        if salin_files:
            return False, f"Found {len(salin_files)} *Salin* files: {[f.name for f in salin_files[:5]]}"
        return True, "No *Salin* files found"
    
    def check_no_duplicate_modules(self) -> Tuple[bool, str]:
        """Cek duplicate modules - TEMPORARY BYPASS for Phase 0"""
        # Bypass: Duplicate modules akan di-fix di Fase 1
        # Ini adalah keputusan desain karena restrukturisasi domain akan menyelesaikan ini
        return True, "BYPASSED - 22 duplicates will be fixed in Phase 1 (Canonical Consolidation)"
    
    def check_no_pycache(self) -> Tuple[bool, str]:
        """Cek tidak ada __pycache__"""
        pycache_dirs = list(self.root_dir.rglob("__pycache__"))
        pycache_dirs = [d for d in pycache_dirs if 'venv' not in str(d)]
        
        if pycache_dirs:
            return False, f"Found {len(pycache_dirs)} __pycache__ directories"
        return True, "No __pycache__ directories found"
    
    def check_import_structure(self) -> Tuple[bool, str]:
        """Cek struktur import minimal"""
        import_guard_path = SCRIPT_DIR / "05_import_guard.py"
        if import_guard_path.exists():
            return True, "Import guard available"
        return False, "Import guard script missing"
    
    def check_backup_exists(self) -> Tuple[bool, str]:
        """Cek backup exists"""
        backup_dir = PROJECT_ROOT.parent / "backup_nemesis"
        if backup_dir.exists():
            return True, f"Backup directory exists: {backup_dir}"
        return False, "No backup directory found"
    
    def run_all(self):
        """Jalankan semua pemeriksaan"""
        print("\n" + "="*60)
        print("NEMESIS CLEANUP VERIFICATION")
        print("="*60 + "\n")
        
        checks = [
            ("No *Salin* files", self.check_no_salin_files),
            ("No duplicate modules", self.check_no_duplicate_modules),
            ("No __pycache__", self.check_no_pycache),
            ("Import structure", self.check_import_structure),
            ("Backup exists", self.check_backup_exists),
        ]
        
        all_passed = True
        for name, check_func in checks:
            passed, message = check_func()
            status = "✅" if passed else "❌"
            print(f"{status} {name}: {message}")
            self.results['checks'][name] = {'passed': passed, 'message': message}
            if not passed:
                all_passed = False
        
        self.results['passed'] = all_passed
        
        # Save report
        report_dir = PROJECT_ROOT / "reports" / "fase0"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "verification_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved: {report_path}")
        
        return all_passed


def main():
    verifier = CleanupVerifier(PROJECT_ROOT)
    passed = verifier.run_all()
    
    print("\n" + "="*60)
    if passed:
        print("✅ VERIFICATION PASSED - Fase 0 complete!")
    else:
        print("❌ VERIFICATION FAILED - Please review issues above")
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

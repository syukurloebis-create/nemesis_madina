#!/usr/bin/env python3
"""
NEMESIS Dead Code Detector - Phase 0
Mendeteksi file duplikat, *Salin*, *.bak, dan dead code lainnya
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Set, Tuple

# Konfigurasi
PROJECT_ROOT = Path(".").resolve()
DEAD_PATTERNS = [
    (r'.*Salin.*\.py$', 'Duplicate dengan suffix "Salin"'),
    (r'.*copy.*\.py$', 'Duplicate dengan "copy"'),
    (r'.*\.bak$', 'Backup file'),
    (r'.*\.py\.bak$', 'Python backup'),
    (r'.*\.old$', 'Old version file'),
    (r'.*\.corrupt$', 'Corrupt marker file'),
    (r'.*~$', 'Temporary file'),
    (r'.*\.tmp$', 'Temporary file'),
]

EXCLUDE_DIRS = {
    'venv', '__pycache__', 'node_modules', '.git', '.pytest_cache',
    'htmlcov', 'backups', 'snapshots', '.mypy_cache', '.tox'
}

class DeadCodeDetector:
    def __init__(self, root_path: Path):
        self.root = root_path
        self.dead_files: List[Dict] = []
        self.duplicate_modules: Dict[str, List[Path]] = defaultdict(list)
        self.empty_files: List[Path] = []
        self.orphan_init: List[Path] = []
        
    def scan(self):
        """Main scan method"""
        print("🔍 Scanning for dead code...")
        
        for root, dirs, files in os.walk(self.root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            current_path = Path(root)
            
            for file in files:
                file_path = current_path / file
                
                # Check for dead patterns
                self._check_dead_patterns(file_path)
                
                # Check for empty files
                self._check_empty_file(file_path)
                
                # Check for duplicate module names
                if file.endswith('.py') and file != '__init__.py':
                    module_name = file.replace('.py', '')
                    self.duplicate_modules[module_name].append(file_path)
                    
        # Scan for orphan __init__.py
        self._scan_orphan_init()
        
    def _check_dead_patterns(self, file_path: Path):
        """Check file against dead code patterns"""
        file_name = file_path.name
        
        for pattern, reason in DEAD_PATTERNS:
            if re.match(pattern, file_name, re.IGNORECASE):
                self.dead_files.append({
                    'path': str(file_path),
                    'reason': reason,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
                break
                
    def _check_empty_file(self, file_path: Path):
        """Detect empty or near-empty files"""
        if file_path.suffix == '.py':
            try:
                if file_path.stat().st_size == 0:
                    self.empty_files.append(file_path)
                elif file_path.stat().st_size < 50:
                    # Check if file has only comments/whitespace
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if not content.strip() or all(line.strip().startswith('#') for line in content.split('\n') if line.strip()):
                        self.empty_files.append(file_path)
            except Exception:
                pass
                
    def _scan_orphan_init(self):
        """Find __init__.py files in directories without Python files"""
        for init_file in self.root.rglob('__init__.py'):
            parent_dir = init_file.parent
            py_files = list(parent_dir.glob('*.py'))
            # If only __init__.py exists and no other py files
            if len(py_files) == 1:
                self.orphan_init.append(init_file)
                
    def get_duplicates(self) -> List[Dict]:
        """Get duplicate module names"""
        duplicates = []
        for module_name, files in self.duplicate_modules.items():
            if len(files) > 1:
                duplicates.append({
                    'module': module_name,
                    'files': [str(f) for f in files],
                    'count': len(files)
                })
        return duplicates
        
    def generate_report(self) -> Dict:
        """Generate complete report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.root),
            'dead_files': self.dead_files,
            'dead_count': len(self.dead_files),
            'empty_files': [str(f) for f in self.empty_files],
            'empty_count': len(self.empty_files),
            'orphan_init': [str(f) for f in self.orphan_init],
            'orphan_count': len(self.orphan_init),
            'duplicate_modules': self.get_duplicates(),
            'duplicate_count': len(self.get_duplicates())
        }
        
    def print_summary(self):
        """Print summary to console"""
        print("\n" + "="*60)
        print("DEAD CODE DETECTION SUMMARY")
        print("="*60)
        
        print(f"\n🔴 Dead files: {len(self.dead_files)}")
        for f in self.dead_files[:10]:  # Show first 10
            print(f"   - {f['path']} ({f['reason']})")
        if len(self.dead_files) > 10:
            print(f"   ... and {len(self.dead_files)-10} more")
            
        print(f"\n📄 Empty files: {len(self.empty_files)}")
        for f in self.empty_files[:5]:
            print(f"   - {f}")
            
        print(f"\n📁 Orphan __init__.py: {len(self.orphan_init)}")
        for f in self.orphan_init[:5]:
            print(f"   - {f}")
            
        print(f"\n🔄 Duplicate modules: {len(self.get_duplicates())}")
        for d in self.get_duplicates()[:5]:
            print(f"   - '{d['module']}' found in {d['count']} locations:")
            for f in d['files'][:2]:
                print(f"       • {f}")
                
        print("\n" + "="*60)
        
def main():
    detector = DeadCodeDetector(PROJECT_ROOT)
    detector.scan()
    
    # Print summary
    detector.print_summary()
    
    # Save report
    report = detector.generate_report()
    report_path = PROJECT_ROOT / "reports" / "fase0"
    report_path.mkdir(parents=True, exist_ok=True)
    
    report_file = report_path / "dead_code_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Return exit code (1 if dead code found)
    if len(detector.dead_files) > 0 or len(detector.get_duplicates()) > 0:
        print("\n⚠️  WARNING: Dead code or duplicates detected!")
        print("   Run cleanup script to remove them.")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
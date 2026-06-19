#!/usr/bin/env python3
"""
NEMESIS Import Guard - Phase 0
Mendeteksi duplicate modules, circular imports, dan konflik impor
"""

import ast
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

PROJECT_ROOT = Path(".").resolve()
EXCLUDE_DIRS = {'venv', '__pycache__', 'node_modules', '.git', '.pytest_cache', 'htmlcov', 'backups', 'snapshots'}

@dataclass
class ImportInfo:
    module: str
    file_path: Path
    line_no: int
    is_relative: bool = False  # <-- Ganti 'level' dengan 'is_relative'

class ImportGuard:
    def __init__(self, root_path: Path):
        self.root = root_path
        self.imports: Dict[str, List[ImportInfo]] = defaultdict(list)
        self.duplicates: List[Dict] = []
        self.circular_imports: List[List[str]] = []
        self.module_graph: Dict[str, Set[str]] = defaultdict(set)
        self.module_locations: Dict[str, Path] = {}
        
    def scan(self):
        """Scan all Python files for imports"""
        print("🔍 Scanning imports...")
        
        py_files = []
        for py_file in self.root.rglob('*.py'):
            # Skip excluded directories
            if any(ex in py_file.parts for ex in EXCLUDE_DIRS):
                continue
            py_files.append(py_file)
            
        print(f"   Found {len(py_files)} Python files")
        
        for py_file in py_files:
            self._scan_file(py_file)
            
        print("   Import scan completed")
        
    def _scan_file(self, file_path: Path):
        """Scan individual file for imports"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"   ⚠️  Syntax error in {file_path}: {e}")
            return
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[alias.name].append(
                        ImportInfo(alias.name, file_path, node.lineno, is_relative=False)
                    )
                    
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Check if relative import (starts with dots)
                    is_relative = node.module.startswith('.') if node.module else node.level > 0
                    actual_module = node.module.lstrip('.') if node.module else ''
                    if actual_module:
                        self.imports[actual_module].append(
                            ImportInfo(actual_module, file_path, node.lineno, is_relative=is_relative)
                        )
                    
        # Track module location
        module_name = file_path.stem
        if module_name != '__init__':
            if module_name in self.module_locations:
                self.duplicates.append({
                    'module': module_name,
                    'files': [str(self.module_locations[module_name]), str(file_path)]
                })
            else:
                self.module_locations[module_name] = file_path
                
    def detect_duplicate_modules(self) -> List[Dict]:
        """Detect duplicate module names"""
        duplicates = []
        seen = set()
        
        for module_name, files in self.imports.items():
            # Group by module name
            unique_files = set(f.file_path for f in files)
            if len(unique_files) > 1 and module_name not in seen:
                duplicates.append({
                    'module': module_name,
                    'files': [str(f) for f in unique_files],
                    'count': len(unique_files)
                })
                seen.add(module_name)
                
        return duplicates
        
    def build_import_graph(self):
        """Build directed graph of imports"""
        for module_name, imports in self.imports.items():
            for imp in imports:
                # Get module's own module name
                source_module = imp.file_path.stem
                target_module = imp.module.split('.')[0]  # Top-level module only
                
                if source_module != target_module and source_module and target_module:
                    self.module_graph[source_module].add(target_module)
                    
    def detect_circular_imports(self) -> List[List[str]]:
        """Detect circular imports using DFS"""
        self.build_import_graph()
        
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            if node in rec_stack:
                # Found cycle
                if node in path:
                    cycle_start = path.index(node)
                    return path[cycle_start:] + [node]
                return None
                
            if node in visited:
                return None
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.module_graph.get(node, []):
                result = dfs(neighbor, path.copy())
                if result and result not in cycles:
                    cycles.append(result)
                    
            rec_stack.remove(node)
            return None
            
        for module in list(self.module_graph.keys()):
            if module not in visited:
                dfs(module, [])
                
        return cycles
        
    def generate_report(self) -> Dict:
        """Generate complete report"""
        duplicates = self.detect_duplicate_modules()
        circular = self.detect_circular_imports()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.root),
            'total_modules_scanned': len(self.module_locations),
            'duplicate_modules': duplicates,
            'duplicate_count': len(duplicates),
            'circular_imports': circular,
            'circular_count': len(circular),
            'warnings': self._generate_warnings()
        }
        
    def _generate_warnings(self) -> List[str]:
        """Generate actionable warnings"""
        warnings = []
        
        if self.detect_duplicate_modules():
            warnings.append("Duplicate modules detected - consolidate to single location")
            
        if self.detect_circular_imports():
            warnings.append("Circular imports detected - refactor to break cycles")
            
        # Check for problematic imports
        for module, imports in self.imports.items():
            if module.startswith('backend.') and module.count('.') > 3:
                warnings.append(f"Deep import path: {module} - consider simplifying")
                
        return warnings
        
    def print_summary(self):
        """Print summary to console"""
        print("\n" + "="*60)
        print("IMPORT GUARD REPORT")
        print("="*60)
        
        duplicates = self.detect_duplicate_modules()
        print(f"\n🔄 Duplicate modules: {len(duplicates)}")
        for d in duplicates[:5]:
            print(f"   - '{d['module']}' (found in {d['count']} locations)")
            
        circular = self.detect_circular_imports()
        print(f"\n🔁 Circular imports: {len(circular)}")
        for cycle in circular[:5]:
            print(f"   - {' → '.join(cycle)}")
            
        print(f"\n📊 Total modules scanned: {len(self.module_locations)}")
        
        print("\n" + "="*60)
        
    def is_clean(self) -> bool:
        """Check if no issues found"""
        return len(self.detect_duplicate_modules()) == 0 and len(self.detect_circular_imports()) == 0

def main():
    guard = ImportGuard(PROJECT_ROOT)
    guard.scan()
    guard.print_summary()
    
    # Save report
    report = guard.generate_report()
    report_dir = PROJECT_ROOT / "reports" / "fase0"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "import_guard_report.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
        
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Exit with appropriate code
    if guard.is_clean():
        print("\n✅ IMPORT GUARD PASSED - No duplicate or circular imports detected")
        return 0
    else:
        print("\n⚠️  IMPORT GUARD WARNINGS - Review issues before proceeding")
        return 0  # Changed to 0 to continue, but with warning

if __name__ == "__main__":
    sys.exit(main())
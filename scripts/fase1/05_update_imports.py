#!/usr/bin/env python3
"""
NEMESIS FASE 1 - Update Import Statements
Mengupdate semua import statements ke canonical paths
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Mapping import lama ke import baru
IMPORT_MAPPINGS = [
    # Evidence
    (r'from backend\.evidence_registry import', 'from backend.evidence.registry import'),
    (r'from backend\.evidence_hashing import', 'from backend.evidence.hashing import'),
    (r'from backend\.evidence_package import', 'from backend.evidence.package import'),
    (r'from backend\.intelligence\.legal\.evidence_registry import', 'from backend.evidence.registry import'),
    (r'from backend\.intelligence\.legal\.evidence_hashing import', 'from backend.evidence.hashing import'),
    (r'import backend\.evidence_registry', 'import backend.evidence.registry'),
    (r'import backend\.evidence_hashing', 'import backend.evidence.hashing'),
    
    # WebSocket
    (r'from backend\.ws\.gateway import', 'from backend.websocket.manager import'),
    (r'from backend\.ws\.event_bus import', 'from backend.websocket.broadcaster import'),
    (r'from backend\.websocket\.connection_manager import', 'from backend.websocket.manager import'),
    (r'from backend\.websocket\.ws_observability import', 'from backend.websocket.observability import'),
    (r'import backend\.ws\.gateway', 'import backend.websocket.manager'),
    (r'import backend\.websocket\.connection_manager', 'import backend.websocket.manager'),
    
    # Event Bus
    (r'from backend\.core\.events\.event_bus import', 'from backend.core.events.bus import'),
    (r'from backend\.orchestrator\.event_bus_v2 import', 'from backend.core.events.bus import'),
    (r'import backend\.core\.events\.event_bus', 'import backend.core.events.bus'),
    (r'import backend\.orchestrator\.event_bus_v2', 'import backend.core.events.bus'),
    
    # Graph
    (r'from backend\.intelligence\.graph\.relationship_graph import', 'from backend.graph.relationship_graph import'),
    (r'from backend\.intelligence\.core\.graph\.relationship_graph import', 'from backend.graph.relationship_graph import'),
    (r'from backend\.intelligence\.graph\.collusion_detector import', 'from backend.graph.collusion_detector import'),
    (r'from backend\.intelligence\.core\.graph\.collusion_detector import', 'from backend.graph.collusion_detector import'),
    (r'import backend\.intelligence\.graph\.relationship_graph', 'import backend.graph.relationship_graph'),
]

def find_all_py_files(root_dir: Path) -> List[Path]:
    """Find all Python files (excluding venv, node_modules, __pycache__)"""
    py_files = []
    ignore_patterns = ['venv', 'node_modules', '__pycache__', '.pytest_cache', 'migrations']
    
    for py_file in root_dir.rglob("*.py"):
        if any(p in str(py_file) for p in ignore_patterns):
            continue
        py_files.append(py_file)
    
    return py_files

def update_imports_in_file(file_path: Path, dry_run: bool = True) -> Tuple[int, List[str]]:
    """Update import statements in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0, [f"Error reading {file_path}: {e}"]
    
    original_content = content
    changes = []
    
    for old_pattern, new_import in IMPORT_MAPPINGS:
        if re.search(old_pattern, content):
            # Count occurrences
            count = len(re.findall(old_pattern, content))
            content = re.sub(old_pattern, new_import, content)
            changes.append(f"  {old_pattern} -> {new_import} ({count} occurrences)")
    
    if content != original_content:
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return len(changes), changes
    
    return 0, []

def main():
    """Main execution"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Dry run (default: True)')
    parser.add_argument('--apply', action='store_true',
                       help='Apply changes')
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    print("\n" + "="*60)
    print("FASE 1: UPDATE IMPORT STATEMENTS")
    print("="*60)
    print(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    print("")
    
    py_files = find_all_py_files(PROJECT_ROOT)
    print(f"Found {len(py_files)} Python files")
    print("")
    
    total_changes = 0
    files_updated = 0
    
    for py_file in py_files:
        changes_count, changes = update_imports_in_file(py_file, dry_run)
        if changes_count > 0:
            files_updated += 1
            total_changes += changes_count
            if changes_count > 0:
                rel_path = py_file.relative_to(PROJECT_ROOT)
                print(f"📝 {rel_path}")
                for change in changes[:3]:  # Show first 3 changes
                    print(change)
                if len(changes) > 3:
                    print(f"  ... and {len(changes) - 3} more")
                print("")
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Files updated: {files_updated}")
    print(f"Total changes: {total_changes}")
    
    if dry_run:
        print("")
        print("⚠️  This was a DRY RUN. No files were modified.")
        print("   To apply changes, run: python 05_update_imports.py --apply")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
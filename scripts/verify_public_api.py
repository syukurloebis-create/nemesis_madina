#!/usr/bin/env python3
"""
Verify Public API Stability

Checks that public API hasn't changed since baseline.
"""

import json
from pathlib import Path


def verify_public_api(baseline_path: Path, current_path: Path) -> bool:
    """Verify public API hasn't changed."""
    
    if not baseline_path.exists():
        print("❌ Baseline public_api.json not found!")
        return False
    
    if not current_path.exists():
        print("❌ Current public_api.json not found!")
        return False
    
    with open(baseline_path, 'r', encoding='utf-8') as f:
        baseline = json.load(f)
    
    with open(current_path, 'r', encoding='utf-8') as f:
        current = json.load(f)
    
    baseline_graph = baseline.get("graph_modules", {})
    current_graph = current.get("graph_modules", {})
    
    # Check for removed modules
    removed = set(baseline_graph.keys()) - set(current_graph.keys())
    if removed:
        print(f"❌ Removed modules: {removed}")
        return False
    
    # Check for removed symbols
    all_removed = []
    for module, symbols in baseline_graph.items():
        if module in current_graph:
            removed_symbols = set(symbols) - set(current_graph[module])
            if removed_symbols:
                all_removed.append((module, removed_symbols))
    
    if all_removed:
        print("❌ Removed symbols:")
        for module, symbols in all_removed:
            print(f"   {module}: {symbols}")
        return False
    
    # Check for new modules (warning, not error)
    new_modules = set(current_graph.keys()) - set(baseline_graph.keys())
    if new_modules:
        print(f"⚠️ New modules added: {new_modules}")
    
    print("✅ Public API is stable")
    return True


def main():
    """Main entry point."""
    baseline_path = Path("baseline_public_api.json")
    current_path = Path("public_api.json")
    
    # If baseline doesn't exist, create it
    if not baseline_path.exists():
        print("📝 Creating baseline public_api.json...")
        if current_path.exists():
            import shutil
            shutil.copy(current_path, baseline_path)
            print(f"✅ Baseline saved to {baseline_path}")
        else:
            print("❌ No public_api.json found to create baseline")
            return 1
    
    return 0 if verify_public_api(baseline_path, current_path) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
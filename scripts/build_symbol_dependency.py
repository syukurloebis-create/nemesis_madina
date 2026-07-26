#!/usr/bin/env python3
"""
Build Symbol-Level Dependency Map

Creates symbol_dependency.json mapping imports at class/function level.
"""

import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any


def build_symbol_dependency(root: Path) -> Dict[str, Any]:
    """Build dependency map at symbol level."""
    
    imports = defaultdict(list)
    reverse = defaultdict(list)
    
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file) or "venv" in str(py_file) or ".git" in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                continue
                
            tree = ast.parse(content)
            file_path = str(py_file.relative_to(root))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports[file_path].append({
                            "module": alias.name,
                            "symbol": None,
                            "alias": alias.asname
                        })
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module
                        for alias in node.names:
                            imports[file_path].append({
                                "module": module,
                                "symbol": alias.name,
                                "alias": alias.asname
                            })
                            if alias.name != "*":
                                key = f"{module}.{alias.name}"
                                reverse[key].append({
                                    "file": file_path,
                                    "line": node.lineno,
                                    "alias": alias.asname
                                })
                        
        except SyntaxError:
            print(f"⚠️ Syntax error in {py_file}, skipping")
        except Exception as e:
            print(f"⚠️ Error parsing {py_file}: {e}")
    
    # Convert defaultdict to dict for JSON
    return {
        "imports": dict(imports),
        "reverse": dict(reverse),
        "total_files": len(imports),
        "total_reverse_mappings": len(reverse)
    }


def main():
    """Main entry point."""
    root = Path("backend")
    
    if not root.exists():
        print("❌ backend directory not found!")
        return 1
    
    print("🔍 Building symbol-level dependency map...")
    deps = build_symbol_dependency(root)
    
    # Save to file
    output_path = Path("dependency_map.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(deps, f, indent=2, default=str)
    
    print(f"✅ Symbol dependency map saved to {output_path}")
    print(f"   - Total files analyzed: {deps['total_files']}")
    print(f"   - Total reverse mappings: {deps['total_reverse_mappings']}")
    
    # Also find graph-specific dependencies
    graph_deps = {
        k: v for k, v in deps["reverse"].items()
        if k.startswith("backend.graph")
    }
    
    graph_output = Path("graph_dependencies.json")
    with open(graph_output, "w", encoding='utf-8') as f:
        json.dump(graph_deps, f, indent=2, default=str)
    
    print(f"   - Graph dependencies: {len(graph_deps)}")
    print(f"   - Saved to {graph_output}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
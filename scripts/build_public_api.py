#!/usr/bin/env python3
"""
Build Public API Inventory

Creates public_api.json respecting __all__ and naming conventions.
"""

import ast
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any


def extract_public_api(project_root: Path, backend_root: Path) -> Dict[str, List[str]]:
    """Extract public API respecting __all__."""
    
    public_api = defaultdict(list)
    syntax_errors = []
    
    for py_file in backend_root.rglob("*.py"):
        if "__pycache__" in str(py_file) or "venv" in str(py_file) or ".git" in str(py_file):
            continue
        
        try:
            # ✅ FIX: Use utf-8-sig to strip BOM
            with open(py_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if not content.strip():
                continue
                
            tree = ast.parse(content)
            
            # Build module path from project root
            rel_path = str(py_file.relative_to(project_root))
            module_path = rel_path.replace("\\", ".").replace("/", ".").replace(".py", "")
            if module_path.endswith(".__init__"):
                module_path = module_path[:-9]
            
            # Check for __all__
            has_all = False
            all_symbols = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            has_all = True
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        all_symbols.append(elt.value)
            
            # Extract public symbols
            symbols = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if has_all:
                        if node.name in all_symbols:
                            symbols.append(node.name)
                    elif not node.name.startswith("_"):
                        symbols.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if has_all:
                        if node.name in all_symbols:
                            symbols.append(node.name)
                    elif not node.name.startswith("_"):
                        symbols.append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if has_all:
                                if target.id in all_symbols:
                                    symbols.append(target.id)
                            elif not target.id.startswith("_"):
                                symbols.append(target.id)
            
            # If no __all__ and no symbols found, include all non-private
            if not has_all and not symbols:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not node.name.startswith("_"):
                            symbols.append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith("_"):
                            symbols.append(node.name)
            
            if symbols:
                public_api[module_path] = symbols
                        
        except SyntaxError as e:
            error_info = {
                "file": str(py_file.relative_to(project_root)),
                "line": e.lineno,
                "column": e.offset,
                "message": e.msg,
                "text": e.text.strip() if e.text else ""
            }
            syntax_errors.append(error_info)
            print(f"⚠️ Syntax error: {error_info['file']}:{error_info['line']}:{error_info['column']} - {error_info['message']}")
        except Exception as e:
            print(f"⚠️ Error parsing {py_file}: {e}")
    
    if syntax_errors:
        with open("syntax_errors.json", "w", encoding='utf-8') as f:
            json.dump(syntax_errors, f, indent=2, default=str)
        print(f"   - Syntax errors saved to syntax_errors.json ({len(syntax_errors)} errors)")
    
    return dict(public_api)


def main():
    """Main entry point."""
    project_root = Path.cwd()
    backend_root = project_root / "backend"
    
    if not backend_root.exists():
        print("❌ backend directory not found!")
        return 1
    
    print("🔍 Building public API inventory...")
    api = extract_public_api(project_root, backend_root)
    
    # Filter to graph modules
    graph_api = {
        k: v for k, v in api.items()
        if k.startswith("backend.graph")
    }
    
    # Save full API
    output_path = Path("public_api.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump({
            "all_modules": api,
            "graph_modules": graph_api,
            "all_modules_count": len(api),
            "graph_modules_count": len(graph_api),
        }, f, indent=2, default=str)
    
    print(f"✅ Public API saved to {output_path}")
    print(f"   - Total modules: {len(api)}")
    print(f"   - Graph modules: {len(graph_api)}")
    
    # Save only graph modules separately
    graph_output = Path("graph_public_api.json")
    with open(graph_output, "w", encoding='utf-8') as f:
        json.dump(graph_api, f, indent=2, default=str)
    
    print(f"   - Graph public API saved to {graph_output}")
    
    # Summary of graph modules
    print(f"\n📊 Graph Public API Summary ({len(graph_api)} modules):")
    for module, symbols in sorted(graph_api.items())[:10]:
        print(f"   {module}: {len(symbols)} symbols")
    if len(graph_api) > 10:
        print(f"   ... and {len(graph_api) - 10} more modules")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
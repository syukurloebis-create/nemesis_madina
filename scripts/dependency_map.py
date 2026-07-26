# scripts/dependency_map.py

import ast
import sys
from pathlib import Path


def build_import_map(root: Path) -> Dict[str, List[str]]:
    """Build import dependency map."""
    import_map = {}
    
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            rel_path = str(py_file.relative_to(root))
            import_map[rel_path] = imports
            
        except Exception as e:
            print(f"Error parsing {py_file}: {e}")
    
    return import_map


def find_orphans(import_map: Dict[str, List[str]]) -> List[str]:
    """Find orphan files (no one imports them)."""
    all_files = set(import_map.keys())
    imported_files = set()
    
    for imports in import_map.values():
        for imp in imports:
            # Convert import to file path
            imp_path = imp.replace(".", "/") + ".py"
            imported_files.add(imp_path)
            # Also check __init__.py
            imported_files.add(imp.replace(".", "/") + "/__init__.py")
    
    # Find orphans
    orphans = all_files - imported_files
    return list(orphans)


def main():
    root = Path("backend")
    import_map = build_import_map(root)
    
    print("=" * 60)
    print("DEPENDENCY MAP - ORPHAN FILES")
    print("=" * 60)
    
    orphans = find_orphans(import_map)
    for orphan in sorted(orphans):
        print(f"  {orphan}")
    
    print(f"\nTotal orphans: {len(orphans)}")


if __name__ == "__main__":
    main()
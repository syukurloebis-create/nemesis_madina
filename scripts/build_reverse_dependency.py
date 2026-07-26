#!/usr/bin/env python3
"""
Build Reverse Dependency Map

Creates reverse_dependency.json showing who imports what.
"""

import json
from pathlib import Path
from collections import defaultdict


def build_reverse_dependency(dep_map: dict) -> dict:
    """Build reverse dependency map."""
    
    reverse = dep_map.get("reverse", {})
    
    # Group by module prefix
    graph_deps = defaultdict(list)
    platform_deps = defaultdict(list)
    other_deps = defaultdict(list)
    
    for symbol, dependents in reverse.items():
        # Convert symbol to module
        module = symbol.rsplit(".", 1)[0] if "." in symbol else symbol
        
        if module.startswith("backend.graph"):
            graph_deps[module].extend(dependents)
        elif module.startswith("backend."):
            platform_deps[module].extend(dependents)
        else:
            other_deps[module].extend(dependents)
    
    # Deduplicate and count
    def deduplicate_and_count(deps_dict):
        result = {}
        for module, dependents in deps_dict.items():
            # Deduplicate by (file, line)
            unique = {}
            for dep in dependents:
                key = (dep.get("file"), dep.get("line"))
                if key not in unique:
                    unique[key] = dep
            result[module] = {
                "count": len(unique),
                "dependents": list(unique.values())
            }
        # Sort by count
        return dict(sorted(result.items(), key=lambda x: x[1]["count"], reverse=True))
    
    return {
        "graph_modules": deduplicate_and_count(graph_deps),
        "platform_modules": deduplicate_and_count(platform_deps),
        "other_modules": deduplicate_and_count(other_deps),
    }


def main():
    """Main entry point."""
    dep_map_path = Path("dependency_map.json")
    
    if not dep_map_path.exists():
        print("❌ dependency_map.json not found! Run build_symbol_dependency.py first.")
        return 1
    
    print("🔍 Building reverse dependency map...")
    
    with open(dep_map_path, 'r', encoding='utf-8') as f:
        dep_map = json.load(f)
    
    reverse_deps = build_reverse_dependency(dep_map)
    
    # Save
    output_path = Path("reverse_dependency.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(reverse_deps, f, indent=2, default=str)
    
    print(f"✅ Reverse dependency map saved to {output_path}")
    
    # Summary
    print(f"\n📊 Reverse Dependency Summary:")
    print(f"   Graph modules with dependents: {len(reverse_deps['graph_modules'])}")
    print(f"   Platform modules with dependents: {len(reverse_deps['platform_modules'])}")
    print(f"   Other modules with dependents: {len(reverse_deps['other_modules'])}")
    
    # Show top graph dependencies
    print(f"\n📊 Top 5 Graph Modules by Dependents:")
    for i, (module, info) in enumerate(list(reverse_deps['graph_modules'].items())[:5]):
        print(f"   {i+1}. {module}: {info['count']} dependents")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
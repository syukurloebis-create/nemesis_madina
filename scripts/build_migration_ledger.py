#!/usr/bin/env python3
"""
Build Migration Ledger

Creates migration_ledger.yaml tracking only architectural components.
"""

import json
import yaml
from pathlib import Path


# Components that are migration targets
ARCHITECTURAL_COMPONENTS = {
    "Repository",
    "Service",
    "Factory",
    "Mapper",
    "Assembler",
    "Collector",
    "Calculator",
    "Presenter",
    "Aggregate",
    "DTO",
    "Policy",
    "Validator",
    "Adapter",
    "Controller",
    "Handler",
    "Manager",
    "Orchestrator",
    "Coordinator",
    "Router",
    "UseCase",
    "Command",
    "Query",
    "EventHandler",
    "EventListener",
}


def is_architectural_component(name: str) -> bool:
    """Check if a symbol is an architectural component."""
    for comp in ARCHITECTURAL_COMPONENTS:
        if name.endswith(comp):
            return True
        if name == comp:
            return True
    return False


def build_migration_ledger(dep_map: dict, public_api: dict) -> dict:
    """Build migration ledger with only architectural components."""
    
    reverse = dep_map.get("reverse", {})
    graph_api = public_api.get("graph_modules", {})
    
    # Find architectural components
    components = {}
    
    for module, symbols in graph_api.items():
        if "graph" not in module:
            continue
        
        for symbol in symbols:
            # Only include architectural components
            if not is_architectural_component(symbol):
                continue
            
            key = f"{module}.{symbol}"
            dependents = reverse.get(key, [])
            
            components[key] = {
                "module": module,
                "symbol": symbol,
                "dependents_count": len(dependents),
                "phase": "Baseline",
                "wrapper_created": False,
                "compatibility_tests": False,
                "migrated_imports": 0,
                "remaining_imports": len(dependents),
                "is_active": len(dependents) > 0,
            }
    
    # Sort by dependents count
    sorted_components = sorted(
        components.items(),
        key=lambda x: x[1]["dependents_count"],
        reverse=True
    )
    
    # Build ledger
    ledger = {
        "components": {},
        "summary": {
            "total_components": len(sorted_components),
            "active_components": len([_ for _, info in sorted_components if info["is_active"]]),
            "total_dependents": sum(info["dependents_count"] for _, info in sorted_components),
        }
    }
    
    for key, info in sorted_components:
        component_name = f"{info['module']}.{info['symbol']}"
        ledger["components"][component_name] = {
            "source": component_name,
            "phase": info["phase"],
            "owner": "Graph Context" if info["is_active"] else "Candidate for Review",
            "dependents_count": info["dependents_count"],
            "wrapper_created": info.get("wrapper_created", False),
            "compatibility_tests": info.get("compatibility_tests", False),
            "migrated_imports": 0,
            "remaining_imports": info["dependents_count"],
        }
    
    return ledger


def main():
    """Main entry point."""
    dep_map_path = Path("dependency_map.json")
    public_api_path = Path("public_api.json")
    
    if not dep_map_path.exists():
        print("❌ dependency_map.json not found! Run build_symbol_dependency.py first.")
        return 1
    
    if not public_api_path.exists():
        print("❌ public_api.json not found! Run build_public_api.py first.")
        return 1
    
    print("🔍 Building migration ledger (architectural components only)...")
    
    with open(dep_map_path, 'r', encoding='utf-8') as f:
        dep_map = json.load(f)
    
    with open(public_api_path, 'r', encoding='utf-8') as f:
        public_api = json.load(f)
    
    ledger = build_migration_ledger(dep_map, public_api)
    
    # Save as YAML
    output_path = Path("migration_ledger.yaml")
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(ledger, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Migration ledger saved to {output_path}")
    print(f"   - Total components: {ledger['summary']['total_components']}")
    print(f"   - Active components: {ledger['summary']['active_components']}")
    print(f"   - Total dependents: {ledger['summary']['total_dependents']}")
    
    # Also save as JSON
    json_path = Path("migration_ledger.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2, default=str)
    
    print(f"   - Also saved as JSON: {json_path}")
    
    # Show top components
    print(f"\n📊 Top 10 Active Components by Dependents:")
    components = list(ledger["components"].items())
    active = [(name, info) for name, info in components if info["dependents_count"] > 0]
    for i, (name, info) in enumerate(active[:10]):
        print(f"   {i+1}. {name}: {info['dependents_count']} dependents")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
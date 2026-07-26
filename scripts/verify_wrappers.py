# scripts/verify_wrappers.py

import ast
import json
from pathlib import Path
from typing import Dict, List, Set


def extract_public_methods(file_path: Path) -> Set[str]:
    """Extract all public method names from a Python file."""
    methods = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith('_'):
                            methods.add(item.name)
    except Exception as e:
        print(f"⚠️ Error parsing {file_path}: {e}")
    
    return methods


def verify_wrapper_contracts():
    """Verify each wrapper mirrors its legacy implementation."""
    
    # Legacy → Wrapper mapping
    mapping = {
        "backend/graph/application/assembler.py": {
            "class": "GraphAssembler",
            "wrapper": "backend/factories/graph_factory.py"
        },
        "backend/graph/application/service.py": {
            "class": "GraphRegenerationService",
            "wrapper": "backend/services/graph_service.py"
        },
        "backend/graph/application/dto.py": {
            "class": "GraphBuildRequest",
            "wrapper": "backend/dtos/graph_dto.py"
        },
        "backend/graph/application/statistics.py": {
            "class": "BuilderStatistics",
            "wrapper": "backend/dtos/graph_statistics.py"
        },
        "backend/graph/application/projection_mapper.py": {
            "class": "GraphProjectionMapper",
            "wrapper": "backend/presenters/graph_presenter.py"
        },
    }
    
    root = Path.cwd()
    results = {}
    
    for legacy_path, info in mapping.items():
        legacy_file = root / legacy_path
        wrapper_file = root / info["wrapper"]
        class_name = info["class"]
        
        if not legacy_file.exists():
            results[class_name] = {"status": "ERROR", "message": f"Legacy file not found: {legacy_path}"}
            continue
        
        if not wrapper_file.exists():
            results[class_name] = {"status": "ERROR", "message": f"Wrapper file not found: {info['wrapper']}"}
            continue
        
        # Extract methods
        legacy_methods = extract_public_methods(legacy_file)
        wrapper_methods = extract_public_methods(wrapper_file)
        
        # Find missing methods
        missing = legacy_methods - wrapper_methods
        extra = wrapper_methods - legacy_methods
        
        if not missing and not extra:
            results[class_name] = {"status": "PASS", "message": "All methods mirrored"}
        else:
            results[class_name] = {
                "status": "FAIL",
                "missing": list(missing),
                "extra": list(extra),
                "legacy_methods": list(legacy_methods),
                "wrapper_methods": list(wrapper_methods),
            }
    
    return results


def main():
    print("🔍 Verifying wrapper contracts...")
    results = verify_wrapper_contracts()
    
    print("\n📊 Wrapper Verification Results:")
    print("-" * 60)
    
    all_pass = True
    for class_name, result in results.items():
        if result["status"] == "PASS":
            print(f"✅ {class_name}: {result['message']}")
        elif result["status"] == "ERROR":
            print(f"❌ {class_name}: {result['message']}")
            all_pass = False
        else:
            print(f"❌ {class_name}:")
            if result.get("missing"):
                print(f"   Missing methods: {result['missing']}")
            if result.get("extra"):
                print(f"   Extra methods: {result['extra']}")
            all_pass = False
    
    if all_pass:
        print("\n✅ All wrappers verified successfully!")
    else:
        print("\n❌ Some wrappers need to be updated.")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
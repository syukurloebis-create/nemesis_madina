#!/usr/bin/env python3
"""
Verify Constructor Compatibility

Checks that wrapper constructors match legacy implementations.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any  # ← ADDED


def get_constructor_params(file_path: Path, class_name: str) -> List[str]:
    """Get constructor parameters from a class."""
    params = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        for arg in item.args.args:
                            if arg.arg != 'self':
                                params.append(arg.arg)
                        break
    except Exception as e:
        print(f"⚠️ Error parsing {file_path}: {e}")
    
    return params


def verify_constructors():
    """Verify wrapper constructors match legacy."""
    
    mapping = {
        "GraphAssembler": {
            "legacy": "backend/graph/application/assembler.py",
            "wrapper": "backend/factories/graph_factory.py"
        },
        "GraphRegenerationService": {
            "legacy": "backend/graph/application/service.py",
            "wrapper": "backend/services/graph_service.py"
        },
        "GraphProjectionMapper": {
            "legacy": "backend/graph/application/projection_mapper.py",
            "wrapper": "backend/presenters/graph_presenter.py"
        },
    }
    
    root = Path.cwd()
    results = {}
    
    for class_name, info in mapping.items():
        legacy_file = root / info["legacy"]
        wrapper_file = root / info["wrapper"]
        
        if not legacy_file.exists():
            results[class_name] = {"status": "ERROR", "message": f"Legacy file not found: {info['legacy']}"}
            continue
        
        if not wrapper_file.exists():
            results[class_name] = {"status": "ERROR", "message": f"Wrapper file not found: {info['wrapper']}"}
            continue
        
        legacy_params = get_constructor_params(legacy_file, class_name)
        wrapper_params = get_constructor_params(wrapper_file, class_name)
        
        if legacy_params == wrapper_params:
            results[class_name] = {"status": "PASS", "message": "Constructors match"}
        else:
            results[class_name] = {
                "status": "FAIL",
                "legacy_params": legacy_params,
                "wrapper_params": wrapper_params,
            }
    
    return results


def main():
    print("🔍 Verifying constructor compatibility...")
    results = verify_constructors()
    
    print("\n📊 Constructor Verification Results:")
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
            print(f"   Legacy params: {result['legacy_params']}")
            print(f"   Wrapper params: {result['wrapper_params']}")
            all_pass = False
    
    if all_pass:
        print("\n✅ All constructors verified successfully!")
    else:
        print("\n❌ Some constructors need to be updated.")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
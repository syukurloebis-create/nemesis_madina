#!/usr/bin/env python3
"""
check_frozen_imports.py — ADR-030 Revision v4

Migration-Aware Architecture Freeze Validator with Baseline Comparison.

Rules:
  - Entrypoint → Existing Frozen (baseline) = PASS
  - Entrypoint → New Frozen (not in baseline) = FAIL
  - Frozen → Frozen = PASS (internal)
  - Entrypoint → Non-Frozen = PASS

Configuration: config/architecture.yml
Baseline: config/frozen_dependency_baseline.json
"""

import ast
import json
import sys
import yaml
from pathlib import Path
from typing import Set, Dict, Any, List


def load_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent.parent / "config" / "architecture.yml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {
        "frozen_components": {
            "FR-001": {"module": "backend.application.queries.get_dashboard_handler"},
            "FR-002": {"module": "backend.application.queries.dashboard_query"},
            "FR-003": {"module": "backend.infrastructure.repositories.dashboard_read_repository"},
            "FR-004": {"module": "backend.infrastructure.projections.dashboard_projection"},
            "FR-005": {"module": "backend.services.workflow_service"},
            "FR-006": {"module": "backend.infrastructure.projections.rebuild"},
            "FR-007": {"module": "backend.infrastructure.models.projection_checkpoint"},
            "FR-008": {"module": "backend.infrastructure.outbox.publisher"},
            "FR-009": {"module": "backend.application.commands.analysis_mapper"},
        },
        "runtime_entrypoints": ["backend.main", "backend.api", "backend.routers", "backend.bootstrap"],
        "excluded_directories": ["tests", "docs", "migrations", "scripts", "archive", "__pycache__", ".git"]
    }


def load_baseline() -> Dict[str, List[str]]:
    """Load baseline from config/frozen_dependency_baseline.json"""
    baseline_path = Path(__file__).parent.parent / "config" / "frozen_dependency_baseline.json"
    if baseline_path.exists():
        with open(baseline_path, 'r') as f:
            data = json.load(f)
            return data.get("dependencies", {})
    return {}


def is_frozen_module(module: str, frozen_modules: Set[str]) -> bool:
    for frozen in frozen_modules:
        if module == frozen:
            return True
        if module.startswith(frozen + "."):
            return True
    return False


def get_entrypoint_files(root: Path, entrypoints: List[str], excluded_dirs: List[str]) -> List[Path]:
    files = []
    for ep in entrypoints:
        path_parts = ep.split('.')
        filepath = root / Path(*path_parts).with_suffix('.py')
        if filepath.exists():
            files.append(filepath)
        dirpath = root / Path(*path_parts)
        if dirpath.exists() and dirpath.is_dir():
            files.extend(dirpath.rglob("*.py"))
    return [f for f in files if not any(excl in str(f) for excl in excluded_dirs)]


def extract_imports(filepath: Path) -> Set[str]:
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(filepath))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
    except Exception:
        pass
    return imports


def file_to_module(filepath: Path, root: Path) -> str:
    rel_path = filepath.relative_to(root)
    return str(rel_path).replace("/", ".").replace("\\", ".").replace(".py", "")


def is_in_baseline(entrypoint: str, dependency: str, baseline: Dict[str, List[str]]) -> bool:
    """Check if entrypoint → dependency exists in baseline"""
    for baseline_entrypoint, baseline_imports in baseline.items():
        if entrypoint == baseline_entrypoint:
            for baselined in baseline_imports:
                if dependency == baselined or dependency.startswith(baselined + "."):
                    return True
        elif entrypoint.startswith(baseline_entrypoint + "."):
            for baselined in baseline_imports:
                if dependency == baselined or dependency.startswith(baselined + "."):
                    return True
    return False


def main():
    config = load_config()
    baseline = load_baseline()
    root = Path(__file__).parent.parent

    frozen_modules = set()
    frozen_names = {}
    for fr_id, info in config["frozen_components"].items():
        frozen_modules.add(info["module"])
        frozen_names[info["module"]] = fr_id

    entrypoints = config.get("runtime_entrypoints", ["backend.main"])
    excluded_dirs = config.get("excluded_directories", [])

    entry_files = get_entrypoint_files(root, entrypoints, excluded_dirs)

    violations = []
    grandfathered = []

    for filepath in entry_files:
        module_name = file_to_module(filepath, root)

        if is_frozen_module(module_name, frozen_modules):
            continue

        imports = extract_imports(filepath)

        for imp in imports:
            if is_frozen_module(imp, frozen_modules):
                if is_in_baseline(module_name, imp, baseline):
                    grandfathered.append({
                        "entrypoint": module_name,
                        "import": imp,
                        "fr_id": frozen_names.get(imp, "UNKNOWN")
                    })
                else:
                    violations.append({
                        "entrypoint": module_name,
                        "import": imp,
                        "fr_id": frozen_names.get(imp, "UNKNOWN")
                    })

    if violations:
        print("❌ Architecture Freeze Validation FAILED")
        print("New frozen dependencies detected (not in baseline):")
        for v in violations:
            print(f"  - {v['entrypoint']} imports {v['fr_id']} ({v['import']})")
        print("\n💡 To fix:")
        print("  1. Remove the new import, OR")
        print("  2. If intentional, update baseline with ADR approval")
        return 1
    else:
        print("✅ Architecture Freeze Validation PASSED")
        if grandfathered:
            print(f"📊 Grandfathered frozen dependencies: {len(grandfathered)}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
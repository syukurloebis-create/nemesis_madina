#!/usr/bin/env python3
"""
check_dependency_graph.py — ADR-030 Revision v4

Migration-Aware Dependency Graph Validator with Baseline Comparison.

Rules:
  - Entrypoint → Existing Frozen (baseline) = PASS
  - Entrypoint → New Frozen (not in baseline) = FAIL
  - Frozen → Frozen = PASS (internal)

Configuration: config/architecture.yml
Baseline: config/frozen_dependency_baseline.json
"""

import ast
import json
import sys
import yaml
from pathlib import Path
from typing import Set, Dict, Any, List, Tuple
from collections import deque


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


def resolve_relative_import(module: str, level: int, current_module: str) -> str:
    if level == 0:
        return module
    parts = current_module.split('.')
    if level <= len(parts):
        base_parts = parts[:-level]
    else:
        base_parts = []
    if module:
        return '.'.join(base_parts + [module])
    return '.'.join(base_parts)


def expand_entrypoints(entrypoints: List[str], graph: Dict[str, Set[str]]) -> List[str]:
    """Expand package entrypoints to actual modules"""
    result = []
    for ep in entrypoints:
        for module in graph.keys():
            if module == ep or module.startswith(ep + "."):
                result.append(module)
    return list(set(result))


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


def build_dependency_graph(root: Path, excluded_dirs: List[str]) -> Dict[str, Set[str]]:
    graph = {}
    for filepath in root.rglob("*.py"):
        if any(excl in str(filepath) for excl in excluded_dirs):
            continue
        if "backend" not in str(filepath):
            continue
        rel_path = filepath.relative_to(root)
        module = str(rel_path).replace("/", ".").replace("\\", ".").replace(".py", "")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(filepath))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.add(name.name)
                elif isinstance(node, ast.ImportFrom):
                    level = node.level
                    module_name = node.module or ""
                    resolved = resolve_relative_import(module_name, level, module)
                    if resolved:
                        imports.add(resolved)
            graph[module] = imports
        except Exception:
            pass
    return graph


def main():
    config = load_config()
    baseline = load_baseline()
    root = Path(__file__).parent.parent

    frozen_modules = set()
    for info in config["frozen_components"].values():
        frozen_modules.add(info["module"])

    entrypoints = config.get("runtime_entrypoints", ["backend.main"])
    excluded_dirs = config.get("excluded_directories", [])

    graph = build_dependency_graph(root, excluded_dirs)
    entry_modules = expand_entrypoints(entrypoints, graph)

    violations = []
    grandfathered = []

    for entrypoint in entry_modules:
        if entrypoint not in graph:
            continue

        visited = set()
        queue = deque([(entrypoint, [entrypoint])])

        while queue:
            current, path = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if is_frozen_module(current, frozen_modules):
                # Check if this path is in baseline
                if is_in_baseline(entrypoint, current, baseline):
                    grandfathered.append(path)
                else:
                    violations.append(path)
                continue

            for dep in graph.get(current, set()):
                if dep not in visited:
                    queue.append((dep, path + [dep]))

    if violations:
        print("❌ Dependency Graph Validation FAILED")
        print(f"Found {len(violations)} new paths from entrypoint to frozen:")
        for v in violations[:10]:
            path_str = " → ".join(v)
            print(f"  - {path_str}")
        return 1
    else:
        print("✅ Dependency Graph Validation PASSED")
        if grandfathered:
            print(f"📊 Grandfathered paths: {len(grandfathered)}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
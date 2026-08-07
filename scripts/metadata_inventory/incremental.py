# incremental.py
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ChangeSet:
    added: List[str]
    modified: List[str]
    deleted: List[str]
    affected_modules: List[str]
    affected_registries: List[str]
    has_changes: bool = False

class ChangeDetector:
    """Detect changes for incremental verification."""
    
    def __init__(self, baseline_dir: Path, current_dir: Path):
        self.baseline_dir = baseline_dir
        self.current_dir = current_dir
        self._hash_cache: Dict[str, str] = {}
    
    def hash_file(self, file_path: Path) -> str:
        """Hash a file for change detection."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def scan_files(self, directory: Path) -> Dict[str, str]:
        """Scan all Python files in a directory."""
        hashes = {}
        for py_file in directory.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            rel_path = str(py_file.relative_to(directory))
            hashes[rel_path] = self.hash_file(py_file)
        return hashes
    
    def detect_changes(self) -> ChangeSet:
        """Detect changes between baseline and current."""
        baseline_hashes = self.scan_files(self.baseline_dir)
        current_hashes = self.scan_files(self.current_dir)
        
        baseline_files = set(baseline_hashes.keys())
        current_files = set(current_hashes.keys())
        
        added = list(current_files - baseline_files)
        deleted = list(baseline_files - current_files)
        
        modified = []
        for file in current_files & baseline_files:
            if baseline_hashes[file] != current_hashes[file]:
                modified.append(file)
        
        # Determine affected modules
        affected_modules = set()
        for file in added + modified + deleted:
            # Convert file path to module
            module = file.replace("/", ".").replace(".py", "")
            affected_modules.add(module)
        
        # Determine affected registries
        affected_registries = set()
        for module in affected_modules:
            if "models" in module or "infrastructure" in module:
                affected_registries.add("main")
        
        return ChangeSet(
            added=added,
            modified=modified,
            deleted=deleted,
            affected_modules=list(affected_modules),
            affected_registries=list(affected_registries),
            has_changes=bool(added or modified or deleted)
        )
    
    def get_relevant_nodes(self, changes: ChangeSet, dag_nodes: List[str]) -> List[str]:
        """Get DAG nodes relevant to changes."""
        # Map modules to DAG nodes
        module_to_nodes = {
            "models": ["model_discovery", "bootstrap_completeness"],
            "infrastructure": ["registry_discovery", "registry_consistency"],
            "database": ["registry_discovery", "metadata_ownership"],
            "domain": ["cross_registry_deps"],
        }
        
        relevant = set()
        for module in changes.affected_modules:
            for key, nodes in module_to_nodes.items():
                if key in module:
                    relevant.update(nodes)
        
        # Always include core nodes
        relevant.update(["registry_discovery", "mapper_integrity", "mapper_configuration"])
        
        # If any model changed, include identity map and persistence
        if changes.affected_modules:
            relevant.update(["persistence_contract", "identity_map", "unit_of_work"])
        
        return list(relevant)
    
    def get_incremental_plan(self, all_nodes: List[str]) -> Dict[str, Any]:
        """Get incremental execution plan."""
        changes = self.detect_changes()
        
        if not changes.has_changes:
            return {
                "mode": "no_changes",
                "nodes": [],
                "changes": changes,
                "message": "No changes detected"
            }
        
        relevant_nodes = self.get_relevant_nodes(changes, all_nodes)
        
        return {
            "mode": "incremental",
            "nodes": relevant_nodes,
            "changes": changes,
            "message": f"Running incremental verification for {len(relevant_nodes)} nodes"
        }
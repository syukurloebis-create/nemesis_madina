# semantic_change_detector.py
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

@dataclass
class SemanticChange:
    file: str
    type: str  # "model", "relationship", "mapping", "column", "index", "constraint"
    before: Optional[str] = None
    after: Optional[str] = None
    affected_nodes: List[str] = None

class SemanticChangeDetector:
    """Detect semantic changes in ORM models."""
    
    def __init__(self):
        self._baseline: Dict[str, str] = {}
    
    def extract_semantic_model(self, file_path: Path) -> Dict[str, str]:
        """Extract semantic model from a Python file."""
        try:
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())
            
            model = {}
            
            for node in ast.walk(tree):
                # Detect model classes
                if isinstance(node, ast.ClassDef):
                    # Check if it's a model class
                    has_base = False
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id in ["Base", "DeclarativeBase"]:
                            has_base = True
                            break
                    
                    if has_base:
                        # Extract model name and fields
                        model[node.name] = {
                            "type": "model",
                            "fields": []
                        }
                        
                        # Extract fields
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        if not target.id.startswith("__"):
                                            model[node.name]["fields"].append(target.id)
            
            return model
            
        except Exception:
            return {}
    
    def detect_changes(self, baseline_dir: Path, current_dir: Path) -> List[SemanticChange]:
        """Detect semantic changes."""
        changes = []
        
        # Scan baseline
        baseline_models = {}
        for py_file in baseline_dir.rglob("*.py"):
            if "models" in str(py_file):
                model = self.extract_semantic_model(py_file)
                if model:
                    baseline_models[str(py_file)] = model
        
        # Scan current
        current_models = {}
        for py_file in current_dir.rglob("*.py"):
            if "models" in str(py_file):
                model = self.extract_semantic_model(py_file)
                if model:
                    current_models[str(py_file)] = model
        
        # Compare
        all_files = set(baseline_models.keys()) | set(current_models.keys())
        
        for file in all_files:
            baseline = baseline_models.get(file, {})
            current = current_models.get(file, {})
            
            # New file
            if file not in baseline_models:
                changes.append(SemanticChange(
                    file=file,
                    type="model",
                    after="new file",
                    affected_nodes=["model_discovery", "bootstrap_completeness", "registry_consistency"]
                ))
                continue
            
            # Deleted file
            if file not in current_models:
                changes.append(SemanticChange(
                    file=file,
                    type="model",
                    before="deleted file",
                    affected_nodes=["registry_consistency", "cross_registry_deps"]
                ))
                continue
            
            # Check for model changes
            for model_name in set(baseline.keys()) | set(current.keys()):
                if model_name not in baseline:
                    changes.append(SemanticChange(
                        file=file,
                        type="model",
                        after=f"added {model_name}",
                        affected_nodes=["model_discovery", "bootstrap_completeness"]
                    ))
                elif model_name not in current:
                    changes.append(SemanticChange(
                        file=file,
                        type="model",
                        before=f"removed {model_name}",
                        affected_nodes=["registry_consistency", "cross_registry_deps"]
                    ))
                else:
                    # Check field changes
                    baseline_fields = set(baseline[model_name].get("fields", []))
                    current_fields = set(current[model_name].get("fields", []))
                    
                    if baseline_fields != current_fields:
                        added = current_fields - baseline_fields
                        removed = baseline_fields - current_fields
                        
                        if added:
                            changes.append(SemanticChange(
                                file=file,
                                type="column",
                                after=f"added fields: {added}",
                                affected_nodes=["metadata_ownership", "mapper_integrity"]
                            ))
                        if removed:
                            changes.append(SemanticChange(
                                file=file,
                                type="column",
                                before=f"removed fields: {removed}",
                                affected_nodes=["metadata_ownership", "mapper_integrity"]
                            ))
        
        return changes
    
    def get_affected_nodes(self, changes: List[SemanticChange]) -> Set[str]:
        """Get all affected nodes from semantic changes."""
        affected = set()
        for change in changes:
            if change.affected_nodes:
                affected.update(change.affected_nodes)
        return affected
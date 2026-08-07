# determinism_engine.py
import hashlib
import json
from typing import Any, Dict, List
from dataclasses import dataclass

@dataclass
class DeterminismResult:
    hash1: str
    hash2: str
    match: bool
    differences: List[str]

class DeterminismEngine:
    """Verify reproducibility of audit results."""
    
    def __init__(self, run_fn):
        self.run_fn = run_fn
        self.results = []
    
    def run_twice(self) -> DeterminismResult:
        """Run audit twice and compare results."""
        result1 = self.run_fn()
        result2 = self.run_fn()
        
        self.results = [result1, result2]
        
        # Canonicalize results
        canonical1 = self._canonicalize(result1)
        canonical2 = self._canonicalize(result2)
        
        # Compare hashes
        hash1 = hashlib.sha256(json.dumps(canonical1, sort_keys=True, default=str).encode()).hexdigest()
        hash2 = hashlib.sha256(json.dumps(canonical2, sort_keys=True, default=str).encode()).hexdigest()
        
        match = hash1 == hash2
        differences = []
        
        if not match:
            differences = self._diff(canonical1, canonical2)
        
        return DeterminismResult(
            hash1=hash1,
            hash2=hash2,
            match=match,
            differences=differences
        )
    
    def _canonicalize(self, result: Any) -> Dict:
        """Canonicalize result for deterministic comparison."""
        if hasattr(result, '__dict__'):
            return {k: self._canonicalize(v) for k, v in result.__dict__.items() if not k.startswith('_')}
        elif isinstance(result, dict):
            return {k: self._canonicalize(v) for k, v in sorted(result.items())}
        elif isinstance(result, list):
            return [self._canonicalize(v) for v in result]
        elif isinstance(result, (str, int, float, bool)):
            return result
        elif result is None:
            return None
        else:
            return str(result)
    
    def _diff(self, obj1: Any, obj2: Any, path: str = "") -> List[str]:
        """Recursive diff between two objects."""
        differences = []
        
        if type(obj1) != type(obj2):
            differences.append(f"{path}: type mismatch ({type(obj1)} vs {type(obj2)})")
            return differences
        
        if isinstance(obj1, dict):
            keys1 = set(obj1.keys())
            keys2 = set(obj2.keys())
            
            for key in keys1 - keys2:
                differences.append(f"{path}.{key}: missing in second")
            for key in keys2 - keys1:
                differences.append(f"{path}.{key}: missing in first")
            
            for key in keys1 & keys2:
                if obj1[key] != obj2[key]:
                    differences.extend(self._diff(obj1[key], obj2[key], f"{path}.{key}"))
        
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                differences.append(f"{path}: length mismatch ({len(obj1)} vs {len(obj2)})")
            else:
                for i, (a, b) in enumerate(zip(obj1, obj2)):
                    if a != b:
                        differences.extend(self._diff(a, b, f"{path}[{i}]"))
        
        elif obj1 != obj2:
            differences.append(f"{path}: {obj1} vs {obj2}")
        
        return differences
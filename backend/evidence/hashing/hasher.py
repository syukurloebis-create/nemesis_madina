"""Evidence Hasher - Hash computation for evidence"""

import hashlib
import json
from typing import Dict, Any, Union


class EvidenceHasher:
    """Hash computation for evidence"""
    
    @staticmethod
    def compute_hash(data: Dict[str, Any]) -> str:
        """Compute deterministic hash from dictionary"""
        sorted_data = EvidenceHasher._sort_dict(data)
        json_string = json.dumps(sorted_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_string.encode()).hexdigest()
    
    @staticmethod
    def compute_file_hash(content: bytes) -> str:
        """Compute hash from file content"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def _sort_dict(obj: Any) -> Any:
        """Recursively sort dictionary keys"""
        if isinstance(obj, dict):
            return {k: EvidenceHasher._sort_dict(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [EvidenceHasher._sort_dict(item) for item in obj]
        return obj

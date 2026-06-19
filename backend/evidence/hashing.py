"""Evidence Hashing - Deterministic hash computation"""

import hashlib
import json
from typing import Dict, Any, Union


class EvidenceHasher:
    """Deterministic hasher for evidence payloads"""
    
    @staticmethod
    def compute_hash(payload: Union[Dict, str, bytes]) -> str:
        """Compute SHA-256 hash of payload deterministically"""
        if isinstance(payload, dict):
            # Sort keys for deterministic JSON
            normalized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            content = normalized.encode('utf-8')
        elif isinstance(payload, str):
            content = payload.encode('utf-8')
        elif isinstance(payload, bytes):
            content = payload
        else:
            content = str(payload).encode('utf-8')
        
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def verify_hash(payload: Union[Dict, str, bytes], expected_hash: str) -> bool:
        """Verify that payload matches expected hash"""
        computed = EvidenceHasher.compute_hash(payload)
        return computed == expected_hash
    
    @staticmethod
    def compute_chain_hash(hashes: list) -> str:
        """Compute combined hash of hash chain"""
        combined = ''.join(hashes)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def quick_hash(data: str) -> str:
        """Quick hash for simple strings"""
        return hashlib.md5(data.encode()).hexdigest()[:16]

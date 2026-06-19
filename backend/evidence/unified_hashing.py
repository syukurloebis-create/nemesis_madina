"""
Unified Hashing - Single Source of Truth for All Hashes
"""

import hashlib
import json
from typing import Dict, Any


class UnifiedHasher:
    """Single hashing implementation for entire system"""
    
    @staticmethod
    def compute_event_hash(event: Dict[str, Any]) -> str:
        """Compute deterministic hash for event"""
        components = [
            event.get('aggregate_id', ''),
            str(event.get('sequence_num', 0)),
            event.get('event_type', ''),
            json.dumps(event.get('payload', {}), sort_keys=True),
            event.get('previous_hash', '0')
        ]
        return hashlib.sha256('|'.join(components).encode()).hexdigest()
    
    @staticmethod
    def compute_evidence_hash(content: Dict[str, Any]) -> str:
        """Compute hash for evidence content"""
        normalized = json.dumps(content, sort_keys=True)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    @staticmethod
    def verify_chain(events: list) -> tuple:
        """Verify hash chain integrity"""
        previous_hash = "0"
        for i, event in enumerate(events):
            computed = UnifiedHasher.compute_event_hash(event)
            if computed != event.get('event_hash'):
                return False, i, f"Hash mismatch at event {i}"
            if event.get('previous_hash') != previous_hash:
                return False, i, f"Chain broken at event {i}"
            previous_hash = computed
        return True, -1, "Chain valid"

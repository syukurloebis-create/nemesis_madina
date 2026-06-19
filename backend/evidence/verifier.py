"""Evidence Verifier - Integrity checking"""

import hashlib
import json
from typing import Dict, Any
from backend.evidence.hashing import EvidenceHasher

class EvidenceVerifier:
    @staticmethod
    def verify_integrity(evidence: Dict[str, Any]) -> bool:
        """Verify evidence integrity using hash chain"""
        computed_hash = EvidenceHasher.compute_hash(evidence.get("payload", {}))
        return computed_hash == evidence.get("hash")
    
    @staticmethod
    def verify_chain(evidence_chain: list) -> bool:
        """Verify entire chain of custody"""
        for i in range(1, len(evidence_chain)):
            prev = evidence_chain[i-1]
            curr = evidence_chain[i]
            if curr.get("previous_hash") != prev.get("hash"):
                return False
        return True

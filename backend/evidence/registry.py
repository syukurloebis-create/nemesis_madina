"""Evidence Registry - Single source of truth for evidence management"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class EvidenceStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    INVALID = "invalid"
    ARCHIVED = "archived"


@dataclass
class CustodyEvent:
    """Chain of custody event"""
    action: str
    actor: str
    timestamp: datetime
    reason: Optional[str] = None
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "action": self.action,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "signature": self.signature
        }


@dataclass
class Evidence:
    """Immutable evidence record"""
    id: str
    hash: str
    created_at: datetime
    source: str
    payload: Dict[str, Any]
    status: EvidenceStatus = EvidenceStatus.PENDING
    custody_chain: List[CustodyEvent] = field(default_factory=list)
    version: int = 1
    previous_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "hash": self.hash,
            "created_at": self.created_at.isoformat(),
            "source": self.source,
            "payload": self.payload,
            "status": self.status.value,
            "custody_chain": [c.to_dict() for c in self.custody_chain],
            "version": self.version,
            "previous_hash": self.previous_hash
        }


class EvidenceRegistry:
    """Singleton registry for evidence management"""
    
    _instance = None
    _evidences: Dict[str, Evidence] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def _compute_hash(payload: Dict[str, Any]) -> str:
        """Compute deterministic hash of payload"""
        sorted_payload = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(sorted_payload.encode()).hexdigest()
    
    def create(self, payload: Dict[str, Any], source: str, actor: str = "system") -> Evidence:
        """Create new evidence record"""
        evidence_id = str(uuid.uuid4())
        evidence_hash = self._compute_hash(payload)
        
        custody_event = CustodyEvent(
            action="created",
            actor=actor,
            timestamp=datetime.now(),
            reason="Initial evidence creation"
        )
        
        evidence = Evidence(
            id=evidence_id,
            hash=evidence_hash,
            created_at=datetime.now(),
            source=source,
            payload=payload,
            custody_chain=[custody_event]
        )
        
        self._evidences[evidence_id] = evidence
        return evidence
    
    def get(self, evidence_id: str) -> Optional[Evidence]:
        """Get evidence by ID"""
        return self._evidences.get(evidence_id)
    
    def verify(self, evidence_id: str) -> bool:
        """Verify evidence integrity"""
        evidence = self.get(evidence_id)
        if not evidence:
            return False
        
        computed_hash = self._compute_hash(evidence.payload)
        return computed_hash == evidence.hash
    
    def add_custody_event(self, evidence_id: str, action: str, actor: str, reason: str = None) -> Optional[Evidence]:
        """Add custody chain event"""
        evidence = self.get(evidence_id)
        if not evidence:
            return None
        
        event = CustodyEvent(
            action=action,
            actor=actor,
            timestamp=datetime.now(),
            reason=reason
        )
        evidence.custody_chain.append(event)
        return evidence
    
    def list_all(self) -> List[Evidence]:
        """List all evidence"""
        return list(self._evidences.values())
    
    def get_custody_chain(self, evidence_id: str) -> List[Dict]:
        """Get full custody chain"""
        evidence = self.get(evidence_id)
        if not evidence:
            return []
        return [e.to_dict() for e in evidence.custody_chain]

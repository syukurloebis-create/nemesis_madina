"""
Evidence DTOs - Data Transfer Objects
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class EvidenceType(str, Enum):
    """Type of evidence"""
    GENERIC = "generic"
    EVENT = "event"
    ALERT = "alert"
    FORENSIC = "forensic"
    AUDIT = "audit"
    LEGAL = "legal"


@dataclass
class CustodyEvent:
    """Single event in custody chain"""
    action: str  # created, verified, transferred, archived
    actor: str
    timestamp: datetime
    reason: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class Evidence:
    """Immutable evidence record"""
    id: str
    hash: str
    created_at: datetime
    source: str
    payload: Dict[str, Any]
    evidence_type: EvidenceType = EvidenceType.GENERIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    custody_chain: List[CustodyEvent] = field(default_factory=list)
    version: int = 1
    previous_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "hash": self.hash,
            "created_at": self.created_at.isoformat(),
            "source": self.source,
            "payload": self.payload,
            "evidence_type": self.evidence_type.value,
            "metadata": self.metadata,
            "custody_chain": [
                {
                    "action": e.action,
                    "actor": e.actor,
                    "timestamp": e.timestamp.isoformat(),
                    "reason": e.reason
                }
                for e in self.custody_chain
            ],
            "version": self.version,
            "previous_hash": self.previous_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        """Create from dictionary"""
        from .dto import CustodyEvent, EvidenceType
        
        return cls(
            id=data["id"],
            hash=data["hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            source=data["source"],
            payload=data["payload"],
            evidence_type=EvidenceType(data["evidence_type"]),
            metadata=data.get("metadata", {}),
            custody_chain=[
                CustodyEvent(
                    action=e["action"],
                    actor=e["actor"],
                    timestamp=datetime.fromisoformat(e["timestamp"]),
                    reason=e.get("reason")
                )
                for e in data.get("custody_chain", [])
            ],
            version=data.get("version", 1),
            previous_hash=data.get("previous_hash")
        )

# backend/domain/events/evidence_events.py
"""
NEMESIS Madina - Evidence Domain Events
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from uuid import UUID

from backend.domain.events.base import DomainEvent
from backend.domain.value_objects.evidence_verification import EvidenceVerification
from backend.domain.value_objects.case_id import CaseId


@dataclass(frozen=True)
class EvidencePayload:
    """New-style payload for evidence events."""

    case_id: CaseId
    verified_count: int = 0
    pending_count: int = 0
    rejected_count: int = 0
    total_count: int = 0
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "verified_count": self.verified_count,
            "pending_count": self.pending_count,
            "rejected_count": self.rejected_count,
            "total_count": self.total_count,
            "score": self.score,  # ← ADD THIS
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidencePayload":
        return cls(
            case_id=CaseId(data["case_id"]),
            verified_count=data.get("verified_count", 0),
            pending_count=data.get("pending_count", 0),
            rejected_count=data.get("rejected_count", 0),
            total_count=data.get("total_count", 0),
            score=data.get("score", 0.0),  # ← ADD THIS
        )


@dataclass(frozen=True)
class EvidenceVerificationCompleted(DomainEvent[EvidencePayload]):
    EVENT_NAME = "EvidenceVerificationCompleted"
    EVENT_VERSION = "1"


# ============================================================================
# COMPATIBILITY ADAPTER (Plain Class)
# ============================================================================

class EvidenceVerified(EvidenceVerificationCompleted):
    """Compatibility adapter for old aggregate calls."""
    
    def __init__(self, case_id: CaseId, verification: EvidenceVerification):
        payload = EvidencePayload(
            case_id=case_id,
            verified_count=verification.verified_count,
            pending_count=verification.pending_count,
            rejected_count=verification.rejected_count,
            total_count=verification.total_count,
        )
        super().__init__(payload=payload)

@dataclass(frozen=True)
class LegacyEvidencePayload:
    """Legacy payload for backward compatibility."""
    score: float = 0.0
    case_id: Optional[CaseId] = None
    verified_count: int = 0
    pending_count: int = 0
    rejected_count: int = 0
    total_count: int = 0

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "case_id": str(self.case_id) if self.case_id else None,
            "verified_count": self.verified_count,
            "pending_count": self.pending_count,
            "rejected_count": self.rejected_count,
            "total_count": self.total_count,
        }
# backend/domain/events/evidence_events.py
"""
NEMESIS Madina - Evidence Domain Events
"""

from dataclasses import dataclass
from typing import Dict, Any
from uuid import UUID

from backend.domain.events.base import DomainEvent
from backend.domain.value_objects.evidence_verification import EvidenceVerification
from backend.domain.value_objects.case_id import CaseId


@dataclass(frozen=True)
class EvidencePayload:
    """New-style payload for evidence events."""
    
    case_id: CaseId
    verified_count: int
    pending_count: int
    rejected_count: int
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "verified_count": self.verified_count,
            "pending_count": self.pending_count,
            "rejected_count": self.rejected_count,
            "total_count": self.total_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidencePayload":
        return cls(
            case_id=CaseId(data["case_id"]),
            verified_count=data["verified_count"],
            pending_count=data["pending_count"],
            rejected_count=data["rejected_count"],
            total_count=data["total_count"],
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
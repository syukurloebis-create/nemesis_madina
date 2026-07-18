"""
NEMESIS Madina - Application Events
"""

from dataclasses import dataclass
from typing import Dict, Any
from typing import ClassVar
from uuid import UUID

from backend.domain.events.base import DomainEvent
from backend.domain.events.metadata import EventMetadata


@dataclass(frozen=True)
class IntelligenceAssessmentPayload:
    """Payload for intelligence assessment application event."""
    
    case_id: UUID
    status: str
    confidence: float
    version: str
    duration_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "status": self.status,
            "confidence": self.confidence,
            "version": self.version,
            "duration_ms": self.duration_ms,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntelligenceAssessmentPayload":
        return cls(
            case_id=UUID(data["case_id"]),
            status=data["status"],
            confidence=data["confidence"],
            version=data["version"],
            duration_ms=data["duration_ms"],
        )


@dataclass(frozen=True)
class IntelligenceAssessmentCompleted(DomainEvent[IntelligenceAssessmentPayload]):
    """Application event emitted when intelligence assessment completes."""
    EVENT_NAME: ClassVar[str] = "IntelligenceAssessmentCompleted"
    EVENT_VERSION: ClassVar[str] = "1"
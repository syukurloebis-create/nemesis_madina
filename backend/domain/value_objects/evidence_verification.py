# backend/domain/value_objects/evidence_verification.py
"""
NEMESIS Madina - Evidence Verification Value Object
✅ Pure Value Object - no aggregate knowledge
✅ Immutable fields
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class EvidenceVerification:
    """Evidence verification result - Pure Value Object."""

    # Core fields (required)
    case_id: str = ""
    verified_count: int = 0
    pending_count: int = 0
    rejected_count: int = 0
    total_count: int = 0
    
    # Additional fields (with defaults)
    score: float = 0.0
    level: str = "UNKNOWN"
    avg_trust: float = 0.0
    avg_confidence: float = 0.0
    confidence_level: str = "UNKNOWN"

    @property
    def completion_percentage(self) -> float:
        """Calculate verification completion percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.verified_count / self.total_count) * 100

    @property
    def is_complete(self) -> bool:
        """Check if verification is complete."""
        return self.pending_count == 0

    @property
    def is_verified(self) -> bool:
        """Check if all evidence is verified."""
        return self.is_complete and self.rejected_count == 0
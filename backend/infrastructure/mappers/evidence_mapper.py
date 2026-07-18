# backend/infrastructure/mappers/evidence_mapper.py
"""
NEMESIS Madina - Evidence Verification Mapper
✅ Maps EvidenceVerification Value Object ↔ JSONB
✅ Stateless, pure functions
"""

from typing import Optional, Dict, Any
from backend.domain.value_objects.evidence_verification import EvidenceVerification


class EvidenceVerificationMapper:
    """Evidence Verification mapper for DDD infrastructure."""

    @staticmethod
    def to_dict(verification: Optional[EvidenceVerification]) -> Optional[Dict[str, Any]]:
        """Convert domain object to JSONB data."""
        if verification is None:
            return None
        
        return {
            "case_id": verification.case_id,
            "verified_count": verification.verified_count,
            "pending_count": verification.pending_count,
            "rejected_count": verification.rejected_count,
            "total_count": verification.total_count,
            "score": verification.score,
            "level": verification.level,
            "avg_trust": verification.avg_trust,
            "avg_confidence": verification.avg_confidence,
            "confidence_level": verification.confidence_level,
        }

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> Optional[EvidenceVerification]:
        """Convert JSONB data to domain object."""
        if data is None:
            return None
        
        return EvidenceVerification(
            case_id=data.get("case_id", ""),
            verified_count=data.get("verified_count", 0),
            pending_count=data.get("pending_count", 0),
            rejected_count=data.get("rejected_count", 0),
            total_count=data.get("total_count", 0),
            score=float(data.get("score", 0.0)),
            level=data.get("level", "UNKNOWN"),
            avg_trust=float(data.get("avg_trust", 0.0)),
            avg_confidence=float(data.get("avg_confidence", 0.0)),
            confidence_level=data.get("confidence_level", "UNKNOWN"),
        )
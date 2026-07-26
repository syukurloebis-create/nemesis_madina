"""
Evidence Score Calculator — Pure Business Logic.
"""

from typing import Optional
from dataclasses import dataclass

from backend.dtos.collector_dtos import EvidenceCollectorDTO
from backend.calculators.config import CalculatorConfig, EvidenceWeights
from backend.domain.enums import EngineStatus


@dataclass(frozen=True, slots=True)
class CalculatedEvidence:
    """Calculator output for Evidence."""
    score: float
    level: str
    confidence_level: str


class EvidenceScoreCalculator:
    """Evidence Score Calculator — Pure Function."""

    @classmethod
    def calculate(
        cls,
        dto: EvidenceCollectorDTO,
        weights: Optional[EvidenceWeights] = None,
    ) -> CalculatedEvidence:
        """Calculate evidence metrics from DTO."""
        if weights is None:
            config = CalculatorConfig.default()
            weights = config.get_evidence_weights()

        total = dto.total
        verified = dto.verified
        pending = dto.pending
        rejected = dto.rejected

        if total == 0:
            return CalculatedEvidence(
                score=0.0,
                level="NO_DATA",
                confidence_level="UNKNOWN",
            )

        # ✅ FIXED: Use correct EvidenceWeights fields
        # Component scores (0-100 scale)
        trust_score = (dto.avg_trust / 100.0) * 100 * weights.trust_weight
        confidence_score = (dto.avg_confidence / 100.0) * 100 * weights.confidence_weight
        verification_score = (verified / total) * 100 * weights.verification_weight

        # Total score (0-100)
        score = trust_score + confidence_score + verification_score

        # Determine level
        if score >= 80:
            level = "EXCELLENT"
        elif score >= 60:
            level = "GOOD"
        elif score >= 40:
            level = "MEDIUM"
        elif score >= 20:
            level = "POOR"
        else:
            level = "NO_DATA"

        # Determine confidence level
        if dto.avg_confidence >= 80:
            confidence_level = "HIGH"
        elif dto.avg_confidence >= 50:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        return CalculatedEvidence(
            score=round(score, 2),
            level=level,
            confidence_level=confidence_level,
        )
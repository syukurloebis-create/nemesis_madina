"""
Evidence Score Calculator — Pure Function.
"""

from dataclasses import dataclass

from backend.dtos.collector_dtos import EvidenceCollectorDTO
from backend.calculators.config import EvidenceWeights
from backend.domain.enums import EvidenceLevel


@dataclass(frozen=True, slots=True)
class CalculatedEvidence:
    """Hasil perhitungan dari EvidenceScoreCalculator."""
    score: float          
    trust_score: float    
    confidence_score: float
    verification_score: float
    level: EvidenceLevel


class EvidenceScoreCalculator:
    """Evidence Score Calculator — Pure Function."""

    @classmethod
    def calculate(
        cls,
        dto: EvidenceCollectorDTO,
        weights: EvidenceWeights
    ) -> CalculatedEvidence:
        """Calculate evidence score."""
        if dto.total == 0:
            return CalculatedEvidence(
                score=0,
                level=EvidenceLevel.NO_DATA,
                trust_score=0,
                confidence_score=0,
                verification_score=0
            )

        score = (
            dto.avg_trust * weights.trust_weight +
            dto.avg_confidence * weights.confidence_weight +
            (dto.verified / dto.total * 100) * weights.verification_weight
        )

        if score >= 80:
            level = EvidenceLevel.EXCELLENT
        elif score >= 60:
            level = EvidenceLevel.GOOD
        elif score >= 40:
            level = EvidenceLevel.MEDIUM
        elif score >= 20:
            level = EvidenceLevel.POOR
        else:
            level = EvidenceLevel.NO_DATA

        return CalculatedEvidence(
            score=round(score, 2),
            level=level,
            trust_score=round(dto.avg_trust, 2),           
            confidence_score=round(dto.avg_confidence, 2),
            verification_score=round((dto.verified / dto.total * 100) if dto.total > 0 else 0, 2)
        )
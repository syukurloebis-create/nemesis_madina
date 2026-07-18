"""
Evidence Mapper — HANYA mapping, TIDAK ada perhitungan.
"""

from backend.dtos.collector_dtos import EvidenceCollectorDTO
from backend.calculators.evidence_score_calculator import CalculatedEvidence
from backend.domain.summary_objects import EvidenceSummary
from backend.domain.enums import EngineType


class EvidenceMapper:
    """Evidence Mapper — HANYA mapping."""

    @staticmethod
    def to_summary(
        dto: EvidenceCollectorDTO,
        calculated: CalculatedEvidence
    ) -> EvidenceSummary:
        """Convert DTO + Calculated to EvidenceSummary."""
        return EvidenceSummary(
            score=calculated.score,
            level=calculated.level,
            total=dto.total,
            verified=dto.verified,
            rejected=dto.rejected,
            pending=dto.pending,
            avg_trust=dto.avg_trust,
            avg_confidence=dto.avg_confidence,
            confidence_level="UNKNOWN",
            engine=EngineType.EVIDENCE,
            engine_status=dto.engine_status
        )
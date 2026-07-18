# backend/mappers/risk_mapper.py

"""
Risk Mapper — HANYA mapping, TIDAK ada perhitungan.
"""

from backend.dtos.collector_dtos import RiskCollectorDTO
from backend.calculators.risk_score_calculator import CalculatedRisk
from backend.domain.summary_objects import RiskSummary
from backend.domain.enums import EngineType, EngineStatus
from backend.domain.enums import RiskLevel
# ✅ Import single source of truth
from backend.domain.risk_level_normalizer import normalize_risk_level


class RiskMapper:
    """Risk Mapper — HANYA mapping."""

    def to_summary(
        self,
        dto: RiskCollectorDTO,
        calculated: CalculatedRisk
    ) -> RiskSummary:
        """Convert DTO + Calculated to RiskSummary."""
        status = "SUCCESS" if dto.engine_status == EngineStatus.OK else "FAILED"

        # ✅ Use normalized level from DTO
        # (Already normalized in repository)
        level = normalize_risk_level(dto.level) if dto.level else RiskLevel.UNKNOWN

        return RiskSummary(
            score=calculated.score,
            level=level,
            status=status,
            anomaly_score=calculated.anomaly_score,
            collusion_score=calculated.collusion_score,
            financial_score=calculated.financial_score,
            recommendations=list(dto.recommendations) if dto.recommendations else [],
            engine=EngineType.RISK,
            engine_status=dto.engine_status
        )
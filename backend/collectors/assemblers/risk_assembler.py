"""
Risk Assembler — Row → DTO.
"""

from typing import Tuple, Optional  # ← TAMBAHKAN Optional
from backend.repositories.rows.risk_rows import RiskSummaryRow
from backend.dtos.collector_dtos import RiskCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason


class RiskAssembler:
    """Risk Assembler — Row → DTO."""

    @classmethod
    def assemble(
        cls,
        row: RiskSummaryRow,
        engine_status: EngineStatus = EngineStatus.OK,
        fallback_reason: Optional[FallbackReason] = None,
        error: Optional[str] = None
    ) -> RiskCollectorDTO:
        return RiskCollectorDTO(
            score=row.score,
            level=row.level,
            anomaly_score=row.anomaly_score,
            collusion_score=row.collusion_score,
            financial_score=row.financial_score,
            recommendations=row.recommendations or (),
            engine_status=engine_status,
            fallback_reason=fallback_reason,
            error=error
        )

    @classmethod
    def assemble_empty(cls) -> RiskCollectorDTO:
        return RiskCollectorDTO(
            score=0,
            level="UNKNOWN",
            anomaly_score=0,
            collusion_score=0,
            financial_score=0,
            recommendations=(),
            engine_status=EngineStatus.OK
        )
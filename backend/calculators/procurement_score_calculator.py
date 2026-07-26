"""
Procurement Score Calculator — Pure Business Logic.

ADR-018:
Calculator = ONLY place for business logic.
"""

from dataclasses import dataclass

from backend.dtos.collector_dtos import ProcurementCollectorDTO
from backend.domain.enums import EngineStatus


@dataclass(frozen=True, slots=True)
class CalculatedProcurement:
    """Calculator output for Procurement."""
    risk_score: float
    confidence: float
    engine_status: EngineStatus = EngineStatus.OK


class ProcurementScoreCalculator:
    """
    Procurement Risk Calculator.

    Pure function:
    DTO -> CalculatedProcurement
    """

    @classmethod
    def calculate(
        cls,
        dto: ProcurementCollectorDTO,
    ) -> CalculatedProcurement:
        """Calculate procurement risk from DTO."""

        if dto.packages == 0:
            return CalculatedProcurement(
                risk_score=0.0,
                confidence=0.0,
                engine_status=dto.engine_status,
            )

        # ----------------------------
        # Vendor concentration risk
        # ----------------------------
        vendor_ratio = dto.vendors / dto.packages
        vendor_risk = max(0, min(1, 1 - vendor_ratio))

        # ----------------------------
        # Transaction value risk
        # ----------------------------
        if dto.avg_value <= 0:
            value_risk = 0
        else:
            # Logarithmic normalization
            value_risk = min(1, dto.avg_value / 100_000_000)

        # ----------------------------
        # Instansi concentration risk
        # ----------------------------
        if dto.instansi_count <= 1:
            concentration_risk = 1
        else:
            concentration_risk = 1 / dto.instansi_count

        # ----------------------------
        # Final risk score (0-100)
        # ----------------------------
        risk_score = (
            vendor_risk * 0.35 +
            value_risk * 0.45 +
            concentration_risk * 0.20
        ) * 100

        # ----------------------------
        # Confidence (0-100)
        # ----------------------------
        confidence = min(
            100,
            (min(dto.packages / 100, 1) * 50) +
            (min(dto.vendors / 20, 1) * 30) +
            20
        )

        return CalculatedProcurement(
            risk_score=round(risk_score, 2),
            confidence=round(confidence, 2),
            engine_status=dto.engine_status,
        )

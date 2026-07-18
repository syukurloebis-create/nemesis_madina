"""
Status Calculator — Domain Service.
"""

from enum import Enum
from dataclasses import dataclass

# ✅ PERBAIKAN: Import dari summary_objects
from backend.domain.summary_objects import (
    FraudSummary,
    GraphSummary,
    RiskSummary,
    EvidenceSummary,
    ProcurementSummary
)


class DashboardStatus(str, Enum):
    """Dashboard status enum."""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MINIMAL = "minimal"


@dataclass(frozen=True, slots=True)
class StatusResult:
    """Status calculation result."""
    status: DashboardStatus
    reason: str


class StatusCalculator:
    """Status Calculator — Domain Service."""

    @classmethod
    def calculate(
        cls,
        fraud: FraudSummary,
        graph: GraphSummary,
        risk: RiskSummary,
        evidence: EvidenceSummary,
        procurement: ProcurementSummary
    ) -> StatusResult:
        """Calculate overall status."""
        # Jika fraud atau risk memiliki status FAILED
        if fraud.engine_status == "FAILED" or risk.engine_status == "FAILED":
            return StatusResult(
                status=DashboardStatus.DEGRADED,
                reason="Fraud or Risk engine failed"
            )

        # Jika semua data kosong
        if (fraud.total_patterns == 0 and graph.entities == 0 and 
            evidence.total == 0 and procurement.vendors == 0):
            return StatusResult(
                status=DashboardStatus.MINIMAL,
                reason="No data available"
            )

        # Jika ada data
        return StatusResult(
            status=DashboardStatus.OPERATIONAL,
            reason="All systems operational"
        )
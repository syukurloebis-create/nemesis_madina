"""
NEMESIS Madina - Dashboard Query
✅ Separate read model
✅ Materialized view for performance
"""

from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.risk_assessment import RiskAssessment


# ============================================================================
# QUERY DTO
# ============================================================================

@dataclass(frozen=True)
class GetDashboardQuery:
    """
    CQRS Query object for dashboard retrieval.
    ✅ Immutable query request
    ✅ Pure DTO - no business logic
    """
    case_id: CaseId


# ============================================================================
# READ MODEL
# ============================================================================

@dataclass
class DashboardProjection:
    """Materialized view for dashboard."""
    case_id: CaseId
    status: str
    fraud_score: float
    risk_level: str
    confidence: float
    last_updated: str
    analysis_count: int
    # Denormalized fields for performance
    latest_fraud: Optional[FraudAnalysis]
    latest_risk: Optional[RiskAssessment]
    # Aggregated metrics
    total_events: int
    avg_confidence: float


# ============================================================================
# REPOSITORY INTERFACE
# ============================================================================

class IDashboardReadRepository:
    """Read repository for dashboard projections."""

    async def get_by_case_id(self, case_id: CaseId) -> Optional[DashboardProjection]:
        """Get dashboard by case ID."""
        pass

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[DashboardProjection]:
        """Get all dashboards with pagination."""
        pass

    async def get_high_risk(self, threshold: float) -> List[DashboardProjection]:
        """Get high-risk cases."""
        pass


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "GetDashboardQuery",
    "DashboardProjection",
    "IDashboardReadRepository",
]
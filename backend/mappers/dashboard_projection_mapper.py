# backend/mappers/dashboard_projection_mapper.py

from datetime import datetime
from typing import Optional  
from backend.application.queries.dashboard_query import DashboardProjection
from backend.mappers.projection_mapping_result import ProjectionMappingResult
from backend.domain.summary_objects import FraudSummary, RiskSummary


class DashboardProjectionMapper:
    """Pure transformer: Projection → MappingResult."""

    def map(self, projection: DashboardProjection) -> ProjectionMappingResult:
        return ProjectionMappingResult(
            fraud_summary=self._to_fraud_summary(projection),
            risk_summary=self._to_risk_summary(projection),
            status=projection.status,
            updated_at=self._parse_timestamp(projection.last_updated),
            has_data=projection.analysis_count > 0,
        )

    def _to_fraud_summary(self, projection: DashboardProjection) -> FraudSummary:
        if projection.latest_fraud:
            return FraudSummary(
                score=projection.fraud_score,
                # Map from actual FraudAnalysis fields
            )
        return FraudSummary.empty()

    def _to_risk_summary(self, projection: DashboardProjection) -> RiskSummary:
        if projection.latest_risk:
            return RiskSummary(
                level=projection.risk_level,
                # Map from actual RiskAssessment fields
            )
        return RiskSummary.empty()

    def _parse_timestamp(self, value: str) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
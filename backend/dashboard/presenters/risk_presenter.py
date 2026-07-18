# backend/dashboard/presenters/risk_presenter.py

from backend.dashboard.presenters.base import Presenter
from backend.dashboard.models.risk_response import RiskSummaryResponse
from backend.domain.summary_objects import RiskSummary
from backend.domain.enums import RiskLevel, EngineStatus


class RiskPresenter(Presenter[RiskSummary, RiskSummaryResponse]):
    """Present RiskSummary as API response."""
    
    def present(self, data: RiskSummary) -> RiskSummaryResponse:
        """Convert RiskSummary to RiskSummaryResponse."""
        return RiskSummaryResponse(
            score=data.score,
            level=data.level.value if hasattr(data.level, 'value') else str(data.level),
            status="SUCCESS" if data.engine_status == EngineStatus.OK else "FAILED",
            anomaly_score=data.anomaly_score,
            collusion_score=data.collusion_score,
            financial_score=data.financial_score,
            recommendations=data.recommendations or [],
            engine_status=data.engine_status.value if hasattr(data.engine_status, 'value') else str(data.engine_status),
            has_data=data.has_data
        )
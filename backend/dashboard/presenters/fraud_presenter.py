# backend/dashboard/presenters/fraud_presenter.py

from backend.dashboard.presenters.base import Presenter
from backend.dashboard.models.fraud_response import FraudSummaryResponse, PatternResponse
from backend.domain.summary_objects import FraudSummary
from backend.domain.enums import EngineStatus


class FraudPresenter(Presenter[FraudSummary, FraudSummaryResponse]):
    """Present FraudSummary as API response."""
    
    def present(self, data: FraudSummary) -> FraudSummaryResponse:
        """Convert FraudSummary to FraudSummaryResponse."""
        return FraudSummaryResponse(
            total_patterns=data.total_patterns,
            critical=data.critical,
            high=data.high,
            medium=data.medium,
            low=data.low,
            avg_confidence=data.avg_confidence,
            highest_confidence=data.highest_confidence,
            validated_patterns=data.validated_patterns,
            patterns=[
                PatternResponse(
                    id=p.id,
                    type=p.type,
                    severity=p.severity,
                    confidence=p.confidence,
                    description=p.description
                )
                for p in data.patterns
            ] if hasattr(data, 'patterns') else [],
            engine_status=data.engine_status.value if hasattr(data.engine_status, 'value') else str(data.engine_status),
            has_data=data.has_data
        )
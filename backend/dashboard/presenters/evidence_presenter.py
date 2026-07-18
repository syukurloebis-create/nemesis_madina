# backend/dashboard/presenters/evidence_presenter.py

from backend.dashboard.presenters.base import Presenter
from backend.dashboard.models.evidence_response import EvidenceSummaryResponse
from backend.domain.summary_objects import EvidenceSummary
from backend.domain.enums import EngineStatus


class EvidencePresenter(Presenter[EvidenceSummary, EvidenceSummaryResponse]):
    """Present EvidenceSummary as API response."""
    
    def present(self, data: EvidenceSummary) -> EvidenceSummaryResponse:
        """Convert EvidenceSummary to EvidenceSummaryResponse."""
        return EvidenceSummaryResponse(
            total=data.total,
            verified=data.verified,
            rejected=data.rejected,
            pending=data.pending,
            avg_trust=data.avg_trust,
            avg_confidence=data.avg_confidence,
            engine_status=data.engine_status.value if hasattr(data.engine_status, 'value') else str(data.engine_status),
            has_data=data.has_data
        )
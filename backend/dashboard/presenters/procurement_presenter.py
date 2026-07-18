# backend/dashboard/presenters/procurement_presenter.py

from backend.dashboard.presenters.base import Presenter
from backend.dashboard.models.procurement_response import ProcurementSummaryResponse
from backend.domain.summary_objects import ProcurementSummary
from backend.domain.enums import EngineStatus


class ProcurementPresenter(Presenter[ProcurementSummary, ProcurementSummaryResponse]):
    """Present ProcurementSummary as API response."""
    
    def present(self, data: ProcurementSummary) -> ProcurementSummaryResponse:
        """Convert ProcurementSummary to ProcurementSummaryResponse."""
        return ProcurementSummaryResponse(
            packages=data.packages,
            vendors=data.vendors,
            instansi_count=data.instansi_count,
            avg_value=data.avg_value,
            total_value=data.total_value,
            engine_status=data.engine_status.value if hasattr(data.engine_status, 'value') else str(data.engine_status),
            has_data=data.has_data
        )
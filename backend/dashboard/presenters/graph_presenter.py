# backend/dashboard/presenters/graph_presenter.py

from backend.dashboard.presenters.base import Presenter
from backend.dashboard.models.graph_response import GraphSummaryResponse
from backend.domain.summary_objects import GraphSummary
from backend.domain.enums import EngineStatus


class GraphPresenter(Presenter[GraphSummary, GraphSummaryResponse]):
    """Present GraphSummary as API response."""
    
    def present(self, data: GraphSummary) -> GraphSummaryResponse:
        """Convert GraphSummary to GraphSummaryResponse."""
        return GraphSummaryResponse(
            entities=data.entities,
            relationships=data.relationships,
            engine_status=data.engine_status.value if hasattr(data.engine_status, 'value') else str(data.engine_status),
            has_data=data.has_data
        )
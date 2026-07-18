# backend/dashboard/presenters/dashboard_presenter.py

from backend.dashboard.presenters.base import Presenter
from backend.dashboard.presenters.risk_presenter import RiskPresenter
from backend.dashboard.presenters.fraud_presenter import FraudPresenter
from backend.dashboard.presenters.graph_presenter import GraphPresenter
from backend.dashboard.presenters.evidence_presenter import EvidencePresenter
from backend.dashboard.presenters.procurement_presenter import ProcurementPresenter
from backend.dashboard.models.dashboard_response import (
    DashboardResponse,
    DashboardDataResponse,
    ResponseMeta
)
from backend.dashboard.snapshot import DashboardSnapshot
from backend.dashboard.status import DashboardStatus


class DashboardPresenter(Presenter[DashboardSnapshot, DashboardResponse]):
    """
    Composed Presenter for DashboardSnapshot.
    
    Delegates to specific presenters for each section.
    """
    
    def __init__(
        self,
        risk_presenter: RiskPresenter,
        fraud_presenter: FraudPresenter,
        graph_presenter: GraphPresenter,
        evidence_presenter: EvidencePresenter,
        procurement_presenter: ProcurementPresenter
    ):
        self._risk_presenter = risk_presenter
        self._fraud_presenter = fraud_presenter
        self._graph_presenter = graph_presenter
        self._evidence_presenter = evidence_presenter
        self._procurement_presenter = procurement_presenter
    
    def present(self, snapshot: DashboardSnapshot) -> DashboardResponse:
        """Present DashboardSnapshot as API response."""
        return DashboardResponse(
            data=DashboardDataResponse(
                risk=self._risk_presenter.present(snapshot.risk_summary),
                fraud=self._fraud_presenter.present(snapshot.fraud_summary),
                graph=self._graph_presenter.present(snapshot.graph_summary),
                evidence=self._evidence_presenter.present(snapshot.evidence_summary),
                procurement=self._procurement_presenter.present(snapshot.procurement_summary),
                total_risk_score=snapshot.total_risk_score,
                overall_status=snapshot.overall_status.value if hasattr(snapshot.overall_status, 'value') else str(snapshot.overall_status),
                has_data=snapshot.has_data
            ),
            meta=ResponseMeta(
                status="success" if snapshot.has_data else "empty",
                has_data=snapshot.has_data,
                message="Dashboard data retrieved successfully" if snapshot.has_data else "No data available"
            )
        )
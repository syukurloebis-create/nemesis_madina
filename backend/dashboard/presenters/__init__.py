# backend/dashboard/presenters/__init__.py

from .risk_presenter import RiskPresenter
from .fraud_presenter import FraudPresenter
from .graph_presenter import GraphPresenter
from .evidence_presenter import EvidencePresenter
from .procurement_presenter import ProcurementPresenter
from .dashboard_presenter import DashboardPresenter

__all__ = [
    "RiskPresenter",
    "FraudPresenter",
    "GraphPresenter",
    "EvidencePresenter",
    "ProcurementPresenter",
    "DashboardPresenter",
]
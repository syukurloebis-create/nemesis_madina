# backend/dashboard/models/dashboard_response.py

from pydantic import Field
from typing import Optional
from backend.dashboard.models.base import BaseResponse, ResponseMeta
from backend.dashboard.models.risk_response import RiskSummaryResponse
from backend.dashboard.models.fraud_response import FraudSummaryResponse
from backend.dashboard.models.graph_response import GraphSummaryResponse
from backend.dashboard.models.evidence_response import EvidenceSummaryResponse
from backend.dashboard.models.procurement_response import ProcurementSummaryResponse


class DashboardDataResponse(BaseResponse):
    """Dashboard data API response model."""
    
    risk: RiskSummaryResponse
    fraud: FraudSummaryResponse
    graph: GraphSummaryResponse
    evidence: EvidenceSummaryResponse
    procurement: ProcurementSummaryResponse
    total_risk_score: float = Field(default=0.0)
    overall_status: str = Field(default="UNKNOWN")
    has_data: bool = Field(default=False)


class DashboardResponse(BaseResponse):
    """Full dashboard API response."""
    
    data: DashboardDataResponse
    meta: ResponseMeta
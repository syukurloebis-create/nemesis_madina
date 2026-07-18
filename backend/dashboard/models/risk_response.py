# backend/dashboard/models/risk_response.py

from pydantic import Field
from typing import List
from backend.dashboard.models.base import BaseResponse


class RiskSummaryResponse(BaseResponse):
    """Risk summary API response model."""
    
    score: float = Field(ge=0, le=100, description="Risk score (0-100)")
    level: str = Field(description="Risk level: LOW, MEDIUM, HIGH, CRITICAL, UNKNOWN")
    status: str = Field(description="Execution status: SUCCESS, FAILED")
    anomaly_score: float = Field(ge=0, le=100, default=0)
    collusion_score: float = Field(ge=0, le=100, default=0)
    financial_score: float = Field(ge=0, le=100, default=0)
    recommendations: List[str] = Field(default_factory=list)
    engine_status: str = Field(default="NOT_EXECUTED")
    has_data: bool = Field(default=False)
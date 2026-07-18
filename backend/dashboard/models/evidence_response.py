# backend/dashboard/models/evidence_response.py

from pydantic import Field
from backend.dashboard.models.base import BaseResponse


class EvidenceSummaryResponse(BaseResponse):
    """Evidence summary API response model."""
    
    total: int = Field(default=0)
    verified: int = Field(default=0)
    rejected: int = Field(default=0)
    pending: int = Field(default=0)
    avg_trust: float = Field(default=0.0)
    avg_confidence: float = Field(default=0.0)
    engine_status: str = Field(default="NOT_EXECUTED")
    has_data: bool = Field(default=False)
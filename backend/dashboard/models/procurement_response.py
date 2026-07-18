# backend/dashboard/models/procurement_response.py

from pydantic import Field
from backend.dashboard.models.base import BaseResponse


class ProcurementSummaryResponse(BaseResponse):
    """Procurement summary API response model."""
    
    packages: int = Field(default=0)
    vendors: int = Field(default=0)
    instansi_count: int = Field(default=0)
    avg_value: float = Field(default=0.0)
    total_value: float = Field(default=0.0)
    engine_status: str = Field(default="NOT_EXECUTED")
    has_data: bool = Field(default=False)
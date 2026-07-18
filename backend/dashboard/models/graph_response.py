# backend/dashboard/models/graph_response.py

from pydantic import Field
from backend.dashboard.models.base import BaseResponse


class GraphSummaryResponse(BaseResponse):
    """Graph summary API response model."""
    
    entities: int = Field(default=0)
    relationships: int = Field(default=0)
    engine_status: str = Field(default="NOT_EXECUTED")
    has_data: bool = Field(default=False)
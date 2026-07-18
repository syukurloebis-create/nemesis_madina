# backend/dashboard/models/fraud_response.py

from pydantic import BaseModel, Field
from typing import List, Optional
from backend.dashboard.models.base import BaseResponse


class PatternResponse(BaseResponse):
    """Fraud pattern response."""
    id: str
    type: str
    severity: str
    confidence: float
    description: str
    
    class Config:
        frozen = True


class FraudSummaryResponse(BaseResponse):
    """Fraud summary API response model."""
    
    total_patterns: int = Field(default=0)
    critical: int = Field(default=0)
    high: int = Field(default=0)
    medium: int = Field(default=0)
    low: int = Field(default=0)
    avg_confidence: float = Field(default=0.0)
    highest_confidence: float = Field(default=0.0)
    validated_patterns: int = Field(default=0)
    patterns: List[PatternResponse] = Field(default_factory=list)
    engine_status: str = Field(default="NOT_EXECUTED")
    has_data: bool = Field(default=False)
# backend/mappers/projection_mapping_result.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from backend.domain.summary_objects import FraudSummary, RiskSummary


@dataclass(frozen=True, slots=True)
class ProjectionMappingResult:
    """Result of mapping DashboardProjection to summaries."""
    
    fraud_summary: FraudSummary
    risk_summary: RiskSummary
    status: str
    updated_at: Optional[datetime]
    has_data: bool
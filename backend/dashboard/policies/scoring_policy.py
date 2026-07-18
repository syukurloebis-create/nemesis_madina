# backend/dashboard/policies/scoring_policy.py

from dataclasses import dataclass
from typing import List, Iterable
from backend.domain.summary_objects import (
    RiskSummary,
    FraudSummary,
    GraphSummary,
    EvidenceSummary,
    ProcurementSummary
)
from backend.domain.enums import EngineStatus
from backend.domain.summary_base import BaseSummary


class DashboardScoringPolicy:
    # ...
    
    def has_any_data(self, summaries: Iterable[BaseSummary]) -> bool:
        """Check if any summary has actual data."""
        for summary in summaries:
            if summary.has_data:
                return True
            if hasattr(summary, 'score') and summary.score > 0:
                return True
        return False
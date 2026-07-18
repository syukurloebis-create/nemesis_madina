"""
Dashboard Status Calculator — Pure Business Logic.
"""

from backend.domain.enums import EngineStatus, DashboardStatus
from backend.domain.summary_objects import DashboardSummary


class DashboardStatusCalculator:
    """Pure business logic for dashboard status."""
    
    @classmethod
    def calculate(cls, summary: DashboardSummary) -> DashboardStatus:
        engines = [
            summary.fraud,
            summary.graph,
            summary.risk,
            summary.evidence,
            summary.procurement,
            summary.recovery,
        ]
        
        if any(e.engine_status == EngineStatus.FAILED for e in engines):
            return DashboardStatus.FAILED
        
        if any(e.engine_status == EngineStatus.PARTIAL for e in engines):
            return DashboardStatus.PARTIAL
        
        return DashboardStatus.OK
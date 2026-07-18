"""
Service Interfaces — Protocol untuk Dependency Inversion.
"""

from typing import Protocol, Optional
from uuid import UUID

from backend.core.context import ExecutionContext
from backend.domain.models.case_intelligence import CaseIntelligence


class IDashboardService(Protocol):
    """Dashboard Service Interface — untuk dependency inversion."""
    
    async def get_case_intelligence(
        self,
        case_id: UUID,
        context: Optional[ExecutionContext] = None
    ) -> CaseIntelligence:
        """Get dashboard intelligence for a case."""
        ...
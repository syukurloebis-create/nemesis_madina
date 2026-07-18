"""
NEMESIS Madina - Get Dashboard Query Handler
✅ Query handler with validation
✅ Returns read model
"""

from typing import Optional
from backend.application.queries.dashboard_query import (
    GetDashboardQuery,
    DashboardProjection,
)
from backend.infrastructure.repositories.dashboard_read_repository import (
    DashboardReadRepository,
)
from backend.domain.exceptions import AggregateNotFound


class GetDashboardQueryHandler:
    """Handler for GetDashboardQuery."""
    
    def __init__(self, read_repository: DashboardReadRepository):
        self._read_repo = read_repository
    
    async def handle(self, query: GetDashboardQuery) -> Optional[DashboardProjection]:
        """Handle query."""
        result = await self._read_repo.get_by_case_id(query.case_id)
        if not result:
            raise AggregateNotFound(f"Dashboard not found for {query.case_id}")
        return result
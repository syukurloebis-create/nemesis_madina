"""
Graph Repository Implementation — SQLAlchemy.
"""

from uuid import UUID

from backend.repositories.interfaces.graph_repository import IGraphRepository
from backend.repositories.rows.graph_rows import GraphSummaryRow
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.unit_of_work import IUnitOfWork

import logging
logger = logging.getLogger(__name__)

class GraphRepositoryImpl(IGraphRepository):
    """Graph Repository Implementation — SQLAlchemy."""
    
    def __init__(self, sql_repo: SQLRepository):
        self._sql_repo = sql_repo
    
    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> GraphSummaryRow:
        logger.error("🚨🚨🚨 GraphRepositoryImpl.get_summary() WAS CALLED! 🚨🚨🚨")
        logger.error("🚨 case_id: %s", case_id)
        """Get graph summary — SQL Audit #4.1."""

        logger.info(
            "🔍 GraphRepositoryImpl.get_summary() called for case_id=%s",
            case_id
        )

        row = await self._sql_repo.fetch_one(
            uow,
            SQLKey.GRAPH_SUMMARY,
            case_id=str(case_id)
        )
        
        if not row:
            return GraphSummaryRow()
        
        return GraphSummaryRow(
            entities=row.get("entities", 0),
            relationships=row.get("relationships", 0)
        )
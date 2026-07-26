"""
Graph Repository Implementation — SQLAlchemy.

PHASE 1: Minimalist Compatibility Adapter
"""

from uuid import UUID
from typing import List, Dict, Any
import logging

from backend.repositories.interfaces.graph_repository import IGraphRepository
from backend.repositories.rows.graph_rows import GraphSummaryRow
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.infrastructure.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class GraphRepositoryImpl(IGraphRepository):
    """Graph Repository Implementation — SQLAlchemy."""

    def __init__(self, sql_repo: SQLRepository):
        self._sql_repo = sql_repo

    # ============================================================
    # READ Operations
    # ============================================================

    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> GraphSummaryRow:
        """Get graph summary — SQL Audit #4.1."""
        logger.debug("GraphRepositoryImpl.get_summary() called for case_id=%s", case_id)

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

    async def get_entities(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get graph entities — NOT USED in current startup.
        PHASE 2: Full implementation.
        """
        logger.debug("GraphRepositoryImpl.get_entities() called for case_id=%s", case_id)
        return []

    async def get_relationships(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get graph relationships — NOT USED in current startup.
        PHASE 2: Full implementation.
        """
        logger.debug("GraphRepositoryImpl.get_relationships() called for case_id=%s", case_id)
        return []

    # ============================================================
    # WRITE Operations — Phase 2
    # ============================================================

    async def save_entities(
        self,
        uow: IUnitOfWork,
        entities: List[Dict[str, Any]],
    ) -> None:
        """WRITE — NOT USED in current startup."""
        raise RepositoryError("Graph write repository not implemented in Phase 1")

    async def save_relationships(
        self,
        uow: IUnitOfWork,
        relationships: List[Dict[str, Any]],
    ) -> None:
        """WRITE — NOT USED in current startup."""
        raise RepositoryError("Graph write repository not implemented in Phase 1")

    # ============================================================
    # DELETE Operations — Phase 2
    # ============================================================

    async def clear_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """DELETE — NOT USED in current startup."""
        raise RepositoryError("Graph maintenance repository not implemented in Phase 1")
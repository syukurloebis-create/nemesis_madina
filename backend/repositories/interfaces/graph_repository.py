from abc import ABC, abstractmethod
from uuid import UUID
from typing import Sequence  # ← TAMBAHKAN

from backend.repositories.rows.graph_rows import GraphSummaryRow
from backend.infrastructure.unit_of_work import IUnitOfWork


class IGraphRepository(ABC):
    """Graph Repository Interface."""
    
    @abstractmethod
    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> GraphSummaryRow:
        """Get graph summary (SQL Audit #4.1)."""
        pass
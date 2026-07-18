from abc import ABC, abstractmethod
from uuid import UUID

from backend.repositories.rows.risk_rows import RiskSummaryRow
from backend.infrastructure.unit_of_work import IUnitOfWork


class IRiskRepository(ABC):
    """Risk Repository Interface."""
    
    @abstractmethod
    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> RiskSummaryRow:
        """Get risk summary (SQL Audit #6.1)."""
        pass
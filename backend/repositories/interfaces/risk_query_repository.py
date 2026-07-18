"""
Risk Query Repository — READ only.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from backend.repositories.rows.risk_rows import RiskSummaryRow
from backend.infrastructure.unit_of_work import IUnitOfWork


class IRiskQueryRepository(ABC):
    """Risk Query Repository — READ only."""
    
    @abstractmethod
    async def get_summary(
        self,
        uow: IUnitOfWork,
        case_id: UUID
    ) -> Optional[RiskSummaryRow]:
        """Get risk summary (SQL Audit #6.1)."""
        pass
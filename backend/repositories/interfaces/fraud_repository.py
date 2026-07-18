"""
Fraud Repository Interface — Collector hanya tahu interface ini.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Tuple

from backend.repositories.rows.fraud_rows import FraudSummaryRow, FraudPatternRow
from backend.infrastructure.unit_of_work import IUnitOfWork


class IFraudRepository(ABC):
    """Fraud Repository Interface."""
    
    @abstractmethod
    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> FraudSummaryRow:
        """Get fraud summary."""
        pass
    
    @abstractmethod
    async def get_patterns(self, uow: IUnitOfWork, case_id: UUID) -> Tuple[FraudPatternRow, ...]:
        """Get fraud patterns detail."""
        pass
"""
Procurement Repository Interface — GLOBAL (tidak ada case_id).
"""

from abc import ABC, abstractmethod

from backend.repositories.rows.procurement_rows import ProcurementSummaryRow
from backend.infrastructure.unit_of_work import IUnitOfWork


class IProcurementRepository(ABC):
    """Procurement Repository Interface — GLOBAL."""
    
    @abstractmethod
    async def get_summary(self, uow: IUnitOfWork) -> ProcurementSummaryRow:
        """Get procurement summary (global)."""
        pass
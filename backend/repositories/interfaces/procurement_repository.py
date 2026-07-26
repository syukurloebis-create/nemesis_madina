# backend/repositories/interfaces/procurement_repository.py

from typing import Protocol, Optional, Sequence
from abc import ABC, abstractmethod

from backend.application.dto.investigation_criteria import InvestigationCriteria
from backend.application.dto.procurement_record import ProcurementRecord
from backend.application.dto.search_options import SearchOptions

from backend.repositories.rows.procurement_rows import ProcurementSummaryRow
from backend.infrastructure.unit_of_work import IUnitOfWork


class IProcurementRepository(ABC):
    """Procurement Repository Interface — GLOBAL."""
    
    @abstractmethod
    async def get_summary(self, uow: IUnitOfWork) -> ProcurementSummaryRow:
        """Get procurement summary (global)."""
        pass


class ProcurementRepository(Protocol):
    """Repository protocol for procurement data."""

    async def search(
        self,
        criteria: InvestigationCriteria,
        options: Optional[SearchOptions] = None,
    ) -> Sequence[ProcurementRecord]:
        """Search procurement records by criteria."""
        ...
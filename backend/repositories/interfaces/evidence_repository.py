from abc import ABC, abstractmethod
from uuid import UUID

from backend.repositories.rows.evidence_rows import EvidenceSummaryRow
from backend.infrastructure.unit_of_work import IUnitOfWork


class IEvidenceRepository(ABC):
    """Evidence Repository Interface."""
    
    @abstractmethod
    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> EvidenceSummaryRow:
        """Get evidence summary (SQL Audit #5.1)."""
        pass
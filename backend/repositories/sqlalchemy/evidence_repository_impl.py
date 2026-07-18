"""
Evidence Repository Implementation — SQLAlchemy.
"""

from uuid import UUID

from backend.repositories.interfaces.evidence_repository import IEvidenceRepository
from backend.repositories.rows.evidence_rows import EvidenceSummaryRow
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.unit_of_work import IUnitOfWork


class EvidenceRepositoryImpl(IEvidenceRepository):
    """Evidence Repository Implementation — SQLAlchemy."""
    
    def __init__(self, sql_repo: SQLRepository):
        self._sql_repo = sql_repo
    
    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> EvidenceSummaryRow:
        """Get evidence summary — SQL Audit #5.1."""
        row = await self._sql_repo.fetch_one(
            uow,
            SQLKey.EVIDENCE_SUMMARY,
            case_id=str(case_id)
        )
        
        if not row:
            return EvidenceSummaryRow()
        
        return EvidenceSummaryRow(
            total=row.get("total", 0),
            verified=row.get("verified", 0),
            rejected=row.get("rejected", 0),
            pending=row.get("pending", 0),
            avg_trust=float(row.get("avg_trust", 0) or 0),
            avg_confidence=float(row.get("avg_confidence", 0) or 0)
        )
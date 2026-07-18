"""
Procurement Repository Implementation — SQLAlchemy.
"""

from backend.repositories.interfaces.procurement_repository import IProcurementRepository
from backend.repositories.rows.procurement_rows import ProcurementSummaryRow
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.unit_of_work import IUnitOfWork


class ProcurementRepositoryImpl(IProcurementRepository):
    """Procurement Repository Implementation — SQLAlchemy."""
    
    def __init__(self, sql_repo: SQLRepository):
        self._sql_repo = sql_repo
    
    async def get_summary(self, uow: IUnitOfWork) -> ProcurementSummaryRow:
        """Get procurement summary — SQL Audit #7.1 (Global)."""
        row = await self._sql_repo.fetch_one(
            uow,
            SQLKey.PROCUREMENT_SUMMARY
        )
        
        if not row:
            return ProcurementSummaryRow()
        
        return ProcurementSummaryRow(
            packages=row.get("packages", 0),
            vendors=row.get("vendors", 0),
            instansi_count=row.get("instansi_count", 0),
            avg_value=float(row.get("avg_value", 0) or 0),
            total_value=float(row.get("total_value", 0) or 0)
        )
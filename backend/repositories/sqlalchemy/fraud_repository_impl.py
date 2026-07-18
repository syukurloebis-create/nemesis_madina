"""
Fraud Repository Implementation — SQLAlchemy.

✅ RepositoryError membawa metadata
✅ Exception chaining dengan 'from e'
"""

from uuid import UUID
from typing import Tuple
from sqlalchemy.exc import SQLAlchemyError

from backend.repositories.interfaces.fraud_repository import IFraudRepository
from backend.repositories.rows.fraud_rows import FraudSummaryRow, FraudPatternRow
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.exceptions import RepositoryError
from backend.infrastructure.unit_of_work import IUnitOfWork


class FraudRepositoryImpl(IFraudRepository):
    """Fraud Repository Implementation."""
    
    def __init__(self, sql_repo: SQLRepository):
        self._sql_repo = sql_repo
    
    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> FraudSummaryRow:
        """Get fraud summary."""
        try:
            row = await self._sql_repo.fetch_one(
                uow,
                SQLKey.FRAUD_SUMMARY,
                case_id=case_id
            )
            
            if not row:
                return FraudSummaryRow()
            
            return FraudSummaryRow(
                total_patterns=row.get("total_patterns", 0),
                critical=row.get("critical", 0),
                high=row.get("high", 0),
                medium=row.get("medium", 0),
                low=row.get("low", 0),
                avg_confidence=float(row.get("avg_confidence", 0) or 0),
                highest_confidence=float(row.get("highest_confidence", 0) or 0),
                validated=row.get("validated", 0)
            )
        except SQLAlchemyError as e:
            # ✅ RepositoryError dengan metadata
            raise RepositoryError(
                operation="get_summary",
                repository="FraudRepository",
                case_id=str(case_id),
                original_error=e
            ) from e
    
    async def get_patterns(self, uow: IUnitOfWork, case_id: UUID) -> Tuple[FraudPatternRow, ...]:
        """Get fraud patterns detail."""
        try:
            rows = await self._sql_repo.fetch_all(
                uow,
                SQLKey.FRAUD_PATTERNS,
                case_id=case_id
            )
            
            return tuple(
                FraudPatternRow(
                    pattern_type=row.get("pattern_type", ""),
                    severity=row.get("severity", "UNKNOWN"),
                    confidence_score=float(row.get("confidence_score", 0) or 0),
                    is_validated=row.get("is_validated", False) or False,
                    detected_at=row.get("detected_at")
                )
                for row in rows
            )
        except SQLAlchemyError as e:
            raise RepositoryError(
                operation="get_patterns",
                repository="FraudRepository",
                case_id=str(case_id),
                original_error=e
            ) from e
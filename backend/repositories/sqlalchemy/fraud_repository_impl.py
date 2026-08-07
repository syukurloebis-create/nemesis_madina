# backend/repositories/sqlalchemy/fraud_repository_impl.py
"""
Fraud Repository Implementation — SQLAlchemy.
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

    def _to_int(self, value) -> int:
        """Normalize value to int, handling None and null."""
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def _to_float(self, value) -> float:
        """Normalize value to float, handling None and null."""
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

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
                total_patterns=self._to_int(row.get("total_patterns")),
                critical=self._to_int(row.get("critical")),
                high=self._to_int(row.get("high")),
                medium=self._to_int(row.get("medium")),
                low=self._to_int(row.get("low")),
                avg_confidence=self._to_float(row.get("avg_confidence")),
                highest_confidence=self._to_float(row.get("highest_confidence")),
                validated_patterns=self._to_int(row.get("validated_patterns")),
            )

        except SQLAlchemyError as e:
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
                    confidence_score=self._to_float(row.get("confidence_score")),
                    is_validated=bool(row.get("is_validated", False)),
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
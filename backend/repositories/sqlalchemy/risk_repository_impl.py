# backend/repositories/sqlalchemy/risk_repository_impl.py

from uuid import UUID
from typing import Optional

from backend.repositories.interfaces.risk_repository import IRiskRepository
from backend.repositories.rows.risk_rows import RiskSummaryRow
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.unit_of_work import IUnitOfWork
# ✅ Import single source of truth
from backend.domain.risk_level_normalizer import normalize_risk_level_str


class RiskRepositoryImpl(IRiskRepository):
    """Risk Repository Implementation — SQLAlchemy."""

    def __init__(self, sql_repo: SQLRepository):
        self._sql_repo = sql_repo

    async def get_summary(self, uow: IUnitOfWork, case_id: UUID) -> Optional[RiskSummaryRow]:
        """Get risk summary — SQL Audit #6.1."""
        row = await self._sql_repo.fetch_one(
            uow,
            SQLKey.RISK_SUMMARY,
            case_id=str(case_id)  # ✅ Consistent with other repositories
        )

        if not row:
            return None

        # ✅ Normalize level using single source of truth
        level = normalize_risk_level_str(row.get("risk_level", "UNKNOWN"))

        # ✅ Extract recommendations safely
        recommendations = tuple(row.get("recommendations") or ())

        return RiskSummaryRow(
            score=float(row.get("overall_score", 0) or 0),
            level=level,
            anomaly_score=float(row.get("anomaly_score", 0) or 0),
            collusion_score=float(row.get("collusion_score", 0) or 0),
            financial_score=float(row.get("financial_score", 0) or 0),
            recommendations=recommendations,
            calculated_at=row.get("calculated_at"),
        )
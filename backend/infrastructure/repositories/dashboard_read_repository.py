"""
NEMESIS Madina - Dashboard Read Repository
✅ SQLAlchemy read models
✅ Separate from write repository
"""

from typing import Optional, List
from sqlalchemy import select, desc, and_

from backend.application.queries.dashboard_query import (
    DashboardProjection,
    IDashboardReadRepository, 
)
from backend.domain.value_objects.case_id import CaseId
from backend.infrastructure.models.read_models import DashboardView
from sqlalchemy.ext.asyncio import AsyncSession


class DashboardReadRepository(IDashboardReadRepository):
    """Read repository for dashboard using materialized view."""
    
    def __init__(self, session: AsyncSession, projection_name: str):
        self._session = session
    
    async def get_by_case_id(self, case_id: CaseId) -> Optional[DashboardProjection]:
        """Get dashboard by case ID from materialized view."""
        result = await self._session.execute(
            select(DashboardView)
            .where(DashboardView.case_id == str(case_id))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_projection(model)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[DashboardProjection]:
        """Get all dashboards with pagination."""
        result = await self._session.execute(
            select(DashboardView)
            .order_by(desc(DashboardView.last_updated))
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_projection(m) for m in models]
    
    async def get_high_risk(self, threshold: float) -> List[DashboardProjection]:
        """Get high-risk cases."""
        result = await self._session.execute(
            select(DashboardView)
            .where(DashboardView.risk_score >= threshold)
            .order_by(desc(DashboardView.risk_score))
        )
        models = result.scalars().all()
        return [self._to_projection(m) for m in models]
    
    def _to_projection(self, model) -> DashboardProjection:
        """Map model to projection."""
        return DashboardProjection(
            case_id=CaseId(model.case_id),
            status=model.status,
            fraud_score=model.fraud_score,
            risk_level=model.risk_level,
            confidence=model.confidence,
            last_updated=model.last_updated.isoformat(),
            analysis_count=model.analysis_count,
            latest_fraud=model.latest_fraud,
            latest_risk=model.latest_risk,
            total_events=model.total_events,
            avg_confidence=model.avg_confidence,
        )
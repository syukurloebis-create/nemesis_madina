# backend/infrastructure/projections/dashboard_projection.py

"""
NEMESIS Madina - Dashboard Projection
✅ Pure read model updater
✅ No checkpoint management (handled by Rebuilder)
✅ No ordering/sequence (handled by Rebuilder)
✅ No duplicate detection (handled by Rebuilder)
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.domain.events.base import DomainEvent
from backend.domain.events.fraud_events import FraudAnalysisRecorded
from backend.domain.events.risk_events import RiskAssessmentRecorded
from backend.domain.events.evidence_events import EvidenceVerified
from backend.infrastructure.models.read_models import DashboardView

logger = logging.getLogger(__name__)


class DashboardProjection:
    """
    Pure projection for DashboardView read model.
    ✅ ONLY updates read model from events
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def apply(self, event: DomainEvent) -> None:
        """Apply event to read model."""
        if isinstance(event, FraudAnalysisRecorded):
            await self._handle_fraud_analysis(event)
            return

        if isinstance(event, RiskAssessmentRecorded):
            await self._handle_risk_assessment(event)
            return

        if isinstance(event, EvidenceVerified):
            await self._handle_evidence_verified(event)
            return

        logger.debug(f"No handler for event type: {type(event).__name__}")

    async def _handle_fraud_analysis(self, event: FraudAnalysisRecorded) -> None:
        """Update dashboard with fraud analysis data."""
        case_id = str(event.case_id)
        analysis = event.analysis

        confidence = analysis.highest_confidence
        if confidence is None:
            confidence = analysis.average_confidence
        if confidence is None:
            confidence = 0.0

        stmt = pg_insert(DashboardView).values(
            case_id=case_id,
            fraud_score=analysis.score,
            confidence=confidence,
            analysis_count=1,
            last_updated=event.occurred_at,
            version=1,
        ).on_conflict_do_update(
            index_elements=['case_id'],
            set_={
                'fraud_score': analysis.score,
                'confidence': confidence,
                'analysis_count': DashboardView.analysis_count + 1,
                'last_updated': event.occurred_at,
                'version': DashboardView.version + 1,
            }
        )
        await self._session.execute(stmt)

    async def _handle_risk_assessment(self, event: RiskAssessmentRecorded) -> None:
        """
        Update dashboard with risk assessment data.
        ✅ Migrated to new contract
        """
        case_id = str(event.case_id)
        assessment = event.assessment

        stmt = pg_insert(DashboardView).values(
            case_id=case_id,
            risk_score=assessment.score,
            risk_level=assessment.level.value if hasattr(assessment.level, 'value') else str(assessment.level),
            last_updated=event.occurred_at,
            version=1,
        ).on_conflict_do_update(
            index_elements=['case_id'],
            set_={
                'risk_score': assessment.score,
                'risk_level': assessment.level.value if hasattr(assessment.level, 'value') else str(assessment.level),
                'last_updated': event.occurred_at,
                'version': DashboardView.version + 1,
            }
        )
        await self._session.execute(stmt)

    async def _handle_evidence_verified(self, event: EvidenceVerified) -> None:
        """
        Evidence handler - not yet migrated.
        Log warning and skip (graceful degradation).
        """
        logger.warning(
            "EvidenceVerified not yet migrated to new contract. "
            "Event ignored for now."
        )

    async def get_by_case_id(self, case_id: str) -> Optional[DashboardView]:
        """Get dashboard view by case_id (read-side API)."""
        result = await self._session.execute(
            select(DashboardView).where(DashboardView.case_id == case_id)
        )
        return result.scalar_one_or_none()
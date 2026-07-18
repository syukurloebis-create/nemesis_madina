"""
NEMESIS Madina - Dashboard Projection
✅ Event-driven projection updates
✅ Idempotent processing
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from sqlalchemy.dialects.postgresql import insert

from backend.domain.events.base import DomainEvent
from backend.domain.events.fraud_events import FraudAnalysisRecorded
from backend.domain.events.risk_events import RiskAssessmentRecorded
from backend.domain.events.evidence_events import EvidenceVerified
from backend.infrastructure.models.read_models import DashboardView


class DashboardProjection:
    """
    Dashboard projection builder.
    ✅ Updates materialized view on events
    ✅ Idempotent using event_id
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._processed_events = set()
    
    async def apply(self, event: DomainEvent) -> None:
        """Apply event with ordering and checkpoint."""
        event_id = str(event.event_id)
        event_sequence = getattr(event, 'sequence', 0)
        aggregate_id = str(event.aggregate_id)
    
        # ✅ Check persistent processed events
        if await self._checkpoint.is_processed(event_id):
            return
    
        # ✅ Check ordering - skip stale events
        last_sequence = await self._get_last_sequence(aggregate_id)
        if event_sequence <= last_sequence:
            logger.warning(f"Skipping stale event {event_id} (seq {event_sequence} <= {last_sequence})")
            return
    
        # Apply event
        handler = self._handlers.get(type(event))
        if handler:
            await handler(event)
        
            # ✅ Mark as processed with checkpoint
            await self._checkpoint.mark_processed(event_id, aggregate_id, event_sequence)
    

    async def _handle_fraud_analysis(self, event: FraudAnalysisRecorded) -> None:
        """Update dashboard with UPSERT."""
        # ✅ UPSERT with ON CONFLICT
        stmt = insert(DashboardView).values(
            case_id=str(event.case_id),
            fraud_score=event.fraud_score,
            confidence=event.confidence,
            analysis_count=1,
            last_updated=event.occurred_at,
            version=1,
        ).on_conflict_do_update(
            index_elements=['case_id'],
            set_={
                'fraud_score': event.fraud_score,
                'confidence': event.confidence,
                'analysis_count': DashboardView.analysis_count + 1,
                'last_updated': event.occurred_at,
                'version': DashboardView.version + 1,
            }
        )
        await self._session.execute(stmt)
        
        # If no row exists, insert
        if result.rowcount == 0:
            await self._session.execute(
                insert(DashboardView).values(
                    case_id=str(event.case_id),
                    fraud_score=event.fraud_score,
                    confidence=event.confidence,
                    analysis_count=1,
                    last_updated=event.occurred_at,
                )
            )
    
    async def _handle_risk_assessment(self, event: RiskAssessmentRecorded) -> None:
        """Update dashboard on risk assessment."""
        await self._session.execute(
            update(DashboardView)
            .where(DashboardView.case_id == str(event.case_id))
            .values(
                risk_level=event.risk_level,
                risk_score=event.risk_score,
                last_updated=event.occurred_at,
            )
        )
    
    async def _handle_evidence_verified(self, event: EvidenceVerified) -> None:
        """Update dashboard on evidence verification."""
        await self._session.execute(
            update(DashboardView)
            .where(DashboardView.case_id == str(event.case_id))
            .values(
                evidence_count=DashboardView.evidence_count + 1,
                last_updated=event.occurred_at,
            )
        )
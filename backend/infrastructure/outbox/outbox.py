"""
Outbox Repository — SQLAlchemy Implementation
✅ Atomic claim with CTE + UPDATE RETURNING
✅ processed_at only set on COMPLETED/FAILED
✅ Unique constraint on event_id prevents duplicates
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.events.base import DomainEvent
from backend.infrastructure.models.outbox import OutboxModel, OutboxStatus
from backend.infrastructure.mappers.outbox_mapper import OutboxMapper, InvalidAggregateIdError


class OutboxRepository:
    def __init__(self, session: AsyncSession, mapper: Optional[OutboxMapper] = None):
        self._session = session
        self._mapper = mapper or OutboxMapper()

    async def save(self, event: DomainEvent) -> None:
        """Save outbox message from DomainEvent."""
        try:
            model = self._mapper.to_model(event)
            self._session.add(model)
        except InvalidAggregateIdError:
            # Re-raise with context
            raise
        except IntegrityError as e:
            # Unique constraint violation on event_id
            if "uq_outbox_event_id" in str(e):
                # Event already saved — idempotent
                return
            raise

    async def save_many(self, events: List[DomainEvent]) -> None:
        for event in events:
            await self.save(event)

    async def claim_pending(self, limit: int = 100) -> List[OutboxModel]:
        """
        Atomically claim pending messages for processing.

        ✅ Single SQL statement using CTE with UPDATE ... RETURNING
        ✅ processed_at remains NULL (message not yet processed)
        """
        cte = (
            select(OutboxModel.id)
            .where(OutboxModel.status.in_([OutboxStatus.PENDING, OutboxStatus.RETRY]))
            .order_by(OutboxModel.created_at.asc(), OutboxModel.id.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
            .cte()
        )

        stmt = (
            update(OutboxModel)
            .where(OutboxModel.id.in_(select(cte.c.id)))
            .values(status=OutboxStatus.PROCESSING)
            .returning(OutboxModel)
        )

        result = await self._session.execute(stmt)
        await self._session.flush()
        return list(result.scalars().all())

    async def mark_completed(self, message_id: UUID) -> bool:
        stmt = (
            update(OutboxModel)
            .where(OutboxModel.id == message_id)
            .values(
                status=OutboxStatus.COMPLETED,
                processed_at=datetime.now(timezone.utc),
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def mark_failed(self, message_id: UUID, error: str) -> bool:
        stmt = (
            update(OutboxModel)
            .where(OutboxModel.id == message_id)
            .values(
                status=OutboxStatus.FAILED,
                error_message=error,
                processed_at=datetime.now(timezone.utc),
                retry_count=OutboxModel.retry_count + 1,
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def mark_retry(self, message_id: UUID) -> bool:
        stmt = (
            update(OutboxModel)
            .where(OutboxModel.id == message_id)
            .values(
                status=OutboxStatus.RETRY,
                retry_count=OutboxModel.retry_count + 1,
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # Backward compatibility
    retry = mark_retry

    async def get_pending(self, limit: int = 100) -> List[OutboxModel]:
        stmt = (
            select(OutboxModel)
            .where(OutboxModel.status.in_([OutboxStatus.PENDING, OutboxStatus.RETRY]))
            .order_by(OutboxModel.created_at.asc(), OutboxModel.id.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_pending(self) -> int:
        stmt = (
            select(func.count())
            .select_from(OutboxModel)
            .where(OutboxModel.status.in_([OutboxStatus.PENDING, OutboxStatus.RETRY]))
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def delete_processed(self, older_than_days: int = 7) -> int:
        """Delete COMPLETED messages older than days. FAILED messages are preserved for audit."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        stmt = (
            delete(OutboxModel)
            .where(
                and_(
                    OutboxModel.status == OutboxStatus.COMPLETED,
                    OutboxModel.processed_at < cutoff,
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount

    async def get_by_event_id(self, event_id: UUID) -> Optional[OutboxModel]:
        stmt = select(OutboxModel).where(OutboxModel.event_id == event_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
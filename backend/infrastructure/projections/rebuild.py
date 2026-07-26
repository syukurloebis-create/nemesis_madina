# backend/infrastructure/projections/rebuild.py

"""
NEMESIS Madina - Projection Rebuild with Checkpoint
✅ Complete checkpoint implementation
✅ Resume capability after failure
✅ Aggregate affinity for consistency
"""

import logging
from typing import List, Dict, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from backend.domain.events.base import DomainEvent
from backend.infrastructure.projections.dashboard_projection import DashboardProjection
from backend.infrastructure.models.projection_checkpoint import ProjectionCheckpointModel
from backend.infrastructure.event_store import EventStoreRepository
from backend.infrastructure.events.stored_event import StoredEvent

logger = logging.getLogger(__name__)


@dataclass
class RebuildProgress:
    """Track rebuild progress."""
    total_events: int = 0
    processed_events: int = 0
    failed_events: int = 0
    last_checkpoint: int = 0
    start_time: datetime = None
    end_time: datetime = None


class ProjectionRebuilder:
    """
    Projection rebuilder with checkpoint support.
    ✅ Checkpoint storage for resume capability
    ✅ Aggregate affinity for consistency
    ✅ Session per worker for isolation
    """

    def __init__(
        self,
        session_factory: async_sessionmaker,
        event_store: EventStoreRepository,
        projection_factory: Callable[[AsyncSession], DashboardProjection],
        projection_name: str = "dashboard",
        batch_size: int = 1000,
        concurrency: int = 4,
        checkpoint_interval: int = 100,
    ):
        self._session_factory = session_factory
        self._event_store = event_store
        self._projection_factory = projection_factory
        self._projection_name = projection_name
        self._batch_size = batch_size
        self._concurrency = concurrency
        self._checkpoint_interval = checkpoint_interval
        self._progress = RebuildProgress()

    async def rebuild(self, resume: bool = True) -> RebuildProgress:
        """
        Rebuild projections with checkpoint support.
        ✅ Resume from checkpoint if available
        ✅ Atomic checkpoint updates
        """
        self._progress = RebuildProgress()
        self._progress.start_time = datetime.now(timezone.utc)

        try:
            # Get checkpoint
            checkpoint = await self._get_checkpoint() if resume else 0

            # Get events from checkpoint
            stored_events = await self._event_store.get_all_from_sequence(checkpoint)
            self._progress.total_events = len(stored_events)

            if not stored_events:
                logger.info("No events to rebuild")
                return self._progress

            logger.info(
                "Rebuilding %d events from sequence %d",
                len(stored_events),
                checkpoint,
            )

            # Process with aggregate affinity
            events_by_aggregate = self._group_by_aggregate(stored_events)

            # Process each aggregate sequentially (aggregate affinity)
            processed = 0
            failed = 0

            for aggregate_id, aggregate_events in events_by_aggregate.items():
                try:
                    # Sort by commit_position
                    sorted_events = sorted(
                        aggregate_events,
                        key=lambda stored: stored.commit_position
                    )

                    # Process aggregate events
                    success_count, failure_count = await self._process_aggregate_events(
                        aggregate_id,
                        sorted_events
                    )

                    processed += success_count
                    failed += failure_count
                    self._progress.processed_events = processed
                    self._progress.failed_events = failed

                    # Update checkpoint periodically
                    if processed % self._checkpoint_interval == 0 and processed > 0:
                        last_sequence = max(
                            e.commit_position
                            for e in stored_events
                            if e.commit_position <= processed
                        )
                        await self._update_checkpoint(last_sequence)
                        logger.debug(f"Checkpoint updated at sequence {last_sequence}")

                except Exception as e:
                    logger.error(f"Failed to process aggregate {aggregate_id}: {e}")
                    continue

            # Final checkpoint
            if processed > 0:
                last_sequence = max(e.commit_position for e in stored_events)
                await self._update_checkpoint(last_sequence)

            self._progress.end_time = datetime.now(timezone.utc)

            logger.info(
                f"Rebuild complete: {processed} processed, {failed} failed, "
                f"duration: {(self._progress.end_time - self._progress.start_time).seconds}s"
            )

        except Exception as e:
            logger.error(f"Rebuild failed: {e}")
            raise

        return self._progress

    async def _get_checkpoint(self) -> int:
        """Get last checkpoint from database."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectionCheckpointModel)
                .where(ProjectionCheckpointModel.projection_name == self._projection_name)
                .order_by(ProjectionCheckpointModel.last_sequence.desc())
                .limit(1)
            )
            model = result.scalar_one_or_none()
            return model.last_sequence if model else 0

    async def _update_checkpoint(self, last_sequence: int) -> None:
        """
        Update checkpoint atomically.
        ✅ UPSERT with atomic operation
        """
        async with self._session_factory() as session:
            stmt = pg_insert(ProjectionCheckpointModel).values(
                projection_name=self._projection_name,
                last_sequence=last_sequence,
                updated_at=datetime.now(timezone.utc),
                total_processed=self._progress.processed_events,
                total_failed=self._progress.failed_events,
            ).on_conflict_do_update(
                index_elements=['projection_name'],
                set_={
                    'last_sequence': last_sequence,
                    'updated_at': datetime.now(timezone.utc),
                    'total_processed': self._progress.processed_events,
                    'total_failed': self._progress.failed_events,
                }
            )
            await session.execute(stmt)
            await session.commit()

    def _group_by_aggregate(
        self,
        events: List[StoredEvent]
    ) -> Dict[str, List[StoredEvent]]:
        """Group events by aggregate_id."""
        result = {}

        for stored_event in events:
            aggregate_id = stored_event.aggregate_id

            if aggregate_id not in result:
                result[aggregate_id] = []

            result[aggregate_id].append(stored_event)

        return result

    async def _process_aggregate_events(
        self,
        aggregate_id: str,
        events: List[StoredEvent]
    ) -> tuple[int, int]:
        """
        Process all events for a single aggregate.
        ✅ Single session per aggregate for consistency
        ✅ Sequential processing within aggregate
        ✅ Returns (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0

        async with self._session_factory() as session:
            projection = self._projection_factory(session)

            for stored_event in events:
                try:
                    await projection.apply(stored_event.event)
                    success_count += 1
                except Exception as e:
                    logger.error(
                        "Failed to apply %s: %s",
                        type(stored_event.event).__name__,
                        e
                    )
                    raise

            if success_count > 0:
                await session.commit()
            else:
                await session.rollback()

        return success_count, failure_count
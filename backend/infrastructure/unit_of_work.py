"""
Infrastructure - Unit of Work Implementation

Implements IUnitOfWork interface.
"""

from typing import Optional, Dict, Any, List, Callable, AsyncContextManager
from contextlib import asynccontextmanager
import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.domain.aggregates.base import AggregateRoot
from backend.domain.events.base import DomainEvent
from backend.domain.repositories.case_repository import ICaseRepository
from backend.graph.infrastructure.interfaces.unit_of_work import IUnitOfWork, IUnitOfWorkFactory
from backend.infrastructure.outbox.outbox import OutboxRepository


class DomainUnitOfWork:
    """
    Domain Unit of Work - Pure DI.
    Digunakan oleh: analysis_mapper, domain layer.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker,
        outbox_repository_factory: Callable[[AsyncSession], OutboxRepository],
        case_repository_factory: Callable[[AsyncSession], ICaseRepository],
    ):
        self._session_factory = session_factory
        self._outbox_factory = outbox_repository_factory
        self._session: Optional[AsyncSession] = None
        self._outbox: Optional[OutboxRepository] = None
        self._case_repo_factory = case_repository_factory
        self._case_repo: Optional[ICaseRepository] = None
        self._tracked: Dict[str, Dict] = {}
        self._collected_events: List[DomainEvent] = []
        self._committed = False
        self._rolled_back = False

    @property
    def cases(self) -> ICaseRepository:
        if self._case_repo is None:
            raise RuntimeError("UnitOfWork not started")
        return self._case_repo

    def track(self, aggregate: AggregateRoot, expected_version: int) -> None:
        self._tracked[str(aggregate.id)] = {
            "aggregate": aggregate,
            "expected_version": expected_version,
        }

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork not started")
        return self._session

    def register_aggregate(
        self,
        aggregate: AggregateRoot,
        expected_version: int = 0,
    ) -> None:
        """
        Register aggregate for persistence.

        Compatibility API for command handlers.
        Internally delegates to the canonical tracking implementation.

        TODO(B2A cleanup):
        Remove track() or register_aggregate() once the UoW contract
        is fully standardized.
        """
        self.track(
            aggregate=aggregate,
            expected_version=expected_version,
        )

    async def commit(self) -> None:
        """Commit all tracked aggregates and outbox events in one transaction."""
        if self._committed or self._rolled_back:
            return

        try:
            # 1. Save aggregates (add to session)
            for key, data in self._tracked.items():
                aggregate = data["aggregate"]
                expected_version = data["expected_version"]
                await self._case_repo.save(aggregate, expected_version)

            # 2. Flush to detect conflicts early (before pulling events)
            await self._session.flush()

            # 3. Collect domain events (only after successful flush)
            for key, data in self._tracked.items():
                aggregate = data["aggregate"]
                if aggregate.has_pending_events():
                    events = aggregate.pull_domain_events()
                    if events:
                        self._collected_events.extend(events)

            # 4. Save outbox events (same transaction)
            if self._collected_events and self._outbox:
                for event in self._collected_events:
                    await self._outbox.save(event)

            # 5. Commit transaction
            await self._session.commit()
            self._committed = True
            self._tracked.clear()
            self._collected_events.clear()

        except Exception:
            await self.rollback()
            raise

    async def rollback(self) -> None:
        """Rollback transaction and clear state."""
        if self._committed or self._rolled_back:
            return
        
        # ✅ Rollback database transaction
        if self._session:
            await self._session.rollback()
        
        self._rolled_back = True
        self._tracked.clear()
        self._collected_events.clear()

    async def __aenter__(self) -> "DomainUnitOfWork":
        self._session = self._session_factory()
        await self._session.__aenter__()
        self._outbox = self._outbox_factory(self._session)
        self._case_repo = self._case_repo_factory(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            if not self._committed and not self._rolled_back:
                await self.commit()
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)


class SessionUnitOfWork(IUnitOfWork):
    """
    Session-based Unit of Work implementation.
    Implements canonical IUnitOfWork interface from graph.infrastructure.interfaces.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._committed = False

    async def commit(self) -> None:
        if not self._committed:
            await self._session.commit()
            self._committed = True

    async def rollback(self) -> None:
        await self._session.rollback()

    async def flush(self) -> None:
        await self._session.flush()

    @property
    def session(self):
        return self._session


class UnitOfWork(DomainUnitOfWork):
    """
    Compatibility wrapper for old contract.
    ✅ Inherits from DomainUnitOfWork
    ✅ Maintains old API
    """
    pass


class UnitOfWorkFactory(IUnitOfWorkFactory):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    @asynccontextmanager
    async def create(self) -> AsyncContextManager[IUnitOfWork]:
        async with self._session_factory() as session:
            uow = SessionUnitOfWork(session)  # ← Renamed
            try:
                yield uow
            # try:
                # yield uow
                # await uow.commit()
            except Exception:
                await uow.rollback()
                raise

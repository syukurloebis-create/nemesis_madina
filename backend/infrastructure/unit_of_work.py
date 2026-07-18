"""
Infrastructure - Unit of Work Implementation

Implements IUnitOfWork interface.
"""

from typing import Optional, Dict, Any, List, Callable
from typing import AsyncContextManager
from abc import ABC, abstractmethod
import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager

from backend.domain.repositories.case_repository import ICaseRepository
from backend.domain.aggregates.base import AggregateRoot
from backend.domain.events.base import DomainEvent
from backend.infrastructure.outbox.outbox import OutboxRepository
from backend.graph.infrastructure.interfaces.unit_of_work import IUnitOfWork


# ============================================================================
# PROTOCOL (Type Hints Only)
# ============================================================================

class IUnitOfWork:
    """
    Unit of Work Protocol.
    ✅ Structural typing - no inheritance required
    ✅ Only defines methods that are actually used
    ✅ Used for type hints only (not runtime checking)
    """
    @property
    def cases(self) -> ICaseRepository:
        ...

    def track(self, aggregate: AggregateRoot, expected_version: int) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...


# ============================================================================
# IMPLEMENTATION
# ============================================================================

class DomainUnitOfWork:
    """
    Domain Unit of Work - Pure DI.
    ✅ All repositories injected directly
    ✅ No registry or service locator
    """

    def __init__(
        self,
        session_factory: async_sessionmaker,
        outbox_repository_factory: Callable[[AsyncSession], OutboxRepository],
        case_repository_factory: Callable[[AsyncSession], ICaseRepository],
    ):
        self._session_factory = session_factory
        self._outbox_factory = outbox_repository_factory
        self._case_repo_factory = case_repository_factory
        self._session: Optional[AsyncSession] = None
        self._outbox: Optional[OutboxRepository] = None
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
        key = str(aggregate.id)
        self._tracked[key] = {
            "aggregate": aggregate,
            "expected_version": expected_version,
        }

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork not started")
        return self._session

    async def commit(self) -> None:
        """Commit all tracked aggregates."""
        for key, data in self._tracked.items():
            aggregate = data["aggregate"]
            expected_version = data["expected_version"]
        
            # ✅ Save aggregate using repository
            await self._case_repo.save(aggregate, expected_version)
    
        await self._session.commit()
        self._committed = True
        self._tracked.clear()

    async def rollback(self) -> None:
        self._tracked.clear()
        self._collected_events.clear()
        self._rolled_back = True

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
            await self.commit()
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)


# ============================================================================
# COMPATIBILITY LAYER (Moved BEFORE Factory)
# ============================================================================

class UnitOfWork(DomainUnitOfWork):
    """
    Compatibility wrapper for old contract.
    ✅ Inherits from DomainUnitOfWork
    ✅ Maintains old API
    """
    pass


class UnitOfWork(IUnitOfWork):
    """
    Unit of Work Implementation.
    
    Manages database transactions.
    Repository uses this for persistence operations.
    Service owns the transaction boundary.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._committed = False
    
    async def commit(self) -> None:
        """Commit transaction."""
        if not self._committed:
            await self._session.commit()
            self._committed = True
    
    async def rollback(self) -> None:
        """Rollback transaction."""
        await self._session.rollback()
    
    async def flush(self) -> None:
        """Flush pending changes."""
        await self._session.flush()
    
    @property
    def session(self) -> AsyncSession:
        """Get session for repository operations."""
        return self._session


class UnitOfWorkFactory:
    """Factory for creating UnitOfWork instances."""
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
    
    @asynccontextmanager
    async def create(self) -> AsyncContextManager[IUnitOfWork]:
        """Create a new Unit of Work context."""
        async with self._session_factory() as session:
            uow = UnitOfWork(session)
            try:
                yield uow
                await uow.commit()
            except Exception:
                await uow.rollback()
                raise



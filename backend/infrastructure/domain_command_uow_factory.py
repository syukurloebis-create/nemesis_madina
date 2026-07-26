# backend/infrastructure/domain_command_uow_factory.py

"""
Domain Command Unit of Work Factory
✅ Separate from Graph Runtime UoW
✅ Used only by CQRS command handlers
"""

from contextlib import asynccontextmanager
from typing import AsyncContextManager, Callable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.infrastructure.unit_of_work import DomainUnitOfWork
from backend.infrastructure.outbox.outbox import OutboxRepository
from backend.domain.repositories.case_repository import ICaseRepository


class DomainCommandUoWFactory:
    def __init__(
        self,
        session_factory: async_sessionmaker,
        outbox_factory: Callable[[AsyncSession], OutboxRepository],
        case_repo_factory: Callable[[AsyncSession], ICaseRepository],
    ):
        self._session_factory = session_factory
        self._outbox_factory = outbox_factory
        self._case_repo_factory = case_repo_factory

    @asynccontextmanager
    async def create(self) -> AsyncContextManager[DomainUnitOfWork]:
        async with DomainUnitOfWork(
            session_factory=self._session_factory,
            outbox_repository_factory=self._outbox_factory,
            case_repository_factory=self._case_repo_factory,
        ) as uow:
            yield uow
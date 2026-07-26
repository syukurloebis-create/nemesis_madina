# backend/infrastructure/outbox/factory.py

"""
Outbox Repository Factory
✅ Reusable factory for OutboxRepository
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.outbox.outbox import OutboxRepository


class OutboxRepositoryFactory:
    def create(self, session: AsyncSession) -> OutboxRepository:
        return OutboxRepository(session)
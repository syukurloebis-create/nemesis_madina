# backend/infrastructure/domain_repository_factory.py

"""
Domain Repository Factory — Separate from Collector RepositoryFactory.
✅ For Domain Aggregates only
✅ Returns factory functions (callable) for DomainUnitOfWork
"""

from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.repositories.case_repository import ICaseRepository
from backend.infrastructure.repositories.case_repository import SQLAlchemyCaseRepository
from backend.infrastructure.mappers.case_mapper import CaseMapper


class DomainRepositoryFactory:
    """Factory for Domain Aggregate repositories."""

    def __init__(self, case_mapper: CaseMapper):
        self._case_mapper = case_mapper

    @property
    def case(self) -> Callable[[AsyncSession], ICaseRepository]:
        """Return factory function for Case repository."""
        def factory(session: AsyncSession) -> ICaseRepository:
            return SQLAlchemyCaseRepository(session, self._case_mapper)
        return factory
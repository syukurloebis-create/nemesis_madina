# backend/infrastructure/repositories/case_repository.py

"""
NEMESIS Madina - Case Repository Implementation
✅ Atomic save with optimistic locking
✅ SQLAlchemy Core for atomic UPDATE
✅ Consistent with Sprint A standards
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func
from sqlalchemy.exc import IntegrityError

from backend.domain.repositories.case_repository import ICaseRepository
from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.value_objects.case_id import CaseId
from backend.infrastructure.mappers.case_mapper import CaseMapper
from backend.cases.models import Case
from backend.domain.exceptions import AggregateNotFound, OptimisticLockException


class SQLAlchemyCaseRepository(ICaseRepository):
    """SQLAlchemy implementation with atomic optimistic locking."""

    def __init__(self, session: AsyncSession, mapper: CaseMapper):
        self._session = session
        self._mapper = mapper

    @staticmethod
    def _validate_pagination(limit: Optional[int], offset: Optional[int]) -> None:
        """Validate pagination parameters (Sprint A standard)."""
        if limit is not None and limit < 0:
            raise ValueError("limit must be >= 0")
        if offset is not None and offset < 0:
            raise ValueError("offset must be >= 0")

    async def save(self, aggregate: CaseIntelligenceAggregate, expected_version: int) -> None:
        """
        Save aggregate atomically with optimistic locking.
        ✅ Single atomic UPDATE with version check
        ✅ SQLAlchemy Core (not raw SQL)
        ✅ Uses single source of truth for update values
        """
        # Check if exists
        existing = await self._session.execute(
            select(Case).where(Case.id == aggregate.case_id.value)
        )
        model = existing.scalar_one_or_none()

        if model:
            # ✅ SQLAlchemy Core update with version check (atomic)
            stmt = (
                update(Case)
                .where(
                    Case.id == aggregate.case_id.value,
                    Case.version == expected_version,
                )
                .values(**self._values_from_aggregate(aggregate))
            )

            result = await self._session.execute(stmt)

            if result.rowcount == 0:
                # Check if record exists (version conflict vs not found)
                current_version = await self._session.execute(
                    select(Case.version).where(Case.id == aggregate.case_id.value)
                )
                version_row = current_version.scalar_one_or_none()
                
                if version_row is None:
                    raise AggregateNotFound(f"Case {aggregate.case_id.value} not found")
                else:
                    raise OptimisticLockException(
                        f"Optimistic lock conflict: expected {expected_version}, "
                        f"actual {version_row}"
                    )

            # Update ORM model state (if UoW requires identity map consistency)
            # Note: This keeps the in-memory model in sync with the database
            self._mapper.update_model(model, aggregate)

        else:
            # Insert new aggregate
            if expected_version != 0:
                raise OptimisticLockException(
                    f"Expected version must be 0 for new aggregate, got {expected_version}"
                )

            model = self._mapper.to_model(aggregate)
            self._session.add(model)

    def _values_from_aggregate(self, aggregate: CaseIntelligenceAggregate) -> dict:
        """Single source of truth for update values."""
        return self._mapper.to_update_values(aggregate)

    async def get(self, case_id: CaseId) -> Optional[CaseIntelligenceAggregate]:
        """Get aggregate by ID."""
        result = await self._session.execute(
            select(Case).where(Case.id == case_id.value)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._mapper.to_aggregate(model)

    async def exists(self, case_id: CaseId) -> bool:
        """Check if aggregate exists."""
        result = await self._session.execute(
            select(Case.id).where(Case.id == case_id.value)
        )
        return result.scalar_one_or_none() is not None

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CaseIntelligenceAggregate]:
        """List aggregates with deterministic pagination."""
        self._validate_pagination(limit, offset)
        
        result = await self._session.execute(
            select(Case)
            .order_by(
                Case.created_at.desc(),
                Case.id,  # ✅ Deterministic tie-breaker
            )
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._mapper.to_aggregate(model) for model in models]

    async def remove(self, aggregate: CaseIntelligenceAggregate) -> None:
        """Remove aggregate from repository."""
        result = await self._session.execute(
            delete(Case).where(Case.id == aggregate.case_id.value)
        )
        if result.rowcount == 0:
            raise AggregateNotFound(f"Case {aggregate.case_id.value} not found")

    async def add(self, aggregate: CaseIntelligenceAggregate) -> None:
        """
        Temporary compatibility adapter.

        Legacy callers may still invoke add(). The canonical persistence
        path is save(aggregate, expected_version).

        TODO(B2A cleanup): Remove after ICaseRepository contract is migrated to save().
        """
        await self.save(
            aggregate=aggregate,
            expected_version=0,
        )
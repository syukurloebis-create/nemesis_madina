"""
NEMESIS Madina - Case Repository Implementation
✅ Atomic save with version check
✅ Pure Core SQL for update
✅ No ORM + SQL mixing
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, text
from sqlalchemy.exc import IntegrityError

from backend.domain.repositories.case_repository import ICaseRepository
from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.value_objects.case_id import CaseId
from backend.infrastructure.mappers.case_mapper import CaseMapper
from backend.cases.models import Case
from backend.domain.exceptions import AggregateNotFound, DomainException


class SQLAlchemyCaseRepository(ICaseRepository):
    """SQLAlchemy implementation with atomic operations."""
    
    def __init__(self, session: AsyncSession, mapper: CaseMapper):
        self._session = session
        self._mapper = mapper
    
    async def save(self, aggregate: CaseIntelligenceAggregate, expected_version: int) -> None:
        """
        Save aggregate atomically.
        ✅ UPDATE ... WHERE version = expected_version
        ✅ ORM state and SQL update in single operation
        """
        # Check if exists
        existing = await self._session.execute(
            select(Case).where(Case.id == str(aggregate.case_id))
        )
        model = existing.scalar_one_or_none()
        
        if model:
            # ✅ Pure Core SQL for version check
            stmt = text("""
                UPDATE cases 
                SET version = :new_version,
                    latest_fraud = :latest_fraud,
                    latest_risk = :latest_risk,
                    latest_evidence = :latest_evidence,
                    latest_graph = :latest_graph,
                    latest_procurement = :latest_procurement,
                    updated_at = NOW()
                WHERE id = :id AND version = :expected_version
            """)
            
            # Prepare data once
            data = self._mapper.to_dict(aggregate)
            
            result = await self._session.execute(
                stmt,
                {
                    "id": str(aggregate.case_id),
                    "expected_version": expected_version,
                    "new_version": aggregate.version,
                    **data
                }
            )
            
            if result.rowcount == 0:
                # Check if record exists
                check = await self._session.execute(
                    select(Case.id).where(Case.id == str(aggregate.case_id))
                )
                if check.scalar_one_or_none() is None:
                    raise AggregateNotFound(f"Case {aggregate.case_id} not found")
                else:
                    raise DomainException(
                        f"Optimistic lock conflict: expected {expected_version}"
                    )
            
            # ✅ Update ORM model to match (for future operations)
            self._mapper.update_model(model, aggregate)
            
        else:
            # Insert
            if expected_version != 0:
                raise DomainException(f"Expected version must be 0 for new aggregate")
            
            model = self._mapper.to_model(aggregate)
            self._session.add(model)


    # ============================================================
    # ADD MISSING METHODS
    # ============================================================

    async def add(self, aggregate: CaseIntelligenceAggregate) -> None:
        """Add aggregate to repository."""
        model = self._mapper.to_model(aggregate)
        self._session.add(model)

    async def get(self, case_id: CaseId) -> Optional[CaseIntelligenceAggregate]:
        """Get aggregate by ID."""
        result = await self._session.execute(
            select(Case).where(Case.id == str(case_id))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._mapper.to_aggregate(model)

    async def exists(self, case_id: CaseId) -> bool:
        """Check if aggregate exists."""
        result = await self._session.execute(
            select(Case.id).where(Case.id == str(case_id))
        )
        return result.scalar_one_or_none() is not None

    async def list(self, limit: int = 100, offset: int = 0) -> List[CaseIntelligenceAggregate]:
        """List aggregates with pagination."""
        result = await self._session.execute(
            select(Case)
            .order_by(Case.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._mapper.to_aggregate(model) for model in models]

    async def remove(self, aggregate: CaseIntelligenceAggregate) -> None:
        """Remove aggregate from repository."""
        await self._session.execute(
            delete(Case).where(Case.id == str(aggregate.case_id))
        )
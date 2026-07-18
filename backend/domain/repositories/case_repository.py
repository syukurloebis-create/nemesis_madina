"""
NEMESIS Madina - Case Repository Interface
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.value_objects.case_id import CaseId


class ICaseRepository(ABC):
    """
    Case Repository Interface.
    ✅ All methods are async (for AsyncSession)
    ✅ Uses CaseId value object, not str
    """

    @abstractmethod
    async def add(self, aggregate: CaseIntelligenceAggregate) -> None:
        """Add aggregate to repository."""
        pass

    @abstractmethod
    async def get(self, case_id: CaseId) -> Optional[CaseIntelligenceAggregate]:
        """Get aggregate by ID."""
        pass

    @abstractmethod
    async def exists(self, case_id: CaseId) -> bool:
        """Check if aggregate exists."""
        pass

    @abstractmethod
    async def list(self, limit: int = 100, offset: int = 0) -> List[CaseIntelligenceAggregate]:
        """List aggregates with pagination."""
        pass

    @abstractmethod
    async def remove(self, aggregate: CaseIntelligenceAggregate) -> None:
        """Remove aggregate from repository."""
        pass
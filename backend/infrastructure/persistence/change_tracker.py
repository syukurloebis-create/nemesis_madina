"""
NEMESIS Madina - Change Tracker
✅ Single dictionary for consistency
✅ No sync issues between maps
"""

from typing import Dict, Any, Optional, Type
from backend.domain.aggregates.base import AggregateRoot


class TrackedAggregate:
    """Single tracked aggregate entry."""
    
    def __init__(self, aggregate: AggregateRoot, expected_version: int, repository_type: Type):
        self.aggregate = aggregate
        self.expected_version = expected_version
        self.repository_type = repository_type
        self.is_new = False
        self.is_dirty = False


class ChangeTracker:
    """
    Change tracker - single source of truth.
    ✅ Single dictionary for all tracked aggregates
    ✅ No sync issues
    """
    
    def __init__(self):
        self._tracked: Dict[str, TrackedAggregate] = {}
    
    def track(self, aggregate: AggregateRoot, expected_version: int, repository_type: Type) -> None:
        """Track aggregate."""
        key = str(aggregate.id)
        self._tracked[key] = TrackedAggregate(
            aggregate=aggregate,
            expected_version=expected_version,
            repository_type=repository_type,
        )
    
    def get_aggregate(self, aggregate_id: str) -> Optional[AggregateRoot]:
        """Get tracked aggregate by ID."""
        tracked = self._tracked.get(aggregate_id)
        return tracked.aggregate if tracked else None
    
    def get_expected_version(self, aggregate_id: str) -> Optional[int]:
        """Get expected version."""
        tracked = self._tracked.get(aggregate_id)
        return tracked.expected_version if tracked else None
    
    def get_repository_type(self, aggregate_id: str) -> Optional[Type]:
        """Get repository type."""
        tracked = self._tracked.get(aggregate_id)
        return tracked.repository_type if tracked else None
    
    def get_tracked_aggregates(self) -> list:
        """Get all tracked aggregates."""
        return [t.aggregate for t in self._tracked.values()]
    
    def is_tracked(self, aggregate_id: str) -> bool:
        return aggregate_id in self._tracked
    
    def clear(self) -> None:
        self._tracked.clear()
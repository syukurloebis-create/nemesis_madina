# backend/dashboard/pipelines/descriptor.py

from dataclasses import dataclass
from typing import Type, Optional, Generic, TypeVar, Callable
from backend.dashboard.builders.dashboard_snapshot_builder import DashboardSnapshotBuilder

T = TypeVar('T')


@dataclass(slots=True, frozen=True)
class PipelineDescriptor(Generic[T]):
    """
    Metadata for pipeline results.
    
    Uses typed Callable for type safety.
    """
    result_type: Type[T]
    setter: Callable[[DashboardSnapshotBuilder, T], DashboardSnapshotBuilder]
    timeout: float = 5.0
    required: bool = True
    display_name: Optional[str] = None
    
    @property
    def title(self) -> str:
        return self.display_name or self.result_type.__name__
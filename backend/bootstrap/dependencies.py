# backend/bootstrap/dependencies.py

from dataclasses import dataclass
from typing import Optional

from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.event_bus import IEventBus
from backend.infrastructure.parallel_executor import ParallelExecutor
from backend.core.version import VersionInfo
from backend.collectors.registry import CollectorRegistry
from backend.factories.case_intelligence_factory import CaseIntelligenceFactory


@dataclass(frozen=True)
class BootstrapContainer:
    """Container for bootstrap dependencies."""
    registry: CollectorRegistry
    uow_factory: UnitOfWorkFactory
    executor: ParallelExecutor
    factory: CaseIntelligenceFactory
    event_bus: Optional[IEventBus] = None
    version: Optional[VersionInfo] = None


# ✅ ADD THIS
@dataclass(frozen=True)
class DashboardDependencies:
    """Dependencies for dashboard service creation."""
    uow_factory: UnitOfWorkFactory
    executor: ParallelExecutor
    event_bus: IEventBus
    registry: CollectorRegistry
    factory: CaseIntelligenceFactory
    version: Optional[VersionInfo] = None
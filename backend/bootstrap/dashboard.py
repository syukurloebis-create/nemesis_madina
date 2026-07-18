# backend/bootstrap/dashboard.py

import logging
from typing import Optional, Dict, Any
from datetime import timedelta

from backend.dashboard.executor.parallel_executor import ParallelExecutor
from backend.dashboard.orchestrators.dashboard_orchestrator import DashboardOrchestrator
from backend.dashboard.aggregators.intelligence_aggregator import IntelligenceAggregator
from backend.dashboard.policies.scoring_policy import DashboardScoringPolicy
from backend.dashboard.presenters import (
    RiskPresenter,
    FraudPresenter,
    GraphPresenter,
    EvidencePresenter,
    ProcurementPresenter,
    DashboardPresenter
)
from backend.dashboard.pipelines.registry import PipelineRegistry
from backend.dashboard.executor.circuit_breaker import CircuitBreakerRegistry
from backend.dashboard.protocols.feature_flags import MemoryFeatureFlagProvider, NoOpFeatureFlagProvider
from backend.dashboard.protocols.metrics import NoOpMetricsRecorder, ConsoleMetricsRecorder
from backend.services.dashboard_intelligence_service import (
    DashboardIntelligenceService,
    DashboardServiceDependencies,
)
from backend.bootstrap.dependencies import BootstrapContainer

logger = logging.getLogger(__name__)


def create_dashboard_service(
    container: BootstrapContainer,
    config: Optional[Dict[str, Any]] = None
) -> DashboardIntelligenceService:
    """
    Factory for DashboardIntelligenceService.
    Uses collector-based architecture (working).
    """
    config = config or {}

    # ✅ Build collector-based dependencies
    service_deps = DashboardServiceDependencies(
        uow_factory=container.uow_factory,
        executor=container.executor,
        registry=container.registry,
        factory=container.factory,
        event_bus=container.event_bus,
        version=container.version,
    )

    return DashboardIntelligenceService(deps=service_deps)


def bootstrap_dashboard(container: BootstrapContainer) -> DashboardIntelligenceService:
    """
    Compatibility wrapper for container_builder.py.
    """
    return create_dashboard_service(container)

"""
Dashboard Intelligence Service — PURE ORCHESTRATOR.

Architecture Decision:
- Service adalah pure orchestrator
- HANYA mengoordinasikan collector melalui registry
- TIDAK ada business logic (pindah ke Factory)
- Menggunakan ParallelExecutor existing
"""

import time
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from dataclasses import dataclass

from backend.core.context import ExecutionContext
from backend.core.version import VersionInfo
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.parallel_executor import ParallelExecutor
from backend.infrastructure.event_bus import IEventBus, DashboardGeneratedEvent
from backend.collectors.registry import CollectorRegistry
from backend.factories.case_intelligence_factory import CaseIntelligenceFactory
from backend.domain.models.case_intelligence import CaseIntelligence
from backend.dashboard.presenters.dashboard_presenter import DashboardPresenter  # ← SINGLE IMPORT
from backend.config.features import FeatureFlags
from backend.adapters.legacy.dashboard_adapter import DashboardLegacyAdapter

# ===== HAPUS UNUSED IMPORTS =====
# from backend.dashboard.models.dashboard_response import DashboardResponse
# from backend.dashboard.pipelines.constants import PipelineName
# from backend.dashboard.protocols.pipeline_context import PipelineContext
# from backend.dashboard.orchestrators.dashboard_orchestrator import DashboardOrchestrator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DashboardServiceDependencies:
    """Dependencies untuk DashboardService."""
    uow_factory: UnitOfWorkFactory
    executor: ParallelExecutor
    registry: CollectorRegistry
    factory: CaseIntelligenceFactory
    event_bus: Optional[IEventBus] = None
    version: Optional[VersionInfo] = None


class DashboardIntelligenceService:
    """Pure orchestration — NO business logic."""

    def __init__(
        self,
        deps: Optional[DashboardServiceDependencies] = None,
        # ===== HAPUS PARAMETER YANG TIDAK DIGUNAKAN =====
        # orchestrator: Optional[DashboardOrchestrator] = None,
        # presenter: Optional[DashboardPresenter] = None,
    ):
        self._deps = deps
        # ===== HAPUS ATRIBUT YANG TIDAK ADA =====
        # self._orchestrator = orchestrator
        # self._presenter = presenter

    async def get_case_intelligence(
        self,
        case_id: UUID,
        context: Optional[ExecutionContext] = None
    ) -> CaseIntelligence:
        """Legacy collector-based implementation."""
    
        if self._deps is None:
            raise RuntimeError("Service not configured for collector mode.")

        start_time = time.time()
        ctx = context or ExecutionContext.create(
            case_id=case_id,
            version=self._deps.version
        )

        logger.info("DashboardService: Starting for case %s", case_id)

        try:
            collectors = self._deps.registry.get_all()
            logger.debug("Got %d collectors: %s", len(collectors), [type(c).__name__ for c in collectors])

            results = await self._deps.executor.execute(
                collectors=collectors,
                uow_factory=self._deps.uow_factory,
                context=ctx
            )

            result = self._deps.factory.create_from_results(
                case_id=case_id,
                results=results,
                context=ctx
            )

            if self._deps.event_bus:
                duration_ms = (time.time() - start_time) * 1000
                await self._deps.event_bus.publish(
                    DashboardGeneratedEvent(
                        case_id=case_id,
                        status=result.status,
                        confidence=result.confidence,
                        duration_ms=round(duration_ms, 2)
                    )
                )

            logger.info(
                "DashboardService: Completed for case %s in %.2fms (status=%s)",
                case_id,
                (time.time() - start_time) * 1000,
                result.status
            )

            return result

        except Exception as e:
            logger.exception("DashboardService: Failed for case %s: %s", case_id, e)
            raise


    async def get_dashboard(self, case_id: str) -> dict:
        """
        ⚠️ DEPRECATED - Delegates to get_case_intelligence().
    
        This method is kept for backward compatibility.
        Use get_case_intelligence() for new code.
        """
        logger.warning(
            "get_dashboard() is deprecated. "
            "Use get_case_intelligence() instead."
        )
    
        intelligence = await self.get_case_intelligence(
            UUID(case_id)
        )
    
        return DashboardPresenter.to_api_response(
            intelligence
        )

        if self._deps is None:
            raise RuntimeError("Service not configured.")

        # 1. Collect via registry (bukan self._collector)
        results = await self._deps.registry.collect(case_id)  # ← FIX

        # 2. Build intelligence via factory (bukan self._factory)
        intelligence = self._deps.factory.create_from_results(  # ← FIX
            case_id=case_id,
            results=results,
            context=self._create_context(),
        )

        # 3. Present (dengan feature flag)
        if FeatureFlags.USE_LEGACY_ADAPTER:
            logger.debug("Using legacy adapter for dashboard response")
            return DashboardLegacyAdapter.to_legacy(intelligence)

        # 4. New presenter (pure serialization)
        logger.debug("Using new presenter for dashboard response")
        return DashboardPresenter.to_api_response(intelligence)

    def _create_context(self) -> ExecutionContext:
        """Create execution context."""
        return ExecutionContext.create(
            version=self._deps.version if self._deps else None
        )
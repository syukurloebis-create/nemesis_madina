"""
Dashboard Intelligence Service — PURE ORCHESTRATOR.

Architecture Decision:
- Service adalah pure orchestrator
- HANYA mengoordinasikan collector melalui registry
- TIDAK ada business logic (pindah ke Factory)
- Menggunakan ParallelExecutor existing
"""

import logging
from types import SimpleNamespace
from typing import List, Dict, Any, Optional
from uuid import UUID
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.context import ExecutionContext
from backend.core.version import VersionInfo
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.parallel_executor import ParallelExecutor, CollectorResultRegistry
from backend.infrastructure.event_bus import IEventBus
from backend.infrastructure.repositories.dashboard_read_repository import DashboardReadRepository
from backend.collectors.registry import CollectorRegistry
from backend.factories.case_intelligence_factory import CaseIntelligenceFactory
from backend.domain.models.case_intelligence import CaseIntelligence
from backend.dashboard.snapshot import DashboardSnapshot
from backend.dashboard.status import DashboardStatus
from backend.dashboard.presenters.dashboard_presenter import DashboardPresenter
from backend.mappers.dashboard_projection_mapper import DashboardProjectionMapper
from backend.application.queries.dashboard_query import CaseId

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
        read_repository: Optional[DashboardReadRepository] = None,
        projection_mapper: Optional[DashboardProjectionMapper] = None,
    ):
        self._deps = deps
        self._read_repository = read_repository
        self._projection_mapper = projection_mapper or DashboardProjectionMapper()
        self._factory = deps.factory if deps else None

    # Update get_case_intelligence to use the new helper
    async def get_case_intelligence(
        self,
        case_id: UUID,
        context: Optional[ExecutionContext] = None,
        session: Optional[AsyncSession] = None,
    ) -> CaseIntelligence:
        """Hybrid: Projection for Fraud/Risk, Collectors for Graph/Evidence/Procurement."""

        if self._read_repository and session:
            try:
                projection = await self._read_repository.get_by_case_id(
                    CaseId(str(case_id)), session
                )
                if projection is not None:
                    logger.info("Using read model for case %s", case_id)

                    # 1. Map projection
                    mapping = self._projection_mapper.map(projection)

                    # 2. Get collector results
                    collector_results = await self._get_collector_results(case_id, context)

                    # 3. Use factory to build complete CaseIntelligence
                    # We need to combine projection data with collector data
                    # Option: Use factory private methods (temporary) or create snapshot

                    # For now, build snapshot manually (will be refactored later)
                    snapshot = DashboardSnapshot(
                        fraud_summary=mapping.fraud_summary,
                        risk_summary=mapping.risk_summary,
                        graph_summary=self._factory._build_graph(collector_results),
                        evidence_summary=self._factory._build_evidence(collector_results),
                        procurement_summary=self._factory._build_procurement(collector_results),
                        total_risk_score=mapping.risk_score or 0.0,
                        overall_status=self._status_from_string(mapping.status),
                        has_data=mapping.has_data,
                    )

                    return self._factory.create_from_snapshot(
                        case_id=case_id,
                        snapshot=snapshot,
                        context=context or ExecutionContext.create(case_id=case_id),
                    )
            except Exception as e:
                logger.error("Projection error for case %s: %s", case_id, e)
                raise  # ✅ Re-raise, don't swallow!

        # ⚠️ Fallback to legacy collectors
        logger.info("Using collector path for case %s", case_id)
        return await self._get_case_intelligence_legacy(case_id, context)


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

        # ✅ Use Pydantic v2 model_dump()
        return intelligence.model_dump()


    async def _run_collector_pipeline(
        self,
        case_id: UUID,
        context: Optional[ExecutionContext] = None,
    ) -> CaseIntelligence:
        """
        Run collector pipeline - single source of truth.

        ✅ Uses factory.create_from_results()
        """
        collector_results = await self._get_collector_results(case_id, context)

        return self._factory.create_from_results(
            case_id=case_id,
            results=collector_results,
            context=context or ExecutionContext.create(case_id=case_id),
        )


    async def _get_collector_results(
        self,
        case_id: UUID,
        context: Optional[ExecutionContext] = None,
    ) -> CollectorResultRegistry:
        """
        Execute all registered collectors in parallel.

        ✅ Uses ParallelExecutor.execute()
        ✅ Returns CollectorResultRegistry
        """
        if not self._deps:
            raise RuntimeError("Dashboard dependencies are not initialized")

        execution_context = context or ExecutionContext.create(case_id=case_id)

        # ✅ Use ParallelExecutor with verified signature
        return await self._deps.executor.execute(
            collectors=self._deps.registry.get_all(),
            uow_factory=self._deps.uow_factory,
            context=execution_context,
        )


        async with self._deps.uow_factory.create() as uow:
            for collector in self._deps.registry.get_all():
                collector_name = collector.__class__.__name__
                key = collector_name.replace("Collector", "").lower()

                try:
                    result = await collector.collect(
                        uow,
                        execution_context,
                    )
                    results[key] = result
                    logger.debug(
                        "Collector completed: %s case=%s",
                        key,
                        case_id,
                    )
                except Exception as exc:
                    logger.exception(
                        "Collector failed: %s case=%s",
                        collector_name,
                        case_id,
                    )
                    results[key] = None

        return results


    async def _get_case_intelligence_legacy(
        self,
        case_id: UUID,
        context: Optional[ExecutionContext] = None,
    ) -> CaseIntelligence:
        """
        Backward-compatibility wrapper for legacy callers.

        This method exists solely to maintain the contract expected by
        the hybrid architecture's fallback path. It delegates to the
        single source of truth: _run_collector_pipeline.
        """
        logger.info("Legacy collector path called for case %s", case_id)
        return await self._run_collector_pipeline(case_id, context)


    def _status_from_string(self, status: str) -> DashboardStatus:
        """Convert string status to DashboardStatus enum."""
        mapping = {
            "active": DashboardStatus.OK,
            "pending": DashboardStatus.PARTIAL,
            "empty": DashboardStatus.EMPTY,
            "error": DashboardStatus.FAILED,
            "unknown": DashboardStatus.UNKNOWN,
            "operational": DashboardStatus.OK,
        }
        return mapping.get(status.lower(), DashboardStatus.UNKNOWN)
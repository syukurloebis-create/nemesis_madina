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
from typing import List, Dict, Any, Optional
from uuid import UUID
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession  

from backend.core.context import ExecutionContext
from backend.core.version import VersionInfo
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.parallel_executor import ParallelExecutor
from backend.infrastructure.event_bus import IEventBus, DashboardGeneratedEvent
from backend.infrastructure.repositories.dashboard_read_repository import DashboardReadRepository
from backend.collectors.registry import CollectorRegistry
from backend.factories.case_intelligence_factory import CaseIntelligenceFactory
from backend.domain.models.case_intelligence import CaseIntelligence
from backend.dashboard.snapshot import DashboardSnapshot
from backend.dashboard.presenters.dashboard_presenter import DashboardPresenter 
from backend.config.features import FeatureFlags
from backend.adapters.legacy.dashboard_adapter import DashboardLegacyAdapter
from backend.mappers.dashboard_projection_mapper import (
    DashboardProjectionMapper,
)
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
                
                    # 1. Map projection → Fraud/Risk
                    mapping = self._projection_mapper.map(projection)
                
                    # 2. Get Graph/Evidence/Procurement from collectors
                    #    Reuses existing CollectorResultRegistry
                    collector_results = await self._get_collector_results(case_id) 
                    graph = self._factory._build_graph(collector_results)
                    evidence = self._factory._build_evidence(collector_results)
                    procurement = self._factory._build_procurement(collector_results)
                
                    # 3. Compose DashboardSnapshot (Service orchestrates)
                    snapshot = DashboardSnapshot(
                        fraud_summary=mapping.fraud_summary,
                        risk_summary=mapping.risk_summary,
                        graph_summary=graph,
                        evidence_summary=evidence,
                        procurement_summary=procurement,
                        total_risk_score=0.0,  # ✅ Factory calculates from summary
                        overall_status=self._status_from_string(mapping.status),
                        has_data=mapping.has_data,
                    )
                
                    return self._deps.factory.create_from_snapshot(
                        case_id=case_id,
                        snapshot=snapshot,
                        context=context or ExecutionContext.create(case_id=case_id),
                    )
            except Exception as e:
                logger.error("Read repository error for case %s: %s", case_id, e)

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
    
        return DashboardPresenter.to_api_response(intelligence)
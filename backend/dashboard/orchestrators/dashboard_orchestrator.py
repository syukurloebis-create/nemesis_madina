# backend/dashboard/orchestrators/dashboard_orchestrator.py

from __future__ import annotations

from typing import Optional, Dict, Any
import logging

from backend.dashboard.protocols.pipeline_context import PipelineContext
from backend.dashboard.pipelines.constants import PipelineName
from backend.dashboard.snapshot import DashboardSnapshot
from backend.dashboard.executor.parallel_executor import ParallelExecutor
from backend.dashboard.events.pipeline_events import EventBus
from backend.dashboard.pipelines.registry import PipelineRegistry
from backend.dashboard.aggregators.intelligence_aggregator import IntelligenceAggregator


class DashboardOrchestrator:
    """
    Pure orchestrator - coordinates planning, execution, aggregation.
    
    Responsibilities:
    1. Receive planning from PipelinePlanner
    2. Execute tasks via ParallelExecutor
    3. Aggregate results via IntelligenceAggregator
    
    This is the ONLY orchestration logic.
    """
    
    def __init__(
        self,
        planner: PipelinePlanner,
        executor: ParallelExecutor,
        aggregator: IntelligenceAggregator
    ):
        self._planner = planner
        self._executor = executor
        self._aggregator = aggregator
    
    async def get_dashboard_snapshot(
        self,
        context: PipelineContext,
        sections: Optional[List[PipelineName]] = None
    ) -> DashboardSnapshot:
        # 1. Plan
        plan = await self._planner.plan(context, sections)
        
        if not plan.tasks:
            return self._aggregator.empty_snapshot()
        
        # 2. Execute (pure execution - no policies)
        results = await self._executor.execute(plan.tasks)
        
        # 3. Aggregate
        return self._aggregator.aggregate_from_dict(
            self._extract_results(results)
        )
    
    def _extract_results(self, results: Dict[str, ExecutionResult]) -> Dict[str, Any]:
        """Extract successful results from execution."""
        return {
            name: result.result
            for name, result in results.items()
            if result.success
        }
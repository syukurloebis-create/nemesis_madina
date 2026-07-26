# tests/unit/dashboard/test_orchestrator.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.dashboard.orchestrators.dashboard_orchestrator import DashboardOrchestrator
from backend.dashboard.orchestrators.pipeline_planner import PipelinePlanner, PipelineExecutionPlan
from backend.dashboard.executor.parallel_executor import ParallelExecutor, ExecutionResult
from backend.dashboard.aggregators.intelligence_aggregator import IntelligenceAggregator
from backend.dashboard.protocols.pipeline_context import PipelineContext


class TestDashboardOrchestrator:
    """Test DashboardOrchestrator."""
    
    @pytest.fixture
    def planner(self):
        planner = MagicMock(spec=PipelinePlanner)
        planner.plan.return_value = PipelineExecutionPlan(
            tasks=(),
            sections=()
        )
        return planner
    
    @pytest.fixture
    def executor(self):
        executor = MagicMock(spec=ParallelExecutor)
        executor.execute.return_value = {}
        return executor
    
    @pytest.fixture
    def aggregator(self):
        aggregator = MagicMock(spec=IntelligenceAggregator)
        aggregator.empty_snapshot.return_value = MagicMock()
        aggregator.aggregate_from_dict.return_value = MagicMock()
        return aggregator
    
    @pytest.fixture
    def orchestrator(self, planner, executor, aggregator):
        return DashboardOrchestrator(planner, executor, aggregator)
    
    @pytest.mark.asyncio
    async def test_orchestrator_returns_empty_snapshot(self, orchestrator, planner):
        """Orchestrator should return empty snapshot when no tasks."""
        context = PipelineContext.from_case("case-123")
        result = await orchestrator.get_dashboard_snapshot(context)
        assert result is not None


# tests/unit/dashboard/test_parallel_executor.py

import asyncio
import pytest
from datetime import timedelta
from backend.dashboard.executor.parallel_executor import ParallelExecutor, ExecutionResult
from backend.dashboard.executor.task_definition import TaskDefinition


class TestParallelExecutor:
    """Test ParallelExecutor."""
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Executor should execute tasks successfully."""
        executor = ParallelExecutor()
        tasks = [
            TaskDefinition(
                name="task1",
                coroutine=asyncio.sleep(0.01, result="done1"),
                timeout=timedelta(seconds=1.0)
            ),
        ]
        results = await executor.execute(tasks)
        assert len(results) == 1
        assert "task1" in results
        result = results["task1"]

        assert result.success is True
        assert result.result == "done1"
        assert result.exception is None
    
    @pytest.mark.asyncio
    async def test_execute_timeout(self):
        """Executor should handle timeouts."""
        executor = ParallelExecutor()
        tasks = [
            TaskDefinition(
                name="slow",
                coroutine=asyncio.sleep(0.5, result="done"),
                timeout=timedelta(milliseconds=100)
            ),
        ]
        results = await executor.execute(tasks)
        assert len(results) == 1

        assert "slow" in results
        result = results["slow"]

        assert result.success is False
        assert result.exception is not None
        assert isinstance(result.exception, TimeoutError)
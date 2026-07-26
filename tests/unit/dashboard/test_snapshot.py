# tests/unit/dashboard/test_snapshot.py

import asyncio  
import pytest
from backend.dashboard.snapshot import DashboardSnapshot
from backend.dashboard.policies.scoring_policy import DashboardScoringPolicy
from backend.dashboard.builders.dashboard_snapshot_builder import DashboardSnapshotBuilder
from backend.dashboard.aggregators.intelligence_aggregator import IntelligenceAggregator
from backend.dashboard.executor.task_definition import TaskDefinition
from backend.dashboard.executor.parallel_executor import ParallelExecutor
from backend.dashboard.protocols.circuit_breaker import MemoryCircuitBreaker, NoOpCircuitBreaker
from backend.domain.summary_objects import (
    RiskSummary,
    FraudSummary,
    GraphSummary,
    EvidenceSummary,
    ProcurementSummary,
)
from backend.domain.enums import RiskLevel, EngineStatus


class TestDashboardSnapshot:
    """Test DashboardSnapshot and related classes."""

    def test_snapshot_empty(self):
        snapshot = DashboardSnapshot.empty()
        assert snapshot.has_data is False
        assert snapshot.overall_status == "EMPTY"

    def test_builder_immutable(self):
        policy = DashboardScoringPolicy()
        builder1 = DashboardSnapshotBuilder(policy)
        builder2 = builder1.with_risk(RiskSummary.empty())

        assert builder1 is not builder2
        assert builder1._risk is None
        assert builder2._risk is not None

    def test_aggregator_aggregate(self):
        policy = DashboardScoringPolicy()
        aggregator = IntelligenceAggregator(policy)

        risk = RiskSummary(score=75.0, level=RiskLevel.HIGH, engine_status=EngineStatus.OK)
        fraud = FraudSummary(score=60.0, engine_status=EngineStatus.OK)
        graph = GraphSummary.empty()
        evidence = EvidenceSummary.empty()
        procurement = ProcurementSummary.empty()

        snapshot = aggregator.aggregate(
            risk=risk,
            fraud=fraud,
            graph=GraphSummary.empty(),
            evidence=EvidenceSummary.empty(),
            procurement=ProcurementSummary.empty(),
        )

        assert snapshot.risk_summary.score == 75.0
        assert snapshot.fraud_summary.score == 60.0
        assert snapshot.has_data is True


class TestParallelExecutor:
    """Test ParallelExecutor."""

    async def test_parallel_execution(self):
        executor = ParallelExecutor()
        tasks = [
            TaskDefinition.create("task1", asyncio.sleep(0.1, result="done1")),
            TaskDefinition.create("task2", asyncio.sleep(0.1, result="done2")),
        ]
        results = await executor.execute(tasks)
        assert results["task1"].success is True
        assert results["task1"].result == "done1"

    async def test_timeout(self):
        executor = ParallelExecutor()
        tasks = [
            TaskDefinition.create(
                "slow",
                asyncio.sleep(0.5, result="done"),
                timeout=0.1
            ),
        ]
        results = await executor.execute(tasks, raise_on_required_error=False)
        assert results["slow"].success is False
        assert "Timeout" in results["slow"].error
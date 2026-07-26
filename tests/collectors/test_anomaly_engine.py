import pytest
from unittest.mock import AsyncMock
from uuid import UUID

from backend.collectors.fraud_collector import FraudCollector
from backend.core.context import ExecutionContext
from backend.repositories.rows.fraud_rows import FraudSummaryRow, FraudPatternRow
from backend.domain.enums import EngineStatus, FallbackReason
from backend.infrastructure.exceptions import RepositoryError


class TestFraudCollector:
    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"

    @pytest.fixture
    def mock_repository(self):
        repo = AsyncMock()
        repo.get_summary.return_value = FraudSummaryRow(
            total_patterns=4,
            critical=1,
            high=2,
            avg_confidence=45.0
        )
        repo.get_patterns.return_value = (
            FraudPatternRow("type1", "HIGH", 80.0, False, None),
            FraudPatternRow("type2", "MEDIUM", 60.0, False, None),
        )
        return repo

    @pytest.fixture
    def mock_uow_factory(self):
        return AsyncMock()

    @pytest.fixture
    def uow(self):  # ← TAMBAHKAN
        """Mock Unit of Work untuk unit test."""
        return AsyncMock()

    @pytest.fixture
    def collector(self, mock_repository, mock_uow_factory):
        return FraudCollector(
            repository=mock_repository,
            uow_factory=mock_uow_factory,
        )

    @pytest.mark.asyncio
    async def test_collect_returns_dto(self, collector, mock_repository, uow):
        context = ExecutionContext.create(UUID(self.CASE_ID))
        result = await collector.collect(uow, context)

        assert result.total_patterns == 4
        assert result.critical == 1
        assert result.high == 2
        assert len(result.patterns) == 2
        assert result.engine_status == EngineStatus.OK

    @pytest.mark.asyncio
    async def test_collect_returns_fallback_on_error(self, collector, mock_repository, uow):
        # ✅ Gunakan RepositoryError, bukan Exception
        mock_repository.get_summary.side_effect = RepositoryError("Database error")
        context = ExecutionContext.create(UUID(self.CASE_ID))
        result = await collector.collect(uow, context)

        assert result.total_patterns == 0
        assert result.engine_status == EngineStatus.FAILED
        assert result.fallback_reason == FallbackReason.QUERY_ERROR
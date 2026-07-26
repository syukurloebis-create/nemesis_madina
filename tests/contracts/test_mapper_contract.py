"""
Mapper Contract Test — Level 4: Mapper == DTO + Calculated.

Memastikan mapper mengembalikan domain object yang valid.
"""

import pytest
from uuid import UUID

from backend.core.context import ExecutionContext
from backend.infrastructure.unit_of_work import UnitOfWork
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.repository_factory import RepositoryFactory
from backend.collectors.fraud_collector import FraudCollector
from backend.calculators.fraud_score_calculator import FraudScoreCalculator
from backend.calculators.config import CalculatorConfig
from backend.mappers.fraud_mapper import FraudMapper


class TestMapperContract:
    """Mapper Contract Test — Level 4."""
    
    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    @pytest.mark.asyncio
    async def test_fraud_mapper_contract(self, db_session, uow_factory):
        """Mapper harus menghasilkan FraudSummary yang valid."""
        sql_repo = SQLRepository().initialize()
        repo_factory = RepositoryFactory(sql_repo)
        repository = repo_factory.fraud()
        collector = FraudCollector(
            repository=repository,
            uow_factory=uow_factory,
        )
        
        context = ExecutionContext.create(UUID(self.CASE_ID))
        
        async with uow_factory.create() as uow:
            dto = await collector.collect(uow, context)
        
        # Calculate
        config = CalculatorConfig.default()
        weights = config.get_fraud_weights()
        calculated = FraudScoreCalculator.calculate(dto, weights)
        
        # Map
        summary = FraudMapper.to_summary(dto, calculated)
        
        # Contract: Summary harus valid
        assert summary.total_patterns > 0
        assert summary.score > 0
        assert summary.overall_risk != "UNKNOWN"
        assert summary.engine_status == "OK"
# tests/contracts/test_collector_contract.py

import pytest

from backend.core.context import ExecutionContext
from uuid import UUID
from backend.domain.enums import EngineStatus


class TestCollectorContract:

    CASE_ID = UUID(
        "446e216d-eb0e-487e-8e6b-ec943468ea20"
    )

    @pytest.mark.asyncio
    async def test_fraud_collector_contract(
        self,
        fraud_collector,
        db_uow_factory,
    ):
        context = ExecutionContext.create(
            self.CASE_ID
        )

        async with db_uow_factory.create() as uow:

            dto = await fraud_collector.collect(
                uow,
                context
            )

        assert dto is not None
        assert dto.engine_status == EngineStatus.OK
        assert dto.total_patterns >= 0
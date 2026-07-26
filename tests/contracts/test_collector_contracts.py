# tests/contracts/test_collector_contracts.py

"""
Collector SQL Parity Test.

Memastikan Collector DTO sama dengan hasil SQL Audit.
"""

import pytest
from uuid import UUID

from backend.core.context import ExecutionContext  # ← Tambahkan import
from backend.domain.enums import EngineStatus
from tests.helpers.sql_audit import SQLAuditHelper


class TestCollectorContract:
    """Collector SQL Parity Tests."""

    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"

    @pytest.mark.asyncio
    async def test_fraud_collector_matches_sql_audit(
        self,
        fraud_collector,
        db_uow_factory,
        db_session,
    ):
        """Fraud collector harus match SQL Audit."""
        case_uuid = UUID(self.CASE_ID)
        context = ExecutionContext.create(case_uuid)

        async with db_uow_factory.create() as uow:
            dto = await fraud_collector.collect(uow, context)

        helper = SQLAuditHelper(db_session)
        expected = await helper.get_fraud_expected(case_uuid)

        assert dto.total_patterns == expected.total_patterns
        assert dto.critical == expected.critical
        assert dto.high == expected.high
        assert dto.engine_status == EngineStatus.OK
# tests/contracts/test_collector_contracts.py

import pytest
from uuid import UUID
from backend.domain.enums import EngineStatus
from tests.helpers.sql_audit import SQLAuditHelper


class TestCollectorContract:
    """Collector Contract — SQL Parity Test."""

    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"

    @pytest.mark.asyncio
    async def test_fraud_collector_matches_sql_audit(self, case_intelligence, db_session):
        fraud = case_intelligence.fraud

        helper = SQLAuditHelper(db_session)
        expected = await helper.get_fraud_expected(UUID(self.CASE_ID))

        assert fraud.total_patterns == expected.total_patterns
        assert fraud.critical == expected.critical
        assert fraud.high == expected.high
        assert fraud.engine_status == EngineStatus.OK
"""
Repository Contract Test — Repository == SQL Audit.

Memastikan repository mengembalikan data yang sama dengan SQL Audit.
"""

import pytest
from uuid import UUID

from backend.repositories.sqlalchemy.fraud_repository_impl import FraudRepositoryImpl
from backend.repositories.sqlalchemy.graph_repository_impl import GraphRepositoryImpl
from backend.repositories.sqlalchemy.risk_repository_impl import RiskRepositoryImpl
from backend.repositories.sqlalchemy.evidence_repository_impl import EvidenceRepositoryImpl
from backend.repositories.sqlalchemy.procurement_repository_impl import ProcurementRepositoryImpl
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.exceptions import SQLExecutionError
from backend.infrastructure.unit_of_work import UnitOfWork
from tests.helpers.sql_audit import SQLAuditHelper


class TestRepositoryContract:
    """Repository Contract Test — Level 2."""
    
    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    @pytest.fixture
    async def uow(self, db_session_factory):
        """Create UnitOfWork for testing."""
        # Simplified UoW for testing
        return UnitOfWork(db_session_factory)
    
    @pytest.mark.asyncio
    async def test_fraud_repository_contract(self, db_session, uow_factory):
        """Repository harus match SQL Audit #3.1."""
        sql_repo = SQLRepository().initialize()
        repo = FraudRepositoryImpl(sql_repo)
        helper = SQLAuditHelper(db_session)
        case_uuid = UUID(self.CASE_ID)
        
        async with uow_factory.create() as uow:
            row = await repo.get_summary(uow, case_uuid)
        
        expected = await helper.get_fraud_expected(case_uuid)
        
        assert row.total_patterns == expected.total_patterns
        assert row.critical == expected.critical
        assert row.high == expected.high
        assert row.avg_confidence == pytest.approx(expected.avg_confidence, 0.1)
    
    @pytest.mark.asyncio
    async def test_procurement_repository_contract(self, db_session, uow_factory):
        """Procurement repository harus konsisten (global)."""
        sql_repo = SQLRepository().initialize()
        repo = ProcurementRepositoryImpl(sql_repo)
        helper = SQLAuditHelper(db_session)
        
        async with uow_factory.create() as uow:
            row = await repo.get_summary(uow)
        
        expected = await helper.get_procurement_expected()
        
        assert row.packages == expected.packages
        assert row.vendors == expected.vendors
        assert row.total_value == pytest.approx(expected.total_value, 0.01)
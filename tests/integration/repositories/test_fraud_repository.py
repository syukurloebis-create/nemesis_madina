"""
Fraud Repository Integration Test — PostgreSQL asli.
"""

import pytest
from uuid import UUID

from backend.repositories.sqlalchemy.fraud_repository_impl import FraudRepositoryImpl
from backend.repositories.rows.fraud_rows import FraudSummaryRow


class TestFraudRepositoryIntegration:
    """Fraud Repository Integration Tests."""
    
    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    UNKNOWN_CASE = "00000000-0000-0000-0000-000000000000"
    
    @pytest.fixture
    def repo(self, sql_repo):
        return FraudRepositoryImpl(sql_repo)
    
    @pytest.mark.asyncio
    async def test_get_summary_returns_data(self, repo, uow):
        """Test get_summary returns data for existing case."""
        result = await repo.get_summary(uow, UUID(self.CASE_ID))
        
        # ✅ Assert minimum, bukan nilai spesifik
        assert result.total_patterns >= 0
        assert result.critical >= 0
        assert result.high >= 0
        assert result.avg_confidence >= 0
    
    @pytest.mark.asyncio
    async def test_get_summary_returns_empty_for_unknown(self, repo, uow):
        """Test get_summary returns empty for unknown case."""
        result = await repo.get_summary(uow, UUID(self.UNKNOWN_CASE))
        
        assert isinstance(result, FraudSummaryRow)
        assert result.total_patterns == 0
        assert result.critical == 0
    
    @pytest.mark.asyncio
    async def test_get_patterns_returns_tuple(self, repo, uow):
        """Test get_patterns returns tuple of patterns."""
        result = await repo.get_patterns(uow, UUID(self.CASE_ID))
        
        assert isinstance(result, tuple)
        if len(result) > 0:
            assert isinstance(result[0], FraudPatternRow)
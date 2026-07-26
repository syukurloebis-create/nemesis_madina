"""
SQL Contract Tests — Column subset + NULLability.
"""

import pytest
from sqlalchemy import text

from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.sql_keys import SQLKey


class TestSQLContract:
    """SQL Contract Tests."""
    
    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    # ✅ Expected columns (minimal set)
    FRAUD_SUMMARY_COLUMNS = {
        "total_patterns", "critical", "high", "medium", "low",
        "avg_confidence", "highest_confidence", "validated"
    }
    
    @pytest.fixture
    def sql_repo(self):
        return SQLRepository().initialize()
    
    @pytest.mark.asyncio
    async def test_fraud_summary_contract(self, sql_repo, db_session):
        """Fraud Summary Contract: column subset + NULLability."""
        sql = sql_repo.load(SQLKey.FRAUD_SUMMARY)
        
        result = await db_session.execute(
            text(sql),
            {"case_id": self.CASE_ID}
        )
        row = result.mappings().first()
        
        # ✅ Contract: All expected columns must exist (subset, not exact match)
        assert self.FRAUD_SUMMARY_COLUMNS.issubset(set(row.keys())), \
            f"Missing columns. Expected {self.FRAUD_SUMMARY_COLUMNS}, got {set(row.keys())}"
        
        # ✅ Contract: Non-NULL columns
        non_null = ["total_patterns", "critical", "high", "medium", "low", "validated"]
        for col in non_null:
            assert row[col] is not None, f"Column {col} should not be NULL"
        
        # ✅ Contract: Types
        assert isinstance(row["total_patterns"], int)
        assert row["avg_confidence"] is None or isinstance(row["avg_confidence"], (int, float))
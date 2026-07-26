"""
End-to-End API Test — Fraud Vertical Slice.

✅ HTTP 200 untuk case valid
✅ Struktur JSON sesuai kontrak
✅ Bagian fraud terisi dari collector
✅ Fallback DTO jika repository error
✅ Collector lain tetap menghasilkan summary kosong
"""

import pytest
from uuid import UUID

from backend.main import app


class TestDashboardIntelligenceAPI:
    """End-to-End API Tests."""
    
    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    UNKNOWN_CASE = "00000000-0000-0000-0000-000000000000"
    
    @pytest.mark.asyncio
    async def test_endpoint_returns_200_for_valid_case(self, client):
        """Test endpoint returns HTTP 200 for valid case."""
        response = await client.get(f"/api/v1/dashboard/intelligence/{self.CASE_ID}")
        
        assert response.status_code == 200
        data = response.json()
        
        # ✅ Struktur JSON sesuai kontrak
        assert "case_id" in data
        assert "fraud" in data
        assert "graph" in data
        assert "risk" in data
        assert "evidence" in data
        assert "procurement" in data
        assert "confidence" in data
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_fraud_section_populated(self, client):
        """Test Fraud section is populated from collector."""
        response = await client.get(f"/api/v1/dashboard/intelligence/{self.CASE_ID}")
        assert response.status_code == 200
        
        data = response.json()
        fraud = data["fraud"]
        
        # ✅ Fraud data dari collector
        assert fraud["total_patterns"] >= 0
        assert fraud["overall_risk"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]
        assert fraud["score"] >= 0
        assert fraud["engine_status"] in ["OK", "FAILED", "PARTIAL", "SKIPPED"]
    
    @pytest.mark.asyncio
    async def test_fallback_on_repository_error(self, client, monkeypatch):
        """Test endpoint returns fallback DTO if repository error."""
        # Simulasikan RepositoryError
        async def mock_get_summary(*args, **kwargs):
            from backend.infrastructure.exceptions import RepositoryError
            raise RepositoryError(
                operation="get_summary",
                repository="FraudRepository",
                case_id=self.CASE_ID
            )
        
        # Patch repository
        from backend.repositories.sqlalchemy.fraud_repository_impl import FraudRepositoryImpl
        monkeypatch.setattr(
            FraudRepositoryImpl,
            "get_summary",
            mock_get_summary
        )
        
        response = await client.get(f"/api/v1/dashboard/intelligence/{self.CASE_ID}")
        
        # ✅ Tetap 200 (partial failure)
        assert response.status_code == 200
        data = response.json()
        
        # ✅ Fraud fallback DTO
        assert data["fraud"]["engine_status"] == "FAILED"
        assert data["fraud"]["total_patterns"] == 0
        assert data["fraud"]["score"] == 0
    
    @pytest.mark.asyncio
    async def test_empty_summary_for_other_collectors(self, client):
        """Test other collectors return empty summary."""
        response = await client.get(f"/api/v1/dashboard/intelligence/{self.CASE_ID}")
        assert response.status_code == 200
        
        data = response.json()
        
        # ✅ Graph, Risk, Evidence, Procurement tetap kosong (Fraud only)
        assert data["graph"]["entities"] == 0
        assert data["graph"]["relationships"] == 0
        assert data["risk"]["score"] == 0
        assert data["evidence"]["total"] == 0
        assert data["procurement"]["vendors"] == 0
    
    @pytest.mark.asyncio
    async def test_endpoint_returns_200_for_unknown_case(self, client):
        """Test endpoint returns HTTP 200 for unknown case."""
        response = await client.get(f"/api/v1/dashboard/intelligence/{self.UNKNOWN_CASE}")
        
        # ✅ Unknown case tetap 200 (bukan 404)
        assert response.status_code == 200
        data = response.json()
        
        # ✅ Fraud empty
        assert data["fraud"]["total_patterns"] == 0
        assert data["fraud"]["overall_risk"] == "UNKNOWN"
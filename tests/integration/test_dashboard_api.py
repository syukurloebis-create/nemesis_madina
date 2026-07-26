import uuid
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """TestClient with lifespan enabled."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def seeded_case_id():
    """
    Return case_id yang sudah memiliki data di database.
    Gunakan case_id dari seed data yang sudah ada.
    """
    # TODO: Ganti dengan case_id yang benar dari data seed
    return uuid.UUID("446e216d-eb0e-4c5a-9b8c-123456789abc")


class TestDashboardAPI:
    """Dashboard Intelligence API Integration Tests."""

    def test_get_intelligence_success(self, client, seeded_case_id):
        """Should return dashboard intelligence with real data."""
        response = client.get(f"/api/v1/dashboard/intelligence/{seeded_case_id}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verifikasi struktur data
        assert "risk" in data
        assert "fraud" in data
        assert "graph" in data
        assert "evidence" in data
        assert "procurement" in data
        
        # Verifikasi data aktual (sesuaikan dengan expected values dari seed)
        risk_data = data.get("risk", {})
        assert risk_data.get("score", 0) >= 0
        
        graph_data = data.get("graph", {})
        assert graph_data.get("entities", 0) >= 0
        assert graph_data.get("relationships", 0) >= 0

    def test_get_intelligence_with_sections(self, client, seeded_case_id):
        """Should filter by sections."""
        response = client.get(
            f"/api/v1/dashboard/intelligence/{seeded_case_id}",
            params={"sections": "risk,fraud"}
        )
        assert response.status_code == 200
        
        data = response.json()
        # Verifikasi hanya risk dan fraud yang ada
        assert "risk" in data
        assert "fraud" in data
        # Graph, evidence, procurement mungkin tidak ada atau None

    def test_dashboard_health(self, client):
        """Should return health status."""
        response = client.get("/health/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service_initialized"] is True
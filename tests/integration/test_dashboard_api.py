"""
Dashboard Intelligence API Integration Tests
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.main import app

CANONICAL_CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"


@pytest.fixture
def client():
    """TestClient with lifespan enabled."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def seeded_case_id():
    """Return canonical case ID from fixture."""
    return uuid.UUID(CANONICAL_CASE_ID)


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test_user",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestDashboardAPI:
    """Dashboard Intelligence API Integration Tests."""

    def test_get_intelligence_success(
        self,
        client,
        seeded_case_id,
        auth_headers,
        test_db,  # ✅ TRIGGERS tenant + user + case seeding
    ):
        """Should return dashboard intelligence with real data."""
        response = client.get(
            f"/api/v1/dashboard/intelligence/{seeded_case_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "risk" in data
        assert "fraud" in data
        assert "graph" in data
        assert "evidence" in data
        assert "procurement" in data

    def test_get_intelligence_with_sections(
        self,
        client,
        seeded_case_id,
        auth_headers,
        test_db,
    ):
        """Should filter by sections."""
        response = client.get(
            f"/api/v1/dashboard/intelligence/{seeded_case_id}",
            params={"sections": "risk,fraud"},
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "risk" in data
        assert "fraud" in data

    def test_dashboard_health(self, client):
        """Should return health status (public endpoint)."""
        response = client.get("/health/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
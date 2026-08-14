# tests/golden/test_dashboard_intelligence.py

import json
import pytest
from pathlib import Path
from typing import Dict, Any

GOLDEN_DIR = Path(__file__).parent / "golden_responses"


class TestGoldenResponse:
    """Golden Response Test - Bandingkan business fields saja."""

    CASE_ID = "446e216d-eb0e-487e-8e6b-ec943468ea20"

    @pytest.mark.golden
    @pytest.mark.asyncio
    async def test_golden_response_business_fields(
        self,
        client,
        test_db,
        test_user,
    ):
        """Golden response test untuk business fields."""

        # Login to get JWT
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "test_user",
                "password": "TestPass123!",
            },
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["access_token"]

        # Request with Authorization header
        response = await client.get(
            f"/api/v1/dashboard/intelligence/{self.CASE_ID}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200, response.text

        data = response.json()
        business_fields = self._extract_business_fields(data)

        golden_file = GOLDEN_DIR / f"{self.CASE_ID}_business.json"

        if golden_file.exists():
            with open(golden_file) as f:
                golden = json.load(f)
            assert business_fields == golden, "Business fields mismatch!"
        else:
            # ✅ Create directory if it doesn't exist
            GOLDEN_DIR.mkdir(parents=True, exist_ok=True)

            with open(golden_file, "w") as f:
                json.dump(business_fields, f, indent=2)
            pytest.skip("Golden response created")

    def _extract_business_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ekstrak business fields saja - tanpa timestamp, metadata, dll."""
        return {
            "fraud": {
                "overall_risk": data["fraud"]["overall_risk"],
                "score": data["fraud"]["score"],
                "total_patterns": data["fraud"]["total_patterns"],
                "active_alerts": data["fraud"]["active_alerts"],
            },
            "graph": {
                "entities": data["graph"]["entities"],
                "relationships": data["graph"]["relationships"],
            },
            "risk": {
                "score": data["risk"]["score"],
                "level": data["risk"]["level"],
                "anomaly_score": data["risk"]["anomaly_score"],
                "collusion_score": data["risk"]["collusion_score"],
                "financial_score": data["risk"]["financial_score"],
            },
            "evidence": {
                "total": data["evidence"]["total"],
                "verified": data["evidence"]["verified"],
                "level": data["evidence"]["level"],
            },
            "procurement": {
                "vendors": data["procurement"]["vendors"],
                "packages": data["procurement"]["packages"],
            },
        }
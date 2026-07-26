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
    async def test_golden_response_business_fields(self, client):
        """Golden response test untuk business fields."""
        response = await client.get(f"/api/v1/dashboard/intelligence/{self.CASE_ID}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Extract business fields (tanpa metadata, timestamp, dll)
        business_fields = self._extract_business_fields(data)
        
        # Load golden response
        golden_file = GOLDEN_DIR / f"{self.CASE_ID}_business.json"
        
        if golden_file.exists():
            with open(golden_file) as f:
                golden = json.load(f)
            
            # Bandingkan business fields
            assert business_fields == golden, "Business fields mismatch!"
        else:
            # Save sebagai golden jika belum ada
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
                "status": data["risk"]["status"],
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
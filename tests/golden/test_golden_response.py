"""
Golden Response Test — 13 Dataset Categories.

Memastikan response API stabil untuk berbagai skenario.
Business fields only, exclude runtime fields.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any
from uuid import UUID

GOLDEN_DIR = Path(__file__).parent / "snapshots"


# 13 dataset categories
GOLDEN_DATASETS = {
    "empty": "00000000-0000-0000-0000-000000000000",
    "small": "11111111-1111-1111-1111-111111111111",
    "medium": "22222222-2222-2222-2222-222222222222",
    "large": "33333333-3333-3333-3333-333333333333",
    "corrupted": "44444444-4444-4444-4444-444444444444",
    "timeout": "55555555-5555-5555-5555-555555555555",
    "partial_collector": "66666666-6666-6666-6666-666666666666",
    "sql_empty": "77777777-7777-7777-7777-777777777777",
    "missing_relation": "88888888-8888-8888-8888-888888888888",
    "extreme": "99999999-9999-9999-9999-999999999999",
    "fraud_only": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "evidence_only": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    "procurement_only": "cccccccc-cccc-cccc-cccc-cccccccccccc",
}


class TestGoldenResponse:
    """Golden Response Test — 13 Dataset Categories."""
    
    @pytest.mark.golden
    @pytest.mark.parametrize("category,case_id", GOLDEN_DATASETS.items())
    @pytest.mark.asyncio
    async def test_golden_response_business_fields(self, client, category, case_id):
        """Golden response test untuk 13 kategori."""
        response = await client.get(f"/api/v1/dashboard/intelligence/{case_id}")
        
        # Empty case: bisa 200 dengan status degraded/minimal
        if category == "empty":
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                data = response.json()
                # Empty case: status minimal atau degraded
                assert data.get("status") in ["minimal", "degraded"]
            return
        
        # Corrupted case: harus handle gracefully
        if category == "corrupted":
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                data = response.json()
                # Harus tetap return struktur yang valid
                assert "fraud" in data
                assert "graph" in data
            return
        
        # Happy path: harus 200
        if category not in ["corrupted", "empty", "timeout"]:
            assert response.status_code == 200
            data = response.json()
            
            # Extract business fields
            business_fields = self._extract_business_fields(data)
            
            # Load/save golden response
            golden_file = GOLDEN_DIR / f"golden_{category}.json"
            
            if golden_file.exists():
                with open(golden_file) as f:
                    golden = json.load(f)
                
                # Bandingkan business fields
                assert business_fields == golden, f"Business fields mismatch for {category}"
            else:
                # Save as golden if not exists
                GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
                with open(golden_file, "w") as f:
                    json.dump(business_fields, f, indent=2)
                pytest.skip(f"Golden response created: {category}")
    
    def _extract_business_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ekstrak business fields — exclude runtime fields."""
        return {
            "fraud": {
                "overall_risk": data.get("fraud", {}).get("overall_risk", "UNKNOWN"),
                "score": data.get("fraud", {}).get("score", 0),
                "total_patterns": data.get("fraud", {}).get("total_patterns", 0),
                "active_alerts": data.get("fraud", {}).get("active_alerts", 0),
            },
            "graph": {
                "entities": data.get("graph", {}).get("entities", 0),
                "relationships": data.get("graph", {}).get("relationships", 0),
            },
            "risk": {
                "score": data.get("risk", {}).get("score", 0),
                "level": data.get("risk", {}).get("level", "UNKNOWN"),
                "status": data.get("risk", {}).get("status", "UNKNOWN"),
            },
            "evidence": {
                "total": data.get("evidence", {}).get("total", 0),
                "verified": data.get("evidence", {}).get("verified", 0),
                "level": data.get("evidence", {}).get("level", "NO_DATA"),
            },
            "procurement": {
                "vendors": data.get("procurement", {}).get("vendors", 0),
                "packages": data.get("procurement", {}).get("packages", 0),
            },
            "status": data.get("status", "unknown"),
            "confidence": data.get("confidence", 0),
        }
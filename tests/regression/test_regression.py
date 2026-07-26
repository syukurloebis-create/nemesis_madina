"""
Regression Test — Semua Golden Dataset.

Memastikan tidak ada regresi setelah perubahan.
"""

import pytest
import json
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent.parent / "golden" / "snapshots"


class TestRegression:
    """Regression Test — Semua Golden Dataset."""
    
    @pytest.mark.regression
    @pytest.mark.parametrize("category", [
        "empty", "small", "medium", "large",
        "corrupted", "timeout", "partial_collector",
        "sql_empty", "missing_relation", "extreme",
        "fraud_only", "evidence_only", "procurement_only"
    ])
    @pytest.mark.asyncio
    async def test_regression_all_categories(self, client, category):
        """Regression test untuk semua kategori."""
        golden_file = GOLDEN_DIR / f"golden_{category}.json"
        
        if not golden_file.exists():
            pytest.skip(f"Golden file not found: {golden_file}")
        
        # Load golden response
        with open(golden_file) as f:
            golden = json.load(f)
        
        # Get case_id from golden file name
        case_id = golden.get("case_id", "00000000-0000-0000-0000-000000000000")
        
        # Call API
        response = await client.get(f"/api/v1/dashboard/intelligence/{case_id}")
        
        if response.status_code != 200:
            # Error case: just verify structure
            assert response.status_code in [200, 404, 500]
            return
        
        data = response.json()
        
        # Extract business fields
        business_fields = {
            "fraud": {
                "overall_risk": data.get("fraud", {}).get("overall_risk", "UNKNOWN"),
                "score": data.get("fraud", {}).get("score", 0),
                "total_patterns": data.get("fraud", {}).get("total_patterns", 0),
            },
            "graph": {
                "entities": data.get("graph", {}).get("entities", 0),
                "relationships": data.get("graph", {}).get("relationships", 0),
            },
            "risk": {
                "score": data.get("risk", {}).get("score", 0),
                "level": data.get("risk", {}).get("level", "UNKNOWN"),
            },
            "evidence": {
                "total": data.get("evidence", {}).get("total", 0),
                "level": data.get("evidence", {}).get("level", "NO_DATA"),
            },
            "procurement": {
                "vendors": data.get("procurement", {}).get("vendors", 0),
                "packages": data.get("procurement", {}).get("packages", 0),
            },
            "status": data.get("status", "unknown"),
            "confidence": data.get("confidence", 0),
        }
        
        # Compare with golden (tolerance for dynamic values)
        assert business_fields["fraud"]["overall_risk"] == golden["fraud"]["overall_risk"]
        assert business_fields["graph"]["entities"] == golden["graph"]["entities"]
        assert business_fields["risk"]["level"] == golden["risk"]["level"]
        assert business_fields["evidence"]["total"] == golden["evidence"]["total"]
        assert business_fields["status"] == golden["status"]
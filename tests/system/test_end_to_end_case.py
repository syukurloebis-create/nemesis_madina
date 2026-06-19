import pytest
import json
from pathlib import Path

@pytest.mark.slow
def test_full_paket_flow(tmp_path, sample_paket_data):
    """Test end-to-end untuk satu paket pengadaan."""
    # 1. Simulate ingestion
    ingested = sample_paket_data
    
    # 2. Simulate normalization
    normalized = {
        **ingested,
        "normalized_title": ingested["title"].lower(),
        "budget_bracket": "medium" if ingested["budget"] < 1000000000 else "high"
    }
    
    # 3. Simulate risk scoring
    from backend.core.scoring.engine import calculate_risk_score
    risk_score = calculate_risk_score(normalized)
    
    # 4. Simulate anomaly detection
    is_anomaly = risk_score > 70
    
    # 5. Simulate graph insertion
    if not is_anomaly:
        edge = {
            "source_id": normalized.get("opd"),
            "target_id": normalized["id"],
            "edge_type": "procures"
        }
        assert edge["source_id"] is not None
    
    # Final assertions
    assert 0 <= risk_score <= 100
    assert isinstance(normalized["budget_bracket"], str)

@pytest.mark.slow
async def test_trust_lineage_verification(sample_rup_payload):
    """Test verifikasi trust lineage untuk paket."""
    # Simulate that paket has been stored
    aggregate_id = sample_rup_payload["aggregate_id"]
    
    # In real test, you would call actual verification
    # For now, we test the structure
    assert aggregate_id.startswith("rup-")
    assert sample_rup_payload["event_type"] == "procurement.created"

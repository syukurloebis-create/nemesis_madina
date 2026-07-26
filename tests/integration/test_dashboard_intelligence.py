"""
Integration Test - Dashboard Intelligence Endpoint.

Verifies that /api/v1/dashboard/intelligence/{case_id}
returns correct data structure and contract.
"""

import pytest
from httpx import AsyncClient
from uuid import UUID


@pytest.mark.asyncio
async def test_dashboard_intelligence_contract(client: AsyncClient, test_db):
    """
    Test contract of dashboard intelligence response.
    
    This test verifies:
    - HTTP 200
    - All required fields present
    - Engine statuses are OK
    - Data types are correct
    - Confidence and status are valid
    """
    case_id = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    response = await client.get(
        f"/api/v1/dashboard/intelligence/{case_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # 1. Contract Validation - All required sections
    required = {"fraud", "graph", "risk", "evidence", "procurement", "confidence", "status"}
    assert required.issubset(data.keys())
    
    # 2. Engine Status - All OK
    assert data["fraud"]["engine_status"] == "OK"
    assert data["graph"]["engine_status"] == "OK"
    assert data["risk"]["engine_status"] == "OK"
    assert data["evidence"]["engine_status"] == "OK"
    assert data["procurement"]["engine_status"] == "OK"
    
    # 3. Data Type Validation
    assert isinstance(data["risk"]["recommendations"], list)
    assert isinstance(data["confidence"], (int, float))
    assert isinstance(data["graph"]["entities"], int)
    assert isinstance(data["graph"]["relationships"], int)
    assert isinstance(data["fraud"]["score"], (int, float))
    assert isinstance(data["evidence"]["score"], (int, float))
    assert isinstance(data["procurement"]["packages"], int)
    
    # 4. Value Validation
    assert data["confidence"] >= 0
    assert data["status"] == "operational"
    assert data["risk"]["score"] >= 0
    assert data["graph"]["entities"] >= 0
    assert data["graph"]["relationships"] >= 0
    
    # 5. Optional: Risk level is one of allowed values
    allowed_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"}
    assert data["risk"]["level"] in allowed_levels


@pytest.mark.asyncio
async def test_dashboard_intelligence_risk_non_default(client: AsyncClient, test_db):
    """
    Test that risk returns actual data when available.
    
    This test verifies that the risk engine is not returning
    default values (0/UNKNOWN) when data exists.
    """
    case_id = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    response = await client.get(
        f"/api/v1/dashboard/intelligence/{case_id}"
    )
    
    data = response.json()
    
    # Risk should have data (not 0/UNKNOWN)
    assert data["risk"]["score"] > 0
    assert data["risk"]["level"] != "UNKNOWN"


@pytest.mark.asyncio
async def test_dashboard_intelligence_engine_consistency(client: AsyncClient, test_db):
    """
    Test that all engines return consistent data types and structure.
    """
    case_id = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    response = await client.get(
        f"/api/v1/dashboard/intelligence/{case_id}"
    )
    
    data = response.json()
    
    # Each engine should have engine_status
    engines = ["fraud", "graph", "risk", "evidence", "procurement"]
    for engine in engines:
        assert "engine_status" in data[engine]
        assert data[engine]["engine_status"] == "OK"
    
    # Graph should have entities and relationships
    assert "entities" in data["graph"]
    assert "relationships" in data["graph"]
    
    # Risk should have score and level
    assert "score" in data["risk"]
    assert "level" in data["risk"]
    
    # Fraud should have overall_risk and score
    assert "overall_risk" in data["fraud"]
    assert "score" in data["fraud"]
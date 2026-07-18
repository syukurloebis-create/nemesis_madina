"""Contract tests for Risk API."""

import pytest
from backend.domain.summary_objects import RiskSummary
from backend.domain.enums import RiskLevel, EngineStatus
from backend.adapters.legacy.risk_adapter import RiskLegacyAdapter


class TestRiskContract:
    """Test Risk API contract."""
    
    def test_risk_response_has_legacy_status(self):
        """Test that RiskSummary includes legacy 'status' field."""
        summary = RiskSummary(
            score=75.0,
            level=RiskLevel.HIGH,
            engine_status=EngineStatus.OK,
        )
        response = RiskLegacyAdapter.to_legacy(summary)
        
        assert "status" in response
        assert response["status"] == "SUCCESS"
    
    def test_risk_response_has_engine_status(self):
        """Test that RiskSummary includes new 'engine_status' field."""
        summary = RiskSummary(
            score=75.0,
            level=RiskLevel.HIGH,
            engine_status=EngineStatus.FAILED,
        )
        response = RiskLegacyAdapter.to_legacy(summary)
        
        assert "engine_status" in response
        assert response["engine_status"] == "FAILED"
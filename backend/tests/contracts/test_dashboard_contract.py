"""Contract tests for Dashboard API."""

import pytest
import json
from datetime import datetime, timezone

from backend.domain.summary_objects import (
    DashboardSummary,
    FraudSummary,
    RiskSummary,
    GraphSummary,
    EvidenceSummary,
    ProcurementSummary,
    RecoverySummary,
)
from backend.domain.enums import (
    Severity,
    EngineStatus,
    RiskLevel,
    DashboardStatus,
    RecoveryState,
)
from backend.adapters.legacy.dashboard_adapter import DashboardLegacyAdapter
from backend.calculators.dashboard_status_calculator import DashboardStatusCalculator


class TestDashboardContract:
    """Test Dashboard API contract."""
    
    def test_dashboard_response_has_required_fields(self):
        """Test that dashboard response has all required fields."""
        summary = self._create_test_summary()
        response = DashboardLegacyAdapter.to_legacy(summary)
        
        required_fields = [
            "case_id",
            "fraud",
            "risk",
            "graph",
            "evidence",
            "procurement",
            "recovery",
            "confidence",
            "status",
            "generated_at",
        ]
        
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
    
    def test_dashboard_status_calculation(self):
        """Test that dashboard status is calculated correctly."""
        # Test 1: All OK
        summary = self._create_test_summary()
        status = DashboardStatusCalculator.calculate(summary)
        assert status == DashboardStatus.OK
        
        # Test 2: One FAILED
        summary = self._create_test_summary(
            risk_status=EngineStatus.FAILED
        )
        status = DashboardStatusCalculator.calculate(summary)
        assert status == DashboardStatus.FAILED
        
        # Test 3: One PARTIAL
        summary = self._create_test_summary(
            graph_status=EngineStatus.PARTIAL
        )
        status = DashboardStatusCalculator.calculate(summary)
        assert status == DashboardStatus.PARTIAL
    
    def test_enum_serialization(self):
        """Test that enums are serialized to strings correctly."""
        summary = self._create_test_summary()
        response = DashboardLegacyAdapter.to_legacy(summary)
        
        # Status should be string, not enum
        assert isinstance(response["status"], str)
        assert response["status"] in ["OK", "PARTIAL", "FAILED"]
        
        # Engine status should be string
        assert isinstance(response["fraud"]["engine_status"], str)
        assert response["fraud"]["engine_status"] in ["OK", "FAILED", "PARTIAL", "SKIPPED"]
        
        # Risk level should be string
        assert isinstance(response["risk"]["level"], str)
        assert response["risk"]["level"] in ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def test_json_serializable(self):
        """Test that response is JSON serializable."""
        summary = self._create_test_summary()
        response = DashboardLegacyAdapter.to_legacy(summary)
        
        # Should not raise
        json_str = json.dumps(response)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["case_id"] == response["case_id"]
    
    def _create_test_summary(
        self,
        risk_status: EngineStatus = EngineStatus.OK,
        graph_status: EngineStatus = EngineStatus.OK,
        evidence_status: EngineStatus = EngineStatus.OK,
        procurement_status: EngineStatus = EngineStatus.OK,
        recovery_status: EngineStatus = EngineStatus.OK,
    ) -> DashboardSummary:
        """Create test DashboardSummary."""
        return DashboardSummary(
            case_id="test-case-123",
            fraud=FraudSummary(
                overall_risk=Severity.LOW,
                score=50.0,
                total_patterns=1,
                patterns=[],
                engine_status=EngineStatus.OK,
            ),
            risk=RiskSummary(
                score=50.0,
                level=RiskLevel.MEDIUM,
                engine_status=risk_status,
            ),
            graph=GraphSummary(
                entities=10,
                relationships=20,
                engine_status=graph_status,
            ),
            evidence=EvidenceSummary(
                total=5,
                verified=3,
                engine_status=evidence_status,
            ),
            procurement=ProcurementSummary(
                packages=100,
                vendors=25,
                engine_status=procurement_status,
            ),
            recovery=RecoverySummary(
                business_state=RecoveryState.READY,
                engine_status=recovery_status,
            ),
            confidence=75.0,
            generated_at=datetime.now(timezone.utc),
        )
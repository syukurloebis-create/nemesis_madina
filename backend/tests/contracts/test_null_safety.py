# tests/contracts/test_null_safety.py

import inspect
from typing import Optional
from backend.dtos.collector_dtos import (
    RiskCollectorDTO,
    FraudCollectorDTO,
    GraphCollectorDTO,
    EvidenceCollectorDTO,
    ProcurementCollectorDTO
)

class TestNullSafety:
    """Test bahwa business fields tidak menggunakan Optional."""

    def test_risk_collector_business_fields_not_optional(self):
        """RiskCollectorDTO business fields must not be Optional."""
        dto = RiskCollectorDTO
        for field_name in ['score', 'level', 'anomaly_score', 'collusion_score', 'financial_score']:
            field_type = dto.__annotations__.get(field_name)
            # Check if Optional
            if hasattr(field_type, '__origin__'):
                assert field_type.__origin__ is not Optional, \
                    f"Field '{field_name}' should not be Optional"

    def test_fraud_collector_business_fields_not_optional(self):
        """FraudCollectorDTO business fields must not be Optional."""
        dto = FraudCollectorDTO
        for field_name in ['total_patterns', 'critical', 'high', 'medium', 'low', 
                          'avg_confidence', 'highest_confidence', 'validated_patterns']:
            field_type = dto.__annotations__.get(field_name)
            if hasattr(field_type, '__origin__'):
                assert field_type.__origin__ is not Optional, \
                    f"Field '{field_name}' should not be Optional"
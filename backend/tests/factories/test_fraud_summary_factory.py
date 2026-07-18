"""
Unit tests for FraudSummaryFactory (factories/fraud_summary_factory.py)
"""

import pytest
from datetime import datetime, timezone

from backend.dtos.collector_dtos import FraudCollectorDTO, PatternDTO
from backend.calculators.fraud_score_calculator import CalculatedFraud
from backend.factories.fraud_summary_factory import FraudSummaryFactory
from backend.domain.enums import Severity, EngineStatus
from backend.domain.summary_objects import FraudSummary


class TestFraudSummaryFactory:
    """Test FraudSummaryFactory composition."""
    
    def test_create_from_dto_and_calculated(self):
        """Test that Factory correctly composes Summary."""
        # 1. Create DTO
        dto = FraudCollectorDTO(
            total_patterns=3,
            critical=1,
            high=1,
            medium=1,
            low=0,
            avg_confidence=78.5,
            highest_confidence=95.0,
            validated_patterns=2,
            patterns=(
                PatternDTO(
                    pattern_type="price_anomaly",
                    severity=Severity.CRITICAL,
                    confidence=95.0,
                    validated=True,
                    detected_at=datetime.now(timezone.utc),
                ),
                PatternDTO(
                    pattern_type="vendor_collusion",
                    severity=Severity.HIGH,
                    confidence=85.0,
                    validated=True,
                    detected_at=datetime.now(timezone.utc),
                ),
                PatternDTO(
                    pattern_type="duplicate_bid",
                    severity=Severity.MEDIUM,
                    confidence=55.0,
                    validated=False,
                    detected_at=datetime.now(timezone.utc),
                ),
            ),
            engine_status=EngineStatus.OK,
        )
        
        # 2. Create CalculatedFraud
        calculated = CalculatedFraud(
            overall_risk=Severity.CRITICAL,
            score=82.5,
            severity_score=100.0,
            confidence_score=78.5,
            validated_score=66.7,
            pattern_variety_score=75.0,
            active_alerts=2,
            high_confidence=2,
            engine_status=EngineStatus.OK,
        )
        
        # 3. Create Summary
        summary = FraudSummaryFactory.create(
            collector=dto,
            calculation=calculated
        )
        
        # 4. Assertions
        assert summary.overall_risk == Severity.CRITICAL
        assert summary.score == 82.5
        assert summary.total_patterns == 3
        assert summary.active_alerts == 2
        assert summary.high_confidence == 2
        assert len(summary.patterns) == 3
        
        # Pattern transformation
        assert summary.patterns[0].type == "price_anomaly"
        assert summary.patterns[0].severity == Severity.CRITICAL
        assert summary.patterns[0].confidence == 95.0
        
        assert summary.patterns[2].type == "duplicate_bid"
        assert summary.patterns[2].confidence == 55.0
        assert summary.patterns[2].validated is False
    
    def test_create_empty(self):
        """Test create_empty returns valid FraudSummary."""
        summary = FraudSummaryFactory.create_empty()
        
        # Assertions
        assert summary.overall_risk == Severity.UNKNOWN
        assert summary.score == 0.0
        assert summary.total_patterns == 0
        assert len(summary.patterns) == 0
        assert summary.engine_status == EngineStatus.FAILED  
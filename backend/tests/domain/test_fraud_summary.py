"""
Unit tests for FraudSummary (domain/summary_objects.py)
"""

import pytest
from datetime import datetime, timezone

from backend.domain.summary_objects import FraudSummary, FraudPatternSummary
from backend.domain.enums import Severity, EngineStatus


class TestFraudSummary:
    """Test FraudSummary validation and invariants."""
    
    def test_valid_fraud_summary(self):
        """Test that valid FraudSummary passes validation."""
        summary = FraudSummary(
            overall_risk=Severity.HIGH,
            score=75.0,
            total_patterns=5,
            validated_patterns=3,
            highest_confidence=95.0,
            average_confidence=78.5,
            patterns=[
                FraudPatternSummary(
                    type="price_anomaly",
                    severity=Severity.HIGH,
                    confidence=85.0,
                ),
                FraudPatternSummary(
                    type="vendor_collusion",
                    severity=Severity.CRITICAL,
                    confidence=92.0,
                ),
            ],
            engine="fraud",
            engine_status=EngineStatus.OK,
        )
        
        # Should not raise
        assert summary.total_patterns == 5
        assert len(summary.patterns) == 2
        assert summary.highest_confidence == 95.0
    
    def test_invariant_total_patterns_less_than_patterns_length(self):
        """Test that total_patterns < len(patterns) raises error."""
        with pytest.raises(ValueError) as exc_info:
            FraudSummary(
                total_patterns=1,  # ← Less than len(patterns)
                validated_patterns=0,
                highest_confidence=80.0,
                average_confidence=70.0,
                patterns=[
                    FraudPatternSummary(
                        type="price_anomaly",
                        severity=Severity.HIGH,
                        confidence=85.0,
                    ),
                    FraudPatternSummary(
                        type="vendor_collusion",
                        severity=Severity.CRITICAL,
                        confidence=92.0,
                    ),
                ],
            )
        
        assert "total_patterns" in str(exc_info.value)
        assert "less than" in str(exc_info.value)
    
    def test_invariant_validated_exceeds_total(self):
        """Test that validated_patterns > total_patterns raises error."""
        with pytest.raises(ValueError) as exc_info:
            FraudSummary(
                total_patterns=3,
                validated_patterns=5,  # ← Exceeds total
                highest_confidence=80.0,
                average_confidence=70.0,
                patterns=[],
            )
        
        assert "validated_patterns" in str(exc_info.value)
        assert "cannot exceed" in str(exc_info.value)
    
    def test_invariant_highest_less_than_average(self):
        """Test that highest_confidence < average_confidence raises error."""
        with pytest.raises(ValueError) as exc_info:
            FraudSummary(
                total_patterns=3,
                validated_patterns=1,
                highest_confidence=65.0,  # ← Less than average
                average_confidence=78.0,
                patterns=[],
            )
        
        assert "highest_confidence" in str(exc_info.value)
        assert "less than" in str(exc_info.value)
    
    def test_does_not_validate_active_alerts(self):
        """Test that active_alerts is NOT validated against total_patterns."""
        # This should NOT raise even though active_alerts > total_patterns
        # Because the definition of active_alerts may change
        summary = FraudSummary(
            total_patterns=2,
            validated_patterns=1,
            active_alerts=5,  # ← > total_patterns, but NOT validated
            high_confidence=3,  # ← > total_patterns, but NOT validated
            highest_confidence=80.0,
            average_confidence=70.0,
            patterns=[],
        )
        
        # Should not raise
        assert summary.active_alerts == 5
        assert summary.high_confidence == 3
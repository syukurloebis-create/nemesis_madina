"""
Calculator Contract Test — Level 5: Calculator == Expected Formula.

Memastikan calculator menghitung sesuai formula yang diharapkan.
"""

import pytest

from backend.dtos.collector_dtos import FraudCollectorDTO, PatternDTO
from backend.calculators.fraud_score_calculator import FraudScoreCalculator
from backend.calculators.config import FraudWeights
from backend.domain.enums import Severity


class TestCalculatorContract:
    """Calculator Contract Test — Level 5."""
    
    def test_fraud_calculator_with_data(self):
        """Calculator harus menghitung score dengan benar."""
        # Create test DTO
        patterns = [
            PatternDTO("type1", Severity.CRITICAL, 90.0, False, None),
            PatternDTO("type2", Severity.HIGH, 75.0, False, None),
        ]
        
        dto = FraudCollectorDTO(
            total_patterns=2,
            critical=1,
            high=1,
            medium=0,
            low=0,
            avg_confidence=82.5,
            highest_confidence=90.0,
            validated_patterns=0,
            patterns=patterns
        )
        
        weights = FraudWeights()
        
        # Calculate
        result = FraudScoreCalculator.calculate(dto, weights)
        
        # Contract: Hasil harus sesuai formula
        assert result.overall_risk == Severity.CRITICAL
        assert result.score > 0
        assert result.score <= 100
        assert result.severity_score == 100  # CRITICAL = 100
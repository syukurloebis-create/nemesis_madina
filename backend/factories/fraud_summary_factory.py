"""
Fraud Summary Factory — Pure Composition.

Architecture Decision (ADR-017):
- Factory is pure composition: DTO + Calculated → Summary
- STATELESS: no cache, no repository, no database
- NO calculations: all business logic already in Calculator
- NO hasattr(): deterministic transformation

Engine Pipeline Standard:
- All engines (Fraud, Risk, Evidence, Graph, Procurement) follow same pattern
"""

from typing import List

from backend.dtos.collector_dtos import FraudCollectorDTO
from backend.calculators.fraud_score_calculator import CalculatedFraud
from backend.domain.summary_objects import FraudSummary, FraudPatternSummary
from backend.domain.enums import Severity, EngineStatus


class FraudSummaryFactory:
    """
    Fraud Summary Factory — Pure Composition.
    
    Combines FraudCollectorDTO + CalculatedFraud → FraudSummary.
    
    NO business logic.
    NO calculations.
    NO database.
    NO hasattr().
    
    Pure deterministic transformation.
    """
    
    @staticmethod
    def create(
        collector: FraudCollectorDTO,
        calculation: CalculatedFraud
    ) -> FraudSummary:
        """
        Compose FraudSummary from DTO and CalculatedFraud.
        
        Args:
            collector: Raw data from collector
            calculation: Calculated results from FraudScoreCalculator
            
        Returns:
            FraudSummary: Complete validated read model
        """
        # ===== 1. Transform patterns =====
        # PatternDTO → FraudPatternSummary
        # NO hasattr() — deterministic transformation
        patterns = [
            FraudPatternSummary(
                type=p.pattern_type,
                severity=p.severity,
                confidence=p.confidence,
                detected_at=p.detected_at,
                validated=p.validated,
                description=None,  # PatternDTO tidak memiliki description (saat ini)
            )
            for p in collector.patterns
        ]
        
        # ===== 2. Compose Summary =====
        # All fields come from either DTO or CalculatedFraud
        # NO calculations here
        return FraudSummary(
            # ===== From Calculator =====
            overall_risk=calculation.overall_risk,
            score=calculation.score,
            active_alerts=calculation.active_alerts,
            high_confidence=calculation.high_confidence,
            
            # ===== From DTO =====
            total_patterns=collector.total_patterns,
            validated_patterns=collector.validated_patterns,
            highest_confidence=collector.highest_confidence,
            average_confidence=collector.avg_confidence,
            
            # ===== Patterns =====
            patterns=patterns,
            
            # ===== Engine metadata =====
            engine="fraud",
            engine_status=calculation.engine_status,
        )
    
    @staticmethod
    def create_empty() -> FraudSummary:
        """Create empty FraudSummary for fallback cases."""
        return FraudSummary(
            overall_risk=Severity.UNKNOWN,
            score=0.0,
            active_alerts=0,
            high_confidence=0,
            total_patterns=0,
            validated_patterns=0,
            highest_confidence=0.0,
            average_confidence=0.0,
            patterns=[],
            engine="fraud",
            engine_status=EngineStatus.FAILED,  # ← FIX: ERROR → FAILED
        )
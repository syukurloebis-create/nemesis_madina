# backend/mappers/fraud_mapper.py

from typing import List
from backend.dtos.collector_dtos import FraudCollectorDTO
from backend.calculators.fraud_score_calculator import CalculatedFraud
from backend.domain.summary_objects import FraudSummary, FraudPatternSummary
from backend.domain.enums import EngineStatus


class FraudMapper:
    """
    Fraud Mapper — Pure Transformer.
    
    ONLY transforms DTO + Calculated → Summary.
    NO business logic.
    NO calculations.
    """

    @staticmethod
    def to_summary(
        dto: FraudCollectorDTO,
        calculated: CalculatedFraud
    ) -> FraudSummary:
        """
        Transform FraudCollectorDTO and CalculatedFraud to FraudSummary.
        
        Args:
            dto: Raw data from collector
            calculated: Calculated results from FraudScoreCalculator
            
        Returns:
            FraudSummary: Complete fraud summary
        """
        # 1. Transform patterns — langsung dari typed PatternDTO
        patterns = [
            FraudPatternSummary(
                type=p.pattern_type,
                severity=p.severity,
                confidence=p.confidence,
                detected_at=p.detected_at,
                validated=p.validated,
                description=None,  # PatternDTO tidak punya description
            )
            for p in dto.patterns
        ]

        # 2. Build summary — semua field dari DTO atau Calculated
        return FraudSummary(
            # ===== From Calculator =====
            overall_risk=calculated.overall_risk,
            score=calculated.score,
            
            # ===== From DTO =====
            total_patterns=dto.total_patterns,
            active_alerts=dto.critical + dto.high,  # active alerts = critical + high
            high_confidence=dto.high,  # high confidence patterns count
            validated_patterns=dto.validated_patterns,
            highest_confidence=dto.highest_confidence,
            average_confidence=dto.avg_confidence,
            
            # ===== Patterns =====
            patterns=patterns,
            
            # ===== Engine metadata =====
            engine="fraud",
            engine_status=dto.engine_status,
        )
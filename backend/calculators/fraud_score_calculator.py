"""
Fraud Score Calculator — Pure Business Logic.

ADR-018: Calculator = The ONLY place for business logic.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from backend.dtos.collector_dtos import FraudCollectorDTO
from backend.calculators.config import FraudWeights, CalculatorConfig
from backend.domain.enums import Severity, EngineStatus, FallbackReason
from backend.domain.enums.severity import SeverityRank


@dataclass(frozen=True, slots=True)
class CalculatedFraud:
    """Calculator output for Fraud."""
    overall_risk: Severity
    score: float
    severity_score: float
    confidence_score: float
    validated_score: float
    pattern_variety_score: float
    active_alerts: int = 0
    high_confidence: int = 0
    engine_status: EngineStatus = EngineStatus.OK
    fallback_reason: Optional[FallbackReason] = None
    error: Optional[str] = None


class FraudScoreCalculator:
    """Fraud Score Calculator — Pure Function."""

    @classmethod
    def calculate(
        cls,
        dto: FraudCollectorDTO,
        weights: Optional[FraudWeights] = None,
    ) -> CalculatedFraud:
        """Calculate fraud metrics from DTO."""
        if weights is None:
            weights = cls._default_weights()

        overall_risk = cls._calculate_overall_risk(dto)
        severity_score = cls._calculate_severity_score(overall_risk)
        confidence_score = cls._calculate_confidence_score(dto)
        validated_score = cls._calculate_validated_score(dto)
        pattern_variety_score = cls._calculate_pattern_variety_score(dto)

        score = cls._calculate_weighted_score(
            severity_score=severity_score,
            confidence_score=confidence_score,
            validated_score=validated_score,
            pattern_variety_score=pattern_variety_score,
            weights=weights,
        )

        active_alerts = cls._calculate_active_alerts(dto)
        high_confidence = cls._calculate_high_confidence(dto)

        return CalculatedFraud(
            overall_risk=overall_risk,
            score=round(score, 2),
            severity_score=round(severity_score, 2),
            confidence_score=round(confidence_score, 2),
            validated_score=round(validated_score, 2),
            pattern_variety_score=round(pattern_variety_score, 2),
            active_alerts=active_alerts,
            high_confidence=high_confidence,
            engine_status=dto.engine_status,
            fallback_reason=getattr(dto, 'fallback_reason', None),
            error=getattr(dto, 'error', None),
        )

    @classmethod
    def _default_weights(cls) -> FraudWeights:
        """Default weights for fraud scoring."""
        return FraudWeights(
            severity_weight=0.25,
            confidence_weight=0.25,
            validated_weight=0.25,
            variety_weight=0.25,
        )

    @classmethod
    def _calculate_weighted_score(
        cls,
        severity_score: float,
        confidence_score: float,
        validated_score: float,
        pattern_variety_score: float,
        weights: FraudWeights,
    ) -> float:
        """Weighted combination of component scores."""
        return (
            severity_score * weights.severity_weight +
            confidence_score * weights.confidence_weight +
            validated_score * weights.validated_weight +
            pattern_variety_score * weights.variety_weight
        )

    # ===== Business Rules =====

    @classmethod
    def _calculate_overall_risk(cls, dto: FraudCollectorDTO) -> Severity:
        """Highest severity present."""
        if dto.critical > 0:
            return Severity.CRITICAL
        if dto.high > 0:
            return Severity.HIGH
        if dto.medium > 0:
            return Severity.MEDIUM
        if dto.low > 0:
            return Severity.LOW
        return Severity.LOW

    @classmethod
    def _calculate_active_alerts(cls, dto: FraudCollectorDTO) -> int:
        """CRITICAL + HIGH patterns."""
        return dto.critical + dto.high

    @classmethod
    def _calculate_high_confidence(cls, dto: FraudCollectorDTO) -> int:
        """Patterns with confidence >= 80%."""
        return sum(1 for p in dto.patterns if p.confidence >= 80.0)

    @classmethod
    def _calculate_severity_score(cls, overall_risk: Severity) -> float:
        """Convert severity to score 0-100."""
        rank = SeverityRank.from_string(overall_risk.value)
        return (rank.value / 4) * 100

    @classmethod
    def _calculate_confidence_score(cls, dto: FraudCollectorDTO) -> float:
        return dto.avg_confidence or 0.0

    @classmethod
    def _calculate_validated_score(cls, dto: FraudCollectorDTO) -> float:
        if dto.total_patterns > 0:
            return (dto.validated_patterns / dto.total_patterns) * 100
        return 0.0

    @classmethod
    def _calculate_pattern_variety_score(cls, dto: FraudCollectorDTO) -> float:
        levels_present = 0
        if dto.critical > 0:
            levels_present += 1
        if dto.high > 0:
            levels_present += 1
        if dto.medium > 0:
            levels_present += 1
        if dto.low > 0:
            levels_present += 1
        return (levels_present / 4) * 100
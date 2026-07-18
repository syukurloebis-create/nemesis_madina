"""
Risk Score Calculator — Pure Business Logic.

ADR-018: Calculator = The ONLY place for business logic.
"""

from dataclasses import dataclass
from typing import Tuple

from backend.dtos.collector_dtos import RiskCollectorDTO
from backend.calculators.config import RiskWeights, CalculatorConfig
from backend.domain.enums import RiskLevel, EngineStatus
from backend.domain.risk_level_normalizer import normalize_risk_level


@dataclass(frozen=True, slots=True)
class CalculatedRisk:
    """Calculator output for Risk."""
    score: float
    level: RiskLevel
    anomaly_score: float
    collusion_score: float
    financial_score: float
    recommendations: Tuple[str, ...] = ()
    engine_status: EngineStatus = EngineStatus.OK  # ← DARI DTO


class RiskScoreCalculator:
    """Risk Score Calculator — Pure Function."""
    
    @classmethod
    def calculate(
        cls,
        dto: RiskCollectorDTO,
        weights: RiskWeights = None,  # ← PARAMETER EKSPLISIT
    ) -> CalculatedRisk:
        """
        Calculate risk from DTO.
        
        Args:
            dto: RiskCollectorDTO from collector
            weights: RiskWeights (optional, uses default if None)
            
        Returns:
            CalculatedRisk: Pure calculation result
        """
        # ===== Use default weights if not provided =====
        if weights is None:
            config = CalculatorConfig.default()
            weights = config.get_risk_weights()
        
        # ===== If database already has level, use it =====
        if dto.level and dto.level.upper() != "UNKNOWN":
            return CalculatedRisk(
                score=dto.score,
                level=normalize_risk_level(dto.level),
                anomaly_score=dto.anomaly_score,
                collusion_score=dto.collusion_score,
                financial_score=dto.financial_score,
                engine_status=dto.engine_status,  # ← PROPAGATE
            )
        
        # ===== Otherwise calculate from components =====
        score = (
            dto.anomaly_score * weights.anomaly_weight +
            dto.collusion_score * weights.collusion_weight +
            dto.financial_score * weights.financial_weight
        )
        
        # ===== Determine level from score =====
        if score >= 80:
            level = RiskLevel.CRITICAL
        elif score >= 60:
            level = RiskLevel.HIGH
        elif score >= 40:
            level = RiskLevel.MEDIUM
        elif score >= 20:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.UNKNOWN
        
        return CalculatedRisk(
            score=round(score, 2),
            level=level,
            anomaly_score=round(dto.anomaly_score, 2),
            collusion_score=round(dto.collusion_score, 2),
            financial_score=round(dto.financial_score, 2),
            engine_status=dto.engine_status,  # ← PROPAGATE
        )
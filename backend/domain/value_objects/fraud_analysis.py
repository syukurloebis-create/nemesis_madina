"""
NEMESIS Madina - Fraud Analysis Value Object
✅ Pure Value Object - no aggregate knowledge
✅ Immutable collections (Sequence)
"""

from dataclasses import dataclass
from typing import Sequence

from backend.domain.value_objects.fraud_pattern import FraudPattern
from backend.domain.enums.risk_level import RiskLevel


@dataclass(frozen=True)
class FraudAnalysis:
    """Fraud analysis result - Pure Value Object."""
    
    case_id: str
    patterns: Sequence[FraudPattern]  # ✅ Immutable
    overall_risk: RiskLevel
    score: float
    total_patterns: int
    active_alerts: int
    high_confidence: int
    validated_patterns: int
    highest_confidence: float
    average_confidence: float
    
    # ❌ REMOVED: apply_to_aggregate() - aggregate owns logic
"""
Fraud Row Objects — Immutable, Typed, No Singleton.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class FraudSummaryRow:
    """Fraud Summary Row — Immutable."""
    total_patterns: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    avg_confidence: float = 0.0
    highest_confidence: float = 0.0
    validated: int = 0


@dataclass(frozen=True)
class FraudPatternRow:
    """Fraud Pattern Row — Immutable."""
    pattern_type: str
    severity: str
    confidence_score: float
    is_validated: bool
    detected_at: Optional[datetime] = None
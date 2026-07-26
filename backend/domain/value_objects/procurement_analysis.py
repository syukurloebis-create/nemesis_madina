# backend/domain/value_objects/procurement_analysis.py
"""
NEMESIS Madina - Procurement Analysis Value Object
✅ Pure Value Object - no aggregate knowledge
✅ Immutable fields
"""

from dataclasses import dataclass, field
from typing import Optional, Sequence, List, Dict, Any


@dataclass(frozen=True)
class ProcurementAnalysis:
    """Procurement analysis result - Pure Value Object."""

    # Core fields (required)
    case_id: str = ""
    total_spend: float = 0.0
    vendor_count: int = 0
    transaction_count: int = 0
    flagged_transactions: int = 0
    high_risk_vendors: int = 0
    duplicate_invoices: int = 0
    irregular_patterns: Sequence[dict] = field(default_factory=list)
    fraud_indicators: Sequence[str] = field(default_factory=list)
    risk_score: float = 0.0
    confidence: float = 0.0
    
    # Application layer fields
    packages: List[Any] = field(default_factory=list)
    vendors: List[Any] = field(default_factory=list)
    instansi_count: int = 0
    total_value: float = 0.0
    avg_value: float = 0.0
    completed: bool = False
    engine_status: str = "UNKNOWN"


    def __post_init__(self):
        """Validate value object invariants."""
        if not (0 <= self.risk_score <= 100):
            raise ValueError(
                f"Procurement risk score must be between 0 and 100, got {self.risk_score}"
            )
    
        if not (0 <= self.confidence <= 100):
            raise ValueError(
                f"Procurement confidence must be between 0 and 100, got {self.confidence}"
            )


    @property
    def has_flags(self) -> bool:
        return self.flagged_transactions > 0


    @property
    def is_high_risk(self) -> bool:
        """
        Risk score scale: 0-100
        High risk threshold: > 70
        """
        return self.risk_score > 70
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

    @property
    def has_flags(self) -> bool:
        return len(self.flagged_transactions) > 0

    @property
    def is_high_risk(self) -> bool:
        return self.risk_score > 0.7
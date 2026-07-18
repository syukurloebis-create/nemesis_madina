from dataclasses import dataclass
from typing import Optional, Tuple, Sequence
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RiskSummaryRow:
    """
    Risk Summary Row Object — Immutable, Memory Efficient.
    
    Menggunakan tuple untuk recommendations (immutable).
    """
    score: float = 0.0
    level: str = "UNKNOWN"
    anomaly_score: float = 0.0
    collusion_score: float = 0.0
    financial_score: float = 0.0
    recommendations: Tuple[str, ...] = ()  # ← tuple, bukan list
    calculated_at: Optional[datetime] = None
    

RiskSummaryRow.EMPTY = RiskSummaryRow()
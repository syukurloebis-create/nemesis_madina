"""
Finding With Intelligence - Domain Read Model / Projection
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from backend.domain.finding_intelligence import FindingIntelligence


@dataclass(frozen=True)
class FindingWithIntelligence:
    """
    Finding dengan intelligence enrichment - Domain Read Model.

    Ini adalah projection untuk use case dashboard,
    tetap berada di Domain layer sebagai read model.
    """
    id: str
    title: str
    description: str
    type: str
    severity: str
    status: str
    engine: str
    anomaly_score: float
    confidence: float
    risk_score: float
    created_at: datetime
    intelligence: FindingIntelligence
    metadata: Optional[Dict[str, Any]] = None
    evidence_confidence: Optional[float] = None  # <-- NEW
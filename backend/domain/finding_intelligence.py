"""
Finding Intelligence - Domain Object (IMMUTABLE)
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass(frozen=True)
class IntelligenceTimeline:
    """Timeline summary untuk finding intelligence."""
    events: int = 0
    sla_breach: int = 0
    evidence_actions: int = 0
    last_event: Optional[datetime] = None


@dataclass(frozen=True)
class IntelligenceEvidence:
    """Evidence summary untuk finding intelligence."""
    total: int = 0
    confidence: float = 0.0
    source: str = "evidence"
    verified: int = 0  # <-- NEW
    trust_score: float = 0.0  # <-- NEW
    avg_confidence: float = 0.0  # <-- NEW


@dataclass(frozen=True)
class IntelligenceDecision:
    """Decision summary untuk finding intelligence."""
    status: str = "PENDING"
    confidence: float = 0.0
    actor: Optional[str] = None


@dataclass(frozen=True)
class IntelligenceDrivers:
    """Drivers untuk finding intelligence."""
    finding_risk: float = 0.0
    sla_breach: int = 0
    evidence_confidence: float = 0.0
    decision_status: str = "PENDING"
    decision_confidence: float = 0.0


@dataclass(frozen=True)
class FindingIntelligence:
    """
    Domain object untuk finding intelligence - IMMUTABLE.

    TIDAK memiliki to_dict().
    Representasi API ditangani oleh Presenter.
    """
    finding_id: str
    base_score: float
    intelligence_score: float
    delta: float
    level: str
    drivers: IntelligenceDrivers
    explanations: List[str]
    timeline: IntelligenceTimeline
    evidence: IntelligenceEvidence
    decision: IntelligenceDecision
    recommendations: List[str]
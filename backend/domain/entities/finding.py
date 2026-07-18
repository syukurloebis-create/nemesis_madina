# backend/domain/entities/finding.py (NEW)

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class Finding:
    """Domain finding - actionable insight from collectors."""
    
    id: str
    source: str  # fraud, risk, evidence, graph, procurement
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    confidence: float
    detected_at: datetime
    metadata: Optional[dict] = None
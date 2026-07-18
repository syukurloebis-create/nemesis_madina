"""
Risk Snapshot Projection — Persistence DTO for cases.latest_risk.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class RiskSnapshotProjection:
    """Persistence DTO for cases.latest_risk."""
    score: float
    level: str
    components: Dict[str, float]
    calculated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSONB storage."""
        return {
            "score": self.score,
            "level": self.level,
            "components": self.components,
            "calculated_at": self.calculated_at,
        }
"""
Impact Tracker
Melacak dampak keputusan
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ImpactType(str, Enum):
    """Tipe dampak"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    REPUTATIONAL = "reputational"
    STRATEGIC = "strategic"


@dataclass
class ImpactRecord:
    """Record dampak"""
    id: str
    decision_id: str
    type: ImpactType
    description: str
    value: float
    unit: str = "IDR"
    is_recovery: bool = False
    measured_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "type": self.type.value,
            "description": self.description,
            "value": self.value,
            "unit": self.unit,
            "is_recovery": self.is_recovery,
            "measured_at": self.measured_at.isoformat(),
            "metadata": self.metadata
        }


class ImpactTracker:
    """
    Impact Tracker
    Melacak dan mengukur dampak keputusan
    """

    def __init__(self):
        self.impacts: Dict[str, List[ImpactRecord]] = {}
        self.baselines: Dict[str, Dict[str, float]] = {}

    def add_impact(
        self,
        decision_id: str,
        impact_type: ImpactType,
        description: str,
        value: float,
        unit: str = "IDR",
        is_recovery: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ImpactRecord:
        """
        Add impact record
        """
        impact = ImpactRecord(
            id=f"imp_{decision_id}_{len(self.impacts.get(decision_id, []))}",
            decision_id=decision_id,
            type=impact_type,
            description=description,
            value=value,
            unit=unit,
            is_recovery=is_recovery,
            metadata=metadata or {}
        )

        if decision_id not in self.impacts:
            self.impacts[decision_id] = []
        self.impacts[decision_id].append(impact)

        logger.info(f"Impact recorded for decision {decision_id}: {impact_type.value} - {value} {unit}")
        return impact

    def get_impacts(self, decision_id: str) -> List[ImpactRecord]:
        """Get all impacts for a decision"""
        return self.impacts.get(decision_id, [])

    def get_total_recovery(self, decision_id: str) -> float:
        """Get total recovery from a decision"""
        impacts = self.impacts.get(decision_id, [])
        return sum(i.value for i in impacts if i.is_recovery)

    def get_total_impact(self, decision_id: str) -> float:
        """Get total impact from a decision"""
        impacts = self.impacts.get(decision_id, [])
        return sum(i.value for i in impacts)

    def get_impact_by_type(self, decision_id: str, impact_type: ImpactType) -> List[ImpactRecord]:
        """Get impacts by type"""
        impacts = self.impacts.get(decision_id, [])
        return [i for i in impacts if i.type == impact_type]

    def set_baseline(self, decision_id: str, baseline: Dict[str, float]) -> None:
        """Set baseline for a decision"""
        self.baselines[decision_id] = baseline
        logger.info(f"Baseline set for decision {decision_id}")

    def get_roi(self, decision_id: str) -> float:
        """Calculate ROI for a decision"""
        impacts = self.impacts.get(decision_id, [])
        if not impacts:
            return 0

        total_impact = sum(i.value for i in impacts)
        baseline = self.baselines.get(decision_id, {})

        if baseline and baseline.get("cost", 0) > 0:
            return (total_impact - baseline.get("cost", 0)) / baseline.get("cost", 1) * 100

        return total_impact

    def get_impact_summary(self, decision_id: str) -> Dict[str, Any]:
        """
        Get impact summary
        """
        impacts = self.impacts.get(decision_id, [])
        recovery = self.get_total_recovery(decision_id)
        total_impact = self.get_total_impact(decision_id)
        roi = self.get_roi(decision_id)

        by_type = {}
        for impact in impacts:
            by_type[impact.type.value] = by_type.get(impact.type.value, 0) + impact.value

        return {
            "total_impact": total_impact,
            "total_recovery": recovery,
            "roi": roi,
            "by_type": by_type,
            "count": len(impacts),
            "details": [i.to_dict() for i in impacts]
        }


# Singleton instance
impact_tracker = ImpactTracker()

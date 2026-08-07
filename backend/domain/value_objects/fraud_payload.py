"""
NEMESIS Madina - Fraud Payload for Domain Events
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.fraud_pattern import FraudPattern


@dataclass(frozen=True)
class FraudPayload:
    """Payload for fraud domain events."""

    case_id: CaseId
    analysis: FraudAnalysis
    patterns: Tuple = ()

    def __post_init__(self):
        """Synchronize patterns with analysis.patterns."""
        if not self.patterns and self.analysis and hasattr(self.analysis, "patterns"):
            object.__setattr__(self, "patterns", tuple(self.analysis.patterns))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        analysis_dict = self.analysis.to_dict() if hasattr(self.analysis, "to_dict") else self.analysis
        return {
            "case_id": str(self.case_id),
            "analysis": analysis_dict,
            "patterns": [
                p.to_dict() if hasattr(p, "to_dict") else p
                for p in self.patterns
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FraudPayload":
        """Create from dictionary."""
        from backend.domain.value_objects.fraud_analysis import FraudAnalysis
        from backend.domain.value_objects.fraud_pattern import FraudPattern

        return cls(
            case_id=CaseId(data["case_id"]),
            analysis=FraudAnalysis.from_dict(data["analysis"]) if isinstance(data.get("analysis"), dict) else data.get("analysis"),
            patterns=tuple(
                FraudPattern.from_dict(p) if isinstance(p, dict) else p
                for p in data.get("patterns", [])
            ),
        )
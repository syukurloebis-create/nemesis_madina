"""
NEMESIS Madina - Fraud Payload for Domain Events
"""

from dataclasses import dataclass
from typing import Dict, Any
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis


@dataclass(frozen=True)
class FraudPayload:
    """Payload for fraud domain events."""
    
    case_id: CaseId
    analysis: FraudAnalysis
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "case_id": str(self.case_id),
            "analysis": self.analysis,  # FraudAnalysis has its own serialization
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FraudPayload":
        """Create from dictionary."""
        return cls(
            case_id=CaseId(data["case_id"]),
            analysis=data["analysis"],  # FraudAnalysis has its own deserialization
        )
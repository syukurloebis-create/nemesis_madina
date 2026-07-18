"""
NEMESIS Madina - Analysis Bundle Value Object
✅ Compatible with mapping-based storage
"""

from dataclasses import dataclass
from typing import Optional

from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.risk_assessment import RiskAssessment
from backend.domain.value_objects.evidence_verification import EvidenceVerification
from backend.domain.value_objects.graph_analysis import GraphAnalysis
from backend.domain.value_objects.procurement_analysis import ProcurementAnalysis


@dataclass(frozen=True)
class AnalysisBundle:
    """
    Bundle of all analysis results.
    ✅ Compatible with mapping-based storage
    """
    
    fraud: Optional[FraudAnalysis] = None
    risk: Optional[RiskAssessment] = None
    evidence: Optional[EvidenceVerification] = None
    graph: Optional[GraphAnalysis] = None
    procurement: Optional[ProcurementAnalysis] = None
    
    def has_any(self) -> bool:
        """Check if any analysis is present."""
        return any([
            self.fraud is not None,
            self.risk is not None,
            self.evidence is not None,
            self.graph is not None,
            self.procurement is not None,
        ])
    
    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {
            "fraud": self.fraud,
            "risk": self.risk,
            "evidence": self.evidence,
            "graph": self.graph,
            "procurement": self.procurement,
        }
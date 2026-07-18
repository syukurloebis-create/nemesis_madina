"""
Dashboard Summary - Agregat Domain Object
"""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime

from backend.domain.summary_objects import (
    FraudSummary,
    CollusionSummary,
    GraphSummary,
    RiskSummary,
    EvidenceSummary,
    ProcurementSummary,
    RecoverySummary
)
from backend.domain.projections.finding_with_intelligence import FindingWithIntelligence


@dataclass(frozen=True)
class DashboardSummary:
    """
    Dashboard Summary - Agregat Domain Object.

    Mengandung seluruh summary engine dan findings.
    Ini adalah satu-satunya object yang keluar dari service.
    """
    case_id: str
    fraud: FraudSummary
    collusion: CollusionSummary
    graph: GraphSummary
    risk: RiskSummary
    evidence: EvidenceSummary
    procurement: ProcurementSummary
    recovery: RecoverySummary
    findings: List[FindingWithIntelligence]
    confidence: float
    status: str = "success"
    generated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_findings(self) -> int:
        return len(self.findings)
    
    @property
    def critical_findings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "CRITICAL")
    
    @property
    def high_findings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "HIGH")
    
    @property
    def medium_findings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "MEDIUM")
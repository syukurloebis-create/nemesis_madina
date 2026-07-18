"""
NEMESIS Madina - Infrastructure Builders
✅ Helper functions for building infrastructure components
"""

from backend.infrastructure.mappers.case_mapper import CaseMapper
from backend.infrastructure.mappers.fraud_mapper import FraudAnalysisMapper
from backend.infrastructure.mappers.risk_mapper import RiskAssessmentMapper
from backend.infrastructure.mappers.evidence_mapper import EvidenceVerificationMapper
from backend.infrastructure.mappers.graph_mapper import GraphAnalysisMapper
from backend.infrastructure.mappers.procurement_mapper import ProcurementAnalysisMapper


def build_case_mapper() -> CaseMapper:
    """
    Build CaseMapper with all sub-mappers.
    ✅ Created once at bootstrap
    ✅ All dependencies injected
    """
    return CaseMapper(
        fraud_mapper=FraudAnalysisMapper(),
        risk_mapper=RiskAssessmentMapper(),
        evidence_mapper=EvidenceVerificationMapper(),
        graph_mapper=GraphAnalysisMapper(),
        procurement_mapper=ProcurementAnalysisMapper(),
    )
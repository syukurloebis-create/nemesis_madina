"""
Mappers Assembler — Create all mappers.
"""

from backend.mappers.fraud_mapper import FraudMapper
from backend.mappers.graph_mapper import GraphMapper
from backend.mappers.risk_mapper import RiskMapper
from backend.mappers.evidence_mapper import EvidenceMapper
from backend.mappers.procurement_mapper import ProcurementMapper


def create_mappers():
    """Create all mappers."""
    return {
        "fraud": FraudMapper(),
        "graph": GraphMapper(),
        "risk": RiskMapper(),
        "evidence": EvidenceMapper(),
        "procurement": ProcurementMapper(),
    }
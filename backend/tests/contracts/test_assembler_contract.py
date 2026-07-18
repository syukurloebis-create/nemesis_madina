# tests/contracts/test_assembler_contract.py

"""
Assembler Contract Tests

Memastikan semua assembler mengikuti contract:
- assemble_empty() returns DTO with EngineStatus.OK
- assemble_empty() sets all business fields to zero
"""

import pytest
from backend.collectors.assemblers.risk_assembler import RiskAssembler
from backend.collectors.assemblers.fraud_assembler import FraudAssembler
from backend.collectors.assemblers.graph_assembler import GraphAssembler
from backend.collectors.assemblers.evidence_assembler import EvidenceAssembler
from backend.collectors.assemblers.procurement_assembler import ProcurementAssembler
from backend.domain.enums import EngineStatus


class TestAssemblerContract:
    """Test semua assembler mengikuti contract yang sama."""

    def test_risk_assembler_empty_returns_ok(self):
        dto = RiskAssembler.assemble_empty()
        assert dto.engine_status == EngineStatus.OK
        assert dto.score == 0
        assert dto.level == "UNKNOWN"
        assert dto.anomaly_score == 0
        assert dto.collusion_score == 0
        assert dto.financial_score == 0
        assert dto.recommendations == ()

    def test_fraud_assembler_empty_returns_ok(self):
        dto = FraudAssembler.assemble_empty()
        assert dto.engine_status == EngineStatus.OK
        assert dto.total_patterns == 0
        assert dto.critical == 0
        assert dto.high == 0
        assert dto.medium == 0
        assert dto.low == 0
        assert dto.avg_confidence == 0.0
        assert dto.highest_confidence == 0.0
        assert dto.validated_patterns == 0
        assert dto.patterns == ()

    def test_graph_assembler_empty_returns_ok(self):
        dto = GraphAssembler.assemble_empty()
        assert dto.engine_status == EngineStatus.OK
        assert dto.entities == 0
        assert dto.relationships == 0

    def test_evidence_assembler_empty_returns_ok(self):
        dto = EvidenceAssembler.assemble_empty()
        assert dto.engine_status == EngineStatus.OK
        assert dto.total == 0
        assert dto.verified == 0
        assert dto.rejected == 0
        assert dto.pending == 0
        assert dto.avg_trust == 0.0
        assert dto.avg_confidence == 0.0

    def test_procurement_assembler_empty_returns_ok(self):
        dto = ProcurementAssembler.assemble_empty()
        assert dto.engine_status == EngineStatus.OK
        assert dto.packages == 0
        assert dto.vendors == 0
        assert dto.instansi_count == 0
        assert dto.avg_value == 0.0
        assert dto.total_value == 0.0
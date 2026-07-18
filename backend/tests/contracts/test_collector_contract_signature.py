# tests/contracts/test_collector_contract_signature.py

"""
Contract Signature Tests - ABI Level

Memastikan CollectorDTO contract tidak berubah.
Test ini akan gagal jika ada perubahan pada:
- Nama field
- Tipe field
- Urutan field
- Keberadaan error_fallback()
"""

from dataclasses import fields, is_dataclass
from typing import Tuple
import pytest
from backend.dtos.collector_dtos import (
    RiskCollectorDTO,
    FraudCollectorDTO,
    GraphCollectorDTO,
    EvidenceCollectorDTO,
    ProcurementCollectorDTO
)
from backend.domain.enums import EngineStatus, FallbackReason


class TestCollectorContractSignature:
    """Test contract signature untuk semua CollectorDTO - ABI Level."""

    # ============================================================
    # RiskCollectorDTO Contract
    # ============================================================

    def test_risk_collector_dto_is_dataclass(self):
        """RiskCollectorDTO must be a dataclass."""
        assert is_dataclass(RiskCollectorDTO), "RiskCollectorDTO must be a dataclass"

    def test_risk_collector_dto_is_frozen(self):
        """RiskCollectorDTO must be frozen."""
        # Check that fields are not writable
        dto = RiskCollectorDTO(score=0.0, level="LOW", anomaly_score=0.0, collusion_score=0.0, financial_score=0.0)
        with pytest.raises(Exception):  # dataclass frozen will raise
            dto.score = 100.0

    def test_risk_collector_dto_signature(self):
        """RiskCollectorDTO field signature must match contract v1.0.0."""
        expected_fields = [
            ('score', float),
            ('level', str),
            ('anomaly_score', float),
            ('collusion_score', float),
            ('financial_score', float),
            ('recommendations', Tuple[str, ...]),
            ('engine_type', object),
            ('engine_status', object),
            ('fallback_reason', object),
            ('error', object),
        ]
        actual_fields = [(f.name, f.type) for f in fields(RiskCollectorDTO)]

        assert len(actual_fields) == len(expected_fields), \
            f"Field count changed! Expected {len(expected_fields)}, got {len(actual_fields)}"

        for i, (expected_name, expected_type) in enumerate(expected_fields):
            actual_name, actual_type = actual_fields[i]
            assert actual_name == expected_name, \
                f"Field {i} name changed! Expected '{expected_name}', got '{actual_name}'"

    def test_risk_collector_dto_has_error_fallback(self):
        """RiskCollectorDTO must have error_fallback() method."""
        assert hasattr(RiskCollectorDTO, 'error_fallback')
        assert callable(RiskCollectorDTO.error_fallback)

    def test_risk_collector_dto_error_fallback_returns_valid_dto(self):
        """error_fallback() must return valid DTO with FAILED status."""
        dto = RiskCollectorDTO.error_fallback("Test error", FallbackReason.NO_DATA)
        assert isinstance(dto, RiskCollectorDTO)
        assert dto.engine_status == EngineStatus.FAILED
        assert dto.error == "Test error"
        assert dto.score == 0.0
        assert dto.level == "UNKNOWN"
        assert dto.anomaly_score == 0.0
        assert dto.collusion_score == 0.0
        assert dto.financial_score == 0.0

    # ============================================================
    # FraudCollectorDTO Contract
    # ============================================================

    def test_fraud_collector_dto_is_dataclass(self):
        assert is_dataclass(FraudCollectorDTO)

    def test_fraud_collector_dto_signature(self):
        expected_fields = [
            ('total_patterns', int),
            ('critical', int),
            ('high', int),
            ('medium', int),
            ('low', int),
            ('avg_confidence', float),
            ('highest_confidence', float),
            ('validated_patterns', int),
            ('patterns', tuple),
            ('engine_type', object),
            ('engine_status', object),
            ('fallback_reason', object),
            ('error', object),
        ]
        actual_fields = [(f.name, f.type) for f in fields(FraudCollectorDTO)]
        assert len(actual_fields) == len(expected_fields)

    def test_fraud_collector_dto_has_error_fallback(self):
        assert hasattr(FraudCollectorDTO, 'error_fallback')
        assert callable(FraudCollectorDTO.error_fallback)

    def test_fraud_collector_dto_error_fallback_returns_valid_dto(self):
        dto = FraudCollectorDTO.error_fallback("Test error", FallbackReason.NO_DATA)
        assert isinstance(dto, FraudCollectorDTO)
        assert dto.engine_status == EngineStatus.FAILED
        assert dto.error == "Test error"
        assert dto.total_patterns == 0
        assert dto.critical == 0
        assert dto.high == 0
        assert dto.medium == 0
        assert dto.low == 0
        assert dto.avg_confidence == 0.0
        assert dto.highest_confidence == 0.0
        assert dto.validated_patterns == 0
        assert dto.patterns == ()

    # ============================================================
    # GraphCollectorDTO Contract
    # ============================================================

    def test_graph_collector_dto_is_dataclass(self):
        assert is_dataclass(GraphCollectorDTO)

    def test_graph_collector_dto_signature(self):
        expected_fields = [
            ('entities', int),
            ('relationships', int),
            ('engine_type', object),
            ('engine_status', object),
            ('fallback_reason', object),
            ('error', object),
        ]
        actual_fields = [(f.name, f.type) for f in fields(GraphCollectorDTO)]
        assert len(actual_fields) == len(expected_fields)

    def test_graph_collector_dto_has_error_fallback(self):
        assert hasattr(GraphCollectorDTO, 'error_fallback')
        assert callable(GraphCollectorDTO.error_fallback)

    def test_graph_collector_dto_error_fallback_returns_valid_dto(self):
        dto = GraphCollectorDTO.error_fallback("Test error", FallbackReason.NO_DATA)
        assert isinstance(dto, GraphCollectorDTO)
        assert dto.engine_status == EngineStatus.FAILED
        assert dto.error == "Test error"
        assert dto.entities == 0
        assert dto.relationships == 0

    # ============================================================
    # EvidenceCollectorDTO Contract
    # ============================================================

    def test_evidence_collector_dto_is_dataclass(self):
        assert is_dataclass(EvidenceCollectorDTO)

    def test_evidence_collector_dto_signature(self):
        expected_fields = [
            ('total', int),
            ('verified', int),
            ('rejected', int),
            ('pending', int),
            ('avg_trust', float),
            ('avg_confidence', float),
            ('engine_type', object),
            ('engine_status', object),
            ('fallback_reason', object),
            ('error', object),
        ]
        actual_fields = [(f.name, f.type) for f in fields(EvidenceCollectorDTO)]
        assert len(actual_fields) == len(expected_fields)

    def test_evidence_collector_dto_has_error_fallback(self):
        assert hasattr(EvidenceCollectorDTO, 'error_fallback')
        assert callable(EvidenceCollectorDTO.error_fallback)

    def test_evidence_collector_dto_error_fallback_returns_valid_dto(self):
        dto = EvidenceCollectorDTO.error_fallback("Test error", FallbackReason.NO_DATA)
        assert isinstance(dto, EvidenceCollectorDTO)
        assert dto.engine_status == EngineStatus.FAILED
        assert dto.error == "Test error"
        assert dto.total == 0
        assert dto.verified == 0
        assert dto.rejected == 0
        assert dto.pending == 0
        assert dto.avg_trust == 0.0
        assert dto.avg_confidence == 0.0

    # ============================================================
    # ProcurementCollectorDTO Contract
    # ============================================================

    def test_procurement_collector_dto_is_dataclass(self):
        assert is_dataclass(ProcurementCollectorDTO)

    def test_procurement_collector_dto_signature(self):
        expected_fields = [
            ('packages', int),
            ('vendors', int),
            ('instansi_count', int),
            ('avg_value', float),
            ('total_value', float),
            ('engine_type', object),
            ('engine_status', object),
            ('fallback_reason', object),
            ('error', object),
        ]
        actual_fields = [(f.name, f.type) for f in fields(ProcurementCollectorDTO)]
        assert len(actual_fields) == len(expected_fields)

    def test_procurement_collector_dto_has_error_fallback(self):
        assert hasattr(ProcurementCollectorDTO, 'error_fallback')
        assert callable(ProcurementCollectorDTO.error_fallback)

    def test_procurement_collector_dto_error_fallback_returns_valid_dto(self):
        dto = ProcurementCollectorDTO.error_fallback("Test error", FallbackReason.NO_DATA)
        assert isinstance(dto, ProcurementCollectorDTO)
        assert dto.engine_status == EngineStatus.FAILED
        assert dto.error == "Test error"
        assert dto.packages == 0
        assert dto.vendors == 0
        assert dto.instansi_count == 0
        assert dto.avg_value == 0.0
        assert dto.total_value == 0.0
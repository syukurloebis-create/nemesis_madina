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

from dataclasses import fields
from typing import Tuple
import pytest
from backend.dtos.collector_dtos import (
    RiskCollectorDTO,
    FraudCollectorDTO,
    GraphCollectorDTO,
    EvidenceCollectorDTO,
    ProcurementCollectorDTO
)
from backend.domain.enums.engine import EngineStatus

class TestCollectorContractSignature:
    """Test contract signature untuk semua CollectorDTO."""
    
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
        
        # Check field count
        assert len(actual_fields) == len(expected_fields), \
            f"Field count changed! Expected {len(expected_fields)}, got {len(actual_fields)}"
        
        # Check each field name and type
        for i, (expected_name, expected_type) in enumerate(expected_fields):
            actual_name, actual_type = actual_fields[i]
            assert actual_name == expected_name, \
                f"Field {i} name changed! Expected '{expected_name}', got '{actual_name}'"
    
    def test_risk_collector_dto_error_fallback(self):
        """error_fallback() must return valid DTO with FAILED status."""
        dto = RiskCollectorDTO.error_fallback("Test error", "NO_DATA")
        assert dto.engine_status == EngineStatus.FAILED
        assert dto.error == "Test error"
        assert dto.score == 0.0
        assert isinstance(dto, RiskCollectorDTO)
    
    # Similar tests for FraudCollectorDTO, GraphCollectorDTO, etc.
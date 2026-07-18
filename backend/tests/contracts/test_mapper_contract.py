# tests/contracts/test_mapper_contract.py - FIXED

import inspect
import pytest
from backend.mappers.risk_mapper import RiskMapper
from backend.mappers.fraud_mapper import FraudMapper
from backend.mappers.graph_mapper import GraphMapper
from backend.mappers.evidence_mapper import EvidenceMapper
from backend.mappers.procurement_mapper import ProcurementMapper


class TestMapperContract:
    """Test semua mapper mengikuti contract yang diverifikasi."""

    # ============================================================
    # HELPER: Get signature parameters without 'self'
    # ============================================================

    @staticmethod
    def _get_params(method):
        """Get parameter names from signature, excluding 'self'."""
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        # Remove 'self' if present (unbound method)
        if params and params[0] == "self":
            params = params[1:]
        return params

    # ============================================================
    # EXPECTED SIGNATURES - BERDASARKAN IMPLEMENTASI AKTUAL
    # ============================================================

    EXPECTED_SIGNATURES = {
        RiskMapper: ["dto", "calculated"],
        FraudMapper: ["dto", "calculated"],
        EvidenceMapper: ["dto", "calculated"],
        GraphMapper: ["dto"],
        ProcurementMapper: ["dto"],
    }

    # ============================================================
    # Signature Tests - ABI Freeze
    # ============================================================

    def test_risk_mapper_signature(self):
        """RiskMapper.to_summary must accept (dto, calculated)."""
        params = self._get_params(RiskMapper.to_summary)
        expected = self.EXPECTED_SIGNATURES[RiskMapper]
        assert params == expected, \
            f"RiskMapper signature mismatch! Expected {expected}, got {params}"

    def test_fraud_mapper_signature(self):
        """FraudMapper.to_summary must accept (dto, calculated)."""
        params = self._get_params(FraudMapper.to_summary)
        expected = self.EXPECTED_SIGNATURES[FraudMapper]
        assert params == expected, \
            f"FraudMapper signature mismatch! Expected {expected}, got {params}"

    def test_evidence_mapper_signature(self):
        """EvidenceMapper.to_summary must accept (dto, calculated)."""
        params = self._get_params(EvidenceMapper.to_summary)
        expected = self.EXPECTED_SIGNATURES[EvidenceMapper]
        assert params == expected, \
            f"EvidenceMapper signature mismatch! Expected {expected}, got {params}"

    def test_graph_mapper_signature(self):
        """GraphMapper.to_summary must accept (dto)."""
        params = self._get_params(GraphMapper.to_summary)
        expected = self.EXPECTED_SIGNATURES[GraphMapper]
        assert params == expected, \
            f"GraphMapper signature mismatch! Expected {expected}, got {params}"

    def test_procurement_mapper_signature(self):
        """ProcurementMapper.to_summary must accept (dto)."""
        params = self._get_params(ProcurementMapper.to_summary)
        expected = self.EXPECTED_SIGNATURES[ProcurementMapper]
        assert params == expected, \
            f"ProcurementMapper signature mismatch! Expected {expected}, got {params}"
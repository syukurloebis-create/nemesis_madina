# backend/infrastructure/mappers/procurement_mapper.py
"""
NEMESIS Madina - Procurement Analysis Mapper
✅ Maps ProcurementAnalysis Value Object ↔ JSONB
✅ Stateless, pure functions
"""

from typing import Optional, Dict, Any
from backend.domain.value_objects.procurement_analysis import ProcurementAnalysis


class ProcurementAnalysisMapper:
    """Procurement Analysis mapper for DDD infrastructure."""

    @staticmethod
    def to_dict(analysis: Optional[ProcurementAnalysis]) -> Optional[Dict[str, Any]]:
        """Convert domain object to JSONB data."""
        if analysis is None:
            return None
        
        return {
            "case_id": analysis.case_id,
            "total_spend": analysis.total_spend,
            "vendor_count": analysis.vendor_count,
            "transaction_count": analysis.transaction_count,
            "flagged_transactions": analysis.flagged_transactions,
            "high_risk_vendors": analysis.high_risk_vendors,
            "duplicate_invoices": analysis.duplicate_invoices,
            "irregular_patterns": analysis.irregular_patterns,
            "fraud_indicators": analysis.fraud_indicators,
            "risk_score": analysis.risk_score,
            "confidence": analysis.confidence,
            "packages": analysis.packages,
            "vendors": analysis.vendors,
            "instansi_count": analysis.instansi_count,
            "total_value": analysis.total_value,
            "avg_value": analysis.avg_value,
            "completed": analysis.completed,
            "engine_status": analysis.engine_status,
        }

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> Optional[ProcurementAnalysis]:
        """Convert JSONB data to domain object."""
        if data is None:
            return None
        
        return ProcurementAnalysis(
            case_id=data.get("case_id", ""),
            total_spend=float(data.get("total_spend", 0.0)),
            vendor_count=data.get("vendor_count", 0),
            transaction_count=data.get("transaction_count", 0),
            flagged_transactions=data.get("flagged_transactions", 0),
            high_risk_vendors=data.get("high_risk_vendors", 0),
            duplicate_invoices=data.get("duplicate_invoices", 0),
            irregular_patterns=data.get("irregular_patterns", []),
            fraud_indicators=data.get("fraud_indicators", []),
            risk_score=float(data.get("risk_score", 0.0)),
            confidence=float(data.get("confidence", 0.0)),
            packages=data.get("packages", []),
            vendors=data.get("vendors", []),
            instansi_count=data.get("instansi_count", 0),
            total_value=float(data.get("total_value", 0.0)),
            avg_value=float(data.get("avg_value", 0.0)),
            completed=data.get("completed", False),
            engine_status=data.get("engine_status", "UNKNOWN"),
        )
"""
SQL Audit Helper — For Contract Testing Only.

Architecture Decision:
- SQL Audit Helper is ONLY for testing
- NOT a runtime service
- Used as baseline for contract tests
"""

from dataclasses import dataclass
from typing import Tuple
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class FraudAuditExpected:
    """Expected values dari SQL Audit #3.1."""
    total_patterns: int
    critical: int
    high: int
    medium: int
    low: int
    avg_confidence: float
    highest_confidence: float
    validated: int


@dataclass
class RiskAuditExpected:
    """Expected values dari SQL Audit #6.1."""
    score: float
    level: str
    anomaly_score: float
    collusion_score: float
    financial_score: float


@dataclass
class EvidenceAuditExpected:
    """Expected values dari SQL Audit #5.1."""
    total: int
    verified: int
    rejected: int
    pending: int
    avg_trust: float
    avg_confidence: float


@dataclass
class ProcurementAuditExpected:
    """Expected values dari SQL Audit #7.1."""
    packages: int
    vendors: int
    instansi_count: int
    avg_value: float
    total_value: float


class SQLAuditHelper:
    """
    SQL Audit Helper — HANYA untuk test.
    
    BUKAN runtime service.
    Digunakan di contract test sebagai baseline.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_fraud_expected(self, case_id: UUID) -> FraudAuditExpected:
        """Jalankan SQL Audit #3.1."""
        result = await self._session.execute(
            text("""
                SELECT 
                    COUNT(*) as total_patterns,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'CRITICAL') as critical,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'HIGH') as high,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'MEDIUM') as medium,
                    COUNT(*) FILTER (WHERE UPPER(severity) = 'LOW') as low,
                    AVG(confidence_score) as avg_confidence,
                    MAX(confidence_score) as highest_confidence,
                    COUNT(*) FILTER (WHERE is_validated = true) as validated
                FROM pattern_detections
                WHERE case_id = :case_id
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        return FraudAuditExpected(
            total_patterns=row.total_patterns if row else 0,
            critical=row.critical if row else 0,
            high=row.high if row else 0,
            medium=row.medium if row else 0,
            low=row.low if row else 0,
            avg_confidence=float(row.avg_confidence or 0) if row else 0,
            highest_confidence=float(row.highest_confidence or 0) if row else 0,
            validated=row.validated if row else 0
        )
    
    async def get_graph_expected(self, case_id: UUID) -> Tuple[int, int]:
        """Jalankan SQL Audit #4.1."""
        result = await self._session.execute(
            text("""
                SELECT
                    (SELECT COUNT(*) FROM graph_entities WHERE case_id = :case_id) as entities,
                    (SELECT COUNT(*) FROM graph_relationships WHERE case_id = :case_id) as relationships
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        return (
            row.entities if row else 0,
            row.relationships if row else 0
        )
    
    async def get_risk_expected(self, case_id: UUID) -> RiskAuditExpected:
        """Jalankan SQL Audit #6.1."""
        result = await self._session.execute(
            text("""
                SELECT
                    overall_score,
                    risk_level,
                    anomaly_score,
                    collusion_score,
                    financial_score
                FROM risk_scores
                WHERE case_id = :case_id
                ORDER BY calculated_at DESC
                LIMIT 1
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        return RiskAuditExpected(
            score=float(row.overall_score or 0) if row else 0,
            level=row.risk_level if row else "UNKNOWN",
            anomaly_score=float(row.anomaly_score or 0) if row else 0,
            collusion_score=float(row.collusion_score or 0) if row else 0,
            financial_score=float(row.financial_score or 0) if row else 0
        )
    
    async def get_evidence_expected(self, case_id: UUID) -> EvidenceAuditExpected:
        """Jalankan SQL Audit #5.1."""
        result = await self._session.execute(
            text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE UPPER(status) = 'VERIFIED') as verified,
                    COUNT(*) FILTER (WHERE UPPER(status) = 'REJECTED') as rejected,
                    COUNT(*) FILTER (WHERE UPPER(status) = 'PENDING') as pending,
                    AVG(COALESCE(trust_score, 0)) as avg_trust,
                    AVG(COALESCE(confidence_score, 0)) as avg_confidence
                FROM evidence
                WHERE case_id = :case_id
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        return EvidenceAuditExpected(
            total=row.total if row else 0,
            verified=row.verified if row else 0,
            rejected=row.rejected if row else 0,
            pending=row.pending if row else 0,
            avg_trust=float(row.avg_trust or 0) if row else 0,
            avg_confidence=float(row.avg_confidence or 0) if row else 0
        )
    
    async def get_procurement_expected(self) -> ProcurementAuditExpected:
        """Jalankan SQL Audit #7.1."""
        result = await self._session.execute(
            text("""
                SELECT
                    COUNT(*) as packages,
                    COUNT(DISTINCT nama_penyedia) as vendors,
                    COUNT(DISTINCT nama_instansi) as instansi_count,
                    AVG(total_nilai) as avg_value,
                    SUM(total_nilai) as total_value
                FROM rup_paket_detailed
            """)
        )
        row = result.fetchone()
        
        return ProcurementAuditExpected(
            packages=row.packages if row else 0,
            vendors=row.vendors if row else 0,
            instansi_count=row.instansi_count if row else 0,
            avg_value=float(row.avg_value or 0) if row else 0,
            total_value=float(row.total_value or 0) if row else 0
        )
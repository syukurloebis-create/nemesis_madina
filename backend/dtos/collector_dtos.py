"""
Collector DTOs — Immutable, Slots, Memory Efficient.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Any
from datetime import datetime

from backend.domain.enums import EngineType, EngineStatus, FallbackReason, Severity


@dataclass(frozen=True, slots=True)
class PatternDTO:
    """Pattern Data Transfer Object — Immutable."""
    pattern_type: str
    severity: Severity
    confidence: float
    validated: bool
    detected_at: Optional[datetime] = None


@dataclass(frozen=True, slots=True)
class FraudCollectorDTO:
    """
    Fraud Collector DTO — Immutable, Memory Efficient.

    HANYA membawa data mentah dari database.
    TIDAK ADA perhitungan di sini.
    """
    total_patterns: int
    critical: int
    high: int
    medium: int
    low: int
    avg_confidence: float
    highest_confidence: float
    validated_patterns: int
    patterns: Tuple[PatternDTO, ...]

    # Metadata — menggunakan Enum
    engine_type: EngineType = EngineType.FRAUD
    engine_status: EngineStatus = EngineStatus.OK
    fallback_reason: Optional[FallbackReason] = None
    error: Optional[str] = None

    @classmethod
    def error_fallback(
        cls,
        error: str,
        reason: FallbackReason
    ) -> "FraudCollectorDTO":
        """Factory method untuk error fallback."""
        return cls(
            total_patterns=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            avg_confidence=0,
            highest_confidence=0,
            validated_patterns=0,
            patterns=(),
            engine_status=EngineStatus.FAILED,
            fallback_reason=reason,
            error=error
        )


@dataclass(frozen=True, slots=True)
class GraphCollectorDTO:
    """Graph Collector DTO — Immutable, Typed."""
    entities: int
    relationships: int
    engine_type: EngineType = EngineType.GRAPH
    engine_status: EngineStatus = EngineStatus.OK
    fallback_reason: Optional[FallbackReason] = None
    error: Optional[str] = None

    @classmethod
    def error_fallback(cls, error: str, reason: FallbackReason) -> "GraphCollectorDTO":
        return cls(
            entities=0,
            relationships=0,
            engine_status=EngineStatus.FAILED,
            fallback_reason=reason,
            error=error
        )


@dataclass(frozen=True, slots=True)
class RiskCollectorDTO:
    """Risk Collector DTO — Immutable, Typed."""
    score: float
    level: str
    anomaly_score: float
    collusion_score: float
    financial_score: float
    recommendations: Tuple[str, ...] = ()

    engine_type: EngineType = EngineType.RISK
    engine_status: EngineStatus = EngineStatus.OK
    fallback_reason: Optional[FallbackReason] = None
    error: Optional[str] = None

    @classmethod
    def error_fallback(cls, error: str, reason: FallbackReason) -> "RiskCollectorDTO":
        return cls(
            score=0,
            level="UNKNOWN",
            anomaly_score=0,
            collusion_score=0,
            financial_score=0,
            recommendations=(),
            engine_status=EngineStatus.FAILED,
            fallback_reason=reason,
            error=error
        )


@dataclass(frozen=True, slots=True)
class EvidenceCollectorDTO:
    """Evidence Collector DTO — Immutable, Typed."""
    total: int
    verified: int
    rejected: int
    pending: int
    avg_trust: float
    avg_confidence: float

    engine_type: EngineType = EngineType.EVIDENCE
    engine_status: EngineStatus = EngineStatus.OK
    fallback_reason: Optional[FallbackReason] = None
    error: Optional[str] = None

    @classmethod
    def error_fallback(cls, error: str, reason: FallbackReason) -> "EvidenceCollectorDTO":
        return cls(
            total=0,
            verified=0,
            rejected=0,
            pending=0,
            avg_trust=0,
            avg_confidence=0,
            engine_status=EngineStatus.FAILED,
            fallback_reason=reason,
            error=error
        )


@dataclass(frozen=True, slots=True)
class ProcurementCollectorDTO:
    """Procurement Collector DTO — Immutable, Typed."""
    packages: int
    vendors: int
    instansi_count: int
    avg_value: float
    total_value: float

    engine_type: EngineType = EngineType.PROCUREMENT
    engine_status: EngineStatus = EngineStatus.OK
    fallback_reason: Optional[FallbackReason] = None
    error: Optional[str] = None

    @classmethod
    def error_fallback(cls, error: str, reason: FallbackReason) -> "ProcurementCollectorDTO":
        return cls(
            packages=0,
            vendors=0,
            instansi_count=0,
            avg_value=0,
            total_value=0,
            engine_status=EngineStatus.FAILED,
            fallback_reason=reason,
            error=error
        )
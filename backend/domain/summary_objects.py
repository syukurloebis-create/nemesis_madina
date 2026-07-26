"""
Summary Objects — Pydantic Models for Read Models.

ADR-017, ADR-019, ADR-021:
- Summary = Read Model, NOT Entity, NOT Aggregate
- Contract validation = INVARIANT ONLY
- HANYA engine_status — TIDAK ADA field status
- Semua Summary frozen=True (immutable)
- List → Tuple untuk immutable collections
"""

from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict
from typing import Optional, Tuple, Dict, Any
from datetime import datetime, timezone

# ===== Import dari package enums (bukan file enums.py) =====
from backend.domain.enums import (
    Severity,
    EngineStatus,
    EngineName,
    DashboardStatus,
    RecoveryState,
    EvidenceLevel,
    RiskLevel,
)


# ============================================================================
# 1. FRAUD PATTERN SUMMARY
# ============================================================================

class FraudPatternSummary(BaseModel):
    """Fraud Pattern Summary — Immutable Read Model."""
    
    model_config = ConfigDict(frozen=True)
    
    type: str = Field(..., description="Pattern type identifier")
    severity: Severity = Field(..., description="Pattern severity level")
    confidence: float = Field(ge=0, le=100, description="Confidence score 0-100")
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    validated: bool = Field(default=False)
    description: Optional[str] = Field(default=None)


# ============================================================================
# 2. FRAUD SUMMARY
# ============================================================================

class FraudSummary(BaseModel):
    """Fraud Summary — Immutable Read Model."""
    
    model_config = ConfigDict(frozen=True)
    
    # ===== Stats =====
    overall_risk: Severity = Severity.UNKNOWN
    score: float = Field(ge=0, le=100, default=0)
    active_alerts: int = Field(ge=0, default=0)
    high_confidence: int = Field(ge=0, default=0)
    total_patterns: int = Field(ge=0, default=0)
    validated_patterns: int = Field(ge=0, default=0)
    highest_confidence: float = Field(ge=0, le=100, default=0)
    average_confidence: float = Field(ge=0, le=100, default=0)
    
    # ===== Patterns (TUPLE — immutable) =====
    patterns: Tuple[FraudPatternSummary, ...] = Field(default=())
    
    # ===== Engine Metadata =====
    engine: EngineName = EngineName.FRAUD  # ← Enum, bukan Literal
    engine_status: EngineStatus = EngineStatus.OK

    @field_validator("engine_status")
    @classmethod
    def validate_engine_status(cls, v: EngineStatus) -> EngineStatus:
        if not isinstance(v, EngineStatus):
            raise ValueError(f"engine_status must be one of {list(EngineStatus)}")
        return v

    @field_validator("overall_risk")
    @classmethod
    def validate_overall_risk(cls, v: Severity) -> Severity:
        if not isinstance(v, Severity):
            raise ValueError(f"overall_risk must be one of {list(Severity)}")
        return v

    @model_validator(mode="after")
    def validate_contract(self) -> "FraudSummary":
        if self.total_patterns < len(self.patterns):
            raise ValueError(
                f"total_patterns ({self.total_patterns}) cannot be less than "
                f"len(patterns) ({len(self.patterns)})"
            )
        if self.validated_patterns > self.total_patterns:
            raise ValueError(
                f"validated_patterns ({self.validated_patterns}) cannot exceed "
                f"total_patterns ({self.total_patterns})"
            )
        if self.highest_confidence < self.average_confidence:
            raise ValueError(
                f"highest_confidence ({self.highest_confidence}) cannot be "
                f"less than average_confidence ({self.average_confidence})"
            )
        return self

    @property
    def has_data(self) -> bool:
        return (
            self.score > 0
            or self.total_patterns > 0
            or self.active_alerts > 0
            or self.high_confidence > 0
        )

    @classmethod
    def empty(cls) -> "FraudSummary":
        return cls()


# ============================================================================
# 3. RISK SUMMARY
# ============================================================================

class RiskSummary(BaseModel):
    """Risk Summary — Immutable Read Model."""
    
    model_config = ConfigDict(frozen=True)
    
    score: float = Field(ge=0, le=100, default=0)
    level: RiskLevel = RiskLevel.UNKNOWN
    anomaly_score: float = Field(ge=0, le=100, default=0)
    collusion_score: float = Field(ge=0, le=100, default=0)
    financial_score: float = Field(ge=0, le=100, default=0)
    
    # ===== Recommendations (TUPLE — immutable) =====
    recommendations: Tuple[str, ...] = Field(default=())
    
    # ===== Engine Metadata =====
    engine: EngineName = EngineName.RISK  # ← Enum, bukan Literal
    engine_status: EngineStatus = EngineStatus.OK

    @field_validator("engine_status")
    @classmethod
    def validate_engine_status(cls, v: EngineStatus) -> EngineStatus:
        if not isinstance(v, EngineStatus):
            raise ValueError(f"engine_status must be one of {list(EngineStatus)}")
        return v

    @property
    def has_data(self) -> bool:
        return (
            self.score > 0
            or self.anomaly_score > 0
            or self.collusion_score > 0
            or self.financial_score > 0
        )

    @classmethod
    def empty(cls) -> "RiskSummary":
        return cls()


# ============================================================================
# 4. GRAPH SUMMARY
# ============================================================================

class GraphSummary(BaseModel):
    """Graph Summary — Immutable Read Model."""
    
    model_config = ConfigDict(frozen=True)
    
    entities: int = Field(ge=0, default=0)
    relationships: int = Field(ge=0, default=0)
    
    # ===== Engine Metadata =====
    engine: EngineName = EngineName.GRAPH  # ← Enum, bukan Literal
    engine_status: EngineStatus = EngineStatus.OK

    @field_validator("engine_status")
    @classmethod
    def validate_engine_status(cls, v: EngineStatus) -> EngineStatus:
        if not isinstance(v, EngineStatus):
            raise ValueError(f"engine_status must be one of {list(EngineStatus)}")
        return v

    @property
    def has_data(self) -> bool:
        return self.entities > 0 or self.relationships > 0

    @classmethod
    def empty(cls) -> "GraphSummary":
        return cls()

# ============================================================================
# 5. EVIDENCE SUMMARY
# ============================================================================

class EvidenceSummary(BaseModel):
    """Evidence Summary — Immutable Read Model."""
    
    model_config = ConfigDict(frozen=True)
    
    score: float = Field(ge=0, le=100, default=0)
    level: EvidenceLevel = EvidenceLevel.NO_DATA
    total: int = Field(ge=0, default=0)
    verified: int = Field(ge=0, default=0)
    rejected: int = Field(ge=0, default=0)
    pending: int = Field(ge=0, default=0)
    avg_trust: float = Field(ge=0, le=100, default=0)
    avg_confidence: float = Field(ge=0, le=100, default=0)
    
    # ===== Engine Metadata =====
    engine: EngineName = EngineName.EVIDENCE  # ← Enum, bukan Literal
    engine_status: EngineStatus = EngineStatus.OK

    @field_validator("engine_status")
    @classmethod
    def validate_engine_status(cls, v: EngineStatus) -> EngineStatus:
        if not isinstance(v, EngineStatus):
            raise ValueError(f"engine_status must be one of {list(EngineStatus)}")
        return v

    @property
    def has_data(self) -> bool:
        return self.total > 0 or self.verified > 0

    @classmethod
    def empty(cls) -> "EvidenceSummary":
        return cls()


# ============================================================================
# 6. PROCUREMENT SUMMARY
# ============================================================================

class ProcurementSummary(BaseModel):
    """Procurement Summary — Immutable Read Model."""
    
    model_config = ConfigDict(frozen=True)
    
    packages: int = Field(ge=0, default=0)
    vendors: int = Field(ge=0, default=0)
    instansi_count: int = Field(ge=0, default=0)
    total_value: float = Field(ge=0, default=0)
    avg_value: float = Field(ge=0, default=0)
    completed: int = Field(ge=0, default=0)
    
    # ===== Engine Metadata =====
    engine: EngineName = EngineName.PROCUREMENT  # ← Enum, bukan Literal
    engine_status: EngineStatus = EngineStatus.OK

    @field_validator("engine_status")
    @classmethod
    def validate_engine_status(cls, v: EngineStatus) -> EngineStatus:
        if not isinstance(v, EngineStatus):
            raise ValueError(f"engine_status must be one of {list(EngineStatus)}")
        return v

    @property
    def has_data(self) -> bool:
        return self.packages > 0 or self.vendors > 0 or self.total_value > 0

    @classmethod
    def empty(cls) -> "ProcurementSummary":
        return cls()


# ============================================================================
# 7. RECOVERY SUMMARY - DENGAN 2 STATUS (Enum)
# ============================================================================

class RecoverySummary(BaseModel):
    """
    Recovery Summary — dengan 2 status terpisah (enum).
    
    - engine_status: Status engine (OK/FAILED/PARTIAL/SKIPPED)
    - business_state: Status bisnis recovery (RecoveryState enum)
    """
    
    model_config = ConfigDict(frozen=True)
    
    business_state: RecoveryState = Field(default=RecoveryState.READY)
    
    # ===== Actions (TUPLE — immutable) =====
    actions: Tuple[Dict[str, Any], ...] = Field(default=())
    
    # ===== Engine Metadata =====
    engine: EngineName = EngineName.RECOVERY  # ← Enum, bukan Literal
    engine_status: EngineStatus = EngineStatus.OK

    @field_validator("engine_status")
    @classmethod
    def validate_engine_status(cls, v: EngineStatus) -> EngineStatus:
        if not isinstance(v, EngineStatus):
            raise ValueError(f"engine_status must be one of {list(EngineStatus)}")
        return v

    @property
    def has_data(self) -> bool:
        return len(self.actions) > 0

    @classmethod
    def empty(cls) -> "RecoverySummary":
        return cls(actions=())


# ============================================================================
# 8. DASHBOARD SUMMARY
# ============================================================================

class DashboardSummary(BaseModel):
    case_id: str
    risk: RiskSummary
    fraud: FraudSummary
    graph: GraphSummary
    evidence: EvidenceSummary
    procurement: ProcurementSummary
    recovery: RecoverySummary
    confidence: float = 0.0

    @property
    def has_data(self) -> bool:
        return any([
            self.risk.has_data,
            self.fraud.has_data,
            self.graph.has_data,
            self.evidence.has_data,
            self.procurement.has_data,
            self.recovery.has_data,
        ])

    @classmethod
    def empty(cls) -> "DashboardSummary":
        return cls(
            case_id="",
            risk=RiskSummary.empty(),
            fraud=FraudSummary.empty(),
            graph=GraphSummary.empty(),
            evidence=EvidenceSummary.empty(),
            procurement=ProcurementSummary.empty(),
            recovery=RecoverySummary.empty(),
            confidence=0.0,
        )
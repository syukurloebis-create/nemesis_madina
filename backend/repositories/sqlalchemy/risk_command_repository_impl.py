"""
Risk Command Repository — WRITE only.
SQLAlchemy ORM Implementation.
Complete rewrite - no SQLRepository, no SQLKey, no SQL files.
"""

from uuid import UUID
from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, update

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.intelligence.models import RiskScore, RiskLevel
from backend.domain.enums.risk_calculation_source import RiskCalculationSource
from backend.dtos.risk_snapshot_projection import RiskSnapshotProjection
from backend.repositories.interfaces.risk_command_repository import IRiskCommandRepository
from backend.cases.models import Case


# LEVEL_MAP - module level, tidak dibuat ulang per method
LEVEL_MAP = {
    "CRITICAL": RiskLevel.CRITICAL,
    "HIGH": RiskLevel.HIGH,
    "MEDIUM": RiskLevel.MEDIUM,
    "LOW": RiskLevel.LOW,
    "INFO": RiskLevel.INFO,
}


class RiskCommandRepositoryImpl(IRiskCommandRepository):
    """
    Risk Command Repository using SQLAlchemy ORM.
    
    This repository handles ALL write operations for risk data:
    - risk_scores table (ORM: RiskScore)
    - cases.latest_risk column (ORM: Case)
    
    No SQLRepository, no SQLKey, no SQL files.
    Uses AsyncSession from UnitOfWork.
    """

    def __init__(self):
        """Initialize repository without any dependencies."""
        pass

    async def save_or_update(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        data: Dict[str, Any],
        calculated_by: RiskCalculationSource = RiskCalculationSource.SYSTEM,
    ) -> None:
        """
        Save or update risk score using ORM.

        Canonical contract v3:
        - Writes 4 canonical components: findings_risk, graph_risk, fraud_risk, evidence_risk
        - Writes 2 JSON snapshots: components, weights
        - Writes 3 legacy aliases: anomaly_score, collusion_score, financial_score
        - Writes temporal_score = 0 (belum diimplementasikan)
        - Preserves factors, recommendations

        Idempotency: case_id unique constraint menjamin 1 row per case.

        Args:
            uow: Unit of Work with AsyncSession
            case_id: Case UUID
            data: Risk score data dictionary (from RiskProjectionMapper)
            calculated_by: Source of calculation (SYSTEM, USER, etc.)
        """
        # ===== Extract data with safe defaults =====
        overall_score = data.get("overall_score", 0.0)
        risk_level_str = str(data.get("risk_level", "INFO")).upper()
        risk_level = LEVEL_MAP.get(risk_level_str, RiskLevel.INFO)

        # Canonical components (v3)
        findings_risk = data.get("findings_risk")
        graph_risk = data.get("graph_risk")
        fraud_risk = data.get("fraud_risk")
        evidence_risk = data.get("evidence_risk")

        # JSON snapshots
        components = data.get("components")
        weights = data.get("weights")

        # Legacy aliases (fallback ke canonical jika tidak ada)
        anomaly_score = data.get("anomaly_score", findings_risk if findings_risk is not None else 0.0)
        collusion_score = data.get("collusion_score", graph_risk if graph_risk is not None else 0.0)
        financial_score = data.get("financial_score", fraud_risk if fraud_risk is not None else 0.0)
        temporal_score = data.get("temporal_score", 0.0)

        # ===== Check if risk score exists =====
        stmt = select(RiskScore).where(RiskScore.case_id == case_id)
        result = await uow.session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # ===== UPDATE existing record =====
            # Core
            existing.overall_score = overall_score
            existing.risk_level = risk_level

            # Canonical (v3)
            existing.findings_risk = findings_risk 
            existing.graph_risk = graph_risk
            existing.fraud_risk = fraud_risk
            existing.evidence_risk = evidence_risk
            existing.components = components
            existing.weights = weights

            # Legacy aliases
            existing.anomaly_score = anomaly_score
            existing.collusion_score = collusion_score
            existing.financial_score = financial_score
            existing.temporal_score = temporal_score

            # Metadata
            existing.factors = data.get("factors", [])
            existing.recommendations = data.get("recommendations", [])
            existing.calculated_by = calculated_by.value
            existing.calculated_at = datetime.now(timezone.utc)
        else:
            # ===== INSERT new record =====
            risk_score = RiskScore(
                case_id=case_id,
                overall_score=overall_score,
                risk_level=risk_level,
                # Canonical (v3)
                findings_risk=findings_risk,
                graph_risk=graph_risk,
                fraud_risk=fraud_risk,
                evidence_risk=evidence_risk,
                components=components,
                weights=weights,
                # Legacy aliases
                anomaly_score=anomaly_score,
                collusion_score=collusion_score,
                financial_score=financial_score,
                temporal_score=temporal_score,
                # Metadata
                factors=data.get("factors", []),
                recommendations=data.get("recommendations", []),
                calculated_by=calculated_by.value,
                # calculated_at: server_default
            )
            uow.session.add(risk_score)

    async def update_case_snapshot(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        snapshot: RiskSnapshotProjection,
    ) -> None:
        """
        Update cases.latest_risk for dashboard using UPDATE directly.
        
        Uses direct UPDATE instead of loading object for better performance
        and to avoid identity map pollution (CQRS-friendly).
        
        Args:
            uow: Unit of Work with AsyncSession
            case_id: Case UUID
            snapshot: RiskSnapshotProjection DTO
        """
        await uow.session.execute(
            update(Case)
            .where(Case.id == case_id)
            .values(latest_risk=snapshot.to_dict())
        )
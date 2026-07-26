"""
NEMESIS Madina - Command Pipeline Integration Test
✅ Tests full application pipeline: DTO → Calculator → Mapper → Aggregate → Repository
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone

from backend.bootstrap.functions import bootstrap_infrastructure
from backend.bootstrap.container_builder import build_application_container
from backend.infrastructure.parallel_executor import CollectorResultRegistry
from backend.application.commands.analysis_mapper import AnalyzeCaseCommand
from backend.domain.value_objects.case_id import CaseId
from backend.domain.enums.risk_level import RiskLevel
from backend.domain.enums import Severity, EngineStatus, EngineType
from backend.infrastructure.models.projection_checkpoint import Base as CheckpointBase
from backend.infrastructure.models.read_models import Base as ReadBase
from backend.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.dtos.collector_dtos import (
    PatternDTO,
    FraudCollectorDTO,
    RiskCollectorDTO,
    EvidenceCollectorDTO,
    GraphCollectorDTO,
    ProcurementCollectorDTO,
)


# ============================================================
# TEST HELPERS (Temporary - will move to helpers/dto_factory.py)
# ============================================================

def make_pattern_dto(pattern_type: str, severity: Severity, confidence: float, validated: bool = True):
    return PatternDTO(
        pattern_type=pattern_type,
        severity=severity,
        confidence=confidence,
        validated=validated,
        detected_at=datetime.now(timezone.utc),
    )


def make_fraud_dto(confidence: float, severity: Severity, validated: bool = True) -> FraudCollectorDTO:
    pattern = make_pattern_dto("FRAUD", severity, confidence, validated)
    critical = 1 if severity == Severity.CRITICAL else 0
    high = 1 if severity == Severity.HIGH else 0
    medium = 1 if severity == Severity.MEDIUM else 0
    low = 1 if severity == Severity.LOW else 0
    total_patterns = critical + high + medium + low

    return FraudCollectorDTO(
        total_patterns=total_patterns,
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        avg_confidence=confidence,
        highest_confidence=confidence,
        validated_patterns=1 if validated else 0,
        patterns=(pattern,),
        engine_type=EngineType.FRAUD,
        engine_status=EngineStatus.OK,
    )


def make_risk_dto(score: float, level: str) -> RiskCollectorDTO:
    return RiskCollectorDTO(
        score=score,
        level=level,
        anomaly_score=score * 0.9,
        collusion_score=score * 0.8,
        financial_score=score * 0.95,
        recommendations=(),
        engine_type=EngineType.RISK,
        engine_status=EngineStatus.OK,
    )


def make_evidence_dto(total: int, verified: int, pending: int, rejected: int) -> EvidenceCollectorDTO:
    return EvidenceCollectorDTO(
        total=total,
        verified=verified,
        pending=pending,
        rejected=rejected,
        avg_trust=85.0,
        avg_confidence=88.0,
        engine_type=EngineType.EVIDENCE,
        engine_status=EngineStatus.OK,
    )


def make_graph_dto(entities: int, relationships: int) -> GraphCollectorDTO:
    return GraphCollectorDTO(
        entities=entities,
        relationships=relationships,
        engine_type=EngineType.GRAPH,
        engine_status=EngineStatus.OK,
    )


def make_procurement_dto(packages: int, vendors: int, instansi_count: int, total_value: float, avg_value: float) -> ProcurementCollectorDTO:
    return ProcurementCollectorDTO(
        packages=packages,
        vendors=vendors,
        instansi_count=instansi_count,
        avg_value=avg_value,
        total_value=total_value,
        engine_type=EngineType.PROCUREMENT,
        engine_status=EngineStatus.OK,
    )


# ============================================================
# TEST FIXTURES
# ============================================================

@pytest.fixture(scope="function")
async def container():
    engine = create_async_engine(settings.database.url, poolclass=NullPool, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(CheckpointBase.metadata.drop_all)
        await conn.run_sync(ReadBase.metadata.drop_all)
        await conn.run_sync(CheckpointBase.metadata.create_all)
        await conn.run_sync(ReadBase.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    infra = bootstrap_infrastructure(engine=engine, session_factory=session_factory).infrastructure
    container = build_application_container(infra)
    yield container
    await engine.dispose()


@pytest.fixture
async def uow_factory(container):
    return container.commands.analyze_case._uow_factory


# ============================================================
# INTEGRATION TESTS — Using DTOs
# ============================================================

@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_command_pipeline_with_fraud_data(container, uow_factory):
    case_id = uuid4()
    fraud_dto = make_fraud_dto(confidence=85.0, severity=Severity.HIGH)
    results = CollectorResultRegistry(fraud=fraud_dto)

    handler = container.commands.analyze_case
    command = AnalyzeCaseCommand(case_id=case_id, collector_results=results)
    await handler.execute(command)

    case_id_vo = CaseId(case_id)
    async with uow_factory.create() as uow:
        aggregate = await uow.cases.get(case_id_vo)
        assert aggregate is not None
        assert aggregate.latest_fraud is not None
        assert aggregate.latest_fraud.total_patterns == 1
        assert len(aggregate.latest_fraud.patterns) == 1
        assert aggregate.latest_fraud.patterns[0].confidence_score == 85.0
        assert isinstance(aggregate.latest_fraud.overall_risk, RiskLevel)
        assert aggregate.latest_fraud.score >= 0
        assert aggregate.version == 1


@pytest.mark.asyncio
async def test_command_pipeline_with_all_analyses(container, uow_factory):
    case_id = uuid4()

    fraud_dto = make_fraud_dto(confidence=70.0, severity=Severity.MEDIUM)
    risk_dto = make_risk_dto(score=80.0, level="HIGH")
    evidence_dto = make_evidence_dto(total=20, verified=15, pending=3, rejected=2)
    graph_dto = make_graph_dto(entities=50, relationships=120)
    procurement_dto = make_procurement_dto(
        packages=100, vendors=25, instansi_count=1,
        total_value=5000000000.0, avg_value=50000000.0
    )

    results = CollectorResultRegistry(
        fraud=fraud_dto,
        risk=risk_dto,
        evidence=evidence_dto,
        graph=graph_dto,
        procurement=procurement_dto,
    )

    handler = container.commands.analyze_case
    command = AnalyzeCaseCommand(case_id=case_id, collector_results=results)
    await handler.execute(command)

    case_id_vo = CaseId(case_id)
    async with uow_factory.create() as uow:
        aggregate = await uow.cases.get(case_id_vo)
        assert aggregate is not None

        # ✅ All analyses present
        assert aggregate.latest_fraud is not None
        assert aggregate.latest_risk is not None
        assert aggregate.latest_risk.score == 80.0
        assert aggregate.latest_evidence is not None
        assert aggregate.latest_evidence.total_count == 20
        assert aggregate.latest_evidence.verified_count == 15
        assert aggregate.latest_graph is not None
        assert aggregate.latest_graph.entities == 50
        assert aggregate.latest_procurement is not None
        assert aggregate.latest_procurement.packages == 100

        # ✅ Version = number of analyses (5)
        # Events are already consumed by Unit of Work
        expected_version = sum(
            1 for x in (
                aggregate.latest_fraud,
                aggregate.latest_risk,
                aggregate.latest_evidence,
                aggregate.latest_graph,
                aggregate.latest_procurement,
            ) if x is not None
        )
        assert aggregate.version == expected_version

@pytest.mark.asyncio
async def test_command_pipeline_rehydrates_aggregate(container, uow_factory):
    case_id = uuid4()

    # First command: Fraud only
    fraud_dto = make_fraud_dto(confidence=90.0, severity=Severity.HIGH)
    results = CollectorResultRegistry(fraud=fraud_dto)

    handler = container.commands.analyze_case
    command = AnalyzeCaseCommand(case_id=case_id, collector_results=results)
    await handler.execute(command)

    case_id_vo = CaseId(case_id)
    async with uow_factory.create() as uow:
        aggregate = await uow.cases.get(case_id_vo)
        assert aggregate is not None
        assert aggregate.latest_fraud is not None
        assert aggregate.version == 1

        # Second command: Update Fraud
        new_fraud_dto = make_fraud_dto(confidence=98.0, severity=Severity.CRITICAL)
        new_results = CollectorResultRegistry(fraud=new_fraud_dto)
        new_command = AnalyzeCaseCommand(case_id=case_id, collector_results=new_results)
        await handler.execute(new_command)

        updated_aggregate = await uow.cases.get(case_id_vo)
        assert updated_aggregate is not None
        assert updated_aggregate.latest_fraud is not None
        assert updated_aggregate.latest_fraud.score >= 0
        assert isinstance(updated_aggregate.latest_fraud.overall_risk, RiskLevel)
        assert updated_aggregate.version == 2 


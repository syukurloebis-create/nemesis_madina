# tests/contracts/conftest.py

import pytest
from dataclasses import replace
from uuid import UUID
from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.domain.enums import EngineStatus
from backend.bootstrap.functions import bootstrap_infrastructure
from backend.bootstrap.container_builder import build_application_container
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.repository_factory import RepositoryFactory
from backend.collectors.fraud_collector import FraudCollector
from backend.collectors.graph_collector import GraphCollector
from backend.collectors.risk_collector import RiskCollector
from backend.collectors.evidence_collector import EvidenceCollector
from backend.collectors.procurement_collector import ProcurementCollector
from backend.core.context import ExecutionContext
from backend.infrastructure.parallel_executor import CollectorResultRegistry
from backend.dtos.collector_dtos import (
    FraudCollectorDTO,
    GraphCollectorDTO,
    RiskCollectorDTO,
    EvidenceCollectorDTO,
    ProcurementCollectorDTO,
)



@pytest.fixture
def app_container(db_engine):
    """
    ApplicationContainer dengan bootstrap yang sama dengan production.
    
    Menggunakan bootstrap_infrastructure() + build_application_container()
    dengan override session_factory dan uow_factory menggunakan dataclasses.replace()
    """
    infra = bootstrap_infrastructure().infrastructure

    test_session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    test_uow_factory = UnitOfWorkFactory(test_session_factory)

    infra = replace(
        infra,
        session_factory=test_session_factory,
        uow_factory=test_uow_factory,
    )

    return build_application_container(infra)


@pytest.fixture
def uow_factory(db_uow_factory):
    """
    Compatibility alias.

    Semua contract test lama yang memakai
    uow_factory tetap bekerja tanpa diubah.
    """
    return db_uow_factory


@pytest.fixture
def db_uow_factory(app_container):
    """
    UnitOfWorkFactory yang digunakan ApplicationContainer.

    Contract tests harus menggunakan UoW yang sama
    dengan composition root production.
    """
    return app_container.infrastructure.uow_factory


@pytest.fixture
async def dashboard_service(app_container):
    """Dashboard service dari ApplicationContainer."""
    return app_container.services.dashboard


@pytest.fixture
async def case_intelligence(dashboard_service):
    """CaseIntelligence untuk contract tests (dipanggil sekali)."""
    case_uuid = UUID("446e216d-eb0e-487e-8e6b-ec943468ea20")
    context = ExecutionContext.create(case_uuid)
    return await dashboard_service.get_case_intelligence(case_uuid, context)


@pytest.fixture
def fraud_collector(app_container):
    """
    Production FraudCollector instance.
    
    Menggunakan collector yang sama dengan runtime production.
    Contract test harus menggunakan object yang sama dengan runtime.
    """
    return app_container.collectors.registry.get("fraud")


@pytest.fixture
def graph_collector(app_container):
    """Production GraphCollector instance."""
    return app_container.collectors.registry.get("graph")


@pytest.fixture
def risk_collector(app_container):
    """Production RiskCollector instance."""
    return app_container.collectors.registry.get("risk")


@pytest.fixture
def evidence_collector(app_container):
    """Production EvidenceCollector instance."""
    return app_container.collectors.registry.get("evidence")


@pytest.fixture
def procurement_collector(app_container):
    """Production ProcurementCollector instance."""
    return app_container.collectors.registry.get("procurement")


@pytest.fixture
def collector_registry():
    """
    CollectorResultRegistry dengan DTO valid untuk factory test.
    
    Digunakan untuk menguji CaseIntelligenceFactory.create_from_results()
    tanpa ketergantungan pada database.
    """
    registry = CollectorResultRegistry()

    registry.fraud = FraudCollectorDTO(
        total_patterns=2,
        critical=0,
        high=1,
        medium=1,
        low=0,
        avg_confidence=45.0,
        highest_confidence=80.0,
        validated_patterns=0,
        patterns=(),
        engine_status=EngineStatus.OK,
    )

    registry.graph = GraphCollectorDTO(
        entities=549,
        relationships=5471,
        engine_status=EngineStatus.OK,
    )

    registry.risk = RiskCollectorDTO(
        score=82.0,
        level="HIGH",
        anomaly_score=0,
        collusion_score=0,
        financial_score=0,
        recommendations=(),
        engine_status=EngineStatus.OK,
    )

    registry.evidence = EvidenceCollectorDTO(
        total=9,
        verified=7,
        rejected=0,
        pending=2,
        avg_trust=0,
        avg_confidence=0,
        engine_status=EngineStatus.OK,
    )

    registry.procurement = ProcurementCollectorDTO(
        packages=4,
        vendors=4,
        instansi_count=1,
        avg_value=0,
        total_value=0,
        engine_status=EngineStatus.OK,
    )

    return registry
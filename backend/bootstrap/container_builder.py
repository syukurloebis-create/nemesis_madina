"""
Application Container Builder — Single Composition Root.

Updated with Graph Components (Sprint 3.4B Phase 3).
"""

import os
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.container import (
    ApplicationContainer,
    InfrastructureContainer,
    CalculatorContainer,
    MapperContainer,
    DomainServiceContainer,
    CollectorContainer,
    ServiceContainer,
    HealthContainer,
)
from backend.core.version import VersionInfo
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.parallel_executor import ParallelExecutor
from backend.infrastructure.event_bus import InMemoryEventBus
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.calculators.config import CalculatorConfig
from backend.calculators.fraud_score_calculator import FraudScoreCalculator
from backend.calculators.risk_score_calculator import RiskScoreCalculator
from backend.calculators.evidence_score_calculator import EvidenceScoreCalculator
from backend.mappers.fraud_mapper import FraudMapper
from backend.mappers.graph_mapper import GraphMapper
from backend.mappers.risk_mapper import RiskMapper
from backend.mappers.evidence_mapper import EvidenceMapper
from backend.mappers.procurement_mapper import ProcurementMapper
from backend.factories.case_intelligence_factory import CaseIntelligenceFactory
from backend.services.domain.confidence_calculator import ConfidenceCalculator
from backend.services.domain.status_calculator import StatusCalculator
from backend.bootstrap.collectors import create_collector_registry
from backend.health.factory import HealthCheckerFactory
from backend.health.dependencies import HealthDependencies
from backend.services.dashboard_intelligence_service import (
    DashboardIntelligenceService,
    DashboardServiceDependencies,
)
from backend.services.risk_application_service import RiskApplicationService
from backend.services.risk_projection_service import RiskProjectionService
from backend.repositories.sqlalchemy.graph_repository_impl import GraphRepositoryImpl
from backend.repositories.sqlalchemy.evidence_repository_impl import EvidenceRepositoryImpl
from backend.repositories.sqlalchemy.risk_command_repository_impl import RiskCommandRepositoryImpl

# ============================================================
# PHASE 3: GRAPH COMPONENTS
# ============================================================

from backend.graph.domain.factory import (
    GraphAggregateFactory,
    GraphNodeFactory,
    GraphEdgeFactory,
)
from backend.graph.domain.builder import GraphDomainBuilder
from backend.graph.domain.checksum import GraphChecksumService
from backend.graph.domain.statistics import GraphStatisticsService
from backend.graph.domain.validators import SyntaxValidator, SemanticValidator, BusinessValidator
from backend.graph.domain.policy import PolicyRegistry, NoVendorSelfReferencePolicy, NoDuplicateVendorPolicy
from backend.graph.infrastructure.mappers.to_orm import GraphToOrmMapper
from backend.graph.infrastructure.mappers.to_domain import OrmToGraphMapper
from backend.graph.infrastructure.repositories.metadata import GraphMetadataRepository
from backend.graph.infrastructure.repositories.postgres import PostgresGraphRepository
from backend.graph.infrastructure.factories.metadata import MetadataFactory
from backend.graph.infrastructure.services.checksum import CanonicalChecksumService
from backend.graph.infrastructure.interfaces.identity import UUIDIdentityGenerator
from backend.graph.infrastructure.interfaces.clock import SystemClock
from backend.graph.application.assembler import GraphAssembler
from backend.graph.application.projection_mapper import GraphProjectionMapper
from backend.graph.application.service import GraphRegenerationService

logger = logging.getLogger(__name__)

def build_application_container(infra: InfrastructureContainer) -> ApplicationContainer:
    """
    Build Application Container — SINGLE COMPOSITION ROOT.
    """

    # ============================================================
    # 1. Calculators
    # ============================================================

    fraud_calculator = FraudScoreCalculator()
    risk_calculator = RiskScoreCalculator()
    evidence_calculator = EvidenceScoreCalculator()

    calculators = CalculatorContainer(
        config=infra.calculator_config,
        fraud=fraud_calculator,
        risk=risk_calculator,
        evidence=evidence_calculator,
    )

    # ============================================================
    # 2. Mappers
    # ============================================================

    fraud_mapper = FraudMapper()
    graph_mapper = GraphMapper()
    risk_mapper = RiskMapper()
    evidence_mapper = EvidenceMapper()
    procurement_mapper = ProcurementMapper()

    mappers = MapperContainer(
        fraud=fraud_mapper,
        graph=graph_mapper,
        risk=risk_mapper,
        evidence=evidence_mapper,
        procurement=procurement_mapper,
    )

    # ============================================================
    # 3. Domain Services
    # ============================================================

    confidence_calculator = ConfidenceCalculator()
    status_calculator = StatusCalculator()

    case_intelligence_factory = CaseIntelligenceFactory(
        fraud_mapper=fraud_mapper,
        graph_mapper=graph_mapper,
        risk_mapper=risk_mapper,
        evidence_mapper=evidence_mapper,
        procurement_mapper=procurement_mapper,
        fraud_calculator=fraud_calculator,
        risk_calculator=risk_calculator,
        evidence_calculator=evidence_calculator,
        config=infra.calculator_config,
        confidence_calculator=confidence_calculator,
        status_calculator=status_calculator,
    )

    domain_services = DomainServiceContainer(
        confidence=confidence_calculator,
        status=status_calculator,
        factory=case_intelligence_factory,
    )

    # ============================================================
    # 4. Collectors
    # ============================================================

    from backend.infrastructure.repository_factory import RepositoryFactory

    repo_factory = RepositoryFactory(infra.sql_repo)

    collector_registry = create_collector_registry(
        repo_factory=repo_factory,
        uow_factory=infra.uow_factory,
    )

    collectors = CollectorContainer(
        registry=collector_registry,
    )

    # ============================================================
    # 5. Dashboard Service
    # ============================================================

    service_deps = DashboardServiceDependencies(
        uow_factory=infra.uow_factory,
        executor=infra.parallel_executor,
        registry=collector_registry,
        factory=case_intelligence_factory,
        event_bus=infra.event_bus,
        version=infra.version,
    )

    dashboard_service = DashboardIntelligenceService(deps=service_deps)

    # ============================================================
    # 6. Risk Application Service (SINGLETON - STATELESS)
    # ============================================================

    graph_repo = repo_factory.graph()
    evidence_repo = repo_factory.evidence()

    risk_command_repo = repo_factory.risk_command()

    projection_service = RiskProjectionService(
        command_repo=risk_command_repo,
    )

    risk_application_service = RiskApplicationService(
        uow_factory=infra.uow_factory,
        graph_repo=graph_repo,
        evidence_repo=evidence_repo,
        projection_service=projection_service,
        config=infra.calculator_config,
    )

    # ============================================================
    # 7. GRAPH COMPONENTS (Sprint 3.4B Phase 3)
    # ============================================================

    # 7.1 Domain Components
    logger.info("Initializing Graph Domain Components...")
    
    node_factory = GraphNodeFactory()
    edge_factory = GraphEdgeFactory()
    aggregate_factory = GraphAggregateFactory()
    
    domain_builder = GraphDomainBuilder(
        factory=aggregate_factory,
        duplicate_mode="repair",
    )
    
    checksum_service = GraphChecksumService()
    statistics_service = GraphStatisticsService()
    
    syntax_validator = SyntaxValidator()
    semantic_validator = SemanticValidator()
    business_validator = BusinessValidator()

    # 7.2 Policies
    logger.info("Registering Graph Policies...")
    
    policy_registry = PolicyRegistry()
    policy_registry.register("no_self_reference", NoVendorSelfReferencePolicy())
    policy_registry.register("no_duplicate_vendor", NoDuplicateVendorPolicy())

    # 7.3 Infrastructure Components
    logger.info("Initializing Graph Infrastructure Components...")
    
    identity_generator = UUIDIdentityGenerator()
    
    to_orm_mapper = GraphToOrmMapper()
    to_domain_mapper = OrmToGraphMapper(factory=aggregate_factory)
    
    metadata_factory = MetadataFactory()
    metadata_repo = GraphMetadataRepository()
    
    canonical_checksum_service = CanonicalChecksumService()

    # 7.4 Repository (Unified)
    logger.info("Creating Graph Repository...")
    
    graph_repository = PostgresGraphRepository(
        to_orm_mapper=to_orm_mapper,
        identity_generator=identity_generator,
        to_domain_mapper=to_domain_mapper,
        metadata_repo=metadata_repo,
        checksum_service=canonical_checksum_service,
        metadata_factory=metadata_factory,
    )

    # 7.5 Application Components
    logger.info("Initializing Graph Application Components...")
    
    clock = SystemClock()
    
    graph_assembler = GraphAssembler(
        domain_builder=domain_builder,
        node_factory=node_factory,
        edge_factory=edge_factory,
    )
    
    graph_regeneration_service = GraphRegenerationService(
        assembler=graph_assembler,
        checksum_service=checksum_service,
        syntax_validator=syntax_validator,
        semantic_validator=semantic_validator,
        business_validator=business_validator,
        policy_registry=policy_registry,
        write_repository=graph_repository,          
        maintenance_repository=graph_repository,    
        clock=clock,
    )

    logger.info("Graph components initialized successfully")

    # ============================================================
    # 8. Service Container
    # ============================================================

    services = ServiceContainer(
        dashboard=dashboard_service,
        risk_application=risk_application_service,
        graph_regeneration=graph_regeneration_service,
    )

    # ============================================================
    # 9. Health Container
    # ============================================================

    enable_health = os.getenv("ENABLE_HEALTH", "true").lower() == "true"

    if enable_health:
        health_deps = HealthDependencies(
            enabled=enable_health,
            sql_repo=infra.sql_repo,
        )
        health_checker = HealthCheckerFactory.create(health_deps)
        health = HealthContainer(checker=health_checker)
    else:
        health = HealthContainer(checker=None)

    # ============================================================
    # 10. Application Container — SINGLE RETURN
    # ============================================================

    return ApplicationContainer(
        infrastructure=infra,
        calculators=calculators,
        mappers=mappers,
        domain_services=domain_services,
        collectors=collectors,
        services=services,
        health=health,
    )
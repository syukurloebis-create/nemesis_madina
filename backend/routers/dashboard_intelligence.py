"""
Dashboard Intelligence Router — Registrasi endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.dashboard_intelligence_service import DashboardIntelligenceService, DashboardServiceDependencies
from backend.domain.models.case_intelligence import CaseIntelligence
from backend.dependencies.auth import require_intelligence_view
from backend.security.models import User
from backend.infrastructure.repositories.dashboard_read_repository import DashboardReadRepository
from backend.mappers.dashboard_projection_mapper import DashboardProjectionMapper
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.parallel_executor import ParallelExecutor
from backend.infrastructure.event_bus import InMemoryEventBus
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.collectors.registry import CollectorRegistry
from backend.bootstrap.collectors import create_collector_registry
from backend.infrastructure.repository_factory import RepositoryFactory
from backend.factories.case_intelligence_factory import CaseIntelligenceFactory
from backend.mappers.fraud_mapper import FraudMapper
from backend.mappers.graph_mapper import GraphMapper
from backend.mappers.risk_mapper import RiskMapper
from backend.mappers.evidence_mapper import EvidenceMapper
from backend.mappers.procurement_mapper import ProcurementMapper
from backend.calculators.fraud_score_calculator import FraudScoreCalculator
from backend.calculators.risk_score_calculator import RiskScoreCalculator
from backend.calculators.evidence_score_calculator import EvidenceScoreCalculator
from backend.calculators.config import CalculatorConfig
from backend.services.domain.confidence_calculator import ConfidenceCalculator
from backend.services.domain.status_calculator import StatusCalculator
from backend.core.version import VersionInfo

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard/intelligence"
)


def get_dashboard_dependencies() -> DashboardServiceDependencies:
    """Create dashboard dependencies."""
    logger.info("Creating dashboard dependencies...")

    # Create infrastructure
    sql_repo = SQLRepository().initialize()
    uow_factory = UnitOfWorkFactory(sql_repo)
    event_bus = InMemoryEventBus()
    parallel_executor = ParallelExecutor()

    # Create repository factory
    repo_factory = RepositoryFactory(sql_repo)

    # Create collector registry
    collector_registry = create_collector_registry(
        repo_factory=repo_factory,
        uow_factory=uow_factory,
    )

    # Create mappers
    fraud_mapper = FraudMapper()
    graph_mapper = GraphMapper()
    risk_mapper = RiskMapper()
    evidence_mapper = EvidenceMapper()
    procurement_mapper = ProcurementMapper()

    # Create calculators
    config = CalculatorConfig()
    fraud_calculator = FraudScoreCalculator()
    risk_calculator = RiskScoreCalculator()
    evidence_calculator = EvidenceScoreCalculator()

    # Create domain services
    confidence_calculator = ConfidenceCalculator()
    status_calculator = StatusCalculator()

    # Create factory
    factory = CaseIntelligenceFactory(
        fraud_mapper=fraud_mapper,
        graph_mapper=graph_mapper,
        risk_mapper=risk_mapper,
        evidence_mapper=evidence_mapper,
        procurement_mapper=procurement_mapper,
        fraud_calculator=fraud_calculator,
        risk_calculator=risk_calculator,
        evidence_calculator=evidence_calculator,
        config=config,
        confidence_calculator=confidence_calculator,
        status_calculator=status_calculator,
    )

    # Create VersionInfo with ALL required arguments
    version = VersionInfo(
        build="dev",
        commit="dev",
        branch="main",
        api_version="v1",
        schema_version="v3.2",
        engine_version="v1.0",
        calculator_version="v1.0",
        sql_version="v3.2"
    )

    logger.info("Dashboard dependencies created successfully")

    return DashboardServiceDependencies(
        uow_factory=uow_factory,
        executor=parallel_executor,
        registry=collector_registry,
        factory=factory,
        event_bus=event_bus,
        version=version,
    )


# Create dependencies once at module load
logger.info("Loading dashboard dependencies...")
_deps = get_dashboard_dependencies()
logger.info("Dashboard dependencies loaded")


@router.get("/{case_id}")
async def get_dashboard_intelligence(
    request: Request,
    case_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_intelligence_view),
) -> CaseIntelligence:
    """
    Get Dashboard Intelligence for a case.
    """
    logger.info("=== DASHBOARD INTELLIGENCE REQUEST START ===")
    logger.info("case_id: %s", case_id)

    try:
        # Create read repository with the session
        read_repository = DashboardReadRepository(session, "dashboard")
        projection_mapper = DashboardProjectionMapper()
        
        # Log the created objects
        logger.info(f"read_repository: {read_repository}")
        logger.info(f"projection_mapper: {projection_mapper}")

        # Create service WITH read_repository
        service = DashboardIntelligenceService(
            deps=_deps,
            read_repository=read_repository,
            projection_mapper=projection_mapper,
        )
        
        # Log the service's _read_repository
        logger.info(f"service._read_repository: {service._read_repository}")

        result = await service.get_case_intelligence(
            case_id,
            session=session,
        )
        logger.info("=== DASHBOARD INTELLIGENCE REQUEST COMPLETE ===")
        return result
    except Exception as e:
        logger.exception("Dashboard Intelligence failed for case %s: %s", case_id, e)
        raise HTTPException(500, detail=str(e))

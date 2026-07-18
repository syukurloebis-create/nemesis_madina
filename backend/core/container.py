"""
Core Container — Application Container Dataclasses.
"""

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.core.version import VersionInfo
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.parallel_executor import ParallelExecutor
from backend.infrastructure.event_bus import IEventBus
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
from backend.collectors.registry import CollectorRegistry
from backend.services.dashboard_intelligence_service import DashboardIntelligenceService
from backend.services.risk_application_service import RiskApplicationService
from backend.services.graph_regeneration_service import GraphRegenerationService
from backend.health.health_check import HealthChecker  


@dataclass(frozen=True)
class InfrastructureContainer:
    version: VersionInfo
    sql_repo: SQLRepository
    session_factory: async_sessionmaker
    uow_factory: UnitOfWorkFactory
    event_bus: IEventBus
    parallel_executor: ParallelExecutor
    calculator_config: CalculatorConfig


@dataclass(frozen=True)
class CalculatorContainer:
    config: CalculatorConfig
    fraud: FraudScoreCalculator
    risk: RiskScoreCalculator
    evidence: EvidenceScoreCalculator


@dataclass(frozen=True)
class MapperContainer:
    fraud: FraudMapper
    graph: GraphMapper
    risk: RiskMapper
    evidence: EvidenceMapper
    procurement: ProcurementMapper


@dataclass(frozen=True)
class DomainServiceContainer:
    confidence: ConfidenceCalculator
    status: StatusCalculator
    factory: CaseIntelligenceFactory


@dataclass(frozen=True)
class CollectorContainer:
    registry: CollectorRegistry


@dataclass(frozen=True)
class ServiceContainer:
    """Application Services Container."""
    
    dashboard: DashboardIntelligenceService
    risk_application: RiskApplicationService
    graph_regeneration: GraphRegenerationService  # ← NEW


@dataclass(frozen=True)
class HealthContainer:
    checker: Optional[HealthChecker] = None


@dataclass(frozen=True)
class ApplicationContainer:
    infrastructure: InfrastructureContainer
    calculators: CalculatorContainer
    mappers: MapperContainer
    domain_services: DomainServiceContainer
    collectors: CollectorContainer
    services: ServiceContainer
    health: HealthContainer
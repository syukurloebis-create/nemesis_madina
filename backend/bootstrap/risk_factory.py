"""
Risk Factory — Build Risk Application Service with all dependencies.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.repositories.case_repository import SQLAlchemyCaseRepository
from backend.infrastructure.mappers.case_mapper import CaseMapper
from backend.infrastructure.mappers.fraud_mapper import FraudAnalysisMapper
from backend.infrastructure.mappers.risk_mapper import RiskAssessmentMapper
from backend.infrastructure.mappers.evidence_mapper import EvidenceVerificationMapper
from backend.infrastructure.mappers.graph_mapper import GraphAnalysisMapper
from backend.infrastructure.mappers.procurement_mapper import ProcurementAnalysisMapper
from backend.repositories.sqlalchemy.graph_repository_impl import GraphRepositoryImpl
from backend.repositories.sqlalchemy.evidence_repository_impl import EvidenceRepositoryImpl
from backend.repositories.sqlalchemy.risk_command_repository_impl import RiskCommandRepositoryImpl
from backend.services.risk_projection_service import RiskProjectionService
from backend.services.risk_application_service import RiskApplicationService


class RiskFactory:
    """Factory for Risk Application Service."""

    @staticmethod
    def create(db: AsyncSession) -> RiskApplicationService:
        """Build RiskApplicationService with all dependencies."""
        sql_repo = SQLRepository()
        uow_factory = UnitOfWorkFactory(db)

        # Mappers (5 dependencies)
        fraud_mapper = FraudAnalysisMapper()
        risk_mapper = RiskAssessmentMapper()
        evidence_mapper = EvidenceVerificationMapper()
        graph_mapper = GraphAnalysisMapper()
        procurement_mapper = ProcurementAnalysisMapper()

        # Case Repository
        case_mapper = CaseMapper(
            fraud_mapper=fraud_mapper,
            risk_mapper=risk_mapper,
            evidence_mapper=evidence_mapper,
            graph_mapper=graph_mapper,
            procurement_mapper=procurement_mapper,
        )
        case_repo = SQLAlchemyCaseRepository(db, case_mapper)

        # Graph & Evidence Repositories
        graph_repo = GraphRepositoryImpl(sql_repo)
        evidence_repo = EvidenceRepositoryImpl(sql_repo)

        # Projection Service
        projection_service = RiskProjectionService(
            command_repo=RiskCommandRepositoryImpl(sql_repo),
            uow_factory=uow_factory,
        )

        # Application Service
        return RiskApplicationService(
            case_repo=case_repo,
            graph_repo=graph_repo,
            evidence_repo=evidence_repo,
            projection_service=projection_service,
        )
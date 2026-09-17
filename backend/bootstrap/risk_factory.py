"""
Risk Factory — Canonical construction path untuk RiskApplicationService.

Mengikuti pola container_builder.py:

    session_maker
        ↓
    UnitOfWorkFactory(session_maker)
        ↓
    RiskProjectionService(
        command_repo=RiskCommandRepositoryImpl()
    )
        ↓
    RiskApplicationService(
        uow_factory=uow_factory,
        graph_repo=repo_factory.graph(),
        evidence_repo=repo_factory.evidence(),
        projection_service=projection_service,
        config=CalculatorConfig.default(),
    )

Digunakan oleh router /risk/calculate untuk unifikasi writer.

NOTE: Ini adalah canonical construction path. Jangan duplikasi
logika konstruksi di tempat lain — gunakan factory ini.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker

from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.repository_factory import RepositoryFactory
from backend.repositories.sqlalchemy.risk_command_repository_impl import (
    RiskCommandRepositoryImpl,
)
from backend.services.risk_projection_service import RiskProjectionService
from backend.services.risk_application_service import RiskApplicationService
from backend.calculators.config import CalculatorConfig


class RiskFactory:
    """Canonical factory for RiskApplicationService."""

    @staticmethod
    def create(session_maker: async_sessionmaker) -> RiskApplicationService:
        """
        Build RiskApplicationService with canonical dependencies.

        Args:
            session_maker: SQLAlchemy async_sessionmaker
                          (bukan AsyncSession instance)

        Returns:
            RiskApplicationService yang siap dipakai
        """
        # 1. SQL Repository (untuk RepositoryFactory)
        sql_repo = SQLRepository().initialize()

        # 2. Repository Factory
        repo_factory = RepositoryFactory(sql_repo)

        # 3. Unit of Work Factory (dengan session_maker)
        uow_factory = UnitOfWorkFactory(session_maker)

        # 4. Risk Command Repository (tanpa argumen)
        risk_command_repo = RiskCommandRepositoryImpl()

        # 5. Projection Service (hanya command_repo)
        projection_service = RiskProjectionService(
            command_repo=risk_command_repo,
        )

        # 6. Calculator Config
        config = CalculatorConfig.default()

        # 7. Risk Application Service
        return RiskApplicationService(
            uow_factory=uow_factory,
            graph_repo=repo_factory.graph(),
            evidence_repo=repo_factory.evidence(),
            projection_service=projection_service,
            config=config,
        )
"""
Bootstrap Functions - Infrastructure Setup
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.core.container import InfrastructureContainer
from backend.core.version import VersionInfo
from backend.infrastructure.sql_repository import SQLRepository
from backend.infrastructure.parallel_executor import ParallelExecutor
from backend.infrastructure.event_bus import InMemoryEventBus
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.calculators.config import CalculatorConfig
from backend.config import settings

logger = logging.getLogger(__name__)


@dataclass
class BootstrapResult:
    infrastructure: InfrastructureContainer
    engine: Optional[AsyncEngine] = None


def bootstrap_infrastructure(
    *,
    engine: Optional[AsyncEngine] = None,
    session_factory: Optional[async_sessionmaker] = None,
    sql_repo: Optional[SQLRepository] = None,
    uow_factory: Optional[UnitOfWorkFactory] = None,
    event_bus: Optional[InMemoryEventBus] = None,
    parallel_executor: Optional[ParallelExecutor] = None,
    calculator_config: Optional[CalculatorConfig] = None,
    version: Optional[VersionInfo] = None,
) -> BootstrapResult:
    """
    Bootstrap infrastructure dependencies.

    All dependencies can be overridden for testing.
    Production uses defaults.

    Args:
        engine: Pre-configured async engine (for testing)
        session_factory: Pre-configured session factory (for testing)
        sql_repo: Pre-configured SQL repository (for testing)
        uow_factory: Pre-configured UoW factory (for testing)
        event_bus: Pre-configured event bus (for testing)
        parallel_executor: Pre-configured executor (for testing)
        calculator_config: Pre-configured calculator config (for testing)
        version: Pre-configured version info (for testing)
    """
    logger.info("Bootstrapping infrastructure...")

    # 1. Database
    if engine is None:
        database_url = settings.database.url
        logger.info("Database configured (%s)", settings.database.host)
        engine = create_async_engine(
            database_url,
            echo=settings.database.echo,
            pool_pre_ping=True,
            poolclass=NullPool,
        )

    # 2. Session Factory
    if session_factory is None:
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    # 3. SQL Repository
    if sql_repo is None:
        sql_repo = SQLRepository().initialize()

    # 4. Unit of Work Factory
    if uow_factory is None:
        uow_factory = UnitOfWorkFactory(session_factory)

    # 5. Event Bus
    if event_bus is None:
        event_bus = InMemoryEventBus()

    # 6. Parallel Executor
    if parallel_executor is None:
        parallel_executor = ParallelExecutor()

    # 7. Calculator Config
    if calculator_config is None:
        calculator_config = CalculatorConfig.from_environment()

    # 8. Version Info
    if version is None:
        version = VersionInfo.from_environment()

    # 9. Infrastructure Container
    infrastructure = InfrastructureContainer(
        version=version,
        sql_repo=sql_repo,
        session_factory=session_factory,
        uow_factory=uow_factory,
        event_bus=event_bus,
        parallel_executor=parallel_executor,
        calculator_config=calculator_config,
    )

    logger.info("Infrastructure bootstrapped successfully")

    return BootstrapResult(
        infrastructure=infrastructure,
        engine=engine,
    )
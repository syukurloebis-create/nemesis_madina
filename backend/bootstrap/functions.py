import os
import logging
from dataclasses import dataclass
from typing import Optional

# ✅ Load .env file
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

logger = logging.getLogger(__name__)


def _build_database_url() -> str:
    """
    Build DATABASE_URL from environment variables.
    
    Precedence:
    1. DATABASE_URL (if set directly)
    2. DB_* variables (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
    """
    # Check if DATABASE_URL is set directly
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Build from DB_* variables
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    # Validate required variables
    if not all([name, user, password]):
        raise ValueError(
            "DATABASE_URL or DB_NAME, DB_USER, and DB_PASSWORD "
            "must be configured in environment"
        )
    
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


@dataclass
class BootstrapResult:
    infrastructure: InfrastructureContainer
    engine: Optional[AsyncEngine] = None


def bootstrap_infrastructure() -> BootstrapResult:
    """
    Bootstrap infrastructure dependencies.
    """
    logger.info("Bootstrapping infrastructure...")

    # 1. Database - Build URL
    database_url = _build_database_url()
    # Hide password in logs
    safe_url = database_url.replace(
        os.getenv("DB_PASSWORD", ""), "***"
    ) if os.getenv("DB_PASSWORD") else database_url
    logger.info(f"Using database: {safe_url}")

    engine = create_async_engine(
        database_url,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        pool_pre_ping=True,
        poolclass=NullPool,
    )

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # ... rest of function remains the same

    # 2. SQL Repository
    sql_repo = SQLRepository().initialize()

    # 3. Unit of Work Factory
    uow_factory = UnitOfWorkFactory(session_factory)

    # 4. Event Bus
    event_bus = InMemoryEventBus()

    # 5. Parallel Executor
    parallel_executor = ParallelExecutor()

    # 6. Calculator Config
    calculator_config = CalculatorConfig.default()

    # 7. Version Info
    version = VersionInfo.from_environment()

    # 8. Infrastructure Container
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


@classmethod
def from_env(cls) -> "CalculatorConfig":
    """
    Build calculator configuration from environment.

    CALCULATOR_PROFILE:
        default
        government
    """

    profile = os.getenv(
        "CALCULATOR_PROFILE",
        "default",
    ).lower()

    if profile == "government":
        return cls.government()

    return cls.default()
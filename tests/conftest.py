# test/confest.py

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.config import settings
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.evidence import EvidenceRegistry  
from backend.lineage.tracker import LineageTracker


# ============================================================
# TEMPORARY: Gunakan database development untuk test
# TODO: Tambahkan test_url ke settings dan gunakan di sini
# ============================================================

TEST_DATABASE_URL = settings.database.url


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Session-scoped engine for all tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_connection(db_engine):
    """Function-scoped connection with transaction."""
    async with db_engine.connect() as conn:
        async with conn.begin():
            yield conn


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """
    Function-scoped session with transaction isolation.
    Uses SQLAlchemy's begin_nested() for test isolation.
    """
    async with db_engine.connect() as conn:
        async with conn.begin():
            async with conn.begin_nested():
                session = AsyncSession(bind=conn, expire_on_commit=False)
                try:
                    yield session
                finally:
                    await session.close()


@pytest.fixture
def evidence_registry():
    """
    Fresh EvidenceRegistry instance per test.

    Used by evidence unit/integration/performance tests.
    """
    return EvidenceRegistry()


@pytest.fixture(autouse=True)
def reset_evidence_registry():
    """
    Guarantee EvidenceRegistry isolation between tests.

    ✅ Reset sebelum test (state bersih)
    ✅ Reset sesudah test (mencegah state leakage ke test berikutnya)
    """
    registry = EvidenceRegistry()
    registry.reset()

    yield

    registry.reset()


@pytest.fixture(autouse=True)
def reset_lineage_tracker():
    """
    Clear LineageTracker state before each test.

    Ensures test isolation for lineage module.
    """
    tracker = LineageTracker()
    tracker.clear()
    yield
    tracker.clear()
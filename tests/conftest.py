# tests/conftest.py
"""
Global pytest configuration for NEMESIS tests.
Supports both backend application tests AND metadata inventory tests.
"""

import sys
import pytest
import pytest_asyncio
from pathlib import Path

# ============================================================================
# PATH CONFIGURATION - Agar metadata_inventory dapat diimport
# ============================================================================

# Tambahkan scripts directory ke PYTHONPATH untuk metadata_inventory
scripts_dir = Path(__file__).parent.parent / "scripts"
if scripts_dir.exists() and str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# ============================================================================
# BACKEND TEST FIXTURES (Existing)
# ============================================================================

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from backend.config import settings
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.evidence import EvidenceRegistry  
from backend.lineage.tracker import LineageTracker
from backend.main import app
from backend.bootstrap.events import EventSystemFactory


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
    """Fresh EvidenceRegistry instance per test."""
    return EvidenceRegistry()


@pytest.fixture(autouse=True)
def reset_evidence_registry():
    """Guarantee EvidenceRegistry isolation between tests."""
    registry = EvidenceRegistry()
    registry.reset()
    yield
    registry.reset()


@pytest.fixture(autouse=True)
def reset_lineage_tracker():
    """Clear LineageTracker state before each test."""
    tracker = LineageTracker()
    tracker.clear()
    yield
    tracker.clear()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Async client for FastAPI app."""
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            yield client


# ============================================================================
# METADATA INVENTORY TEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_payload():
    """Sample payload for metadata inventory tests."""
    return {
        "fingerprint": "a1b2c3d4e5f6g7h8",
        "checksum": "i9j0k1l2m3n4o5p6",
        "timestamp": "2026-08-05T12:00:00",
        "import": {
            "imported": ["backend.models.user", "backend.models.order"],
            "failed": [],
            "mappers_before": 0,
            "mappers_after": 2,
            "mapper_growth": 2
        },
        "registry": {
            "fingerprint": "r1s2t3u4v5w6x7y8",
            "canonical_fingerprint": "c1d2e3f4g5h6i7j8",
            "registry_count": 1,
            "table_count": 2,
            "mapper_count": 2,
            "tables": ["users", "orders"],
            "models": ["User", "Order"]
        }
    }


@pytest.fixture
def sample_import_artifact():
    """Sample ImportArtifact for testing."""
    from metadata_inventory.discovery.import_runtime import ImportArtifact
    return ImportArtifact.create(["backend.models.user", "backend.models.order"])


@pytest.fixture
def sample_registry_artifact():
    """Sample RegistryArtifact for testing."""
    from metadata_inventory.discovery.discovery_artifact import RegistryArtifact
    # Create a minimal registry artifact
    return RegistryArtifact(
        fingerprint="test_fingerprint_1234567890123456",
        canonical_fingerprint="test_canonical_1234567890123456",
        namespace="backend.database",
        registry_count=1,
        table_count=2,
        mapper_count=2,
        tables=("users", "orders"),
        table_infos=(),
        model_infos=(),
        is_canonical=True,
        discovery_method="canonical",
        checksum="test_checksum_1234567890123456"
    )


@pytest.fixture
def sample_import_fingerprint():
    """Sample import fingerprint (string)."""
    return "a2537e4ca64b2f0b"


@pytest.fixture
def sample_registry_fingerprint():
    """Sample registry fingerprint (string)."""
    return "1371e5981ba25e56"


@pytest.fixture
def sample_artifact(sample_import_fingerprint, sample_registry_fingerprint):
    """Sample DiscoveryArtifact for testing."""
    from metadata_inventory.discovery.discovery_artifact import DiscoveryArtifact
    return DiscoveryArtifact.create(
        sample_import_fingerprint,
        sample_registry_fingerprint
    )


@pytest.fixture
def sample_verification_result(sample_artifact):
    """Sample VerificationResult for testing."""
    from metadata_inventory.verification.result import (
        VerificationResult, VerificationStatus, FindingSummary,
        VerificationMetadata, VerificationStatistics
    )
    
    summary = FindingSummary(
        total=0,
        critical=0,
        error=0,
        warning=0,
        info=0
    )
    
    metadata = VerificationMetadata(
        engine_version="1.0.0",
        rule_set_version="2026.08",
        discovery_version="1.0",
        started_at="2026-08-05T12:00:00",
        finished_at="2026-08-05T12:00:01",
        duration_ms=1000,
        rules_executed=8
    )
    
    statistics = VerificationStatistics(
        total_rules=8,
        passed=8,
        failed=0,
        warning=0,
        skipped=0,
        info=0,
        duration_ms=1000,
        rules_executed=8
    )
    
    return VerificationResult(
        artifact_fingerprint=sample_artifact.fingerprint,
        artifact_checksum=sample_artifact.checksum,
        status=VerificationStatus.PASSED,
        summary=summary,
        findings=[],
        metadata=metadata,
        statistics=statistics,
        timestamp="2026-08-05T12:00:00",
        payload_version="1.0"
    )

@pytest.fixture(autouse=True)
def reset_event_system():
    """Reset EventSystemFactory before and after each test."""
    EventSystemFactory.reset()
    yield
    EventSystemFactory.reset()

# ============================================================================
# MARKERS UNTUK METADATA INVENTORY TESTS
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for metadata inventory")
    config.addinivalue_line("markers", "rule: Rule tests for verification rules")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "golden: Golden dataset tests")
    config.addinivalue_line("markers", "property: Property-based tests")
    config.addinivalue_line("markers", "performance: Performance tests")
# tests/unit/repositories/conftest.py

import pytest_asyncio

from backend.repositories.sqlalchemy.procurement_repository_impl import (
    ProcurementRepositoryImpl,
)


@pytest_asyncio.fixture
async def repository(db_session):
    """
    Repository fixture for procurement repository tests.
    
    Reuses the existing db_session fixture from root conftest.py.
    """
    return ProcurementRepositoryImpl(db_session)
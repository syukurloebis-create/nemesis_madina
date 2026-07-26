# tests/integration/conftest.py

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import db_engine  # reuse engine from parent


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    """
    Integration test session with transaction isolation.
    """
    async with db_engine.connect() as conn:
        async with conn.begin():
            async with conn.begin_nested():
                session = AsyncSession(bind=conn, expire_on_commit=False)
                try:
                    yield session
                finally:
                    await session.close()
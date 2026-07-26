# tests/e2e/conftest.py

import pytest_asyncio
from httpx import AsyncClient
from backend.main import app


@pytest_asyncio.fixture(scope="function")
async def client():
    """E2E client - does NOT share SQLAlchemy fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
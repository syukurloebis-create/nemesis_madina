"""
Compatibility database layer.

Legacy modules import:
    from infrastructure.database import ...

Current implementation lives in:
    database
"""

from database import (
    engine,
    Base,
    get_db,
    async_session_maker,
)

from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


# ============================================================
# Legacy alias
# ============================================================

AsyncSessionLocal = async_session_maker


# ============================================================
# Initialization compatibility
# ============================================================

async def init_db():
    """
    Legacy startup hook.
    Creates SQLAlchemy tables if needed.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Legacy shutdown hook.
    """
    await engine.dispose()


# ============================================================
# Dependency compatibility
# ============================================================

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================
# Pool compatibility
# ============================================================

async def get_pool():
    """
    Some legacy modules expect a pool object.
    SQLAlchemy async engine provides equivalent access.
    """
    return engine
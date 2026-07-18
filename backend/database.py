"""
Database Configuration - SINGLE SOURCE OF TRUTH

Centralized database connection and session management for NEMESIS.

This module is the single source of truth for:

- Async engine configuration
- Session factory (AsyncSessionLocal)
- FastAPI dependency (get_db)
- Background session (get_db_session)
- Parallel execution helper (run_with_new_session)

All database access inside NEMESIS should use this module.

Usage:
    # FastAPI dependency
    @router.get("/items")
    async def get_items(db: AsyncSession = Depends(get_db)):
        ...

    # Background task
    session = get_db_session()
    async with session:
        ...

    # Parallel execution
    fraud, graph = await asyncio.gather(
        run_with_new_session(self.get_fraud, case_id),
        run_with_new_session(self.get_graph, case_id),
    )
"""

import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

# Import config - using new settings API
from backend.config import settings

logger = logging.getLogger(__name__)

# ============================================================
# ENGINE - USING NEW SETTINGS API
# ============================================================

# Use settings.database.url instead of settings.DATABASE_URL
engine: AsyncEngine = create_async_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=True,
    pool_recycle=settings.database.pool_recycle,
    pool_timeout=settings.database.pool_timeout,
    echo=settings.base.debug,  # Use settings.base.debug instead of settings.DEBUG
)

# ============================================================
# SESSION FACTORY - SINGLE SOURCE OF TRUTH
# ============================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Alias untuk kemudahan
async_session_maker = AsyncSessionLocal
SessionFactory = AsyncSessionLocal

# ============================================================
# BASE MODEL
# ============================================================

Base = declarative_base()

# ============================================================
# TYPE HINTS
# ============================================================

T = TypeVar("T")

# ============================================================
# DEPENDENCY FUNCTIONS
# ============================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency.

    One request = one AsyncSession.
    Transaction managed automatically.

    Yields:
        AsyncSession: Database session for the request

    Example:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db_session() -> AsyncSession:
    """
    Get a session for background tasks.

    Returns:
        AsyncSession: A session that must be manually managed

    Example:
        session = get_db_session()
        async with session:
            await session.execute(...)
    """
    return AsyncSessionLocal()


async def run_with_new_session(
    func: Callable[..., Awaitable[T]],
    *args,
    **kwargs
) -> T:
    """
    Run a function with a new database session.

    For parallel execution with asyncio.gather.

    Args:
        func: Async function to run
        *args: Arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        T: Result of func

    Example:
        fraud, graph = await asyncio.gather(
            run_with_new_session(self.get_fraud, case_id),
            run_with_new_session(self.get_graph, case_id),
        )
    """
    async with AsyncSessionLocal() as session:
        return await func(session, *args, **kwargs)


async def ensure_db_connection() -> bool:
    """
    Check database connectivity.

    Returns:
        bool: True if connection is successful
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# ============================================================
# COMPATIBILITY LAYER - LEGACY FUNCTIONS
# ============================================================
# These functions maintain backward compatibility with existing modules.
# Do not remove until all modules are migrated to new API.

async def init_db() -> None:
    """
    Initialize database - create all tables.
    
    Legacy function called by infrastructure/database.py and others.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def close_db() -> None:
    """
    Close database connections.
    
    Legacy function for graceful shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")


def get_db_session() -> AsyncSession:
    """
    Get a session for background tasks.
    
    Legacy alias for AsyncSessionLocal.
    """
    return AsyncSessionLocal()


async def ensure_db_connection() -> bool:
    """
    Check database connectivity.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_async_session_maker():
    """
    Get the async session maker.
    
    Legacy function for backward compatibility.
    """
    return AsyncSessionLocal


# Export legacy functions for backward compatibility
__all__ = [
    "engine",
    "AsyncSessionLocal",
    "Base",
    "get_db",
    "get_db_session",
    "run_with_new_session",
    "ensure_db_connection",
    "init_db",
    "close_db",
    "async_session_maker",
    "SessionFactory",
    "check_db_health",
]

# ============================================================
# COMPATIBILITY: check_db_health
# ============================================================

async def check_db_health() -> dict:
    """
    Legacy compatibility health check.

    Used by backend.infrastructure.database and other modules.

    Returns:
        dict: {
            "status": "healthy" | "unhealthy",
            "ok": bool,
            "database": str,
            "driver": str,
            "error": str (only if unhealthy)
        }
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "ok": True,
            "database": str(engine.url),
            "driver": engine.dialect.name,
        }
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "ok": False,
            "database": str(engine.url),
            "driver": engine.dialect.name,
            "error": str(e),
        }

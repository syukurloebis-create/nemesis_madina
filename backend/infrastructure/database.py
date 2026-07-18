"""
Legacy compatibility layer.

This module exists only for older code importing:

    infrastructure.database

The actual implementation lives in:

    backend.database
"""

from backend.database import (
    engine,
    Base,
    AsyncSessionLocal,
    SessionFactory,
    async_session_maker,
    get_db,
    get_db_session,
    run_with_new_session,
    init_db,
    close_db,
    check_db_health,
)

# Legacy aliases
SessionLocal = AsyncSessionLocal
get_pool = AsyncSessionLocal
check_db_connection = check_db_health

__all__ = [
    "engine",
    "Base",
    "AsyncSessionLocal",
    "SessionFactory",
    "async_session_maker",
    "SessionLocal",
    "get_db",
    "get_db_session",
    "get_pool",
    "run_with_new_session",
    "init_db",
    "close_db",
    "check_db_health",
    "check_db_connection",
]
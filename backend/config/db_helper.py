"""
DB Helper — shared DB_CONFIG extraction from environment DSN.

Replaces hardcoded DB_CONFIG dicts in legacy service modules.
Uses DATABASE_SYNC_URL or DATABASE_URL (both present in container env).
"""
import os
from urllib.parse import urlparse


def get_db_config() -> dict:
    """
    Build psycopg2-compatible DB config from environment DSN.

    Priority:
      1. DATABASE_SYNC_URL (psycopg2, sync)
      2. DATABASE_URL (SQLAlchemy asyncpg)

    Both present in container. No hardcoded fallback for password.
    """
    dsn = os.getenv('DATABASE_SYNC_URL') or os.getenv('DATABASE_URL')
    if not dsn:
        raise RuntimeError(
            "DATABASE_SYNC_URL or DATABASE_URL must be set in environment"
        )

    # Strip SQLAlchemy driver suffix for urllib parsing
    clean_dsn = dsn.replace('+asyncpg', '').replace('+psycopg2', '')
    parsed = urlparse(clean_dsn)

    if not parsed.password:
        raise RuntimeError("DB password missing from DSN")

    return {
        'host': parsed.hostname or 'postgres',
        'port': parsed.port or 5432,
        'database': (parsed.path or '/nemesis_db').lstrip('/'),
        'user': parsed.username or 'nemesis',
        'password': parsed.password,
    }


# Module-level singleton for legacy `from ... import DB_CONFIG` pattern
DB_CONFIG = get_db_config()

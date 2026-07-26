"""
SQL Repository — Helper untuk eksekusi query.

Menyediakan:
    - fetch_one: ambil satu row
    - fetch_all: ambil banyak row
    - fetch_scalar: ambil satu nilai
"""

import logging
from typing import Any, Dict, Optional, List, Tuple
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.sql_keys import SQLKey
from backend.infrastructure.exceptions import SQLNotFoundError, SQLExecutionError
from backend.infrastructure.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class SQLRepository:
    """SQL Repository — Helper untuk eksekusi query."""

    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._initialized: bool = False

    def initialize(self) -> "SQLRepository":
        """Initialize — load SQL files."""
        if self._initialized:
            return self

        from pathlib import Path
        import os

        sql_root = Path(os.getenv("SQL_ROOT", "backend/sql/dashboard"))

        for sql_file in sql_root.glob("**/*.sql"):
            relative_path = sql_file.relative_to(sql_root)
            key = str(relative_path).replace("\\", "/").replace(".sql", "")
            with open(sql_file, "r") as f:
                self._cache[key] = f.read()

        self._initialized = True
        logger.info("SQLRepository initialized with %d queries", len(self._cache))
        return self

    def _load(self, key: SQLKey) -> str:
        """
        Internal loader.

        Mengubah SQLKey menjadi cache key dan mengambil SQL
        dari cache yang sudah di-load saat initialize().
        """
        cache_key = f"{key.category}/{key.query}"
        sql = self._cache.get(cache_key)
        if sql is None:
            raise SQLNotFoundError(cache_key)
        return sql

    def load(self, key: SQLKey) -> str:
        """
        Public compatibility API untuk load SQL query.

        Args:
            key: SQLKey enum

        Returns:
            SQL query string

        Raises:
            SQLNotFoundError: Jika query tidak ditemukan
        """
        return self._load(key)

    async def fetch_one(
        self,
        uow: IUnitOfWork,
        key: SQLKey,
        **params: Any
    ) -> Optional[Dict[str, Any]]:
        try:
            sql = self._load(key)
            result = await uow.session.execute(text(sql), params)
            return result.mappings().first()
        except SQLAlchemyError as e:
            raise SQLExecutionError(
                f"Failed to execute {key.category}/{key.query}: {e}",
                original_error=e
            )


    async def fetch_all(
        self,
        uow: IUnitOfWork,
        key: SQLKey,
        **params: Any
    ) -> List[Dict[str, Any]]:
        """
        Execute query and return all rows as dicts.
        
        Usage:
            rows = await sql_repo.fetch_all(uow, SQLKey.FRAUD_PATTERNS, case_id=case_id)
        """
        try:
            sql = self._load(key)
            result = await uow.session.execute(text(sql), params)
            return result.mappings().all()
        except SQLAlchemyError as e:
            raise SQLExecutionError(
                f"Failed to execute {key.category}/{key.query}: {e}",
                original_error=e
            )
    
    async def fetch_scalar(
        self,
        uow: IUnitOfWork,
        key: SQLKey,
        **params: Any
    ) -> Optional[Any]:
        logger.error("🚨🚨🚨 SQLRepository.fetch_one() WAS CALLED! 🚨🚨🚨")
        logger.error("🚨 key: %s", key)
        logger.error("🚨 params: %s", params)
        """
        Execute query and return scalar value.
        
        Usage:
            count = await sql_repo.fetch_scalar(uow, SQLKey.FRAUD_COUNT, case_id=case_id)
        """
        try:
            sql = self._load(key)
            result = await uow.session.execute(text(sql), params)
            return result.scalar()
        except SQLAlchemyError as e:
            raise SQLExecutionError(
                f"Failed to execute {key.category}/{key.query}: {e}",
                original_error=e
            )
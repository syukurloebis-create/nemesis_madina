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
from backend.infrastructure.exceptions import SQLExecutionError
from backend.infrastructure.unit_of_work import IUnitOfWork

logger = logging.getLogger(__name__)


class SQLRepository:
    """
    SQL Repository — Helper untuk eksekusi query.
    
    Repository tidak perlu menangani SQLAlchemyError lagi.
    """
    
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
        """Load SQL by key."""
        cache_key = f"{key.category}/{key.query}"
        if cache_key not in self._cache:
            raise SQLExecutionError(f"SQL query not found: {cache_key}")
        return self._cache[cache_key]

    async def fetch_one(
        self,
        uow: IUnitOfWork,
        key: SQLKey,
        **params: Any
    ) -> Optional[Dict[str, Any]]:
        try:
            sql = self._load(key)
        
            # 🔍 DEBUG: Log query yang akan dieksekusi
            logger.info("=" * 80)
            logger.info("SQL KEY: %s/%s", key.category, key.query)
            logger.info("PARAMS: %s", params)
            logger.info("SQL:\n%s", sql)
        
            result = await uow.session.execute(text(sql), params)
            row = result.mappings().first()
        
            logger.info("RESULT: %s", row)
        
            return row
        except SQLAlchemyError as e:
            # 🔍 DEBUG: Log exception lengkap dengan traceback
            logger.exception(
                "SQL EXECUTION FAILED [%s/%s]",
                key.category,
                key.query
            )

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
"""
Database Configuration - Single Source of Truth.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional


class DatabaseSettings(BaseSettings):
    """Database configuration - Single Source of Truth."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        case_sensitive=False
    )
    
    # Primary: Use DATABASE_URL directly
    database_url: Optional[str] = Field(None, alias="DATABASE_URL")
    database_sync_url: Optional[str] = Field(None, alias="DATABASE_SYNC_URL")
    
    # Fallback: Build from DB_* variables (for local development)
    host: str = Field("localhost", alias="DB_HOST")
    port: int = Field(5432, alias="DB_PORT")
    name: str = Field("nemesis_db", alias="DB_NAME")
    user: str = Field("nemesis", alias="DB_USER")
    password: str = Field("nemesis", alias="DB_PASSWORD")
    
    pool_size: int = Field(20, alias="DB_POOL_SIZE")
    max_overflow: int = Field(10, alias="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(30, alias="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(3600, alias="DB_POOL_RECYCLE")
    echo: bool = Field(False, alias="SQL_ECHO")
    
    @property
    def url(self) -> str:
        """Get async database URL."""
        if self.database_url:
            # Ensure async driver is used
            if "postgresql+asyncpg" not in self.database_url:
                return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
            return self.database_url
        
        # Build from DB_* variables (fallback)
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def sync_url(self) -> str:
        """Get sync database URL (for migrations)."""
        if self.database_sync_url:
            return self.database_sync_url
        
        # Build from DB_* variables (fallback)
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
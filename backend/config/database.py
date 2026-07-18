# backend/config/database.py

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        case_sensitive=False
    )
    
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
        """Get database URL for SQLAlchemy."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def sync_url(self) -> str:
        """Get synchronous database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

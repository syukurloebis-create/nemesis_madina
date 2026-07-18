# backend/config/cache.py

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional
from enum import Enum


class CacheType(str, Enum):
    """Cache implementation types."""
    MEMORY = "memory"
    REDIS = "redis"
    NOCACHE = "nocache"


class CacheSettings(BaseSettings):
    """Cache configuration."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True
    )
    
    type: CacheType = Field(CacheType.MEMORY, alias="CACHE_TYPE")
    default_ttl: int = Field(60, alias="CACHE_DEFAULT_TTL")
    max_size: int = Field(100, alias="CACHE_MAX_SIZE")
    
    # Redis specific
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db: int = Field(0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(None, alias="REDIS_PASSWORD")
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
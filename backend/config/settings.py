"""
Configuration Settings - Single Source of Truth
"""

from backend.config.base import BaseConfig
from backend.config.database import DatabaseSettings
from backend.config.auth import AuthSettings
from backend.config.cache import CacheSettings
from backend.config.security import SecuritySettings


class ApplicationSettings:
    """Application settings - Single source of truth."""
    
    def __init__(self):
        self.base = BaseConfig()
        self.database = DatabaseSettings()
        self.auth = AuthSettings()
    
    # Legacy compatibility - Will be removed in Sprint 3.5
    @property
    def DATABASE_URL(self):
        return self.database.url
    
    @property
    def DATABASE_SYNC_URL(self):
        return self.database.sync_url

    @property
    def DATABASE_ASYNC_URL(self) -> str:
        """Async database URL for SQLAlchemy."""
        # Ensure the URL uses asyncpg driver
        url = self.DATABASE_SYNC_URL
        if "+asyncpg" not in url and url.startswith("postgresql"):
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        return url
    
    @property
    def DEBUG(self):
        return self.base.debug
    
    @property
    def VERSION(self):
        return self.base.version


settings = ApplicationSettings()
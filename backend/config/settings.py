# backend/config/settings.py

from backend.config.base import BaseConfig, Environment
from backend.config.database import DatabaseSettings
from backend.config.cache import CacheSettings
from backend.config.telemetry import TelemetrySettings
from backend.config.security import SecuritySettings


class ApplicationSettings:
    """Application settings container."""

    def __init__(self):
        self.base = BaseConfig()
        self.database = DatabaseSettings()
        self.cache = CacheSettings()
        self.telemetry = TelemetrySettings()
        self.security = SecuritySettings()

    @property
    def is_production(self) -> bool:
        return self.base.is_production()

    @property
    def is_development(self) -> bool:
        return self.base.is_development()


# ==========================================================
# SINGLETON INSTANCE
# ==========================================================

settings = ApplicationSettings()


# ==========================================================
# COMPATIBILITY LAYER - FOR LEGACY MODULES
# ==========================================================

# Legacy modules still use settings.DATABASE_URL, settings.DEBUG, etc.
# This maintains backward compatibility while supporting new architecture.

settings.DATABASE_URL = settings.database.url
settings.DEBUG = settings.base.debug
settings.VERSION = settings.base.version
settings.ENV = settings.base.environment.value
settings.APP_NAME = settings.base.app_name

# For SQLAlchemy echo
settings.SQL_ECHO = settings.base.debug

# Export for direct import
__all__ = [
    "settings",
    "ApplicationSettings",
]

# backend/config/base.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class BaseConfig(BaseSettings):
    """Base configuration with environment support."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        case_sensitive=False
    )
    
    # Application
    app_name: str = Field("NEMESIS Dashboard", alias="APP_NAME")
    environment: Environment = Field(Environment.DEVELOPMENT, alias="ENV")
    version: str = Field("2.0.0", alias="VERSION")
    debug: bool = Field(False, alias="DEBUG")
    
    # API
    api_prefix: str = Field("/api/v1", alias="API_PREFIX")
    cors_origins: List[str] = Field(["*"], alias="CORS_ORIGINS")
    
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT
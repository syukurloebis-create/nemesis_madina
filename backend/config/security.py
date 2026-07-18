# backend/config/security.py

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class SecuritySettings(BaseSettings):
    """Security configuration."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True
    )
    
    secret_key: str = Field("change_me_in_production", alias="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(30, alias="JWT_EXPIRE_MINUTES")
    
    rate_limit_enabled: bool = Field(True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(60, alias="RATE_LIMIT_PERIOD")
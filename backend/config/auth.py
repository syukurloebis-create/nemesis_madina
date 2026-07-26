"""
Authentication Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class AuthSettings(BaseSettings):
    """Authentication settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        case_sensitive=False
    )
    
    secret_key: str = Field("dev-secret-key-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")


# ✅ Create auth_settings here
auth_settings = AuthSettings()

__all__ = ["auth_settings", "AuthSettings"]
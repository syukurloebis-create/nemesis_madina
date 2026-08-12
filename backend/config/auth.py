"""
Authentication Configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class AuthSettings(BaseSettings):
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    password_min_length: int = 8
    password_max_length: int = 72

    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True


auth_settings = AuthSettings()

__all__ = ["auth_settings", "AuthSettings"]
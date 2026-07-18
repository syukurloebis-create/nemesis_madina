"""
Authentication Configuration
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field

class AuthSettings(BaseSettings):
    """Authentication settings"""
    
    # JWT Settings
    JWT_SECRET_KEY: str = Field(
        default=os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    
    # Password Policy
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    PASSWORD_REQUIRE_DIGIT: bool = Field(default=True, env="PASSWORD_REQUIRE_DIGIT")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")
    
    # Rate Limiting
    LOGIN_RATE_LIMIT: int = Field(default=5, env="LOGIN_RATE_LIMIT")  # per minute
    LOGIN_RATE_LIMIT_WINDOW: int = Field(default=60, env="LOGIN_RATE_LIMIT_WINDOW")  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

auth_settings = AuthSettings()
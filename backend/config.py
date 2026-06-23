# backend/config.py
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "NEMESIS V8+"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://nemesis:nemesis123@localhost:5432/nemesis_db"
    )
    DATABASE_SYNC_URL: str = os.getenv(
        "DATABASE_SYNC_URL",
        "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "5"))
    
    # Security - WITH DEFAULT FOR DEVELOPMENT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "nemesis-v8-secret-key-2026-for-development-only"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
    
    # Multi-tenant
    DEFAULT_TENANT_ID: str = os.getenv(
        "DEFAULT_TENANT_ID",
        "00000000-0000-0000-0000-000000000001"
    )
    
    # Storage
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "localhost:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET_EVIDENCE: str = os.getenv("S3_BUCKET_EVIDENCE", "nemesis-evidence")
    S3_BUCKET_BACKUP: str = os.getenv("S3_BUCKET_BACKUP", "nemesis-backup")
    S3_SECURE: bool = os.getenv("S3_SECURE", "false").lower() == "true"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # TSA
    TSA_URL: str = os.getenv("TSA_URL", "http://timestamp.digicert.com")
    TSA_ENABLED: bool = os.getenv("TSA_ENABLED", "false").lower() == "true"
    
    # Performance
    EVENT_BATCH_SIZE: int = int(os.getenv("EVENT_BATCH_SIZE", "10000"))
    SNAPSHOT_INTERVAL: int = int(os.getenv("SNAPSHOT_INTERVAL", "1000"))
    REBUILD_PARALLEL_WORKERS: int = int(os.getenv("REBUILD_PARALLEL_WORKERS", "4"))
    
    # API Version
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": False
    }


settings = Settings()


# Optional: Add validation for production
if settings.ENVIRONMENT == "production":
    if settings.SECRET_KEY == "nemesis-v8-secret-key-2026-for-development-only":
        raise ValueError("❌ Must change SECRET_KEY in production!")
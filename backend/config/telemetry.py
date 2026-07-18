# backend/config/telemetry.py

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import Optional
from enum import Enum


class TelemetrySettings(BaseSettings):
    """Telemetry configuration."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True
    )
    
    prometheus_enabled: bool = Field(True, alias="PROMETHEUS_ENABLED")
    otlp_enabled: bool = Field(False, alias="OTLP_ENABLED")
    otlp_endpoint: Optional[str] = Field(None, alias="OTLP_ENDPOINT")
    log_level: str = Field("info", alias="LOG_LEVEL")
    log_json: bool = Field(True, alias="LOG_JSON")
    
    # Tracing
    trace_sampling_rate: float = Field(0.1, alias="TRACE_SAMPLING_RATE")
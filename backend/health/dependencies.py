"""
Health Dependencies — Data Transfer Object untuk HealthChecker.
"""

from dataclasses import dataclass
from typing import Optional, Any

from backend.infrastructure.sql_repository import SQLRepository


@dataclass(frozen=True)
class HealthDependencies:
    """Dependencies for HealthChecker — future proof."""
    enabled: bool = True
    sql_repo: Optional[SQLRepository] = None
    # Future dependencies (dummy for now)
    redis_client: Optional[Any] = None
    neo4j_client: Optional[Any] = None
    elastic_client: Optional[Any] = None
    kafka_client: Optional[Any] = None
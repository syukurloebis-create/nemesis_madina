"""
Health Interfaces — Protocol untuk Dependency Inversion.
"""

from typing import Protocol

from backend.health.health_check import IHealthChecker
from backend.health.dependencies import HealthDependencies


class IHealthCheckerFactory(Protocol):
    """Health Checker Factory Interface."""
    
    def create(self, deps: HealthDependencies) -> IHealthChecker:
        """Create health checker based on dependencies."""
        ...
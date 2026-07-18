"""
Health Checker Factory — Membuat health checker berdasarkan konfigurasi.
"""

from backend.health.health_check import HealthChecker, IHealthChecker
from backend.health.noop_health_checker import NoOpHealthChecker
from backend.health.dependencies import HealthDependencies
from backend.health.interfaces import IHealthCheckerFactory


class HealthCheckerFactory:
    """Factory untuk membuat HealthChecker — tidak inherit Protocol."""
    
    @staticmethod
    def create(deps: HealthDependencies) -> IHealthChecker:
        """
        Create health checker based on dependencies.
        
        Args:
            deps: HealthDependencies with configuration and dependencies
        
        Returns:
            IHealthChecker: HealthChecker if enabled, NoOpHealthChecker otherwise
        """
        if deps.enabled and deps.sql_repo is not None:
            return HealthChecker(deps.sql_repo)
        
        return NoOpHealthChecker()
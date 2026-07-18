"""
NoOp Health Checker — Default implementation when health check is disabled.
"""

from typing import Dict, Any
from datetime import datetime

from backend.health.health_check import IHealthChecker, HealthStatus


class NoOpHealthChecker:
    """
    NoOp Health Checker — Structural typing satisfies IHealthChecker.
    
    Tidak perlu inherit IHealthChecker (Protocol).
    Cukup memiliki method yang sama.
    """
    
    async def check_all(self) -> Dict[str, HealthStatus]:
        return {
            "noop": HealthStatus(
                component="noop",
                status="healthy",
                message="Health check disabled (NoOp)",
                details={"enabled": False}
            )
        }
    
    def get_summary(self, results: Dict[str, HealthStatus]) -> Dict[str, Any]:
        return {
            "overall": "healthy",
            "components": {
                name: status.to_dict() for name, status in results.items()
            },
            "checked_at": datetime.now().isoformat()
        }
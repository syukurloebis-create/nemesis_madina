"""
Health Check — Interface + Implementation.
"""

from typing import Protocol, Dict, Any, Optional, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from datetime import datetime

from backend.infrastructure.sql_repository import SQLRepository


# ✅ Protocol, bukan ABC
class IHealthChecker(Protocol):
    """Health Checker Interface — Structural Typing."""
    
    async def check_all(self) -> Dict[str, "HealthStatus"]:
        """Check all components."""
        ...
    
    def get_summary(self, results: Dict[str, "HealthStatus"]) -> Dict[str, Any]:
        """Get health summary."""
        ...


@dataclass(frozen=True)
class HealthStatus:
    """
    Health check result — fully immutable.
    
    details is stored as Mapping (read-only) to ensure immutability.
    """
    component: str
    status: str  # "healthy" | "degraded" | "unhealthy"
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Convert details to immutable MappingProxyType."""
        # ✅ Gunakan __post_init__, bukan override __init__
        if not isinstance(self.details, MappingProxyType):
            object.__setattr__(
                self,
                'details',
                MappingProxyType(dict(self.details))
            )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "message": self.message,
            "details": dict(self.details),
            "checked_at": self.checked_at.isoformat()
        }


class HealthChecker:
    """Health Check — Comprehensive Health Monitoring."""
    
    def __init__(self, sql_repo: SQLRepository):
        self._sql_repo = sql_repo
    
    async def check_all(self) -> Dict[str, HealthStatus]:
        """Check all components."""
        results = {}
        
        try:
            if self._sql_repo.count() > 0:
                results["sql_repository"] = HealthStatus(
                    component="sql_repository",
                    status="healthy",
                    message="SQL Repository operational",
                    details={"queries_loaded": self._sql_repo.count()}
                )
            else:
                results["sql_repository"] = HealthStatus(
                    component="sql_repository",
                    status="degraded",
                    message="SQL Repository has no queries loaded"
                )
        except Exception as e:
            results["sql_repository"] = HealthStatus(
                component="sql_repository",
                status="unhealthy",
                message=str(e)
            )
        
        return results
    
    def get_summary(self, results: Dict[str, HealthStatus]) -> Dict[str, Any]:
        """Get health summary."""
        unhealthy = [r for r in results.values() if r.status == "unhealthy"]
        degraded = [r for r in results.values() if r.status == "degraded"]
        
        overall = "unhealthy" if unhealthy else ("degraded" if degraded else "healthy")
        
        return {
            "overall": overall,
            "components": {
                name: status.to_dict() for name, status in results.items()
            },
            "checked_at": datetime.now().isoformat()
        }
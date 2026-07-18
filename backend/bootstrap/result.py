"""
Bootstrap Result — Data Transfer Object untuk hasil bootstrap_infrastructure().
"""

from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.core.container import InfrastructureContainer


@dataclass(frozen=True)
class BootstrapInfrastructureResult:
    """
    Result of bootstrap_infrastructure().
    
    Menggantikan tuple (infra, engine) untuk kejelasan.
    """
    infrastructure: InfrastructureContainer
    engine: AsyncEngine
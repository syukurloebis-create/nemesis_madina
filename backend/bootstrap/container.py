# backend/bootstrap/container.py

from typing import Optional, Dict, Any

from backend.config.settings import ApplicationSettings
from backend.telemetry.provider import TelemetryProvider
from backend.cache.provider import CacheProvider
from backend.cache.memory_cache import MemoryCache
from backend.cache.redis_cache import RedisCache
from backend.cache.no_cache import NoCache
from backend.dashboard.executor.parallel_executor import ParallelExecutor
from backend.dashboard.executor.circuit_breaker import CircuitBreakerRegistry
from backend.dashboard.executor.pipeline_policy import PipelinePolicy
from backend.dashboard.orchestrators.dashboard_orchestrator import DashboardOrchestrator
from backend.dashboard.orchestrators.pipeline_planner import PipelinePlanner
from backend.dashboard.aggregators.intelligence_aggregator import IntelligenceAggregator
from backend.dashboard.policies.scoring_policy import DashboardScoringPolicy
from backend.dashboard.presenters.dashboard_presenter import DashboardPresenter
from backend.services.dashboard_intelligence_service import DashboardIntelligenceService
from backend.bootstrap.modules import (
    build_pipeline_registry,
    build_presenters,
    build_runtime_components
)


class ApplicationContainer:
    """
    Application container - composition root.
    
    All dependencies are wired here.
    """
    
    def __init__(self, settings: ApplicationSettings):
        self.settings = settings
        
        # Cache
        self.cache = self._build_cache()
        
        # Telemetry
        self.telemetry = TelemetryProvider()
        
        # Pipeline Registry
        self.pipeline_registry = build_pipeline_registry()
        
        # Runtime Components
        self.runtime = build_runtime_components(
            registry=self.pipeline_registry,
            cache=self.cache,
            telemetry=self.telemetry
        )
        
        # Presenters
        self.presenters = build_presenters()
        
        # Service
        self.service = DashboardIntelligenceService(
            orchestrator=self.runtime.orchestrator,
            presenter=self.presenters
        )
    
    def _build_cache(self) -> CacheProvider:
        """Build cache based on settings."""
        cache_type = self.settings.cache.type
        
        if cache_type == "redis":
            return RedisCache(
                redis_url=self.settings.cache.redis_url,
                default_ttl=self.settings.cache.default_ttl
            )
        elif cache_type == "nocache":
            return NoCache()
        else:  # memory
            return MemoryCache(
                max_size=self.settings.cache.max_size,
                default_ttl=self.settings.cache.default_ttl
            )
    
    async def startup(self):
        """Startup container."""
        await self.telemetry.startup()
    
    async def shutdown(self):
        """Shutdown container."""
        await self.telemetry.shutdown()
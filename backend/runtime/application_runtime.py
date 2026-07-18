# backend/runtime/application_runtime.py

import asyncio
import signal
import logging
from typing import Optional, List, Callable, Awaitable, Dict, Any
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from backend.config.settings import ApplicationSettings
from backend.telemetry.provider import TelemetryProvider
from backend.cache.provider import CacheProvider
from backend.bootstrap.container import ApplicationContainer

logger = logging.getLogger(__name__)


class ApplicationRuntime:
    """
    Application runtime with full lifecycle management.
    
    Lifecycle:
    1. Startup
    2. Running (serving requests)
    3. Health checks
    4. Graceful shutdown
    5. Reload (optional)
    """
    
    def __init__(
        self,
        settings: ApplicationSettings,
        telemetry: TelemetryProvider,
        cache: CacheProvider,
        container: ApplicationContainer
    ):
        self.settings = settings
        self.telemetry = telemetry
        self.cache = cache
        self.container = container
        
        self._startup_hooks: List[Callable[[], Awaitable[None]]] = []
        self._shutdown_hooks: List[Callable[[], Awaitable[None]]] = []
        self._health_checks: List[Callable[[], Awaitable[Dict[str, Any]]]] = []
        
        self._started_at: Optional[datetime] = None
        self._shutdown_event = asyncio.Event()
    
    def add_startup_hook(self, hook: Callable[[], Awaitable[None]]):
        """Add a startup hook."""
        self._startup_hooks.append(hook)
    
    def add_shutdown_hook(self, hook: Callable[[], Awaitable[None]]):
        """Add a shutdown hook."""
        self._shutdown_hooks.append(hook)
    
    def add_health_check(self, check: Callable[[], Awaitable[Dict[str, Any]]]):
        """Add a health check."""
        self._health_checks.append(check)
    
    async def startup(self):
        """Start the application."""
        logger.info("Starting application...")
        self._started_at = datetime.now(timezone.utc)
        
        # Run startup hooks
        for hook in self._startup_hooks:
            try:
                await hook()
            except Exception as e:
                logger.error(f"Startup hook failed: {e}")
                raise
        
        # Initialize components
        await self.telemetry.startup()
        
        logger.info("Application started successfully")
    
    async def shutdown(self):
        """Shutdown the application gracefully."""
        logger.info("Shutting down application...")
        
        # Run shutdown hooks
        for hook in self._shutdown_hooks:
            try:
                await hook()
            except Exception as e:
                logger.error(f"Shutdown hook failed: {e}")
        
        # Shutdown components
        await self.telemetry.shutdown()
        
        self._shutdown_event.set()
        logger.info("Application shutdown complete")
    
    async def health(self) -> Dict[str, Any]:
        """Get application health."""
        status = "healthy"
        components = {}
        
        for check in self._health_checks:
            try:
                result = await check()
                components.update(result)
                if result.get("status") != "healthy":
                    status = "degraded"
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                status = "unhealthy"
                components["error"] = str(e)
        
        return {
            "status": status,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "uptime_seconds": self._get_uptime_seconds(),
            "components": components,
            "version": self.settings.base.version,
            "environment": self.settings.base.environment.value
        }
    
    async def readiness(self) -> Dict[str, Any]:
        """Readiness check for Kubernetes."""
        health = await self.health()
        if health["status"] != "healthy":
            health["status"] = "not_ready"
        return health
    
    async def liveness(self) -> Dict[str, Any]:
        """Liveness check for Kubernetes."""
        return {
            "status": "alive",
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "version": self.settings.base.version
        }
    
    def _get_uptime_seconds(self) -> float:
        if self._started_at:
            return (datetime.now(timezone.utc) - self._started_at).total_seconds()
        return 0
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        loop = asyncio.get_running_loop()
        
        # Register signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.shutdown())
            )
        
        await self._shutdown_event.wait()
    
    @asynccontextmanager
    async def run(self):
        """Context manager for running the application."""
        try:
            await self.startup()
            yield self
        finally:
            await self.shutdown()
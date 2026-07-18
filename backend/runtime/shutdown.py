# backend/runtime/shutdown.py

import asyncio
import signal
import logging
from typing import List, Callable, Awaitable

logger = logging.getLogger(__name__)


class ShutdownManager:
    """Manages graceful shutdown of services."""
    
    def __init__(self):
        self._shutdown_hooks: List[Callable[[], Awaitable[None]]] = []
        self._shutdown_event = asyncio.Event()
    
    def add_shutdown_hook(self, hook: Callable[[], Awaitable[None]]):
        """Add a shutdown hook."""
        self._shutdown_hooks.append(hook)
    
    async def shutdown(self):
        """Execute all shutdown hooks."""
        logger.info("Starting graceful shutdown...")
        
        for hook in self._shutdown_hooks:
            try:
                await hook()
            except Exception as e:
                logger.error(f"Error in shutdown hook: {e}")
        
        self._shutdown_event.set()
        logger.info("Graceful shutdown complete")
    
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


# Global shutdown manager
shutdown_manager = ShutdownManager()
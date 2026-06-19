#!/usr/bin/env python3
"""
NEMESIS Background Worker
"""

import asyncio
import signal
import sys
from datetime import datetime

from backend.telemetry.logging import get_logger
from backend.telemetry.metrics import metrics_registry

logger = get_logger("worker")
running = True


def signal_handler():
    """Handle shutdown signals"""
    global running
    logger.info("Received shutdown signal")
    running = False


async def process_events():
    """Process events from queue"""
    from backend.core.events import EventBus
    bus = EventBus()
    
    # Subscribe to all events
    async def handler(event):
        logger.debug(f"Processing event: {event.type}")
        metrics_registry.counter("worker_events_processed", 1)
    
    bus.subscribe("*", handler)
    
    while running:
        await asyncio.sleep(1)
    
    logger.info("Worker stopped")


async def main():
    """Main worker loop"""
    logger.info("NEMESIS Worker starting...")
    
    # Set up signal handlers
    loop = asyncio.get_event_loop()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await process_events()
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

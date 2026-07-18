"""
Startup Handler - Initialize services on application start
"""

import logging
from runtime.validator import startup_validator

logger = logging.getLogger(__name__)


async def startup_handler():
    """Initialize all services"""
    print("\n" + "="*60)
    print("NEMESIS STARTUP")
    print("="*60)
    
    # Run validations
    print("\nRunning startup validations...")
    is_valid, errors, warnings = await startup_validator.run_all_async()
    
    if not is_valid:
        print("\n❌ Startup validation failed. Continuing with warnings...")
        # Don't exit, just warn for development
    
    # Initialize evidence registry
    try:
        from backend.evidence import EvidenceRegistry
        registry = EvidenceRegistry()
        logger.info("Evidence registry initialized")
        print("  ✅ Evidence registry")
    except Exception as e:
        logger.error(f"Evidence registry failed: {e}")
        print(f"  ❌ Evidence registry: {e}")
    
    # Initialize event bus
    try:
        from core.events import EventBus
        event_bus = EventBus()
        logger.info("Event bus initialized")
        print("  ✅ Event bus")
    except Exception as e:
        logger.error(f"Event bus failed: {e}")
        print(f"  ❌ Event bus: {e}")
    
    # Initialize WebSocket manager
    try:
        from websocket import ConnectionManager
        ws_manager = ConnectionManager()
        logger.info("WebSocket manager initialized")
        print("  ✅ WebSocket manager")
    except Exception as e:
        logger.error(f"WebSocket manager failed: {e}")
        print(f"  ❌ WebSocket manager: {e}")
    
    # Initialize graph
    try:
        from graph import GraphBuilder
        graph = GraphBuilder()
        logger.info("Graph initialized")
        print("  ✅ Graph builder")
    except Exception as e:
        logger.error(f"Graph failed: {e}")
        print(f"  ❌ Graph: {e}")
    
    print("\n" + "="*60)
    print("NEMESIS STARTUP COMPLETE")
    print("="*60)
    print("API available at: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    return True

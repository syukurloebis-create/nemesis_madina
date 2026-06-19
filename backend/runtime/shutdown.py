"""
Shutdown Handler - Clean up services on application shutdown
"""

import logging
import asyncio

logger = logging.getLogger(__name__)


async def shutdown_handler():
    """Clean up services"""
    print("\n" + "="*60)
    print("NEMESIS SHUTDOWN")
    print("="*60)
    
    # Close WebSocket connections
    try:
        from backend.websocket import ConnectionManager
        ws_manager = ConnectionManager()
        
        # Broadcast shutdown message
        await ws_manager.broadcast({
            "type": "shutdown",
            "message": "Server is shutting down"
        })
        
        # Close all connections
        for client_id in list(ws_manager.connections.keys()):
            await ws_manager.disconnect(client_id)
        
        logger.info("WebSocket connections closed")
        print("  ✅ WebSocket connections closed")
    except Exception as e:
        logger.error(f"WebSocket shutdown error: {e}")
        print(f"  ❌ WebSocket shutdown: {e}")
    
    # Save state if needed
    try:
        from backend.core.events import EventBus
        bus = EventBus()
        
        # Take final snapshot
        from backend.core.events.snapshots import EventSnapshot
        snapshot = EventSnapshot()
        snapshot_id = snapshot.create_snapshot({
            "events": bus.get_history(limit=1000),
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Final snapshot saved: {snapshot_id}")
        print(f"  ✅ Final snapshot: {snapshot_id}")
    except Exception as e:
        logger.warning(f"Snapshot save failed: {e}")
        print(f"  ⚠️ Snapshot save: {e}")
    
    print("\n" + "="*60)
    print("NEMESIS SHUTDOWN COMPLETE")
    print("="*60 + "\n")
    
    return True


from datetime import datetime
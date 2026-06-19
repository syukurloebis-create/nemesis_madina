"""
Simple WebSocket Handler - Uses ConnectionManager
"""

from backend.websocket.manager import ConnectionManager

manager = ConnectionManager()


async def handle_websocket(websocket):
    """Simple WebSocket handler - delegates to manager"""
    await websocket.accept()
    
    client_id = await manager.connect(websocket)
    if client_id is None:
        return
    
    await manager.wait_until_disconnect(client_id)


def get_stats():
    """Get WebSocket statistics"""
    return manager.get_metrics()

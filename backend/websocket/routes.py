"""
WebSocket Routes - Clean, no duplicate readers
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.websocket.manager import ConnectionManager

router = APIRouter(tags=["websocket"])
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint - accepts connection and lets manager handle messages.
    NO duplicate reader here!
    """
    await websocket.accept()
    
    client_id = await manager.connect(websocket)
    if client_id is None:
        return
    
    # Wait for disconnection - manager handles all messages
    await manager.wait_until_disconnect(client_id)


@router.websocket("/ws/{room_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str):
    """
    Room WebSocket endpoint - auto-join room.
    NO duplicate reader here!
    """
    await websocket.accept()
    
    client_id = await manager.connect(websocket)
    if client_id is None:
        return
    
    # Auto-join room
    await manager.join_room(client_id, room_id)
    
    # Send room joined confirmation
    await manager.send(client_id, {
        "type": "room_joined",
        "room_id": room_id,
        "timestamp": datetime.now().isoformat()
    })
    
    # Wait for disconnection
    await manager.wait_until_disconnect(client_id)


@router.get("/websocket/metrics")
async def websocket_metrics():
    """Get WebSocket metrics"""
    return manager.get_metrics()


@router.get("/websocket/connections")
async def websocket_connections():
    """Get active connections"""
    return {
        "total": manager.connection_count,
        "max": 1000,
        "utilization_percent": round(manager.connection_count / 1000 * 100, 1)
    }


from datetime import datetime

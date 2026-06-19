import asyncio
import json
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect  # ← Tambahkan ini
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time alerts"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.rooms: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Also remove from rooms
        for room_name, connections in self.rooms.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def broadcast(self, message: str, room: Optional[str] = None):
        """Broadcast message to all connections or specific room"""
        if room:
            connections = self.rooms.get(room, [])
        else:
            connections = self.active_connections.copy()
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def join_room(self, websocket: WebSocket, room: str):
        """Add connection to a room"""
        if room not in self.rooms:
            self.rooms[room] = []
        if websocket not in self.rooms[room]:
            self.rooms[room].append(websocket)
        logger.info(f"WebSocket joined room '{room}'. Room size: {len(self.rooms[room])}")
    
    async def leave_room(self, websocket: WebSocket, room: str):
        """Remove connection from a room"""
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
            logger.info(f"WebSocket left room '{room}'. Room size: {len(self.rooms[room])}")
    
    async def broadcast_to_room(self, room: str, message: str):
        """Broadcast message to specific room only"""
        await self.broadcast(message, room=room)


# Singleton instance
ws_manager = WebSocketManager()
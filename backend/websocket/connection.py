"""
WebSocket Connection - Individual Connection Wrapper
"""

import json
from starlette.websockets import WebSocketState
from datetime import datetime
from typing import Optional, AsyncIterator, Dict, Any


class WebSocketConnection:
    """Wrapper for individual WebSocket connection"""
    
    def __init__(self, id: str, websocket, connected_at: datetime):
        self.id = id
        self._websocket = websocket
        self.connected_at = connected_at
        self.last_activity = connected_at
        self.metadata: Dict[str, Any] = {}
        self._closed = False
    
    @property
    def is_alive(self) -> bool:
        """Check if connection is still alive"""

        if self._closed:
            return False

        try:
            return (
                self._websocket.client_state == WebSocketState.CONNECTED
                and self._websocket.application_state == WebSocketState.CONNECTED
            )
        except Exception:
            return False
    
    async def send(self, message: dict):
        """Send message to client"""
        if self.is_alive:
            await self._websocket.send_json(message)
            self.last_activity = datetime.now()
    
    async def send_text(self, text: str):
        """Send raw text to client"""
        if self.is_alive:
            await self._websocket.send_text(text)
            self.last_activity = datetime.now()
    
    async def send_bytes(self, data: bytes):
        """Send bytes to client"""
        if self.is_alive:
            await self._websocket.send_bytes(data)
            self.last_activity = datetime.now()
    
    async def receive(self) -> AsyncIterator[dict]:
        """Receive messages from client"""
        try:
            async for message in self._websocket:
                if isinstance(message, str):
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        data = {"raw": message}
                else:
                    data = message
                
                self.last_activity = datetime.now()
                yield data
                
        except Exception:
            pass
    
    async def close(self):
        """Close connection"""
        if not self._closed:
            self._closed = True
            try:
                await self._websocket.close()
            except Exception:
                pass
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "is_alive": self.is_alive,
            "metadata": self.metadata
        }

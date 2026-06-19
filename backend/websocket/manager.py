"""
WebSocket Connection Manager - Single Reader Architecture
"""

import asyncio
import uuid
import json
from typing import Dict, Set, Optional, Any, Callable
from datetime import datetime
from threading import Lock
from collections import defaultdict
import time

# Configuration
MAX_CONNECTIONS = 1000
RATE_LIMIT_WINDOW = 5
RATE_LIMIT_MAX = 20


class ConnectionManager:
    """Manage WebSocket connections - Single reader architecture"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._connections: Dict[str, Any] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._room_connections: Dict[str, Set[str]] = defaultdict(set)
        self._rate_limits: Dict[str, list] = defaultdict(list)
        self._handlers: Dict[str, Callable] = {}
        
        self._message_count = 0
        self._total_connections = 0
        self._initialized = True
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        self.register_handler("ping", self._handle_ping)
        self.register_handler("subscribe", self._handle_subscribe)
        self.register_handler("unsubscribe", self._handle_unsubscribe)
        self.register_handler("broadcast", self._handle_broadcast_message)
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register a message handler"""
        self._handlers[msg_type] = handler
    
    async def _handle_ping(self, message: dict, client_id: str) -> dict:
        """Handle ping message"""
        return {
            "type": "pong",
            "timestamp": message.get("timestamp", datetime.now().isoformat())
        }
    
    async def _handle_subscribe(self, message: dict, client_id: str) -> dict:
        """Handle subscribe message"""
        events = message.get("events", [])
        for event in events:
            await self.join_room(client_id, event)
        return {
            "type": "subscribed",
            "events": events,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_unsubscribe(self, message: dict, client_id: str) -> dict:
        """Handle unsubscribe message"""
        events = message.get("events", [])
        for event in events:
            await self.leave_room(client_id, event)
        return {
            "type": "unsubscribed",
            "events": events,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _message_loop(self, client_id: str):
        """Single message loop for a connection"""
        conn = self._connections.get(client_id)
        if not conn:
            return
        
        websocket = conn["websocket"]
        
        try:
            while True:
                # Single point of reading - NO DUPLICATE READERS
                data = await websocket.receive_text()
                self._message_count += 1
                conn["last_activity"] = datetime.now()
                conn["message_count"] += 1
                
                # Process message
                try:
                    message = json.loads(data)
                    msg_type = message.get("type", "unknown")
                    
                    # Find handler
                    handler = self._handlers.get(msg_type)
                    if handler:
                        response = await handler(message, client_id)
                        if response:
                            await self.send(client_id, response)
                    else:
                        # Echo for unknown types
                        await self.send(client_id, {
                            "type": "echo",
                            "received": message,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                except json.JSONDecodeError:
                    await self.send(client_id, {
                        "type": "error",
                        "message": "Invalid JSON",
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"[WS] Message loop error for {client_id}: {e}")
        finally:
            await self.disconnect(client_id)
    
    def total_connections(self) -> int:
        """Get total number of connections"""
        return len(self._connections)
    
    def can_accept(self) -> bool:
        """Check if new connection can be accepted"""
        return self.total_connections() < MAX_CONNECTIONS
    
    def is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited"""
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW
        
        # Clean old entries
        self._rate_limits[client_id] = [
            t for t in self._rate_limits[client_id]
            if t > window_start
        ]
        
        if len(self._rate_limits[client_id]) >= RATE_LIMIT_MAX:
            return True
        
        self._rate_limits[client_id].append(now)
        return False
    
    async def connect(self, websocket, client_id: Optional[str] = None) -> Optional[str]:
        """Accept new connection with limits"""
        # Check global limit
        if not self.can_accept():
            await websocket.close(code=1013, reason="Server at capacity")
            return None
        
        if client_id is None:
            client_id = str(uuid.uuid4())
        
        # Check rate limit
        if self.is_rate_limited(client_id):
            await websocket.close(code=1013, reason="Rate limit exceeded")
            return None
        
        # Store connection
        self._connections[client_id] = {
            "websocket": websocket,
            "connected_at": datetime.now(),
            "last_activity": datetime.now(),
            "message_count": 0
        }
        self._total_connections += 1
        
        # Start single message loop - THIS IS THE ONLY READER
        task = asyncio.create_task(self._message_loop(client_id))
        self._tasks[client_id] = task
        
        # Send welcome message
        await self.send(client_id, {
            "type": "connected",
            "client_id": client_id,
            "active_connections": self.total_connections(),
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"[WS] Client {client_id} connected. Active: {self.total_connections()}")
        return client_id
    
    async def disconnect(self, client_id: str):
        """Close connection and cancel task"""
        # Cancel message loop task
        task = self._tasks.pop(client_id, None)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Remove from rooms
        for room_id in list(self._room_connections.keys()):
            self._room_connections[room_id].discard(client_id)
        
        # Remove connection
        if client_id in self._connections:
            conn = self._connections[client_id]
            try:
                await conn["websocket"].close()
            except:
                pass
            del self._connections[client_id]
        
        print(f"[WS] Client {client_id} disconnected. Active: {self.total_connections()}")
    
    async def wait_until_disconnect(self, client_id: str):
        """Wait until connection is disconnected"""
        task = self._tasks.get(client_id)
        if task:
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def send(self, client_id: str, message: dict) -> bool:
        """Send message to specific client"""
        conn = self._connections.get(client_id)
        if conn:
            try:
                await conn["websocket"].send_text(json.dumps(message))
                return True
            except Exception:
                await self.disconnect(client_id)
        return False
    
    async def broadcast(self, message: dict, exclude: Set[str] = None):
        """Broadcast to all connected clients"""
        exclude = exclude or set()
        tasks = []
        for client_id in self._connections:
            if client_id not in exclude:
                tasks.append(self.send(client_id, message))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude: Set[str] = None):
        """Broadcast to clients in specific room"""
        exclude = exclude or set()
        tasks = []
        for client_id in self._room_connections.get(room_id, set()):
            if client_id not in exclude:
                tasks.append(self.send(client_id, message))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def join_room(self, client_id: str, room_id: str):
        """Add client to room"""
        self._room_connections[room_id].add(client_id)
    
    async def leave_room(self, client_id: str, room_id: str):
        """Remove client from room"""
        self._room_connections[room_id].discard(client_id)
    
    def get_metrics(self) -> dict:
        """Get connection metrics"""
        return {
            "active_connections": self.total_connections(),
            "max_connections": MAX_CONNECTIONS,
            "utilization_percent": round(self.total_connections() / MAX_CONNECTIONS * 100, 1) if MAX_CONNECTIONS > 0 else 0,
            "total_connections_served": self._total_connections,
            "messages_processed": self._message_count,
            "rooms_count": len(self._room_connections),
            "rate_limit_window_seconds": RATE_LIMIT_WINDOW,
            "rate_limit_max_per_window": RATE_LIMIT_MAX
        }
    
    @property
    def connections(self) -> Dict:
        return self._connections
    
    @property
    def connection_count(self) -> int:
        return self.total_connections()

    async def _handle_broadcast_message(self, message: dict, client_id: str) -> dict:
        """Handle broadcast message from client"""
        room_id = message.get("room")
        payload = message.get("payload", {})
        
        if not room_id:
            return {"type": "error", "message": "Missing 'room' parameter", "timestamp": datetime.now().isoformat()}
        
        # Broadcast to all clients in the room except sender
        await self.broadcast_to_room(room_id, {
            "type": "broadcast",
            "from": client_id,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }, exclude={client_id})
        
        return {
            "type": "broadcast_ack",
            "room": room_id,
            "timestamp": datetime.now().isoformat()
        }

#!/usr/bin/env python3
"""
NEMESIS FASE 1 - WebSocket Domain Canonicalization
Membuat single source of truth untuk WebSocket management
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

WEBSOCKET_DIR = PROJECT_ROOT / "backend" / "websocket"

def create_websocket_directory():
    """Buat struktur direktori websocket"""
    print("\n📁 Creating websocket directory structure...")
    
    WEBSOCKET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Buat __init__.py
    init_file = WEBSOCKET_DIR / "__init__.py"
    init_content = '''"""
NEMESIS WebSocket Domain - Single Source of Truth
==================================================
Modul ini adalah canonical source untuk WebSocket operations.

Exports:
    - ConnectionManager: Manajemen koneksi WebSocket
    - WebSocketConnection: Koneksi individual
    - EventBroadcaster: Broadcast event ke clients
    - WebSocketObservability: Metrics dan monitoring
"""

from backend.websocket.manager import ConnectionManager
from backend.websocket.connection import WebSocketConnection
from backend.websocket.broadcaster import EventBroadcaster
from backend.websocket.observability import WebSocketObservability
from backend.websocket.protocol import MessageProtocol
from backend.websocket.recovery import RecoveryHandler

__all__ = [
    'ConnectionManager',
    'WebSocketConnection',
    'EventBroadcaster',
    'WebSocketObservability',
    'MessageProtocol',
    'RecoveryHandler'
]
'''
    init_file.write_text(init_content)
    print(f"  ✅ Created: {init_file}")
    return True

def create_manager():
    """Buat manager.py - connection management"""
    content = '''"""
WebSocket Connection Manager
"""

import asyncio
import uuid
from typing import Dict, Set, Optional, Any, Callable
from datetime import datetime
from threading import Lock

from backend.websocket.connection import WebSocketConnection
from backend.websocket.observability import WebSocketObservability


class ConnectionManager:
    """Manage all WebSocket connections - SINGLETON"""
    
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
        
        self._connections: Dict[str, WebSocketConnection] = {}
        self._room_connections: Dict[str, Set[str]] = {}
        self._observability = WebSocketObservability()
        self._message_handlers: Dict[str, Callable] = {}
        self._initialized = True
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register handler for specific message type"""
        self._message_handlers[message_type] = handler
    
    async def connect(self, websocket, client_id: Optional[str] = None) -> str:
        """Accept new connection"""
        if client_id is None:
            client_id = str(uuid.uuid4())
        
        connection = WebSocketConnection(
            id=client_id,
            websocket=websocket,
            connected_at=datetime.now()
        )
        
        self._connections[client_id] = connection
        self._observability.connection_opened()
        
        # Start message loop
        asyncio.create_task(self._message_loop(client_id))
        
        return client_id
    
    async def disconnect(self, client_id: str):
        """Close connection"""
        if client_id in self._connections:
            connection = self._connections[client_id]
            await connection.close()
            del self._connections[client_id]
            
            # Remove from rooms
            for room_id in list(self._room_connections.keys()):
                if client_id in self._room_connections.get(room_id, set()):
                    self._room_connections[room_id].discard(client_id)
            
            self._observability.connection_closed()
    
    async def send(self, client_id: str, message: dict) -> bool:
        """Send message to specific client"""
        connection = self._connections.get(client_id)
        if connection and connection.is_alive:
            try:
                await connection.send(message)
                self._observability.message_sent()
                return True
            except Exception:
                await self.disconnect(client_id)
        return False
    
    async def broadcast(self, message: dict, exclude: Set[str] = None):
        """Broadcast message to all connected clients"""
        exclude = exclude or set()
        tasks = []
        
        for client_id, connection in self._connections.items():
            if client_id not in exclude and connection.is_alive:
                tasks.append(self.send(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude: Set[str] = None):
        """Broadcast message to clients in specific room"""
        exclude = exclude or set()
        tasks = []
        
        for client_id in self._room_connections.get(room_id, set()):
            if client_id not in exclude:
                tasks.append(self.send(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def join_room(self, client_id: str, room_id: str):
        """Add client to room"""
        if room_id not in self._room_connections:
            self._room_connections[room_id] = set()
        self._room_connections[room_id].add(client_id)
    
    async def leave_room(self, client_id: str, room_id: str):
        """Remove client from room"""
        if room_id in self._room_connections:
            self._room_connections[room_id].discard(client_id)
    
    async def _message_loop(self, client_id: str):
        """Handle incoming messages from client"""
        connection = self._connections.get(client_id)
        if not connection:
            return
        
        try:
            async for message in connection.receive():
                self._observability.message_received()
                
                # Handle message
                msg_type = message.get("type", "unknown")
                handler = self._message_handlers.get(msg_type)
                
                if handler:
                    try:
                        response = await handler(message, client_id)
                        if response:
                            await self.send(client_id, response)
                    except Exception as e:
                        await self.send(client_id, {
                            "type": "error",
                            "message": str(e)
                        })
                
        except Exception:
            pass
        finally:
            await self.disconnect(client_id)
    
    @property
    def connection_count(self) -> int:
        """Get current connection count"""
        return len(self._connections)
    
    @property
    def connections(self) -> Dict[str, WebSocketConnection]:
        """Get all connections"""
        return self._connections.copy()
    
    def get_metrics(self) -> dict:
        """Get connection metrics"""
        return self._observability.get_metrics()
'''
    
    file_path = WEBSOCKET_DIR / "manager.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_connection():
    """Buat connection.py - individual connection"""
    content = '''"""
WebSocket Connection - Individual Connection Wrapper
"""

import json
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
        return not self._closed and not self._websocket.closed
    
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
'''
    
    file_path = WEBSOCKET_DIR / "connection.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_broadcaster():
    """Buat broadcaster.py - event broadcasting"""
    content = '''"""
Event Broadcaster - Broadcast events to clients
"""

import asyncio
from typing import Dict, Set, Any, Optional
from collections import defaultdict
from datetime import datetime


class EventBroadcaster:
    """Broadcast events to WebSocket clients"""
    
    def __init__(self, connection_manager):
        self.manager = connection_manager
        self._subscriptions: Dict[str, Set[str]] = defaultdict(set)  # event_type -> client_ids
        self._client_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # client_id -> event_types
    
    def subscribe(self, client_id: str, event_type: str):
        """Subscribe client to event type"""
        self._subscriptions[event_type].add(client_id)
        self._client_subscriptions[client_id].add(event_type)
    
    def unsubscribe(self, client_id: str, event_type: str):
        """Unsubscribe client from event type"""
        self._subscriptions[event_type].discard(client_id)
        self._client_subscriptions[client_id].discard(event_type)
    
    def unsubscribe_all(self, client_id: str):
        """Unsubscribe client from all events"""
        for event_type in self._client_subscriptions.get(client_id, set()):
            self._subscriptions[event_type].discard(client_id)
        self._client_subscriptions[client_id].clear()
    
    async def broadcast_event(self, event_type: str, data: Any, exclude: Set[str] = None):
        """Broadcast event to all subscribed clients"""
        exclude = exclude or set()
        subscribers = self._subscriptions.get(event_type, set())
        targets = subscribers - exclude
        
        if not targets:
            return
        
        message = {
            "type": "event",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to each target
        tasks = []
        for client_id in targets:
            tasks.append(self.manager.send(client_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_all(self, event_type: str, data: Any):
        """Broadcast to all connected clients regardless of subscription"""
        message = {
            "type": "broadcast",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast(message)
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for event type"""
        return len(self._subscriptions.get(event_type, set()))
    
    def get_metrics(self) -> dict:
        """Get broadcaster metrics"""
        return {
            "total_subscriptions": sum(len(s) for s in self._subscriptions.values()),
            "event_types": len(self._subscriptions),
            "subscribers_by_type": {
                k: len(v) for k, v in self._subscriptions.items()
            }
        }
'''
    
    file_path = WEBSOCKET_DIR / "broadcaster.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_observability():
    """Buat observability.py - metrics"""
    content = '''"""
WebSocket Observability - Metrics and Monitoring
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from threading import Lock


@dataclass
class WebSocketMetrics:
    """WebSocket metrics data"""
    connections_opened: int = 0
    connections_closed: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    errors: int = 0


class WebSocketObservability:
    """Collect and expose WebSocket metrics"""
    
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
        self._metrics = WebSocketMetrics()
        self._initialized = True
    
    def connection_opened(self):
        """Record connection opened"""
        self._metrics.connections_opened += 1
    
    def connection_closed(self):
        """Record connection closed"""
        self._metrics.connections_closed += 1
    
    def message_sent(self):
        """Record message sent"""
        self._metrics.messages_sent += 1
    
    def message_received(self):
        """Record message received"""
        self._metrics.messages_received += 1
    
    def error_occurred(self):
        """Record error"""
        self._metrics.errors += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "connections_opened": self._metrics.connections_opened,
            "connections_closed": self._metrics.connections_closed,
            "active_connections": self._metrics.connections_opened - self._metrics.connections_closed,
            "messages_sent": self._metrics.messages_sent,
            "messages_received": self._metrics.messages_received,
            "errors": self._metrics.errors
        }
    
    def reset(self):
        """Reset metrics (for testing)"""
        self._metrics = WebSocketMetrics()
'''
    
    file_path = WEBSOCKET_DIR / "observability.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_protocol():
    """Buat protocol.py - message protocol"""
    content = '''"""
Message Protocol - Standard message formats
"""

from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime


class MessageType(str, Enum):
    """Standard message types"""
    PING = "ping"
    PONG = "pong"
    EVENT = "event"
    BROADCAST = "broadcast"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    ERROR = "error"
    ACK = "ack"


class MessageProtocol:
    """Standard message protocol for WebSocket communication"""
    
    @staticmethod
    def ping() -> Dict[str, Any]:
        """Create ping message"""
        return {
            "type": MessageType.PING,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def pong() -> Dict[str, Any]:
        """Create pong message"""
        return {
            "type": MessageType.PONG,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def event(event_type: str, data: Any, event_id: Optional[str] = None) -> Dict[str, Any]:
        """Create event message"""
        return {
            "type": MessageType.EVENT,
            "event_type": event_type,
            "data": data,
            "event_id": event_id,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def broadcast(event_type: str, data: Any) -> Dict[str, Any]:
        """Create broadcast message"""
        return {
            "type": MessageType.BROADCAST,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def subscribe(event_types: list) -> Dict[str, Any]:
        """Create subscribe message"""
        return {
            "type": MessageType.SUBSCRIBE,
            "event_types": event_types,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def unsubscribe(event_types: list) -> Dict[str, Any]:
        """Create unsubscribe message"""
        return {
            "type": MessageType.UNSUBSCRIBE,
            "event_types": event_types,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def ack(message_id: str, status: str = "ok") -> Dict[str, Any]:
        """Create acknowledgment message"""
        return {
            "type": MessageType.ACK,
            "message_id": message_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, code: Optional[int] = None) -> Dict[str, Any]:
        """Create error message"""
        result = {
            "type": MessageType.ERROR,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if code:
            result["code"] = code
        return result
    
    @staticmethod
    def is_valid(message: Dict[str, Any]) -> bool:
        """Validate message format"""
        if "type" not in message:
            return False
        
        msg_type = message["type"]
        if msg_type not in [t.value for t in MessageType]:
            return False
        
        return True
'''
    
    file_path = WEBSOCKET_DIR / "protocol.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_recovery():
    """Buat recovery.py - reconnection logic"""
    content = '''"""
Recovery Handler - Handle reconnection and state recovery
"""

import asyncio
from typing import Dict, Set, Any, Optional
from datetime import datetime


class RecoveryHandler:
    """Handle client reconnection and state recovery"""
    
    def __init__(self, connection_manager, broadcaster):
        self.manager = connection_manager
        self.broadcaster = broadcaster
        self._client_state: Dict[str, Dict[str, Any]] = {}
        self._reconnect_attempts: Dict[str, int] = {}
        self._max_attempts = 5
    
    def save_state(self, client_id: str, state: Dict[str, Any]):
        """Save client state for potential recovery"""
        self._client_state[client_id] = {
            "state": state,
            "saved_at": datetime.now(),
            "subscriptions": self.broadcaster._client_subscriptions.get(client_id, set()).copy()
        }
    
    def get_state(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get saved client state"""
        if client_id in self._client_state:
            return self._client_state[client_id]["state"]
        return None
    
    def restore_subscriptions(self, client_id: str):
        """Restore client subscriptions"""
        if client_id in self._client_state:
            subscriptions = self._client_state[client_id].get("subscriptions", set())
            for event_type in subscriptions:
                self.broadcaster.subscribe(client_id, event_type)
    
    async def handle_reconnect(self, old_client_id: str, new_client_id: str) -> bool:
        """Handle client reconnection"""
        if old_client_id not in self._client_state:
            return False
        
        # Restore subscriptions
        self.restore_subscriptions(old_client_id)
        
        # Transfer state
        state = self.get_state(old_client_id)
        if state:
            self.save_state(new_client_id, state)
        
        # Clean up old state
        if old_client_id != new_client_id:
            del self._client_state[old_client_id]
        
        return True
    
    def record_attempt(self, client_id: str):
        """Record reconnection attempt"""
        if client_id not in self._reconnect_attempts:
            self._reconnect_attempts[client_id] = 0
        self._reconnect_attempts[client_id] += 1
    
    def should_allow_reconnect(self, client_id: str) -> bool:
        """Check if client should be allowed to reconnect"""
        attempts = self._reconnect_attempts.get(client_id, 0)
        return attempts < self._max_attempts
    
    def reset_attempts(self, client_id: str):
        """Reset reconnection attempts"""
        if client_id in self._reconnect_attempts:
            del self._reconnect_attempts[client_id]
    
    def cleanup_stale_state(self, max_age_seconds: int = 3600):
        """Clean up stale client state"""
        now = datetime.now()
        stale_ids = []
        
        for client_id, data in self._client_state.items():
            saved_at = data.get("saved_at")
            if saved_at:
                age = (now - saved_at).total_seconds()
                if age > max_age_seconds:
                    stale_ids.append(client_id)
        
        for client_id in stale_ids:
            del self._client_state[client_id]
        
        return len(stale_ids)
'''
    
    file_path = WEBSOCKET_DIR / "recovery.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_routes():
    """Buat routes.py - FastAPI routes"""
    content = '''"""
WebSocket Routes - FastAPI endpoint definitions
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.websocket.manager import ConnectionManager


router = APIRouter(tags=["websocket"])
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint"""
    await websocket.accept()
    client_id = await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send(client_id, {
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to NEMESIS WebSocket"
        })
        
        # Keep connection alive
        while True:
            # Wait for messages (handled by manager)
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception as e:
        await manager.disconnect(client_id)


@router.websocket("/ws/{room_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint with room support"""
    await websocket.accept()
    client_id = await manager.connect(websocket)
    await manager.join_room(client_id, room_id)
    
    try:
        await manager.send(client_id, {
            "type": "connected",
            "client_id": client_id,
            "room_id": room_id,
            "message": f"Connected to room: {room_id}"
        })
        
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        await manager.leave_room(client_id, room_id)
        await manager.disconnect(client_id)


@router.get("/websocket/metrics")
async def websocket_metrics():
    """Get WebSocket metrics"""
    return manager.get_metrics()


@router.get("/websocket/connections")
async def websocket_connections():
    """Get active connections"""
    return {
        "total": manager.connection_count,
        "connections": [
            conn.to_dict() for conn in manager.connections.values()
        ]
    }
'''
    
    file_path = WEBSOCKET_DIR / "routes.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FASE 1: WEBSOCKET CANONICALIZATION")
    print("="*60)
    
    success = True
    success &= create_websocket_directory()
    success &= create_manager()
    success &= create_connection()
    success &= create_broadcaster()
    success &= create_observability()
    success &= create_protocol()
    success &= create_recovery()
    success &= create_routes()
    
    print("\n" + "="*60)
    if success:
        print("✅ WEBSOCKET CANONICALIZATION COMPLETE")
        print(f"   Location: {WEBSOCKET_DIR}")
    else:
        print("❌ WEBSOCKET CANONICALIZATION FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
import asyncio
import json
import os
from typing import Dict
from fastapi import WebSocket

from backend.websocket.observability import WSObservability


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
        self.enabled = os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true"
        self.ws_observer = WSObservability()

    async def connect(self, client_id: str, websocket: WebSocket):

        if not self.enabled:
            await websocket.close(code=1008, reason="WS disabled")
            return

        await websocket.accept()

        async with self._lock:
            # 🔥 ANTI DOUBLE CONNECT
            if client_id in self.active_connections:
                old = self.active_connections[client_id]
                try:
                    await old.close(code=1001, reason="Replaced by new connection")
                except:
                    pass

            self.active_connections[client_id] = websocket

        await self.ws_observer.log_event({
            "type": "ws_connect",
            "client_id": client_id,
            "total": len(self.active_connections)
        })

        print(f"✅ CONNECT {client_id} | total={len(self.active_connections)}")

    async def disconnect(self, client_id: str):
        async with self._lock:
            self.active_connections.pop(client_id, None)

        await self.ws_observer.log_event({
            "type": "ws_disconnect",
            "client_id": client_id,
            "total": len(self.active_connections)
        })

        print(f"❌ DISCONNECT {client_id} | total={len(self.active_connections)}")

    async def send_personal(self, client_id: str, message: dict):
        ws = self.active_connections.get(client_id)
        if not ws:
            return

        try:
            await ws.send_text(json.dumps(message))
        except:
            await self.disconnect(client_id)

    async def broadcast(self, message: dict):
        dead = []

        for cid, ws in self.active_connections.items():
            try:
                await ws.send_text(json.dumps(message))
            except:
                dead.append(cid)

        for cid in dead:
            await self.disconnect(cid)


manager = ConnectionManager()
"""
WebSocket Routes for Real-time Alerts
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from infrastructure.database import get_db
from alerts.websocket_manager import ws_manager
from security.dependencies import get_current_user_optional

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    client_id: str = "anonymous",
):
    """WebSocket endpoint for real-time alerts"""
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message (for room subscription)
            data = await websocket.receive_json()
            
            if data.get("action") == "subscribe":
                case_id = data.get("case_id")
                if case_id:
                    await ws_manager.join_room(websocket, case_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "case_id": case_id,
                        "message": f"Subscribed to alerts for case {case_id}"
                    })
            
            elif data.get("action") == "unsubscribe":
                case_id = data.get("case_id")
                if case_id:
                    await ws_manager.leave_room(websocket, case_id)
            
            elif data.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, client_id)


@router.websocket("/alerts/case/{case_id}")
async def websocket_case_alerts(
    websocket: WebSocket,
    case_id: str,
):
    """WebSocket endpoint for case-specific alerts"""
    client_id = f"case_{case_id}"
    await ws_manager.connect(websocket, client_id)
    await ws_manager.join_room(websocket, case_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Just keep connection alive
            await websocket.send_text("ok")
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, client_id)
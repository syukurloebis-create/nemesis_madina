"""
WebSocket handler untuk Temporal Replay
"""

import json
import logging
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


async def handle_replay_websocket(websocket: WebSocket):
    """Handle WebSocket connection for replay feature"""
    
    await websocket.accept()
    client_id = f"replay_{id(websocket)}"
    logger.info(f"WebSocket connected: {client_id}")
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({"type": "connected", "message": "Replay WebSocket ready"})
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                elif data == "ping":
                    await websocket.send_text("pong")
                else:
                    # Parse and handle commands
                    try:
                        message = json.loads(data)
                        logger.debug(f"Received: {message.get('type')}")
                        
                        # Echo back for now (implement actual replay logic)
                        await websocket.send_json({
                            "type": "ack",
                            "payload": {"received": message.get("type")}
                        })
                    except json.JSONDecodeError:
                        await websocket.send_json({
                            "type": "error",
                            "payload": {"message": "Invalid JSON"}
                        })
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"WebSocket closed: {client_id}")


async def handle_threat_websocket(websocket: WebSocket):
    """Handle WebSocket connection for threat center"""
    
    await websocket.accept()
    client_id = f"threat_{id(websocket)}"
    logger.info(f"Threat WebSocket connected: {client_id}")
    
    try:
        await websocket.send_json({"type": "connected", "message": "Threat WebSocket ready"})
        
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"Threat WebSocket disconnected: {client_id}")
    finally:
        logger.info(f"Threat WebSocket closed: {client_id}")
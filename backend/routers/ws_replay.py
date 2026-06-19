from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/replay")
async def websocket_replay(websocket: WebSocket):
    client_id = f"replay-{id(websocket)}"

    try:
        # ✅ accept hanya sekali
        await manager.connect(client_id, websocket)

        # 🔥 REAL CONNECT CONFIRMATION (anti false connect)
        await websocket.send_json({
            "type": "SYSTEM",
            "status": "CONNECTED",
            "client_id": client_id
        })

        while True:
            data = await websocket.receive_text()

            await websocket.send_json({
                "type": "ECHO",
                "payload": data,
                "client_id": client_id
            })

    except WebSocketDisconnect:
        await manager.disconnect(client_id)

    except Exception as e:
        await manager.disconnect(client_id)
        print("WS ERROR:", e)
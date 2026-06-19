from fastapi import APIRouter, WebSocket
from backend.websocket.manager import manager

router = APIRouter()

@router.websocket("/ws/replay")
async def ws_replay(websocket: WebSocket):

    client_id = websocket.query_params.get("client_id", "anonymous")

    await manager.connect(client_id, websocket)

    try:
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id
        })

        while True:
            data = await websocket.receive_text()

            await manager.send_personal(client_id, {
                "type": "echo",
                "data": data
            })

    except Exception as e:
        print("WS ERROR:", e)

    finally:
        await manager.disconnect(client_id)
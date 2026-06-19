from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.websocket.manager import manager
from backend.websocket.ws_event_types import WSEvent

router = APIRouter()


@router.websocket("/ws/replay")
async def ws_replay(websocket: WebSocket):
    client_id = websocket.headers.get("sec-websocket-key")

    try:
        await manager.connect(client_id, websocket)

        while True:
            data = await websocket.receive_text()

            await manager.send(client_id, WSEvent(
                type="MESSAGE",
                client_id=client_id,
                payload={"data": data}
            ))

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
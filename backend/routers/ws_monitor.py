from fastapi import APIRouter, WebSocket
from websocket.observability import ws_observability

router = APIRouter()


@router.websocket("/ws/debug")
async def ws_debug(ws: WebSocket):

    await ws.accept()

    while True:
        snapshot = ws_observability.snapshot()

        await ws.send_json({
            "type": "ws_snapshot",
            "data": snapshot
        })

        await asyncio.sleep(1)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from websocket.manager import gateway
from websocket.broadcaster import WSEventBus
from websocket.observability import ws_observability

router = APIRouter()

event_bus = WSEventBus()


@router.websocket("/ws/replay")
async def ws_replay(ws: WebSocket):

    client_id = ws.query_params.get("client_id", "anon")

    # 🔵 CONNECT
    connect_info = await gateway.connect(client_id, ws)
    ws_observability.on_connect()

    await ws.send_json(connect_info)

    try:
        while True:

            raw = await ws.receive_text()

            # 🟡 normalize event
            event = event_bus.normalize(client_id, raw)

            ws_observability.log_event(event)

            # echo balik (debug)
            await gateway.send(client_id, {
                "type": "event_echo",
                "event": event
            })

    except WebSocketDisconnect:
        ws_observability.on_disconnect()
        await gateway.disconnect(client_id)

    except Exception as e:
        ws_observability.log_error(e)
        ws_observability.on_disconnect()
        await gateway.disconnect(client_id)
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()


@router.get("/api/dashboard/stream/{aggregate_id}")
async def stream(aggregate_id: str, request: Request):
    runtime = request.app.state.runtime
    engine = runtime["risk_engine"]

    async def event_stream():
        while True:
            data = await engine.compute_summary(aggregate_id)

            yield f"data: {json.dumps(data)}\n\n"

            await asyncio.sleep(2)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

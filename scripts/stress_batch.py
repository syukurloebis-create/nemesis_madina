#!/usr/bin/env python3
import asyncio
import websockets
import time
from datetime import datetime

URL = "ws://localhost:8000/ws"
TOTAL = 500
BATCH = 20

async def open_conn(i):
    try:
        ws = await websockets.connect(URL, timeout=10)
        await ws.recv()  # welcome
        return ws
    except Exception as e:
        print(f"  Conn {i} failed: {e}")
        return None

async def test_conn(ws):
    try:
        await ws.send('{"type":"ping"}')
        await asyncio.wait_for(ws.recv(), timeout=2)
        return True
    except:
        return False

async def main():
    print(f"Testing {TOTAL} connections...")
    connections = []
    success = 0
    
    for batch_start in range(0, TOTAL, BATCH):
        batch_end = min(batch_start + BATCH, TOTAL)
        tasks = [open_conn(i) for i in range(batch_start, batch_end)]
        results = await asyncio.gather(*tasks)
        for ws in results:
            if ws:
                connections.append(ws)
                success += 1
        print(f"Progress: {success}/{TOTAL}")
        await asyncio.sleep(0.5)
    
    print(f"\nSuccess rate: {success}/{TOTAL} ({success/TOTAL*100:.1f}%)")
    
    # Cleanup
    for ws in connections:
        await ws.close()

asyncio.run(main())

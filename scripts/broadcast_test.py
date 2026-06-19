#!/usr/bin/env python3
"""
Broadcast Fanout Test - 1 sender to 500 receivers
"""

import asyncio
import websockets
import json
import time

TOTAL_RECEIVERS = 500
ROOM_NAME = "test_room"

async def receiver(recv_id: int, received_flag):
    """Receiver that joins room and listens"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri, timeout=10) as ws:
            # Receive welcome
            await ws.recv()
            
            # Join room
            await ws.send(json.dumps({
                "type": "subscribe",
                "events": [ROOM_NAME]
            }))
            await ws.recv()  # Subscribe response
            
            # Wait for broadcast
            msg = await asyncio.wait_for(ws.recv(), timeout=30)
            received_flag[recv_id] = True
            return True
            
    except Exception as e:
        print(f"Receiver {recv_id} failed: {e}")
        return False

async def sender():
    """Sender that broadcasts to room"""
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri, timeout=10) as ws:
        await ws.recv()  # Welcome
        
        # Join room as sender
        await ws.send(json.dumps({
            "type": "subscribe",
            "events": [ROOM_NAME]
        }))
        await ws.recv()  # Response
        
        # Small delay before broadcast
        await asyncio.sleep(1)
        
        # Broadcast message
        await ws.send(json.dumps({
            "type": "broadcast",
            "room": ROOM_NAME,
            "payload": {"message": "test", "timestamp": time.time()}
        }))
        
        # Wait for ack
        ack = await ws.recv()
        return True

async def main():
    print("=" * 60)
    print("BROADCAST FANOUT TEST")
    print("=" * 60)
    print(f"Receivers: {TOTAL_RECEIVERS}")
    print(f"Room: {ROOM_NAME}")
    print("=" * 60)
    print()

    received = [False] * TOTAL_RECEIVERS

    print(f"Starting {TOTAL_RECEIVERS} receivers...")
    start_time = time.time()

    # START receivers in background (NOT waiting for them to finish)
    receiver_tasks = [
        asyncio.create_task(receiver(i, received))
        for i in range(TOTAL_RECEIVERS)
    ]

    # Wait for receivers to connect and subscribe
    print("Waiting for receivers to be ready...")
    await asyncio.sleep(5)  # Give time for all receivers to connect

    connect_time = time.time() - start_time
    print(f"Receivers ready in {connect_time:.2f}s")

    # Check active connections
    import requests
    try:
        resp = requests.get("http://localhost:8000/websocket/connections", timeout=5)
        if resp.status_code == 200:
            conn_data = resp.json()
            print(f"Active connections from API: {conn_data.get('total', 0)}")
    except:
        pass

    # Send broadcast
    print("\nSending broadcast...")
    await sender()
    print("Broadcast sent")

    # Wait for receivers to receive broadcast
    print("Waiting for receivers to receive broadcast...")
    await asyncio.sleep(5)

    # Now wait for all receiver tasks to complete
    receivers_connected = await asyncio.gather(*receiver_tasks)

    end_time = time.time()
    total_time = end_time - start_time

    receivers_ok = sum(receivers_connected)
    received_count = sum(received)

    print()
    print("=" * 60)
    print("BROADCAST RESULTS")
    print("=" * 60)
    print(f"Total receivers: {TOTAL_RECEIVERS}")
    print(f"Receivers connected successfully: {receivers_ok}")
    print(f"Messages received: {received_count}")
    
    if receivers_ok > 0:
        print(f"Delivery rate: {received_count/receivers_ok*100:.1f}%")
    
    print(f"Total test time: {total_time:.2f}s")

    if received_count == receivers_ok and receivers_ok > 0:
        print("\n[OK] BROADCAST TEST PASSED - All receivers got the message!")
    else:
        missed = receivers_ok - received_count
        print(f"\n[WARN] BROADCAST TEST - {missed} receivers missed the message")

if __name__ == "__main__":
    asyncio.run(main())

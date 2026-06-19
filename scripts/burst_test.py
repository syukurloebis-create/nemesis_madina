#!/usr/bin/env python3
"""
Burst Traffic Test - Test high message throughput
"""

import asyncio
import websockets
import json
import time

URL = "ws://localhost:8000/ws"
MESSAGE_COUNT = 1000

async def test_burst():
    print("=" * 60)
    print("BURST TRAFFIC TEST")
    print("=" * 60)
    print(f"Messages: {MESSAGE_COUNT}")
    print(f"URL: {URL}")
    print("=" * 60)
    print()
    
    async with websockets.connect(URL, timeout=10) as ws:
        # Receive welcome
        welcome = await ws.recv()
        print("Connected!")
        
        # Send burst of messages
        print(f"Sending {MESSAGE_COUNT} messages...")
        start_time = time.time()
        
        for i in range(MESSAGE_COUNT):
            await ws.send(json.dumps({
                "type": "ping",
                "sequence": i,
                "timestamp": time.time()
            }))
        
        send_time = time.time() - start_time
        print(f"Send completed in {send_time:.2f}s")
        
        # Receive responses
        print("Receiving responses...")
        received = 0
        receive_start = time.time()
        
        for i in range(MESSAGE_COUNT):
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=0.5)
                received += 1
                if (i + 1) % 100 == 0:
                    print(f"  Received {i+1}/{MESSAGE_COUNT}")
            except asyncio.TimeoutError:
                print(f"  Timeout at message {i}")
                break
        
        receive_time = time.time() - receive_start
        total_time = time.time() - start_time
        
        print()
        print("=" * 60)
        print("BURST TEST RESULTS")
        print("=" * 60)
        print(f"Messages sent: {MESSAGE_COUNT}")
        print(f"Messages received: {received}")
        print(f"Delivery rate: {received/MESSAGE_COUNT*100:.1f}%")
        print(f"Send time: {send_time:.2f}s")
        print(f"Receive time: {receive_time:.2f}s")
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {MESSAGE_COUNT/total_time:.0f} msg/s")
        
        if received == MESSAGE_COUNT:
            print("\n[OK] BURST TEST PASSED - All messages delivered")
        else:
            print(f"\n[WARN] BURST TEST - Lost {MESSAGE_COUNT - received} messages")

if __name__ == "__main__":
    asyncio.run(test_burst())

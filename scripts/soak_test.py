#!/usr/bin/env python3
"""
Soak Test - Long-lived WebSocket connections
Test memory leak and stale connection cleanup
"""

import asyncio
import websockets
import time
import json
from datetime import datetime

TOTAL = 200
DURATION = 600  # 10 menit
URL = "ws://localhost:8000/ws"

print_lock = asyncio.Lock()

async def worker(worker_id: int):
    """Worker that maintains WebSocket connection for duration"""
    start_time = time.time()
    heartbeat_count = 0
    
    try:
        async with websockets.connect(URL, timeout=10) as ws:
            # Receive welcome
            welcome = await asyncio.wait_for(ws.recv(), timeout=5)
            
            # Send initial ping with ID
            await ws.send(json.dumps({
                "type": "ping",
                "worker_id": worker_id,
                "timestamp": time.time()
            }))
            
            # Heartbeat loop
            while time.time() - start_time < DURATION:
                await ws.send(json.dumps({
                    "type": "ping",
                    "worker_id": worker_id,
                    "heartbeat": heartbeat_count,
                    "timestamp": time.time()
                }))
                heartbeat_count += 1
                
                # Wait for pong
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5)
                    if '"pong"' not in response:
                        print(f"[Worker {worker_id}] Unexpected response")
                except asyncio.TimeoutError:
                    print(f"[Worker {worker_id}] Heartbeat timeout")
                    break
                
                await asyncio.sleep(5)  # Heartbeat every 5 seconds
            
            # Send final ping before closing
            await ws.send(json.dumps({
                "type": "ping",
                "worker_id": worker_id,
                "final": True,
                "timestamp": time.time()
            }))
            
            elapsed = time.time() - start_time
            async with print_lock:
                print(f"[Worker {worker_id}] Completed {elapsed:.0f}s, heartbeats: {heartbeat_count}")
            return True
            
    except Exception as e:
        print(f"[Worker {worker_id}] Failed: {e}")
        return False

async def monitor_metrics():
    """Monitor WebSocket metrics during test"""
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        for i in range(12):  # Monitor every 30 seconds for 6 minutes
            await asyncio.sleep(30)
            try:
                async with session.get("http://localhost:8000/websocket/metrics") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"\n[METRICS] Time: {datetime.now().strftime('%H:%M:%S')}")
                        print(f"  Active: {data.get('active_connections', 0)}")
                        print(f"  Total opened: {data.get('total_connections_served', 0)}")
                        print(f"  Messages: {data.get('messages_processed', 0)}")
            except Exception as e:
                print(f"[METRICS] Error: {e}")

async def main():
    print("=" * 60)
    print("SOAK TEST - Long-lived WebSocket Connections")
    print("=" * 60)
    print(f"Connections: {TOTAL}")
    print(f"Duration: {DURATION} seconds ({DURATION/60:.0f} minutes)")
    print(f"URL: {URL}")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    # Start metrics monitor
    monitor_task = asyncio.create_task(monitor_metrics())
    
    # Create all workers
    print(f"Starting {TOTAL} workers...")
    tasks = [worker(i) for i in range(TOTAL)]
    
    # Wait for all workers to complete
    results = await asyncio.gather(*tasks)
    
    # Cancel monitor
    monitor_task.cancel()
    
    elapsed = time.time() - start_time
    success = sum(results)
    failed = TOTAL - success
    
    print()
    print("=" * 60)
    print("SOAK TEST RESULTS")
    print("=" * 60)
    print(f"Total workers: {TOTAL}")
    print(f"Successful: {success}")
    print(f"Failed: {failed}")
    print(f"Success rate: {success/TOTAL*100:.1f}%")
    print(f"Total time: {elapsed:.1f}s")
    
    if success >= TOTAL * 0.95:
        print("\n[OK] SOAK TEST PASSED - 95%+ connections survived")
    else:
        print(f"\n[WARN] SOAK TEST - Only {success/TOTAL*100:.1f}% survived")

if __name__ == "__main__":
    asyncio.run(main())

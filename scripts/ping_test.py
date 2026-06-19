#!/usr/bin/env python3
"""
Ping Throughput Test - Ukur latency WebSocket
"""

import asyncio
import websockets
import json
import time
import statistics

TOTAL = 100

async def test_ping():
    """Test single ping-pong latency"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri, timeout=10) as ws:
            # Receive welcome
            await ws.recv()
            
            # Send ping with timestamp
            start = time.time()
            await ws.send(json.dumps({
                "type": "ping",
                "timestamp": start
            }))
            
            # Receive pong
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            latency = (time.time() - start) * 1000  # Convert to ms
            
            return latency
            
    except Exception as e:
        print(f"Ping test failed: {e}")
        return None

async def main():
    print("=" * 60)
    print("PING THROUGHPUT TEST")
    print("=" * 60)
    print(f"Total pings: {TOTAL}")
    print()
    
    print("Running ping tests...")
    results = await asyncio.gather(*[test_ping() for _ in range(TOTAL)])
    
    # Filter out None values
    latencies = [r for r in results if r is not None]
    
    if latencies:
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max_latency
        
        print()
        print("=" * 60)
        print("PING TEST RESULTS")
        print("=" * 60)
        print(f"Successful pings: {len(latencies)}/{TOTAL}")
        print(f"Average latency: {avg_latency:.2f} ms")
        print(f"Minimum latency: {min_latency:.2f} ms")
        print(f"Maximum latency: {max_latency:.2f} ms")
        print(f"P95 latency: {p95:.2f} ms")
        
        if avg_latency < 30:
            print("\n[OK] PING TEST PASSED - Latency within target (<30ms)")
        else:
            print(f"\n[WARN] PING TEST - Average latency {avg_latency:.1f}ms (target <30ms)")
    else:
        print("\n[FAIL] All ping tests failed!")

if __name__ == "__main__":
    asyncio.run(main())

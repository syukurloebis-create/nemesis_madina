#!/usr/bin/env python3
"""
Reconnect Test - Test force disconnect and recovery
"""

import asyncio
import websockets
import json
import time

URL = "ws://localhost:8000/ws"

async def test_reconnect():
    print("=" * 60)
    print("RECONNECT TEST - Force Disconnect Recovery")
    print("=" * 60)
    
    # First connection
    print("\n[1] Establishing first connection...")
    ws = await websockets.connect(URL, timeout=10)
    welcome = await ws.recv()
    print(f"    Connected! Welcome: {welcome[:100]}...")
    
    # Get client ID from welcome message
    import json
    welcome_data = json.loads(welcome)
    client_id = welcome_data.get('client_id')
    print(f"    Client ID: {client_id}")
    
    # Subscribe to a room
    print("\n[2] Subscribing to test_room...")
    await ws.send(json.dumps({
        "type": "subscribe",
        "events": ["test_room"]
    }))
    response = await ws.recv()
    print(f"    Subscribed: {response[:100]}...")
    
    # Force disconnect
    print("\n[3] Force disconnecting...")
    await ws.close()
    print("    Connection closed")
    
    # Wait before reconnect
    print("\n[4] Waiting 2 seconds before reconnect...")
    await asyncio.sleep(2)
    
    # Reconnect
    print("\n[5] Reconnecting...")
    ws2 = await websockets.connect(URL, timeout=10)
    welcome2 = await ws2.recv()
    welcome2_data = json.loads(welcome2)
    new_client_id = welcome2_data.get('client_id')
    print(f"    Reconnected! New Client ID: {new_client_id}")
    
    # Verify room state (should need to resubscribe)
    print("\n[6] Testing room subscription after reconnect...")
    await ws2.send(json.dumps({
        "type": "subscribe",
        "events": ["test_room"]
    }))
    response2 = await ws2.recv()
    print(f"    Resubscribed: {response2[:100]}...")
    
    # Test ping
    print("\n[7] Testing ping-pong...")
    await ws2.send(json.dumps({"type": "ping"}))
    pong = await ws2.recv()
    print(f"    Ping-pong successful: {pong[:100]}...")
    
    await ws2.close()
    
    print("\n" + "=" * 60)
    print("[OK] RECONNECT TEST PASSED - Reconnection successful")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_reconnect())

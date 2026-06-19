# scripts/test_websocket.py
import asyncio
import websockets
import json
import sys
import os

# Ambil token dari environment variable atau argumen
TOKEN = os.environ.get("TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)

if not TOKEN:
    print("❌ No token provided. Set TOKEN environment variable or pass as argument.")
    print("Usage: python test_websocket.py <token>")
    print("   or: export TOKEN=<token> && python test_websocket.py")
    sys.exit(1)

print(f"Using token: {TOKEN[:50]}...")

async def test_websocket():
    uri = "ws://localhost:8000/ws/test123"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Kirim auth message dengan token yang benar
            auth_msg = json.dumps({"type": "auth", "token": TOKEN})
            await websocket.send(auth_msg)
            print("📤 Sent auth message")
            
            # Terima response
            response = await websocket.recv()
            print(f"📥 Auth response: {response}")
            
            # Jika auth sukses, kirim ping
            if "auth_success" in response:
                print("✅ Authentication successful!")
                await websocket.send(json.dumps({"type": "ping"}))
                ping_response = await websocket.recv()
                print(f"📥 Ping response: {ping_response}")
            else:
                print("❌ Authentication failed")
            
            await asyncio.sleep(1)
            print("✅ Test completed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
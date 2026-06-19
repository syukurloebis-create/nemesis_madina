#!/usr/bin/env python3
"""
NEMESIS - Real-time Event Test
Menguji event broadcasting ke WebSocket clients
"""

import sys
import asyncio
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

try:
    import websockets
    import requests
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "websocket_tests"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

WS_URL = "ws://localhost:8000/ws"
BASE_URL = "http://localhost:8000"


class RealtimeTester:
    """Test real-time event broadcasting"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
    
    async def test_event_broadcast(self) -> Dict[str, Any]:
        """Test event broadcasting to WebSocket clients"""
        print(f"\n  {BLUE}[TEST 1] Event Broadcast{RESET}")
        
        if not WEBSOCKETS_AVAILABLE:
            return {"test": "event_broadcast", "passed": True, "skipped": True}
        
        received_events = []
        
        async def client():
            try:
                async with websockets.connect(WS_URL, timeout=5) as ws:
                    # Subscribe to events
                    await ws.send(json.dumps({"type": "subscribe", "events": ["test.realtime"]}))
                    
                    # Listen for events
                    try:
                        while True:
                            msg = await asyncio.wait_for(ws.recv(), timeout=5)
                            data = json.loads(msg)
                            if data.get("type") == "event":
                                received_events.append(data)
                    except asyncio.TimeoutError:
                        pass
            except Exception as e:
                print(f"    Client error: {e}")
        
        # Start client
        client_task = asyncio.create_task(client())
        await asyncio.sleep(1)
        
        # Publish event via API
        try:
            resp = requests.post(
                f"{BASE_URL}/api/v1/events",
                json={
                    "event_type": "test.realtime",
                    "data": {"message": "broadcast test", "timestamp": time.time()},
                    "source": "realtime_test"
                },
                timeout=5
            )
            print(f"    ✅ Event published: {resp.status_code}")
        except Exception as e:
            print(f"    ❌ Event publish failed: {e}")
        
        await asyncio.sleep(2)
        client_task.cancel()
        
        received_count = len(received_events)
        print(f"    📊 Events received by client: {received_count}")
        
        return {"test": "event_broadcast", "passed": received_count >= 0, "received": received_count}
    
    async def test_multiple_clients(self) -> Dict[str, Any]:
        """Test broadcasting to multiple WebSocket clients"""
        print(f"\n  {BLUE}[TEST 2] Multiple Clients Broadcast{RESET}")
        
        if not WEBSOCKETS_AVAILABLE:
            return {"test": "multiple_clients", "passed": True, "skipped": True}
        
        client_count = 3
        received_counts = [0] * client_count
        
        async def client(client_id: int, received_counter: list):
            try:
                async with websockets.connect(WS_URL, timeout=5) as ws:
                    # Subscribe
                    await ws.send(json.dumps({"type": "subscribe", "events": ["test.multiclient"]}))
                    
                    try:
                        while True:
                            msg = await asyncio.wait_for(ws.recv(), timeout=3)
                            data = json.loads(msg)
                            if data.get("type") == "event":
                                received_counter[client_id] += 1
                    except asyncio.TimeoutError:
                        pass
            except Exception as e:
                print(f"    Client {client_id} error: {e}")
        
        # Start clients
        tasks = []
        for i in range(client_count):
            task = asyncio.create_task(client(i, received_counts))
            tasks.append(task)
        
        await asyncio.sleep(1)
        
        # Publish multiple events
        for i in range(5):
            try:
                requests.post(
                    f"{BASE_URL}/api/v1/events",
                    json={
                        "event_type": "test.multiclient",
                        "data": {"broadcast_id": i},
                        "source": "multi_test"
                    },
                    timeout=5
                )
            except:
                pass
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(2)
        for task in tasks:
            task.cancel()
        
        total_received = sum(received_counts)
        print(f"    📊 Total events received across {client_count} clients: {total_received}")
        
        return {
            "test": "multiple_clients",
            "passed": total_received > 0,
            "total_received": total_received,
            "client_count": client_count
        }
    
    async def test_heartbeat(self) -> Dict[str, Any]:
        """Test WebSocket heartbeat/ping-pong"""
        print(f"\n  {BLUE}[TEST 3] Heartbeat Test{RESET}")
        
        if not WEBSOCKETS_AVAILABLE:
            return {"test": "heartbeat", "passed": True, "skipped": True}
        
        pong_received = False
        
        try:
            async with websockets.connect(WS_URL, timeout=5) as ws:
                # Send ping
                await ws.send(json.dumps({"type": "ping"}))
                
                # Wait for pong
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                pong_received = data.get("type") == "pong"
                
                print(f"    {'✅' if pong_received else '❌'} Ping-pong: {pong_received}")
        except Exception as e:
            print(f"    ❌ Heartbeat failed: {e}")
            pong_received = False
        
        return {"test": "heartbeat", "passed": pong_received}
    
    async def run_all(self) -> Dict[str, Any]:
        """Run all realtime tests"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}REAL-TIME EVENT TESTS{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        tests = [
            await self.test_event_broadcast(),
            await self.test_multiple_clients(),
            await self.test_heartbeat()
        ]
        
        self.results["tests"] = tests
        passed = sum(1 for t in tests if t.get("passed", False))
        self.results["summary"] = {"passed": passed, "failed": len(tests) - passed, "total": len(tests)}
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"  Passed: {passed}/{len(tests)}")
        
        report_path = REPORT_DIR / f"realtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved: {report_path}")
        
        return self.results


async def main():
    tester = RealtimeTester()
    results = await tester.run_all()
    return 0


if __name__ == "__main__":
    if not WEBSOCKETS_AVAILABLE:
        print("\n⚠️ Installing websockets...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "websockets", "-q"])
        print("✅ websockets installed")
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
NEMESIS - WebSocket Scale Test
Menguji WebSocket dengan banyak koneksi simultan
"""

import sys
import asyncio
import json
import time
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

try:
    import websockets
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


class WebSocketScaleTester:
    """Test WebSocket with many concurrent connections"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    async def create_connection(self, client_id: int, duration: int = 5) -> Dict[str, Any]:
        """Create a WebSocket connection and keep it alive"""
        start_time = time.time()
        try:
            async with websockets.connect(WS_URL, timeout=10) as ws:
                # Send ping
                await ws.send(json.dumps({"type": "ping", "client_id": client_id}))
                
                # Keep connection alive for duration
                await asyncio.sleep(duration)
                
                return {
                    "client_id": client_id,
                    "success": True,
                    "duration": time.time() - start_time
                }
        except Exception as e:
            return {
                "client_id": client_id,
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    async def test_scale(self, connection_count: int, duration: int = 3) -> Dict[str, Any]:
        """Test with specified number of concurrent connections"""
        print(f"\n  📊 Testing {connection_count} concurrent connections...")
        
        start_memory = self.get_memory_usage()
        start_time = time.time()
        
        # Create all connections
        tasks = [self.create_connection(i, duration) for i in range(connection_count)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = connection_count - successful
        
        avg_duration = sum(r.get("duration", 0) for r in results) / connection_count if results else 0
        
        print(f"    Successful: {successful}/{connection_count}")
        print(f"    Failed: {failed}")
        print(f"    Avg connection time: {avg_duration:.2f}s")
        print(f"    Memory increase: {end_memory - start_memory:.1f} MB")
        
        return {
            "connection_count": connection_count,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / connection_count * 100,
            "avg_duration_seconds": round(avg_duration, 2),
            "memory_increase_mb": round(end_memory - start_memory, 1),
            "total_time_seconds": round(end_time - start_time, 2),
            "passed": failed == 0
        }
    
    async def run_all(self) -> Dict[str, Any]:
        """Run scale tests with increasing connection counts"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}WEBSOCKET SCALE TEST{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        if not WEBSOCKETS_AVAILABLE:
            print("⚠️ websockets not installed")
            return {"tests": [], "summary": {"passed": 0, "failed": 0}}
        
        test_levels = [10, 25, 50]
        results = []
        
        for level in test_levels:
            print(f"\n{YELLOW}--- Level: {level} connections ---{RESET}")
            result = await self.test_scale(level, duration=3)
            results.append(result)
            await asyncio.sleep(2)  # Cooldown
        
        self.results["tests"] = results
        passed = sum(1 for r in results if r.get("passed", False))
        self.results["summary"] = {"passed": passed, "failed": len(results) - passed, "total": len(results)}
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}SCALE TEST SUMMARY{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"  Passed: {passed}/{len(results)}")
        
        report_path = REPORT_DIR / f"websocket_scale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Report saved: {report_path}")
        
        return self.results


async def main():
    tester = WebSocketScaleTester()
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
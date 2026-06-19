#!/usr/bin/env python3
"""
NEMESIS - Event Burst Test
Menguji kemampuan event bus menangani 1000 event dalam burst
"""

import sys
import asyncio
import time
import json
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "scale_tests"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Colors for output (Windows compatible)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class EventBurstTester:
    """Test event bus with burst of events"""
    
    def __init__(self):
        self.received_events: List[Dict] = []
        self.start_time = None
        self.end_time = None
        self.memory_samples = []
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def record_memory(self):
        """Record current memory usage"""
        self.memory_samples.append({
            "timestamp": time.time(),
            "memory_mb": self.get_memory_usage()
        })
    
    async def run_burst_test(self, event_count: int = 1000) -> Dict[str, Any]:
        """Run burst test with specified number of events"""
        from backend.core.events import EventBus, Event
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}EVENT BURST TEST - {event_count} events{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        bus = EventBus()
        
        # Reset
        self.received_events = []
        self.memory_samples = []
        
        # Record baseline memory
        self.record_memory()
        baseline_memory = self.memory_samples[-1]["memory_mb"]
        print(f"📊 Baseline memory: {baseline_memory:.2f} MB")
        
        # Handler
        async def handler(event):
            self.received_events.append({
                "id": event.id,
                "type": event.type,
                "received_at": time.time()
            })
        
        bus.subscribe("burst.test", handler)
        print(f"✅ Subscribed to burst.test events")
        
        # Create events
        print(f"\n📨 Creating {event_count} events...")
        events = []
        for i in range(event_count):
            event = Event(
                id=f"burst_{i}",
                type="burst.test",
                data={"index": i, "timestamp": datetime.now().isoformat()},
                source="burst_test",
                timestamp=datetime.now()
            )
            events.append(event)
        
        print(f"✅ {len(events)} events created")
        
        # Publish events
        print(f"\n🚀 Publishing events...")
        self.start_time = time.time()
        self.record_memory()
        
        for i, event in enumerate(events):
            await bus.publish(event)
            if (i + 1) % 250 == 0:
                print(f"  Published {i+1}/{event_count} events")
        
        self.end_time = time.time()
        self.record_memory()
        
        # Wait for processing
        print(f"\n⏳ Waiting for processing...")
        await asyncio.sleep(1)
        
        # Results
        duration = self.end_time - self.start_time
        received_count = len(self.received_events)
        success_rate = (received_count / event_count) * 100
        
        # Memory impact
        peak_memory = max(s["memory_mb"] for s in self.memory_samples)
        memory_increase = peak_memory - baseline_memory
        
        # Throughput
        throughput = event_count / duration
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}RESULTS{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"  Events sent:     {event_count}")
        print(f"  Events received: {received_count}")
        print(f"  Success rate:    {success_rate:.1f}%")
        print(f"  Duration:        {duration:.2f}s")
        print(f"  Throughput:      {throughput:.0f} events/sec")
        print(f"  Memory increase: {memory_increase:.1f} MB")
        print(f"  Peak memory:     {peak_memory:.1f} MB")
        
        # Determine status
        status = "PASSED" if received_count == event_count else "FAILED"
        status_color = GREEN if received_count == event_count else RED
        
        print(f"\n  Status: {status_color}{status}{RESET}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "event_count": event_count,
            "received_count": received_count,
            "success_rate": success_rate,
            "duration_seconds": round(duration, 3),
            "throughput": round(throughput, 1),
            "baseline_memory_mb": round(baseline_memory, 1),
            "peak_memory_mb": round(peak_memory, 1),
            "memory_increase_mb": round(memory_increase, 1),
            "status": status,
            "memory_samples": self.memory_samples
        }
    
    async def run_multi_burst(self):
        """Run multiple burst tests with increasing load"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}MULTI-LEVEL BURST TEST{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        test_levels = [100, 500, 1000, 2000]
        results = []
        
        for count in test_levels:
            print(f"\n{YELLOW}--- Testing {count} events ---{RESET}")
            result = await self.run_burst_test(count)
            results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(2)
        
        # Summary
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}SUMMARY - MULTI-LEVEL BURST TEST{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        print(f"{'Events':<10} {'Received':<10} {'Rate (%)':<10} {'Duration (s)':<12} {'Throughput':<12}")
        print(f"{'-'*60}")
        
        for r in results:
            status_mark = "✅" if r["status"] == "PASSED" else "❌"
            print(f"{r['event_count']:<10} {r['received_count']:<10} {r['success_rate']:<10.1f} {r['duration_seconds']:<12.2f} {r['throughput']:<12.0f} {status_mark}")
        
        return results


async def main():
    tester = EventBurstTester()
    
    # Single burst test
    result = await tester.run_burst_test(1000)
    
    # Save results
    report_path = REPORT_DIR / f"event_burst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n📄 Report saved: {report_path}")
    
    # Multi-level test (optional - can be slower)
    # await tester.run_multi_burst()
    
    return 0 if result["status"] == "PASSED" else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
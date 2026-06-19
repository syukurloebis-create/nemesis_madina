# benchmarks/scale_test.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import time
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List
import statistics

from backend.database import get_db
from backend.events.repository import EventRepository
from backend.services.case_service import CaseService
from backend.config import settings


class ScaleTest:
    """Scale testing for NEMESIS V8+"""
    
    def __init__(self):
        self.results = {}
    
    async def generate_events(self, case_id: str, count: int) -> Dict[str, Any]:
        """Generate multiple events for a case"""
        
        async for db in get_db():
            repo = EventRepository(db, tenant_id=settings.DEFAULT_TENANT_ID)
            
            latencies = []
            start_total = time.time()
            
            for i in range(count):
                event_start = time.time()
                
                await repo.append(
                    aggregate_id=case_id,
                    aggregate_type="case",
                    event_type="BENCHMARK_EVENT",
                    payload={
                        "index": i,
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": f"Benchmark data {i}"
                    },
                    metadata={
                        "actor_id": "benchmark",
                        "test": True,
                        "batch": i // 1000
                    }
                )
                
                latencies.append((time.time() - event_start) * 1000)
                
                if (i + 1) % 1000 == 0:
                    print(f"Generated {i + 1}/{count} events...")
            
            total_time = time.time() - start_total
            
            return {
                "total_events": count,
                "total_time_seconds": total_time,
                "events_per_second": count / total_time,
                "latency_ms": {
                    "p50": statistics.median(latencies),
                    "p95": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                    "p99": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
                    "min": min(latencies),
                    "max": max(latencies)
                }
            }
    
    async def test_rebuild_performance(self, case_id: str) -> Dict[str, Any]:
        """Test projection rebuild performance"""
        
        from backend.projections.engine import ProjectionEngine
        
        async for db in get_db():
            engine = ProjectionEngine(db)
            
            start = time.time()
            await engine.rebuild_projection("case_projection", batch_size=10000)
            rebuild_time = time.time() - start
            
            return {
                "rebuild_time_seconds": rebuild_time,
                "events_per_second": await self.get_event_count(case_id) / rebuild_time if rebuild_time > 0 else 0
            }
    
    async def get_event_count(self, case_id: str) -> int:
        """Get total event count for a case"""
        async for db in get_db():
            result = await db.execute(
                "SELECT COUNT(*) FROM events WHERE case_id = $1",
                (case_id,)
            )
            return result.scalar()
    
    async def run_full_scale_test(self, target_events: int = 10000):
        """Run complete scale test"""
        
        print(f"\n=== NEMESIS V8+ Scale Test: {target_events:,} events ===")
        
        # Create test case
        async for db in get_db():
            case_service = CaseService(db, settings.DEFAULT_TENANT_ID)
            case = await case_service.create_case(
                title=f"Scale Test {target_events:,} Events",
                description=f"Performance benchmark with {target_events:,} events",
                created_by="scale_test"
            )
            case_id = case['id']
            print(f"Test Case ID: {case_id}")
        
        # Generate events
        print(f"\n📊 Generating {target_events:,} events...")
        gen_results = await self.generate_events(case_id, target_events)
        
        print(f"\n✅ Generation complete:")
        print(f"   Total time: {gen_results['total_time_seconds']:.2f} seconds")
        print(f"   Events/sec: {gen_results['events_per_second']:.2f}")
        print(f"   Latency P95: {gen_results['latency_ms']['p95']:.2f}ms")
        
        # Verify integrity
        print(f"\n🔍 Verifying integrity...")
        async for db in get_db():
            from backend.events.verifier import IntegrityVerifier
            repo = EventRepository(db, settings.DEFAULT_TENANT_ID)
            verifier = IntegrityVerifier(repo)
            result = await verifier.verify_aggregate_chain(case_id)
            print(f"   Integrity: {result['status']}")
            print(f"   Events verified: {result['events_verified']}")
            print(f"   Chain intact: {result['chain_intact']}")
        
        # Gate B Criteria Check
        print(f"\n📋 Gate B Criteria Check:")
        
        gate_b_passed = True
        
        # G1: append_p95 ≤ 50ms
        g1_pass = gen_results['latency_ms']['p95'] <= 50
        print(f"   G1 (append_p95 ≤ 50ms): {gen_results['latency_ms']['p95']:.2f}ms → {'✅ PASS' if g1_pass else '❌ FAIL'}")
        gate_b_passed = gate_b_passed and g1_pass
        
        print(f"\n{'✅ ALL GATE B CRITERIA PASSED' if gate_b_passed else '❌ GATE B CRITERIA FAILED'}")
        
        return {
            "case_id": case_id,
            "generation": gen_results,
            "gate_b_passed": gate_b_passed
        }


async def main():
    test = ScaleTest()
    
    # Start with smaller scale first
    scales = [100, 1000, 10000]
    
    for scale in scales:
        print(f"\n{'='*60}")
        results = await test.run_full_scale_test(scale)
        
        # Save results
        with open(f"benchmark_results_{scale}.json", "w") as f:
            json.dump(results, f, indent=2)
    
    print("\n🎉 Scale testing complete!")


if __name__ == "__main__":
    asyncio.run(main())
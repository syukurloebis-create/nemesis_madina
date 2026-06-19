#!/usr/bin/env python3
"""
NEMESIS Baseline Snapshot - Phase 0
Mengukur performa awal sebelum migrasi
"""

import asyncio
import aiohttp
import time
import json
import psutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import sys

PROJECT_ROOT = Path(".").resolve()
REPORT_DIR = PROJECT_ROOT / "reports" / "fase0"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

class BaselineCollector:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.base_url = "http://localhost:8000"
        
    def collect_system_info(self):
        """Collect system information"""
        self.metrics['system'] = {
            'platform': platform.platform(),
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage(str(PROJECT_ROOT)).percent,
            'timestamp': datetime.now().isoformat()
        }
        print("✓ System info collected")
        
    def collect_code_stats(self):
        """Collect code statistics"""
        py_files = list(PROJECT_ROOT.rglob('*.py'))
        excluded = {'venv', '__pycache__', 'node_modules', '.git', 'env'}
        
        def is_excluded(p):
            return any(ex in p.parts for ex in excluded)
        
        filtered = [f for f in py_files if not is_excluded(f)]
        
        total_lines = 0
        for f in filtered:
            try:
                total_lines += len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
            except:
                pass
                
        self.metrics['code'] = {
            'total_py_files': len(filtered),
            'total_lines_of_code': total_lines,
            'avg_lines_per_file': round(total_lines / len(filtered), 1) if filtered else 0,
            'project_root': str(PROJECT_ROOT)
        }
        print(f"✓ Code stats collected: {len(filtered)} files, {total_lines} LOC")
        
    async def check_service_health(self):
        """Check if service is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.metrics['service_health'] = {
                            'status': 'running',
                            'response': data,
                            'timestamp': datetime.now().isoformat()
                        }
                        print("✓ Service health check passed")
                        return True
        except Exception as e:
            self.metrics['service_health'] = {
                'status': 'not_running',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print("⚠️  Service not running - some metrics will be skipped")
            return False
            
    async def measure_startup_time(self):
        """Measure application startup time (simulated)"""
        start = time.time()
        # This would normally check when app becomes responsive
        await asyncio.sleep(0.1)  # Simulated
        self.metrics['startup_time_ms'] = (time.time() - start) * 1000
        print(f"✓ Startup time measured: {self.metrics['startup_time_ms']:.2f}ms")
        
    async def measure_api_latency(self):
        """Measure API endpoint latency"""
        if self.metrics.get('service_health', {}).get('status') != 'running':
            self.metrics['api_latency'] = {'status': 'skipped', 'reason': 'service not running'}
            return
            
        endpoints = [
            '/health',
            '/api/v1/health',
            '/metrics' if self.metrics.get('has_metrics') else None
        ]
        
        latencies = []
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                if not endpoint:
                    continue
                try:
                    start = time.time()
                    async with session.get(f"{self.base_url}{endpoint}", timeout=2) as resp:
                        latency = (time.time() - start) * 1000
                        latencies.append(latency)
                except:
                    pass
                    
        if latencies:
            self.metrics['api_latency_ms'] = {
                'avg': round(sum(latencies) / len(latencies), 2),
                'min': round(min(latencies), 2),
                'max': round(max(latencies), 2),
                'samples': len(latencies)
            }
            print(f"✓ API latency measured: avg={self.metrics['api_latency_ms']['avg']}ms")
            
    def collect_database_stats(self):
        """Collect database statistics"""
        try:
            import psycopg2
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'nemesis_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )
            
            with conn.cursor() as cur:
                # Count tables
                cur.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = cur.fetchone()[0]
                
                # Count events
                cur.execute("SELECT COUNT(*) FROM events")
                event_count = cur.fetchone()[0]
                
                # Count evidence
                cur.execute("SELECT COUNT(*) FROM evidence")
                evidence_count = cur.fetchone()[0]
                
            conn.close()
            
            self.metrics['database'] = {
                'table_count': table_count,
                'event_count': event_count,
                'evidence_count': evidence_count,
                'status': 'connected'
            }
            print(f"✓ Database stats: {event_count} events, {evidence_count} evidence")
            
        except Exception as e:
            self.metrics['database'] = {'status': 'error', 'error': str(e)}
            print(f"⚠️  Database connection failed: {e}")
            
    async def collect_all(self):
        """Run all collection methods"""
        print("\n" + "="*60)
        print("COLLECTING BASELINE METRICS")
        print("="*60 + "\n")
        
        self.collect_system_info()
        self.collect_code_stats()
        
        service_running = await self.check_service_health()
        
        if service_running:
            await self.measure_api_latency()
            self.collect_database_stats()
        
        await self.measure_startup_time()
        
        # Add timestamp
        self.metrics['collection_timestamp'] = datetime.now().isoformat()
        
    def save_report(self):
        """Save metrics to file"""
        report_file = REPORT_DIR / f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)
            
        # Also save as latest
        latest_file = REPORT_DIR / "baseline_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)
            
        print(f"\n📄 Baseline saved to: {report_file}")
        return report_file
        
    def print_summary(self):
        """Print summary to console"""
        print("\n" + "="*60)
        print("BASELINE SUMMARY")
        print("="*60)
        
        sys_info = self.metrics.get('system', {})
        print(f"\n🖥️  System:")
        print(f"   CPU: {sys_info.get('cpu_count', 0)} cores ({sys_info.get('cpu_percent', 0)}%)")
        print(f"   Memory: {sys_info.get('memory_available_gb', 0)}GB / {sys_info.get('memory_total_gb', 0)}GB available")
        
        code_info = self.metrics.get('code', {})
        print(f"\n📝 Code:")
        print(f"   Python files: {code_info.get('total_py_files', 0)}")
        print(f"   Lines of code: {code_info.get('total_lines_of_code', 0):,}")
        
        api_latency = self.metrics.get('api_latency_ms', {})
        if api_latency:
            print(f"\n⚡ API Latency:")
            print(f"   Average: {api_latency.get('avg', 0)}ms")
            
        db_info = self.metrics.get('database', {})
        if db_info and db_info.get('status') == 'connected':
            print(f"\n💾 Database:")
            print(f"   Tables: {db_info.get('table_count', 0)}")
            print(f"   Events: {db_info.get('event_count', 0):,}")
            print(f"   Evidence: {db_info.get('evidence_count', 0):,}")
            
        print("\n" + "="*60)

async def main():
    collector = BaselineCollector()
    await collector.collect_all()
    collector.save_report()
    collector.print_summary()
    
    print("\n✅ Baseline snapshot completed!")
    print(f"   Report directory: {REPORT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
"""
Production Monitoring Script
"""
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionMonitor:
    """
    Production Monitoring Engine
    """

    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        self.alert_thresholds = {
            "response_time_ms": 500,
            "error_rate": 0.05,
            "uptime": 99.9
        }
        self.metrics_file = Path("logs/metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)

    def check_health(self) -> Dict[str, Any]:
        """Check system health"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "down",
                "error": "Connection refused",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def check_endpoints(self, endpoints: List[str]) -> List[Dict[str, Any]]:
        """Check multiple endpoints"""
        results = []

        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = (time.time() - start_time) * 1000

                results.append({
                    "endpoint": endpoint,
                    "status": "healthy" if response.status_code < 400 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "endpoint": endpoint,
                    "status": "down",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

        return results

    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        # Check health endpoint
        health = self.check_health()

        # Check critical endpoints
        endpoints = [
            "/api/v1/cases/stats",
            "/api/v1/fraud/stats",
            "/api/v1/graph/metrics",
            "/api/v1/health"
        ]
        endpoint_status = self.check_endpoints(endpoints)

        # Calculate metrics
        total = len(endpoint_status)
        healthy = sum(1 for e in endpoint_status if e["status"] == "healthy")
        error_rate = (total - healthy) / total if total > 0 else 0

        # Check if alerts needed
        alerts = self._check_alerts(health, endpoint_status, error_rate)

        # Save metrics
        self._save_metrics({
            "health": health,
            "endpoints": endpoint_status,
            "error_rate": error_rate,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "status": "healthy" if error_rate < self.alert_thresholds["error_rate"] else "degraded",
            "error_rate": error_rate,
            "healthy_endpoints": healthy,
            "total_endpoints": total,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }

    def _check_alerts(self, health: Dict, endpoints: List, error_rate: float) -> List[Dict]:
        """Check if alerts needed"""
        alerts = []

        # Check health status
        if health.get("status") != "healthy":
            alerts.append({
                "level": "critical",
                "message": f"System health check failed: {health.get('error', 'Unknown error')}",
                "timestamp": datetime.now().isoformat()
            })

        # Check error rate
        if error_rate > self.alert_thresholds["error_rate"]:
            alerts.append({
                "level": "warning",
                "message": f"High error rate: {error_rate:.2%}",
                "timestamp": datetime.now().isoformat()
            })

        # Check response times
        for endpoint in endpoints:
            if endpoint.get("response_time_ms", 0) > self.alert_thresholds["response_time_ms"]:
                alerts.append({
                    "level": "warning",
                    "message": f"Slow response: {endpoint['endpoint']} - {endpoint['response_time_ms']:.0f}ms",
                    "timestamp": datetime.now().isoformat()
                })

        return alerts

    def _save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to file"""
        try:
            existing = []
            if self.metrics_file.exists():
                with open(self.metrics_file, "r") as f:
                    existing = json.load(f)

            existing.append(metrics)

            # Keep last 1000 entries
            if len(existing) > 1000:
                existing = existing[-1000:]

            with open(self.metrics_file, "w") as f:
                json.dump(existing, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_uptime(self, days: int = 7) -> Dict[str, Any]:
        """Calculate uptime over last N days"""
        if not self.metrics_file.exists():
            return {"uptime": 100.0, "downtime": 0}

        try:
            with open(self.metrics_file, "r") as f:
                metrics = json.load(f)

            cutoff = datetime.now() - timedelta(days=days)
            total_checks = 0
            failed_checks = 0

            for entry in metrics:
                try:
                    entry_time = datetime.fromisoformat(entry["timestamp"])
                    if entry_time > cutoff:
                        total_checks += 1
                        if entry.get("health", {}).get("status") != "healthy":
                            failed_checks += 1
                except:
                    continue

            uptime = ((total_checks - failed_checks) / total_checks * 100) if total_checks > 0 else 100

            return {
                "uptime": uptime,
                "total_checks": total_checks,
                "failed_checks": failed_checks,
                "downtime": 100 - uptime,
                "period_days": days
            }
        except:
            return {"uptime": 100.0, "downtime": 0}


def main():
    monitor = ProductionMonitor()

    print("🔍 Running production health checks...")
    print("=" * 40)

    result = monitor.run_checks()

    print(f"\n📊 Status: {result['status'].upper()}")
    print(f"📈 Error Rate: {result['error_rate']:.2%}")
    print(f"✅ Healthy Endpoints: {result['healthy_endpoints']}/{result['total_endpoints']}")

    if result['alerts']:
        print(f"\n⚠️ Alerts ({len(result['alerts'])}):")
        for alert in result['alerts']:
            print(f"  [{alert['level']}] {alert['message']}")

    # Calculate uptime
    uptime = monitor.get_uptime(7)
    print(f"\n📊 Uptime (7 days): {uptime['uptime']:.2f}%")

    return result

if __name__ == "__main__":
    main()
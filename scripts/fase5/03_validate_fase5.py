#!/usr/bin/env python3
"""
NEMESIS FASE 5 - Validation Script
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate():
    print("\n" + "="*60)
    print("FASE 5: VALIDATION")
    print("="*60)
    
    errors = []
    
    # 1. Check Metrics
    print("\n[1/6] Checking Metrics...")
    try:
        from backend.telemetry.metrics import (
            MetricsRegistry, counter_inc, gauge_set, histogram_observe, Timer
        )
        registry = MetricsRegistry()
        counter_inc("test_counter", 5)
        gauge_set("test_gauge", 42)
        histogram_observe("test_histogram", 100)
        
        metrics = registry.get_all_metrics()
        assert metrics.get("test_counter", {}).get("value") == 5
        assert metrics.get("test_gauge", {}).get("value") == 42
        print("  [OK] Metrics registry")
    except Exception as e:
        errors.append(f"Metrics: {e}")
    
    # 2. Check Logging
    print("\n[2/6] Checking Logging...")
    try:
        from backend.telemetry.logging import get_logger, set_trace_context
        logger = get_logger("test")
        logger.info("Test log message", extra={"test": "data"})
        set_trace_context("trace-123")
        print("  [OK] Structured logging")
    except Exception as e:
        errors.append(f"Logging: {e}")
    
    # 3. Check Tracing
    print("\n[3/6] Checking Tracing...")
    try:
        from backend.telemetry.tracing import tracer, trace
        with tracer.trace("test_operation"):
            pass
        
        spans = tracer.get_all_spans()
        print(f"  [OK] Distributed tracing ({len(spans)} spans)")
    except Exception as e:
        errors.append(f"Tracing: {e}")
    
    # 4. Check Dashboard
    print("\n[4/6] Checking Dashboard...")
    try:
        from backend.telemetry.dashboard import get_dashboard_data
        data = get_dashboard_data()
        assert "health" in data
        assert "metrics" in data
        print("  [OK] Metrics dashboard")
    except Exception as e:
        errors.append(f"Dashboard: {e}")
    
    # 5. Check Alerts
    print("\n[5/6] Checking Alerts...")
    try:
        from backend.telemetry.alerts import alert_manager, AlertSeverity
        
        # Add test notifier
        def test_notifier(alert):
            print(f"  [NOTIFY] {alert.name}: {alert.message}")
        
        alert_manager.add_notifier(test_notifier)
        
        # Test rule
        def test_condition(metrics):
            return metrics.get("test", 0) > 10
        
        alert_manager.add_rule(
            name="test_alert",
            condition=test_condition,
            severity=AlertSeverity.WARNING,
            message="Test alert triggered",
            interval_seconds=1
        )
        
        alert_manager.check_rules({"test": 15})
        alerts = alert_manager.get_active_alerts()
        print("  [OK] Alerting system")
    except Exception as e:
        errors.append(f"Alerts: {e}")
    
    # 6. Check Exporters
    print("\n[6/6] Checking Exporters...")
    try:
        from backend.telemetry.exporters import PrometheusExporter, FileExporter
        
        prom = PrometheusExporter()
        prom_metrics = prom.get_metrics()
        assert isinstance(prom_metrics, str)
        print("  [OK] Prometheus exporter")
        
        file_exp = FileExporter()
        file_path = file_exp.export("test_export.json")
        assert file_path.exists()
        print("  [OK] File exporter")
        
    except Exception as e:
        errors.append(f"Exporters: {e}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"[ERR] Validation failed: {len(errors)} errors")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("[OK] All validations passed!")
        print("="*60)
        return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
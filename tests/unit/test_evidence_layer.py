"""
Unit tests for Telemetry module
"""

import pytest
from backend.telemetry.metrics import MetricsRegistry, counter_inc, gauge_set, histogram_observe


class TestMetricsRegistry:
    """Test metrics registry"""
    
    def test_counter_increment(self):
        registry = MetricsRegistry()
        registry.reset()
        
        registry.counter("test_counter", value=1)
        registry.counter("test_counter", value=2)
        
        # Counter accumulates values
        assert registry.get_counter("test_counter") >= 3
    
    def test_gauge_set(self):
        registry = MetricsRegistry()
        registry.gauge("test_gauge", 100)
        
        assert registry.get_gauge("test_gauge") == 100
        
        registry.gauge("test_gauge", 50)
        assert registry.get_gauge("test_gauge") == 50
    
    def test_histogram_observe(self):
        registry = MetricsRegistry()
        
        for i in range(100):
            registry.histogram("test_hist", float(i))
        
        stats = registry.get_histogram_stats("test_hist")
        assert stats["count"] == 100
        assert stats["min"] == 0
        assert stats["max"] == 99
    
    def test_get_all_metrics(self):
        registry = MetricsRegistry()
        registry.reset()
        
        registry.counter("counter1", 5)
        registry.gauge("gauge1", 42)
        
        metrics = registry.get_all_metrics()
        assert "counter1" in metrics
        assert "gauge1" in metrics
    
    def test_prometheus_format(self):
        registry = MetricsRegistry()
        registry.reset()
        
        registry.counter("test_counter", 10)
        registry.gauge("test_gauge", 3.14)
        
        output = registry.get_prometheus_format()
        # Check that metric names appear in output
        assert "test_counter" in output
        assert "test_gauge" in output


class TestConvenienceFunctions:
    """Test convenience metric functions"""
    
    def setup_method(self):
        from backend.telemetry.metrics import metrics_registry
        metrics_registry.reset()
    
    def test_counter_inc(self):
        counter_inc("test", 5)
        counter_inc("test", 3)
        
        from backend.telemetry.metrics import metrics_registry
        assert metrics_registry.get_counter("test") >= 8
    
    def test_gauge_set(self):
        gauge_set("test", 100)
        
        from backend.telemetry.metrics import metrics_registry
        assert metrics_registry.get_gauge("test") == 100
    
    def test_histogram_observe(self):
        histogram_observe("test", 50)
        
        from backend.telemetry.metrics import metrics_registry
        stats = metrics_registry.get_histogram_stats("test")
        assert stats["count"] >= 1
        assert stats["sum"] >= 50


class TestTimerContext:
    """Test timer context manager"""
    
    def test_timer_records_duration(self):
        from backend.telemetry.metrics import Timer, metrics_registry
        import time
        
        metrics_registry.reset()
        
        with Timer("test_operation"):
            time.sleep(0.01)
        
        stats = metrics_registry.get_histogram_stats("test_operation")
        assert stats["count"] >= 1
        assert stats["sum"] > 0

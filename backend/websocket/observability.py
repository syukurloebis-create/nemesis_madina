"""
WebSocket Observability - Metrics and Monitoring
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from threading import Lock


@dataclass
class WebSocketMetrics:
    """WebSocket metrics data"""
    connections_opened: int = 0
    connections_closed: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    errors: int = 0


class WebSocketObservability:
    """Collect and expose WebSocket metrics"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._metrics = WebSocketMetrics()
        self._initialized = True
    
    def connection_opened(self):
        """Record connection opened"""
        self._metrics.connections_opened += 1
    
    def connection_closed(self):
        """Record connection closed"""
        self._metrics.connections_closed += 1
    
    def message_sent(self):
        """Record message sent"""
        self._metrics.messages_sent += 1
    
    def message_received(self):
        """Record message received"""
        self._metrics.messages_received += 1
    
    def error_occurred(self):
        """Record error"""
        self._metrics.errors += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "connections_opened": self._metrics.connections_opened,
            "connections_closed": self._metrics.connections_closed,
            "active_connections": self._metrics.connections_opened - self._metrics.connections_closed,
            "messages_sent": self._metrics.messages_sent,
            "messages_received": self._metrics.messages_received,
            "errors": self._metrics.errors
        }
    
    def reset(self):
        """Reset metrics (for testing)"""
        self._metrics = WebSocketMetrics()

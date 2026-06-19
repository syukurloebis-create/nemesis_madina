"""
Alerts - Alerting Rules and Management
"""

from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Alert instance"""
    name: str
    severity: AlertSeverity
    message: str
    status: AlertStatus = AlertStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


class AlertManager:
    """Manage alerting rules and notifications - Singleton"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._rules: List[Dict[str, Any]] = []
        self._alerts: List[Alert] = []
        self._alert_history: List[Alert] = []
        self._notifiers: List[Callable] = []
        self._initialized = True
    
    def add_rule(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: AlertSeverity,
        message: str,
        interval_seconds: int = 60
    ):
        """Add alerting rule"""
        self._rules.append({
            "name": name,
            "condition": condition,
            "severity": severity,
            "message": message,
            "interval": interval_seconds,
            "last_check": datetime.now()
        })
    
    def add_notifier(self, notifier: Callable[[Alert], None]):
        """Add notification handler"""
        self._notifiers.append(notifier)
    
    def check_rules(self, metrics: Dict[str, Any]):
        """Check all alerting rules against current metrics"""
        now = datetime.now()
        
        for rule in self._rules:
            # Check if enough time has passed
            last_check = rule.get("last_check")
            if last_check and (now - last_check).total_seconds() < rule["interval"]:
                continue
            
            rule["last_check"] = now
            condition = rule["condition"]
            
            try:
                if condition(metrics):
                    self._fire_alert(
                        name=rule["name"],
                        severity=rule["severity"],
                        message=rule["message"]
                    )
            except Exception as e:
                self._fire_alert(
                    name=f"alert_check_failed_{rule['name']}",
                    severity=AlertSeverity.ERROR,
                    message=f"Alert rule check failed: {e}"
                )
    
    def _fire_alert(self, name: str, severity: AlertSeverity, message: str):
        """Fire an alert"""
        # Check if alert already exists and is still firing
        existing = self._get_active_alert(name)
        if existing:
            existing.status = AlertStatus.FIRING
            existing.message = message
            return
        
        alert = Alert(
            name=name,
            severity=severity,
            message=message,
            status=AlertStatus.FIRING
        )
        self._alerts.append(alert)
        self._notify(alert)
    
    def _get_active_alert(self, name: str) -> Optional[Alert]:
        """Get active alert by name"""
        for alert in self._alerts:
            if alert.name == name and alert.status in [AlertStatus.PENDING, AlertStatus.FIRING]:
                return alert
        return None
    
    def resolve_alert(self, name: str):
        """Resolve an alert"""
        alert = self._get_active_alert(name)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            self._alert_history.append(alert)
            self._alerts.remove(alert)
            self._notify_resolved(alert)
    
    def _notify(self, alert: Alert):
        """Send notification for alert"""
        for notifier in self._notifiers:
            try:
                notifier(alert)
            except Exception as e:
                print(f"Notifier failed: {e}")
    
    def _notify_resolved(self, alert: Alert):
        """Send resolution notification"""
        # Similar to _notify but with resolved status
        for notifier in self._notifiers:
            try:
                notifier(alert)
            except Exception:
                pass
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently firing alerts"""
        return [
            {
                "name": a.name,
                "severity": a.severity.value,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
                "status": a.status.value
            }
            for a in self._alerts
            if a.status in [AlertStatus.PENDING, AlertStatus.FIRING]
        ]
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        return [
            {
                "name": a.name,
                "severity": a.severity.value,
                "message": a.message,
                "created_at": a.created_at.isoformat(),
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "status": a.status.value
            }
            for a in self._alert_history[-limit:]
        ]


# Default alert rules
def setup_default_alerts(alert_manager: AlertManager):
    """Setup default alerting rules"""
    
    # High error rate alert
    def high_error_rate(metrics):
        error_count = metrics.get("counters", {}).get("errors_total", 0)
        request_count = metrics.get("counters", {}).get("requests_total", 1)
        return error_count / request_count > 0.05
    
    alert_manager.add_rule(
        name="high_error_rate",
        condition=high_error_rate,
        severity=AlertSeverity.CRITICAL,
        message="Error rate exceeds 5% threshold",
        interval_seconds=60
    )
    
    # Slow response alert
    def slow_response(metrics):
        avg_latency = metrics.get("histograms", {}).get("api_latency_ms", {}).get("avg", 0)
        return avg_latency > 500
    
    alert_manager.add_rule(
        name="slow_response",
        condition=slow_response,
        severity=AlertSeverity.WARNING,
        message="API response time exceeds 500ms",
        interval_seconds=120
    )
    
    # Memory high alert
    def high_memory(metrics):
        memory_usage = metrics.get("gauges", {}).get("memory_usage_mb", 0)
        return memory_usage > 1024  # 1GB
    
    alert_manager.add_rule(
        name="high_memory",
        condition=high_memory,
        severity=AlertSeverity.WARNING,
        message="Memory usage exceeds 1GB",
        interval_seconds=60
    )


# Global alert manager
alert_manager = AlertManager()

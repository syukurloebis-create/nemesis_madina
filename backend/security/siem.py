"""
SIEM Integration
Security Information and Event Management
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging
import os
import requests

logger = logging.getLogger(__name__)


class SIEMIntegration:
    """
    SIEM Integration Engine
    """

    def __init__(self):
        self.siem_url = os.getenv("SIEM_URL", "http://siem.local:8080")
        self.siem_api_key = os.getenv("SIEM_API_KEY", "")
        self.enabled = bool(self.siem_api_key)

    def send_event(self, event: Dict[str, Any]) -> bool:
        """Send event to SIEM"""
        if not self.enabled:
            logger.debug("SIEM integration disabled")
            return False

        try:
            headers = {
                "Authorization": f"Bearer {self.siem_api_key}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"{self.siem_url}/api/events",
                json=event,
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"SIEM send failed: {e}")
            return False

    def send_security_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        actor: Optional[str] = None,
        target: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send security event to SIEM"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "actor": actor,
            "target": target,
            "metadata": metadata or {},
            "source": "nemesis-v8.2"
        }
        return self.send_event(event)

    def send_authentication_event(
        self,
        user: str,
        success: bool,
        ip: Optional[str] = None
    ) -> bool:
        """Send authentication event"""
        return self.send_security_event(
            event_type="authentication",
            severity="info" if success else "warning",
            message=f"User {user} {'logged in' if success else 'failed to log in'}",
            actor=user,
            metadata={"ip": ip, "success": success}
        )

    def send_authorization_event(
        self,
        user: str,
        resource: str,
        action: str,
        allowed: bool
    ) -> bool:
        """Send authorization event"""
        return self.send_security_event(
            event_type="authorization",
            severity="warning" if not allowed else "info",
            message=f"User {user} {'allowed' if allowed else 'denied'} {action} on {resource}",
            actor=user,
            target=resource,
            metadata={"action": action, "allowed": allowed}
        )

    def send_ai_event(
        self,
        model: str,
        prediction: float,
        confidence: float,
        case_id: str
    ) -> bool:
        """Send AI event"""
        return self.send_security_event(
            event_type="ai_prediction",
            severity="info",
            message=f"AI prediction for case {case_id}: {prediction:.2%}",
            metadata={
                "model": model,
                "prediction": prediction,
                "confidence": confidence,
                "case_id": case_id
            }
        )
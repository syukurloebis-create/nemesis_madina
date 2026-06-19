"""Webhook Manager - Send notifications to external systems (APIP, BPK, BPKP)"""

import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class WebhookSubscription:
    id: str
    name: str
    url: str
    events: List[str]  # high_risk_finding, evidence_verified, report_ready
    severity_threshold: str  # low, medium, high, critical
    created_at: datetime
    is_active: bool = True

class WebhookManager:
    """Manage webhook subscriptions and deliveries"""
    
    _subscriptions: Dict[str, WebhookSubscription] = {}
    _delivery_logs: List[Dict] = []
    
    def register(
        self,
        name: str,
        url: str,
        events: List[str],
        severity_threshold: str = "medium"
    ) -> Dict:
        """Register a new webhook"""
        import uuid
        webhook_id = str(uuid.uuid4())
        
        subscription = WebhookSubscription(
            id=webhook_id,
            name=name,
            url=url,
            events=events,
            severity_threshold=severity_threshold,
            created_at=datetime.now()
        )
        
        self._subscriptions[webhook_id] = subscription
        
        return {
            "id": webhook_id,
            "name": name,
            "url": url,
            "events": events,
            "severity_threshold": severity_threshold,
            "created_at": subscription.created_at.isoformat()
        }
    
    def unregister(self, webhook_id: str) -> bool:
        """Unregister a webhook"""
        if webhook_id in self._subscriptions:
            del self._subscriptions[webhook_id]
            return True
        return False
    
    async def trigger(
        self,
        event_type: str,
        payload: Dict[str, Any],
        severity: str = "medium"
    ) -> List[Dict]:
        """Trigger webhook for matching subscriptions"""
        results = []
        
        for sub_id, sub in self._subscriptions.items():
            if not sub.is_active:
                continue
            
            # Check if event matches
            if event_type not in sub.events:
                continue
            
            # Check severity threshold
            severity_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            if severity_levels.get(severity, 0) < severity_levels.get(sub.severity_threshold, 0):
                continue
            
            # Send webhook
            result = await self._send_webhook(sub, event_type, payload)
            results.append(result)
        
        return results
    
    async def _send_webhook(
        self,
        subscription: WebhookSubscription,
        event_type: str,
        payload: Dict
    ) -> Dict:
        """Send webhook to subscriber"""
        start_time = datetime.now()
        
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "subscription_id": subscription.id,
            "subscription_name": subscription.name,
            "data": payload
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    subscription.url,
                    json=webhook_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_text = await response.text()
                    success = response.status in [200, 201, 202]
                    
                    delivery_log = {
                        "subscription_id": subscription.id,
                        "subscription_name": subscription.name,
                        "event_type": event_type,
                        "timestamp": start_time.isoformat(),
                        "status_code": response.status,
                        "success": success,
                        "response": response_text[:200]  # Truncate
                    }
                    self._delivery_logs.append(delivery_log)
                    
                    return {
                        "subscription": subscription.name,
                        "success": success,
                        "status_code": response.status,
                        "message": "Delivered" if success else f"Failed with status {response.status}"
                    }
                    
        except asyncio.TimeoutError:
            delivery_log = {
                "subscription_id": subscription.id,
                "subscription_name": subscription.name,
                "event_type": event_type,
                "timestamp": start_time.isoformat(),
                "status_code": None,
                "success": False,
                "error": "Timeout"
            }
            self._delivery_logs.append(delivery_log)
            
            return {
                "subscription": subscription.name,
                "success": False,
                "status_code": None,
                "message": "Timeout after 10 seconds"
            }
            
        except Exception as e:
            delivery_log = {
                "subscription_id": subscription.id,
                "subscription_name": subscription.name,
                "event_type": event_type,
                "timestamp": start_time.isoformat(),
                "status_code": None,
                "success": False,
                "error": str(e)
            }
            self._delivery_logs.append(delivery_log)
            
            return {
                "subscription": subscription.name,
                "success": False,
                "status_code": None,
                "message": f"Error: {str(e)[:100]}"
            }
    
    def get_delivery_status(self, limit: int = 50) -> List[Dict]:
        """Get webhook delivery status"""
        return self._delivery_logs[-limit:]
    
    def get_subscriptions(self) -> List[Dict]:
        """Get all subscriptions"""
        return [
            {
                "id": s.id,
                "name": s.name,
                "url": s.url,
                "events": s.events,
                "severity_threshold": s.severity_threshold,
                "is_active": s.is_active
            }
            for s in self._subscriptions.values()
        ]

# Singleton
webhook_manager = WebhookManager()

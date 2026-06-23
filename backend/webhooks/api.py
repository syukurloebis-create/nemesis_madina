"""Webhook API Endpoints"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from webhooks.manager import webhook_manager

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

class WebhookRegisterRequest(BaseModel):
    name: str
    url: str
    events: List[str]
    severity_threshold: str = "medium"

class TriggerRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    severity: str = "medium"


@router.post("/register")
async def register_webhook(request: WebhookRegisterRequest):
    """Register a new webhook endpoint"""
    result = webhook_manager.register(
        name=request.name,
        url=request.url,
        events=request.events,
        severity_threshold=request.severity_threshold
    )
    
    return {"message": "Webhook registered", "webhook": result}


@router.delete("/{webhook_id}")
async def unregister_webhook(webhook_id: str):
    """Unregister a webhook"""
    success = webhook_manager.unregister(webhook_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {"message": "Webhook unregistered"}


@router.post("/trigger")
async def trigger_webhook(request: TriggerRequest):
    """Manually trigger webhook (for testing)"""
    results = await webhook_manager.trigger(
        event_type=request.event_type,
        payload=request.payload,
        severity=request.severity
    )
    
    return {
        "message": f"Triggered {len(results)} webhooks",
        "results": results
    }


@router.get("/status")
async def get_webhook_status():
    """Get webhook delivery status"""
    return {
        "subscriptions": webhook_manager.get_subscriptions(),
        "recent_deliveries": webhook_manager.get_delivery_status(limit=20)
    }


@router.get("/subscriptions")
async def list_subscriptions():
    """List all webhook subscriptions"""
    return {
        "total": len(webhook_manager._subscriptions),
        "subscriptions": webhook_manager.get_subscriptions()
    }

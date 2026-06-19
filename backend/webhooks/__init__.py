"""Webhook Domain - External Integrations"""

from backend.webhooks.manager import WebhookManager, webhook_manager
from backend.webhooks.api import router

__all__ = ["WebhookManager", "webhook_manager", "router"]

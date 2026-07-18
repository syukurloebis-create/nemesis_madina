"""
Notification Engine
Alert and notification system
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications"""
    ALERT = "alert"
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"


class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SLACK = "slack"


@dataclass
class Notification:
    """Notification structure"""
    id: str
    type: NotificationType
    channel: NotificationChannel
    title: str
    message: str
    recipient: str
    data: Dict[str, Any] = field(default_factory=dict)
    sent_at: datetime = field(default_factory=datetime.now)
    delivered: bool = False
    read_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "channel": self.channel.value,
            "title": self.title,
            "message": self.message,
            "recipient": self.recipient,
            "data": self.data,
            "sent_at": self.sent_at.isoformat(),
            "delivered": self.delivered,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }


class NotificationEngine:
    """
    Notification Engine
    Send and manage notifications
    """

    def __init__(self):
        self.notifications: List[Notification] = []
        self.max_history = 1000
        self._channels: Dict[NotificationChannel, Callable] = {}

    def register_channel(
        self,
        channel: NotificationChannel,
        handler: Callable[[Notification], bool]
    ) -> None:
        """Register a notification channel handler"""
        self._channels[channel] = handler
        logger.info(f"Channel registered: {channel.value}")

    def send(
        self,
        notification: Notification
    ) -> bool:
        """Send a notification"""
        # Store notification
        self.notifications.append(notification)

        if len(self.notifications) > self.max_history:
            self.notifications = self.notifications[-self.max_history:]

        # Send via channel
        if notification.channel in self._channels:
            try:
                result = self._channels[notification.channel](notification)
                notification.delivered = result
                if result:
                    logger.info(f"Notification sent: {notification.id} via {notification.channel.value}")
                else:
                    logger.warning(f"Notification failed: {notification.id} via {notification.channel.value}")
                return result
            except Exception as e:
                logger.error(f"Notification error: {e}")
                return False

        logger.warning(f"No handler for channel: {notification.channel.value}")
        return False

    def send_alert(
        self,
        recipient: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        channels: List[NotificationChannel] = None
    ) -> List[Notification]:
        """Send an alert notification"""
        if channels is None:
            channels = [NotificationChannel.IN_APP, NotificationChannel.EMAIL]

        sent = []
        for channel in channels:
            notification = Notification(
                id=f"notif_{len(self.notifications) + 1}",
                type=NotificationType.ALERT,
                channel=channel,
                title=title,
                message=message,
                recipient=recipient,
                data=data or {}
            )
            self.send(notification)
            sent.append(notification)

        return sent

    def get_notifications(
        self,
        recipient: Optional[str] = None,
        type: Optional[NotificationType] = None,
        delivered: Optional[bool] = None
    ) -> List[Notification]:
        """Get notifications with filters"""
        result = self.notifications

        if recipient:
            result = [n for n in result if n.recipient == recipient]
        if type:
            result = [n for n in result if n.type == type]
        if delivered is not None:
            result = [n for n in result if n.delivered == delivered]

        return result

    def get_unread(self, recipient: str) -> List[Notification]:
        """Get unread notifications for a recipient"""
        return [
            n for n in self.notifications
            if n.recipient == recipient and not n.read_at
        ]

    def mark_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read_at = datetime.now()
                return True
        return False

    def mark_all_read(self, recipient: str) -> int:
        """Mark all notifications as read for a recipient"""
        count = 0
        for notification in self.notifications:
            if notification.recipient == recipient and not notification.read_at:
                notification.read_at = datetime.now()
                count += 1
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        total = len(self.notifications)
        by_type = {}
        by_channel = {}
        delivered = sum(1 for n in self.notifications if n.delivered)

        for notification in self.notifications:
            by_type[notification.type.value] = by_type.get(notification.type.value, 0) + 1
            by_channel[notification.channel.value] = by_channel.get(notification.channel.value, 0) + 1

        return {
            "total_notifications": total,
            "delivered": delivered,
            "delivery_rate": delivered / total if total > 0 else 0,
            "by_type": by_type,
            "by_channel": by_channel
        }


# Singleton instance
notification_engine = NotificationEngine()
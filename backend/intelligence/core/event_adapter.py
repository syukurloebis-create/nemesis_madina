# backend/intelligence/core/event_adapter.py

from typing import Any, Optional


class EventAdapter:

    def __init__(self, event: Any):
        self._event = event

    @property
    def aggregate_id(self) -> Optional[str]:
        return (
            getattr(self._event, "aggregate_id", None)
            or getattr(self._event, "case_id", None)
        )

    @property
    def case_id(self):
        return self.aggregate_id

    @property
    def event_type(self):
        return getattr(self._event, "event_type", None)

    @property
    def payload(self) -> dict:
        return getattr(self._event, "payload", {}) or {}

    @property
    def data(self) -> dict:
        return self.payload

    @property
    def version(self):
        return (
            getattr(self._event, "event_version", None)
            or getattr(self._event, "version", None)
        )

    @property
    def timestamp(self):
        return (
            getattr(self._event, "created_at", None)
            or getattr(self._event, "timestamp", None)
        )

    @property
    def event_hash(self):
        return getattr(self._event, "event_hash", None)

    @property
    def previous_hash(self):
        return getattr(self._event, "previous_hash", None)

    @property
    def id(self):
        return getattr(self._event, "id", None)

    @property
    def created_by(self):
        return getattr(self._event, "created_by", None)

    def raw(self):
        return self._event

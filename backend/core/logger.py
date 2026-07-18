"""
Logger adapter dengan request ID otomatis.
"""

import logging
from typing import Dict, Any

from backend.core.context import get_request_id


class RequestLogger(logging.LoggerAdapter):
    """Logger adapter yang menambahkan request ID otomatis."""

    def process(self, msg, kwargs):
        request_id = get_request_id()
        if request_id:
            msg = f"[req={request_id}] {msg}"
        return msg, kwargs


def get_logger(name: str) -> RequestLogger:
    """Dapatkan logger dengan request ID."""
    logger = logging.getLogger(name)
    return RequestLogger(logger, {})


# Logger untuk berbagai modul
def get_dashboard_logger():
    return get_logger("nemesis.dashboard")


def get_finding_logger():
    return get_logger("nemesis.finding")


def get_engine_logger(engine_name: str):
    return get_logger(f"nemesis.engine.{engine_name}")
"""API Dependencies - Dependency Injection"""

from typing import Optional
from fastapi import Depends

from backend.evidence import EvidenceRegistry
from websocket import ConnectionManager
from backend.core.events import EventBus
from graph import RelationshipGraph


_evidence_registry = None
_connection_manager = None
_event_bus = None
_graph = None


def get_evidence_registry() -> EvidenceRegistry:
    global _evidence_registry
    if _evidence_registry is None:
        _evidence_registry = EvidenceRegistry()
    return _evidence_registry


def get_connection_manager() -> ConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def get_graph() -> RelationshipGraph:
    global _graph
    if _graph is None:
        _graph = RelationshipGraph()
    return _graph

# backend/graph/registry.py

"""
Extractor Registry - Register and manage graph extractors
"""

from typing import Dict, Any, Callable, List, Tuple, Optional

# ✅ Import dari domain canonical
from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.types import NodeType, EdgeType


class ExtractorRegistry:
    """Registry for graph extractors"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._extractors: Dict[str, Callable] = {}
        self._initialized = True

    def register(self, event_type: str, extractor: Callable):
        self._extractors[event_type] = extractor

    def get(self, event_type: str) -> Optional[Callable]:
        return self._extractors.get(event_type)

    def unregister(self, event_type: str) -> bool:
        if event_type in self._extractors:
            del self._extractors[event_type]
            return True
        return False

    def list_extractors(self) -> List[str]:
        return list(self._extractors.keys())

    def has_extractor(self, event_type: str) -> bool:
        return event_type in self._extractors


# Global registry
extractor_registry = ExtractorRegistry()


def register_extractor(event_type: str):
    def decorator(func):
        extractor_registry.register(event_type, func)
        return func
    return decorator


# Default extractors
@register_extractor("entity.created")
def extract_entity_created(event: Dict[str, Any]) -> Tuple[List[GraphNode], List[GraphEdge]]:
    """Extract graph from entity.created event."""
    nodes = []
    edges = []

    entity_id = event.get("entity_id", event.get("id"))
    if entity_id:
        node = GraphNode(
            business_key=entity_id,
            entity_type=NodeType.ENTITY.value,
            name=event.get("entity_type", "unknown"),
            extra_data={
                "name": event.get("name", ""),
                "created_by": event.get("created_by", ""),
                **event.get("metadata", {})
            }
        )
        nodes.append(node)

    return nodes, edges


@register_extractor("transaction.processed")
def extract_transaction_processed(event: Dict[str, Any]) -> Tuple[List[GraphNode], List[GraphEdge]]:
    """Extract graph from transaction.processed event."""
    nodes = []
    edges = []

    source_id = event.get("source_id")
    if source_id:
        source_node = GraphNode(
            business_key=source_id,
            entity_type=NodeType.ENTITY.value,
            name="source",
            extra_data={"name": event.get("source_name", "")}
        )
        nodes.append(source_node)

    target_id = event.get("target_id")
    if target_id:
        target_node = GraphNode(
            business_key=target_id,
            entity_type=NodeType.ENTITY.value,
            name="target",
            extra_data={"name": event.get("target_name", "")}
        )
        nodes.append(target_node)

    if source_id and target_id:
        # ✅ Extractor hanya extraction, tidak normalisasi
        edge = GraphEdge(
            source_key=source_id,
            target_key=target_id,
            relationship_type=EdgeType.INTERACTS.value,
            weight=1.0,
            amount=event.get("amount", 0.0),
            extra_data={
                "currency": event.get("currency", "USD"),
                "timestamp": event.get("timestamp", "")
            }
        )
        edges.append(edge)

    return nodes, edges


@register_extractor("user.action")
def extract_user_action(event: Dict[str, Any]) -> Tuple[List[GraphNode], List[GraphEdge]]:
    """Extract graph from user.action event."""
    nodes = []
    edges = []

    user_id = event.get("user_id")
    if user_id:
        user_node = GraphNode(
            business_key=user_id,
            entity_type=NodeType.USER.value,
            name="user",
            extra_data={"username": event.get("username", "")}
        )
        nodes.append(user_node)

    target_id = event.get("target_id")
    if target_id:
        target_node = GraphNode(
            business_key=target_id,
            entity_type=NodeType.ENTITY.value,
            name="target",
            extra_data={"type": event.get("target_type", "")}
        )
        nodes.append(target_node)

        if user_id:
            edge = GraphEdge(
                source_key=user_id,
                target_key=target_id,
                relationship_type=EdgeType.INTERACTS.value,
                weight=1.0,
                extra_data={
                    "action": event.get("action", "unknown"),
                    "timestamp": event.get("timestamp", "")
                }
            )
            edges.append(edge)

    return nodes, edges
"""
Extractor Registry - Register and manage graph extractors
"""

from typing import Dict, Any, Callable, List, Tuple, Optional
from backend.graph.models import GraphNode, GraphEdge


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
        """Register an extractor for an event type"""
        self._extractors[event_type] = extractor
    
    def get(self, event_type: str) -> Optional[Callable]:
        """Get extractor for event type"""
        return self._extractors.get(event_type)
    
    def unregister(self, event_type: str) -> bool:
        """Unregister an extractor"""
        if event_type in self._extractors:
            del self._extractors[event_type]
            return True
        return False
    
    def list_extractors(self) -> List[str]:
        """List all registered event types"""
        return list(self._extractors.keys())
    
    def has_extractor(self, event_type: str) -> bool:
        """Check if extractor exists for event type"""
        return event_type in self._extractors


# Global registry
extractor_registry = ExtractorRegistry()


def register_extractor(event_type: str):
    """Decorator to register an extractor"""
    def decorator(func):
        extractor_registry.register(event_type, func)
        return func
    return decorator


# Default extractors
@register_extractor("entity.created")
def extract_entity_created(event: Dict[str, Any]) -> Tuple[List[GraphNode], List[GraphEdge]]:
    """Extract graph from entity.created event"""
    nodes = []
    edges = []
    
    # Create entity node
    entity_id = event.get("entity_id", event.get("id"))
    if entity_id:
        from backend.graph.models import GraphNode, NodeType
        node = GraphNode(
            id=entity_id,
            type=NodeType.ENTITY,
            label=event.get("entity_type", "unknown"),
            properties={
                "name": event.get("name", ""),
                "created_by": event.get("created_by", ""),
                **event.get("metadata", {})
            }
        )
        nodes.append(node)
    
    return nodes, edges


@register_extractor("transaction.processed")
def extract_transaction_processed(event: Dict[str, Any]) -> Tuple[List[GraphNode], List[GraphEdge]]:
    """Extract graph from transaction.processed event"""
    from backend.graph.models import GraphNode, GraphEdge, NodeType, EdgeType
    
    nodes = []
    edges = []
    
    # Source node
    source_id = event.get("source_id")
    if source_id:
        source_node = GraphNode(
            id=source_id,
            type=NodeType.ENTITY,
            label="source",
            properties={"name": event.get("source_name", "")}
        )
        nodes.append(source_node)
    
    # Target node
    target_id = event.get("target_id")
    if target_id:
        target_node = GraphNode(
            id=target_id,
            type=NodeType.ENTITY,
            label="target",
            properties={"name": event.get("target_name", "")}
        )
        nodes.append(target_node)
    
    # Transaction edge
    if source_id and target_id:
        edge = GraphEdge(
            source=source_id,
            target=target_id,
            type=EdgeType.INTERACTS,
            weight=event.get("amount", 1.0),
            properties={
                "amount": event.get("amount", 0),
                "currency": event.get("currency", "USD"),
                "timestamp": event.get("timestamp", "")
            }
        )
        edges.append(edge)
    
    return nodes, edges


@register_extractor("user.action")
def extract_user_action(event: Dict[str, Any]) -> Tuple[List[GraphNode], List[GraphEdge]]:
    """Extract graph from user.action event"""
    from backend.graph.models import GraphNode, GraphEdge, NodeType, EdgeType
    
    nodes = []
    edges = []
    
    # User node
    user_id = event.get("user_id")
    if user_id:
        user_node = GraphNode(
            id=user_id,
            type=NodeType.USER,
            label="user",
            properties={"username": event.get("username", "")}
        )
        nodes.append(user_node)
    
    # Target node (if exists)
    target_id = event.get("target_id")
    if target_id:
        target_node = GraphNode(
            id=target_id,
            type=NodeType.ENTITY,
            label="target",
            properties={"type": event.get("target_type", "")}
        )
        nodes.append(target_node)
        
        # Action edge
        if user_id:
            edge = GraphEdge(
                source=user_id,
                target=target_id,
                type=EdgeType.INTERACTS,
                weight=1.0,
                properties={
                    "action": event.get("action", "unknown"),
                    "timestamp": event.get("timestamp", "")
                }
            )
            edges.append(edge)
    
    return nodes, edges
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, Text, Index
from sqlalchemy.sql import func
from backend.database import Base
import uuid

class GraphEntity(Base):
    __tablename__ = "graph_entities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=True)
    institution_id = Column(String, nullable=True)
    entity_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    external_id = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    attributes = Column(JSON, default=dict)
    extra_data = Column(JSON, default=dict)
    risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)


class GraphRelationship(Base):
    __tablename__ = "graph_relationships"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=True)
    institution_id = Column(String, nullable=True)
    source_id = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    amount = Column(Float, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)


class CollusionDetection(Base):
    __tablename__ = "collusion_detections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)
    pattern_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    entity_ids = Column(JSON, default=list)
    entity_names = Column(JSON, default=list)
    pattern_key = Column(String(64), nullable=True)
    confidence = Column(Float, default=0.0)
    severity = Column(Float, default=0.0)
    evidence = Column(JSON, default=dict)
    is_reviewed = Column(Integer, default=0)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())


class GraphMetadata(Base):
    """ORM model for graph_metadata table."""
    
    __tablename__ = "graph_metadata"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    checksum = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    regenerated_by = Column(String, default="system")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    __table_args__ = (
        Index("idx_graph_metadata_case_id", "case_id"),
        Index("idx_graph_metadata_version", "version"),
    )


# ============================================================
# LEGACY COMPATIBILITY WRAPPER
# ============================================================

from backend.graph.domain.node import GraphNode as DomainGraphNode
from backend.graph.domain.edge import GraphEdge as DomainGraphEdge
from backend.graph.domain.types import NodeType, EdgeType


class GraphNode:
    """Legacy compatibility wrapper for GraphNode."""
    
    def __init__(
        self,
        id: str = None,
        type=None,
        label: str = "",
        properties: dict = None,
        **kwargs
    ):
        self._domain = DomainGraphNode(
            business_key=id or str(uuid.uuid4()),
            entity_type=type.value if hasattr(type, 'value') else str(type),
            name=label or "",
            extra_data=properties or {},
        )

    @property
    def id(self) -> str:
        return self._domain.business_key

    @property
    def type(self):
        value = self._domain.entity_type
        try:
            return NodeType(value)
        except ValueError:
            return value

    @property
    def label(self) -> str:
        return self._domain.name

    @property
    def properties(self) -> dict:
        return self._domain.extra_data

    def to_domain(self) -> DomainGraphNode:
        return self._domain


class GraphEdge:
    """Legacy compatibility wrapper for GraphEdge."""
    
    def __init__(
        self,
        source: str = None,
        target: str = None,
        type=None,
        weight: float = 1.0,
        properties: dict = None,
        **kwargs
    ):
        self._domain = DomainGraphEdge(
            source_key=source or "",
            target_key=target or "",
            relationship_type=type.value if hasattr(type, 'value') else str(type),
            weight=weight,
            amount=properties.get("amount") if properties else None,
            extra_data=properties or {},
        )

    @property
    def source(self) -> str:
        return self._domain.source_key

    @property
    def target(self) -> str:
        return self._domain.target_key

    @property
    def type(self):
        value = self._domain.relationship_type
        try:
            return EdgeType(value)
        except ValueError:
            return value

    @property
    def weight(self) -> float:
        return self._domain.weight

    @property
    def properties(self) -> dict:
        return self._domain.extra_data

    def to_domain(self) -> DomainGraphEdge:
        return self._domain


__all__ = [
    # ORM Models
    "GraphEntity",
    "GraphRelationship",
    "CollusionDetection",
    "GraphMetadata",
    # Legacy Compatibility
    "GraphNode",
    "GraphEdge",
    "NodeType",
    "EdgeType",
]
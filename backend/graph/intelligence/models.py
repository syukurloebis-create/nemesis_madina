"""Graph Intelligence Models - Sesuai schema PostgreSQL"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    VENDOR = "vendor"
    OFFICIAL = "official"
    COMPANY = "company"
    PERSON = "person"
    PACKAGE = "package"


class RelationshipType(str, Enum):
    OWNS = "owns"
    CONTROLS = "controls"
    MANAGES = "manages"
    RELATED_TO = "related_to"
    ENDORSED_BY = "endorsed_by"


class EntityNode(BaseModel):
    node_id: str
    entity_type: EntityType
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)


class EntityEdge(BaseModel):
    edge_id: UUID = Field(default_factory=uuid4)
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float = 0.5
    confidence: float = 0.5
    evidence_ids: List[UUID] = Field(default_factory=list)
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)


class NetworkMetrics(BaseModel):
    node_count: int
    edge_count: int
    density: float
    central_nodes: List[Dict[str, Any]]


class CollusionDetectionResult(BaseModel):
    entities: List[str]
    relationship_type: RelationshipType
    score: float
    confidence: float
    detected_at: datetime = Field(default_factory=datetime.now)
